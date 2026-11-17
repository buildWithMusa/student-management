from django.urls import path,include
from snippets import views
from rest_framework.routers import DefaultRouter

router=DefaultRouter()
router.register(r"students",views.StudentViewSet,basename="student")
router.register(r"users",views.UserViewSet,basename="user")

urlpatterns = [
    path("student-login/", views.student_login, name="student-login"),
    path("student-dashboard/", views.student_dashboard, name="student-dashboard"),
    path("student-results/", views.student_results, name="student-results"),
    path("", include(router.urls)),
]
