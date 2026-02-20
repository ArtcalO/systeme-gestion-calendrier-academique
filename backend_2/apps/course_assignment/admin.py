from django.contrib import admin
from .models import CourseAssignment, TeachingLoadReport, AssignmentAlgorithmRun


@admin.register(CourseAssignment)
class CourseAssignmentAdmin(admin.ModelAdmin):
    list_display = ['course', 'professor', 'status', 'assignment_method', 'score', 'assigned_date']
    list_filter = ['status', 'assignment_method', 'course__academic_year']
    search_fields = ['course__module__name', 'professor__user__last_name']
    readonly_fields = ['assigned_date', 'confirmed_date', 'score']


@admin.register(TeachingLoadReport)
class TeachingLoadReportAdmin(admin.ModelAdmin):
    list_display = ['professor', 'academic_year', 'semester', 'total_weekly_hours', 'load_percentage']
    list_filter = ['academic_year', 'semester']


@admin.register(AssignmentAlgorithmRun)
class AssignmentAlgorithmRunAdmin(admin.ModelAdmin):
    list_display = ['id', 'academic_year', 'semester', 'status', 'courses_assigned',
                    'courses_total', 'execution_time_ms', 'started_at']
    list_filter = ['status', 'academic_year']
    readonly_fields = ['started_at', 'completed_at']
