from django.contrib.auth.models import User
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from snippets.models import Student
from snippets.serializers import StudentSerializer, UserSerializer
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