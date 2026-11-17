from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.decorators import authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from snippets.models import Student, Result
from snippets.serializers import StudentSerializer, UserSerializer, ResultSerializer
from snippets.permissions import IsOwnerOrReadOnly

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

    results = Result.objects.filter(student=student).order_by(
        "academic_year", "semester", "unit_name"
    )

    serializer = ResultSerializer(results, many=True)
    return Response(serializer.data)
