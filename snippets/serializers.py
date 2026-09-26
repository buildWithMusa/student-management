from django.contrib.auth.models import User
from rest_framework import serializers
from snippets.models import Student


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