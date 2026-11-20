from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.shortcuts import render
from django.utils import timezone
import csv
import io
from rest_framework.decorators import authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from snippets.models import Student, Result, Lecturer, Unit, UnitRegistration
from snippets.serializers import (
    StudentSerializer,
    UserSerializer,
    ResultSerializer,
    BulkStudentUploadSerializer,
    UnitSerializer,
    UnitRegistrationSerializer,
)
from snippets.permissions import IsOwnerOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import parser_classes

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly
    ]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["get"])
    def profile(self, request, pk=None):
        student = self.get_object()

        return Response({
            "name": student.name,
            "course": student.course,
            "reg_number": student.reg_number,
            "email": student.email,
        })


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
@api_view(["POST"])
@permission_classes([AllowAny])
def student_login(request):
    reg_number = request.data.get("reg_number")
    password = request.data.get("password")

    if not reg_number or not password:
        return Response(
            {"error": "Registration number and password are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        student = Student.objects.get(reg_number=reg_number)
    except (Student.DoesNotExist, ValueError):
        return Response(
            {"error": "Invalid registration number or password."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    user = authenticate(
        username=student.owner.username,
        password=password
    )

    if user is None or user.id != student.owner_id:
        return Response(
            {"error": "Invalid registration number or password."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    token, created = Token.objects.get_or_create(user=user)

    return Response({
        "token": token.key,
        "student": {
            "name": student.name,
            "reg_number": student.reg_number,
            "email": student.email,
            "course": student.course
        }
    })

@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def lecturer_login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"error": "Username and password are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(
        username=username,
        password=password
    )

    if user is None:
        return Response(
            {"error": "Invalid username or password."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    try:
        lecturer = Lecturer.objects.get(user=user)
    except Lecturer.DoesNotExist:
        return Response(
            {"error": "This account is not registered as a lecturer."},
            status=status.HTTP_403_FORBIDDEN
        )

    token, created = Token.objects.get_or_create(user=user)

    units = lecturer.units.values(
        "unit_code",
        "unit_name"
    )

    return Response({
        "message": "Lecturer login successful.",
        "token": token.key,
        "lecturer": {
            "username": user.username,
            "staff_number": lecturer.staff_number,
            "units": list(units)
        }
    })

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def lecturer_dashboard(request):

    try:
        lecturer = Lecturer.objects.get(user=request.user)

    except Lecturer.DoesNotExist:
        return Response(
            {"error": "Lecturer profile not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    units = lecturer.units.values(
        "id",
        "unit_code",
        "unit_name"
    )

    return Response({
        "username": lecturer.user.username,
        "staff_number": lecturer.staff_number,
        "total_units": lecturer.units.count(),
        "units": list(units)
    })


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def student_dashboard(request):
    try:
        student = Student.objects.get(owner=request.user)
    except Student.DoesNotExist:
        return Response(
            {"error": "No student profile found."},
            status=status.HTTP_404_NOT_FOUND
        )

    return Response({
        "name": student.name,
        "reg_number": student.reg_number,
        "email": student.email,
        "course": student.course
    })

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def student_results(request):
    try:
        student = Student.objects.get(owner=request.user)
    except Student.DoesNotExist:
        return Response(
            {"error": "No student profile found."},
            status=status.HTTP_404_NOT_FOUND
        )

    results = Result.objects.filter(
    student=student,
    status="APPROVED"
).order_by(
    "academic_year", "semester", "unit_name"
)

    serializer = ResultSerializer(results, many=True)
    return Response(serializer.data)

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def student_available_units(request):
    try:
        student = Student.objects.get(owner=request.user)
    except Student.DoesNotExist:
        return Response(
            {"error": "No student profile found."},
            status=status.HTTP_404_NOT_FOUND
        )

    units = Unit.objects.filter(
        course=student.course
    ).order_by("year_of_study", "unit_type", "unit_code")

    serializer = UnitSerializer(units, many=True)
    return Response(serializer.data)



@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def student_register_units(request):
    try:
        student = Student.objects.get(owner=request.user)
    except Student.DoesNotExist:
        return Response(
            {"error": "No student profile found."},
            status=status.HTTP_404_NOT_FOUND
        )

    unit_ids = request.data.get("unit_ids")

    if not isinstance(unit_ids, list) or not unit_ids:
        return Response(
            {"error": "Please provide a list of unit IDs."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(unit_ids) != len(set(unit_ids)):
        return Response(
            {"error": "Duplicate unit IDs are not allowed."},
            status=status.HTTP_400_BAD_REQUEST
        )

    units = Unit.objects.filter(
        id__in=unit_ids,
        course=student.course
    )

    if units.count() != len(unit_ids):
        return Response(
            {"error": "One or more units are invalid or unavailable for your course."},
            status=status.HTTP_400_BAD_REQUEST
        )

    with transaction.atomic():
        registrations = []

        for unit in units:
            registration, created = UnitRegistration.objects.get_or_create(
                student=student,
                unit=unit,
                defaults={"status": "PENDING"}
            )

            if not created and registration.status == "REJECTED":
                registration.status = "PENDING"
                registration.rejection_reason = ""
                registration.reviewed_by = None
                registration.reviewed_at = None
                registration.save()

            elif not created:
                return Response(
                    {
                        "error": f"You have already registered for {unit.unit_code}."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            registrations.append(registration)

    serializer = UnitRegistrationSerializer(registrations, many=True)

    return Response(
        {
            "message": "Unit registrations submitted successfully.",
            "registrations": serializer.data
        },
        status=status.HTTP_201_CREATED
    )

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def student_unit_registrations(request):
    try:
        student = Student.objects.get(owner=request.user)
    except Student.DoesNotExist:
        return Response(
            {"error": "No student profile found."},
            status=status.HTTP_404_NOT_FOUND
        )

    registrations = UnitRegistration.objects.filter(
        student=student
    ).select_related(
        "unit", "reviewed_by"
    ).order_by("unit__unit_code")

    serializer = UnitRegistrationSerializer(
        registrations,
        many=True
    )

    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAdminUser])
def pending_unit_registrations(request):
    registrations = UnitRegistration.objects.filter(
        status="PENDING"
    ).select_related(
        "student", "unit"
    ).order_by("submitted_at")

    serializer = UnitRegistrationSerializer(
        registrations,
        many=True
    )

    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAdminUser])
def review_unit_registration(request, registration_id):
    try:
        registration = UnitRegistration.objects.get(
            id=registration_id
        )
    except UnitRegistration.DoesNotExist:
        return Response(
            {"error": "Unit registration not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    decision = request.data.get("decision")

    if decision not in ["APPROVED", "REJECTED"]:
        return Response(
            {"error": "Decision must be APPROVED or REJECTED."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if registration.status != "PENDING":
        return Response(
            {"error": "This registration has already been reviewed."},
            status=status.HTTP_400_BAD_REQUEST
        )

    rejection_reason = request.data.get("rejection_reason", "")

    if decision == "REJECTED" and not rejection_reason.strip():
        return Response(
            {"error": "Please provide a rejection reason."},
            status=status.HTTP_400_BAD_REQUEST
        )

    registration.status = decision
    registration.reviewed_by = request.user
    registration.reviewed_at = timezone.now()
    registration.rejection_reason = (
        rejection_reason if decision == "REJECTED" else ""
    )

    registration.save()

    serializer = UnitRegistrationSerializer(registration)

    return Response({
        "message": f"Unit registration {decision.lower()} successfully.",
        "registration": serializer.data
    })




def register_student(request):
    name = request.data.get("name")
    reg_number = request.data.get("reg_number")
    email = request.data.get("email")
    course = request.data.get("course")

    if not all([name, reg_number, email, course]):
        return Response(
            {"error": "All student details are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    reg_number = str(reg_number).strip().upper()

    # Generate username and initial password
    username = reg_number
    initial_password = reg_number[:1].upper() + reg_number[1:].lower()

    if Student.objects.filter(reg_number__iexact=reg_number).exists():
        return Response(
            {"error": "This registration number already exists."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username__iexact=username).exists():
        return Response(
            {"error": "This username already exists."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=initial_password
            )

            student = Student.objects.create(
                name=name,
                reg_number=reg_number,
                email=email,
                course=course,
                owner=user
            )

        return Response({
            "message": "Student registered successfully.",
            "student": {
                "name": student.name,
                "reg_number": student.reg_number,
                "username": username,
                "initial_password": initial_password
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response(
        {"error": str(e)},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["POST"])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def bulk_register_students(request):
    serializer = BulkStudentUploadSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    uploaded_file = serializer.validated_data["file"]

    if not uploaded_file.name.lower().endswith(".csv"):
        return Response(
            {"error": "Only CSV files are allowed."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        content = uploaded_file.read().decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(content))

        required_columns = {"name", "reg_number", "email", "course"}

        if not reader.fieldnames or not required_columns.issubset(
            {column.strip().lower() for column in reader.fieldnames}
        ):
            return Response(
                {"error": "CSV must contain name, reg_number, email and course columns."},
                status=status.HTTP_400_BAD_REQUEST
            )

        created_count = 0
        failed_rows = []

        for row_number, row in enumerate(reader, start=2):
            try:
                row = {
                    key.strip().lower(): (value or "").strip()
                    for key, value in row.items()
                    if key
                }

                name = row.get("name", "")
                reg_number = row.get("reg_number", "").upper()
                email = row.get("email", "")
                course = row.get("course", "")

                if not all([name, reg_number, email, course]):
                    raise ValueError("Missing student details.")

                username = reg_number
                initial_password = (
                    reg_number[:1].upper() + reg_number[1:].lower()
                )

                if Student.objects.filter(reg_number__iexact=reg_number).exists():
                    raise ValueError("Registration number already exists.")

                if Student.objects.filter(email__iexact=email).exists():
                    raise ValueError("Email already exists.")

                if User.objects.filter(username__iexact=username).exists():
                    raise ValueError("Username already exists.")

                with transaction.atomic():
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=initial_password
                    )

                    Student.objects.create(
                        name=name,
                        reg_number=reg_number,
                        email=email,
                        course=course,
                        owner=user
                    )

                created_count += 1

            except Exception as error:
                failed_rows.append({
                    "row": row_number,
                    "error": str(error)
                })

        return Response({
            "message": "Bulk registration completed.",
            "created": created_count,
            "failed": len(failed_rows),
            "failed_rows": failed_rows
        }, status=status.HTTP_200_OK)

    except (UnicodeDecodeError, csv.Error):
        return Response(
            {"error": "Unable to read the CSV file. Check its format."},
            status=status.HTTP_400_BAD_REQUEST
        )
def bulk_register_page(request):
    if not request.user.is_staff:
        return Response(
            {"error": "Administrator access required."},
            status=status.HTTP_403_FORBIDDEN
        )

    return render(request, "snippets/bulk_register.html")
@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return HttpResponseForbidden(
            "Only administrators can access this page."
        )

    total_students = Student.objects.count()
    total_results = Result.objects.count()

    return render(request, "snippets/admin_dashboard.html", {
        "total_students": total_students,
        "total_results": total_results,
    })
@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def lecturer_submit_result(request):

    # Confirm that the logged-in user is a lecturer
    try:
        lecturer = Lecturer.objects.get(user=request.user)
    except Lecturer.DoesNotExist:
        return Response(
            {"error": "Only registered lecturers can submit marks."},
            status=status.HTTP_403_FORBIDDEN
        )

    # Get submitted information
    reg_number = request.data.get("reg_number")
    unit_id = request.data.get("unit_id")
    marks = request.data.get("marks")
    semester = request.data.get("semester")
    academic_year = request.data.get("academic_year")

    if not all([reg_number, unit_id, marks, semester, academic_year]):
        return Response(
            {"error": "All fields are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Find the student
    try:
        student = Student.objects.get(reg_number=reg_number)
    except Student.DoesNotExist:
        return Response(
            {"error": "Student not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    # Find the unit
    try:
        unit = Unit.objects.get(id=unit_id)
    except Unit.DoesNotExist:
        return Response(
            {"error": "Unit not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    # Confirm that this lecturer teaches the unit
    if not lecturer.units.filter(id=unit.id).exists():
        return Response(
            {"error": "You are not assigned to this unit."},
            status=status.HTTP_403_FORBIDDEN
        )

    # Validate marks
    try:
        marks = float(marks)
    except (ValueError, TypeError):
        return Response(
            {"error": "Marks must be a number."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if marks < 0 or marks > 100:
        return Response(
            {"error": "Marks must be between 0 and 100."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check whether a result already exists
    existing_result = Result.objects.filter(
        student=student,
        unit_name=unit.unit_name,
        semester=semester,
        academic_year=academic_year
    ).first()

    if existing_result:
        if existing_result.status != "REJECTED":
            return Response(
                {"error": "A result already exists for this student and unit."},
                status=status.HTTP_409_CONFLICT
            )

        # Allow correction of rejected marks
        existing_result.marks = marks
        existing_result.status = "PENDING"
        existing_result.submitted_by = request.user
        existing_result.approved_by = None
        existing_result.approved_at = None
        existing_result.rejection_reason = ""
        existing_result.save()

        return Response(
            {"message": "Corrected marks resubmitted for approval."},
            status=status.HTTP_200_OK
        )

    # Create a new pending result
    result = Result.objects.create(
        student=student,
        unit_name=unit.unit_name,
        marks=marks,
        semester=semester,
        academic_year=academic_year,
        status="PENDING",
        submitted_by=request.user
    )

    return Response(
        {
            "message": "Marks submitted successfully for admin approval.",
            "result_id": result.id,
            "student": student.name,
            "unit": unit.unit_name,
            "marks": result.marks,
            "status": result.status
        },
        status=status.HTTP_201_CREATED
    )
def lecturer_login_page(request):
    return render(request, "snippets/lecturer_login.html")


def lecturer_dashboard_page(request):
    return render(request, "snippets/lecturer_dashboard.html")
@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def pending_results(request):

    results = Result.objects.filter(
        status="PENDING"
    ).order_by("-created")

    serializer = ResultSerializer(results, many=True)

    return Response(serializer.data)
@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def review_result(request, result_id):

    try:
        result = Result.objects.get(id=result_id)
    except Result.DoesNotExist:
        return Response(
            {"error": "Result not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    action = request.data.get("action")

    if action == "approve":

        if result.status != "PENDING":
            return Response(
                {"error": "Only pending results can be approved."},
                status=status.HTTP_400_BAD_REQUEST
            )

        result.status = "APPROVED"
        result.approved_by = request.user
        result.approved_at = timezone.now()
        result.rejection_reason = ""

    elif action == "reject":

        reason = request.data.get("reason", "").strip()

        if result.status != "PENDING":
            return Response(
                {"error": "Only pending results can be rejected."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not reason:
            return Response(
                {"error": "Please provide a rejection reason."},
                status=status.HTTP_400_BAD_REQUEST
            )

        result.status = "REJECTED"
        result.approved_by = None
        result.approved_at = None
        result.rejection_reason = reason

    else:
        return Response(
            {"error": "Action must be approve or reject."},
            status=status.HTTP_400_BAD_REQUEST
        )

    result.save()

    return Response({
        "message": f"Result {action}d successfully.",
        "result_id": result.id,
        "status": result.status
    })


