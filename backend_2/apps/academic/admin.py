from django.contrib import admin
from .models import (Faculty, Department, Program, Level, Subject, Module,
                     AcademicYear, Course, Room, StudentModuleResult)


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'dean']
    search_fields = ['name', 'code']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'faculty']
    list_filter = ['faculty']
    search_fields = ['name', 'code']


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'program_type', 'department', 'is_active']
    list_filter = ['program_type', 'department', 'is_active']
    search_fields = ['name', 'code']


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ['name', 'program', 'year_number']
    list_filter = ['program']


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'level', 'semester', 'credits', 'weekly_hours', 'is_mandatory']
    list_filter = ['level', 'semester', 'module_type', 'is_mandatory']
    search_fields = ['name', 'code']
    filter_horizontal = ['prerequisites']


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_current', 'is_enrollment_open']
    list_filter = ['is_current']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['module', 'academic_year', 'semester', 'weekly_hours', 'status']
    list_filter = ['academic_year', 'semester', 'status']
    search_fields = ['module__name', 'module__code']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'room_type', 'capacity', 'building', 'is_available']
    list_filter = ['room_type', 'building', 'is_available']
    search_fields = ['name', 'code']


@admin.register(StudentModuleResult)
class StudentModuleResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'module', 'academic_year', 'grade', 'is_validated']
    list_filter = ['is_validated', 'academic_year', 'semester']
    search_fields = ['student__registration_number', 'module__code']
