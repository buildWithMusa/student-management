from django.urls import path,include
from snippets import views
from rest_framework.routers import DefaultRouter

router=DefaultRouter()
router.register(r"students",views.StudentViewSet,basename="student")
router.register(r"users",views.UserViewSet,basename="user")

urlpatterns = [
    path("student-login/", views.student_login, name="student-login"),
    path("lecturer-login/", views.lecturer_login, name="lecturer-login"),
    path("student-dashboard/", views.student_dashboard, name="student-dashboard"),
    path("student-results/", views.student_results, name="student-results"),
    path("register-student/", views.register_student, name="register-student"),
    path("bulk-register-students/", views.bulk_register_students, name="bulk-register-students"),
    path(
    "bulk-register-page/",
    views.bulk_register_page,
    name="bulk-register-page"
),
path(
    "admin-dashboard/",
    views.admin_dashboard,
    name="admin-dashboard"
),
path(
    "lecturer-dashboard/",
    views.lecturer_dashboard,
    name="lecturer-dashboard"
),
path(
    "lecturer-submit-result/",
    views.lecturer_submit_result,
    name="lecturer-submit-result"
),
path(
    "lecturer-login-page/",
    views.lecturer_login_page,
    name="lecturer-login-page"
),
path(
    "lecturer-dashboard-page/",
    views.lecturer_dashboard_page,
    name="lecturer-dashboard-page"
),
path(
    "pending-results/",
    views.pending_results,
    name="pending-results"
),
path(
    "review-result/<int:result_id>/",
    views.review_result,
    name="review-result"
),
path(
    "student-available-units/",
    views.student_available_units,
    name="student-available-units"
),
path(
    "student-register-units/",
    views.student_register_units,
    name="student-register-units"
),
path(
    "student-unit-registrations/",
    views.student_unit_registrations,
    name="student-unit-registrations"
),
path(
    "pending-unit-registrations/",
    views.pending_unit_registrations,
    name="pending-unit-registrations"
),
path(
    "review-unit-registration/<int:registration_id>/",
    views.review_unit_registration,
    name="review-unit-registration"
),

    path("", include(router.urls)),
]
