from django.db import models
# make a model class

class Student(models.Model):
    name=models.CharField(max_length=300)
    reg_number=models.IntegerField(unique=True)
    email=models.EmailField(unique=True)
    course=models.CharField(max_length=200)
    created=models.DateTimeField(auto_now_add=True)

    owner=models.ForeignKey(
        "auth.User",
        related_name="students",
        on_delete=models.CASCADE
    )
    def __str__(self):
        return self.name

class Result(models.Model):
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

