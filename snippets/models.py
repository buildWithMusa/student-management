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

