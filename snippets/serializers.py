from django.contrib.auth.models import User
from rest_framework import serializers

from snippets.models import Student, Result


class StudentSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.HyperlinkedRelatedField(
        view_name="user-detail",
        read_only=True
    )

    class Meta:
        model = Student
        fields = [
            "id",
            "name",
            "reg_number",
            "course",
            "email",
            "created",
            "owner",
        ]
        read_only_fields = ["owner"]


class UserSerializer(serializers.HyperlinkedModelSerializer):
    students = serializers.HyperlinkedRelatedField(
        many=True,
        view_name="student-detail",
        read_only=True
    )

    class Meta:
        model = User
        fields = ["url", "id", "username", "students"]


class ResultSerializer(serializers.ModelSerializer):
    grade = serializers.ReadOnlyField()
    description = serializers.ReadOnlyField()

    submitted_by = serializers.StringRelatedField(read_only=True)
    approved_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Result
        fields = [
            "id",
            "student",
            "unit_name",
            "marks",
            "grade",
            "description",
            "semester",
            "academic_year",
            "status",
            "submitted_by",
            "approved_by",
            "approved_at",
            "rejection_reason",
            "created",
        ]

        read_only_fields = [
            "id",
            "created",
            "grade",
            "description",
            "status",
            "submitted_by",
            "approved_by",
            "approved_at",
            "rejection_reason",
        ]


class BulkStudentUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
