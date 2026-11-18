from django.contrib import admin
from .models import Student, Result, Unit, Lecturer


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("name", "reg_number", "email", "course", "owner")
    search_fields = ("name", "reg_number", "email")
    list_filter = ("course",)


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("unit_code", "unit_name")
    search_fields = ("unit_code", "unit_name")


@admin.register(Lecturer)
class LecturerAdmin(admin.ModelAdmin):
    list_display = ("staff_number", "user")
    search_fields = ("staff_number", "user__username")
    filter_horizontal = ("units",)


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "unit_name",
        "marks",
        "semester",
        "academic_year",
        "status",
        "submitted_by",
        "approved_by",
    )

    search_fields = (
        "student__name",
        "student__reg_number",
        "unit_name",
    )

    list_filter = (
        "semester",
        "academic_year",
        "status",
    )
