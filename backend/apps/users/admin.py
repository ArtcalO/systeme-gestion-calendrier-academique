from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Professor, Student


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Informations ULT', {'fields': ('role', 'phone', 'employee_id', 'address', 'photo')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations ULT', {'fields': ('role', 'phone', 'employee_id')}),
    )


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ['user', 'grade', 'department', 'max_weekly_hours', 'is_available']
    list_filter = ['grade', 'department', 'is_available']
    search_fields = ['user__first_name', 'user__last_name', 'user__employee_id']
    filter_horizontal = ['specialities']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['registration_number', 'user', 'program', 'current_level',
                    'enrollment_year', 'status']
    list_filter = ['program', 'status', 'enrollment_year']
    search_fields = ['registration_number', 'user__first_name', 'user__last_name']
