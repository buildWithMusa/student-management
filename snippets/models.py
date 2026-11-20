
from django.db import models
from django.conf import settings


class Student(models.Model):
    name = models.CharField(max_length=300)
    reg_number = models.CharField(max_length=34, unique=True)
    email = models.EmailField(unique=True)
    course = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)

    owner = models.ForeignKey(
        "auth.User",
        related_name="students",
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Unit(models.Model):

    UNIT_TYPES = [
        ("CORE", "Core"),
        ("ELECTIVE", "Elective"),
    ]

    unit_code = models.CharField(max_length=30, unique=True)
    unit_name = models.CharField(max_length=200)

    course = models.CharField(
        max_length=200,
        default="BSc Information Technology"
    )

    year_of_study = models.PositiveSmallIntegerField(default=3)

    semester = models.CharField(
        max_length=50,
        default="Semester One"
    )

    academic_year = models.CharField(
        max_length=20,
        default="2026/2027"
    )

    unit_type = models.CharField(
        max_length=10,
        choices=UNIT_TYPES,
        default="CORE"
    )

    def __str__(self):
        return f"{self.unit_code} - {self.unit_name}"


class UnitRegistration(models.Model):

    REGISTRATION_STATUS = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]

    student = models.ForeignKey(
        Student,
        related_name="unit_registrations",
        on_delete=models.CASCADE
    )

    unit = models.ForeignKey(
        Unit,
        related_name="registrations",
        on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=10,
        choices=REGISTRATION_STATUS,
        default="PENDING"
    )

    submitted_at = models.DateTimeField(auto_now_add=True)

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="reviewed_unit_registrations",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    reviewed_at = models.DateTimeField(null=True, blank=True)

    rejection_reason = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "unit"],
                name="unique_student_unit_registration"
            )
        ]

    def __str__(self):
        return f"{self.student.name} - {self.unit.unit_code}"



class Lecturer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="lecturer_profile",
        on_delete=models.CASCADE
    )

    staff_number = models.CharField(max_length=34, unique=True)

    units = models.ManyToManyField(
        Unit,
        related_name="lecturers",
        blank=True
    )

    def __str__(self):
        return f"{self.staff_number} - {self.user.username}"


class Result(models.Model):

    APPROVAL_STATUS = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]

    student = models.ForeignKey(
        Student,
        related_name="results",
        on_delete=models.CASCADE
    )

    unit_name = models.CharField(max_length=200)

    marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    semester = models.CharField(max_length=50)
    academic_year = models.CharField(max_length=20)

    status = models.CharField(
        max_length=10,
        choices=APPROVAL_STATUS,
        default="PENDING"
    )

    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="submitted_results",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="approved_results",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    approved_at = models.DateTimeField(null=True, blank=True)

    rejection_reason = models.TextField(blank=True)

    created = models.DateTimeField(auto_now_add=True)

    @property
    def grade(self):
        if self.marks is None:
            return "I"
        elif self.marks < 40:
            return "GRA"
        elif self.marks < 50:
            return "D"
        elif self.marks < 60:
            return "C"
        elif self.marks <= 70:
            return "B"
        else:
            return "A"

    @property
    def description(self):
        descriptions = {
            "A": "Excellent",
            "B": "Very Good",
            "C": "Good",
            "D": "Pass",
            "GRA": "Special Examination",
            "I": "Missing Mark"
        }

        return descriptions[self.grade]

    def __str__(self):
        return f"{self.student.name} - {self.unit_name}"
