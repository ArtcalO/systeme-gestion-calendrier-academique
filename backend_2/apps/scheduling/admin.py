from django.contrib import admin
from .models import TimeSlot, ScheduleSlot, Schedule, ScheduleConflict


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['get_day_of_week_display', 'start_time', 'end_time', 'label', 'is_active']
    list_filter = ['day_of_week', 'is_active']


@admin.register(ScheduleSlot)
class ScheduleSlotAdmin(admin.ModelAdmin):
    list_display = ['course', 'professor', 'room', 'time_slot', 'week_reference', 'status']
    list_filter = ['status', 'slot_type', 'week_reference']
    search_fields = ['course__module__code', 'professor__user__last_name', 'room__code']


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'academic_year', 'semester', 'status', 'generated_at']
    list_filter = ['status', 'academic_year', 'semester']
    readonly_fields = ['generated_at']


@admin.register(ScheduleConflict)
class ScheduleConflictAdmin(admin.ModelAdmin):
    list_display = ['conflict_type', 'schedule', 'description', 'is_resolved']
    list_filter = ['conflict_type', 'is_resolved']
