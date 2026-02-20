from django.contrib import admin
from .models import ModulePrerequisite, EnrollmentRequest, PrerequisiteCheckResult


@admin.register(ModulePrerequisite)
class ModulePrerequisiteAdmin(admin.ModelAdmin):
    list_display = ['module', 'prerequisite', 'prerequisite_type', 'minimum_grade']
    list_filter = ['prerequisite_type']
    search_fields = ['module__code', 'prerequisite__code']


@admin.register(EnrollmentRequest)
class EnrollmentRequestAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'request_date', 'status', 'processed_by']
    list_filter = ['status']
    search_fields = ['student__registration_number', 'course__module__code']
    readonly_fields = ['request_date', 'processed_date']


@admin.register(PrerequisiteCheckResult)
class PrerequisiteCheckResultAdmin(admin.ModelAdmin):
    list_display = ['enrollment_request', 'all_prerequisites_met', 'checked_at']
    list_filter = ['all_prerequisites_met']
