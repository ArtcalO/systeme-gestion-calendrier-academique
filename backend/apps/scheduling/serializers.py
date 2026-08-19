from rest_framework import serializers
from .models import TimeSlot, ScheduleSlot, Schedule, ScheduleConflict


class TimeSlotSerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)
    duration = serializers.SerializerMethodField()

    class Meta:
        model = TimeSlot
        fields = ['id', 'day_of_week', 'day_name', 'start_time', 'end_time',
                  'label', 'is_active', 'duration']

    def get_duration(self, obj):
        return obj.duration_hours()


class ScheduleSlotSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.module.name', read_only=True)
    course_code = serializers.CharField(source='course.module.code', read_only=True)
    professor_name = serializers.CharField(source='professor.user.get_full_name', read_only=True)
    room_code = serializers.CharField(source='room.code', read_only=True)
    room_capacity = serializers.IntegerField(source='room.capacity', read_only=True)
    time_slot_info = TimeSlotSerializer(source='time_slot', read_only=True)
    level_name = serializers.CharField(source='course.module.level.name', read_only=True)

    class Meta:
        model = ScheduleSlot
        fields = ['id', 'course', 'course_name', 'course_code', 'level_name',
                  'professor', 'professor_name', 'room', 'room_code', 'room_capacity',
                  'time_slot', 'time_slot_info', 'week_reference', 'slot_type',
                  'status', 'notes', 'created_at']


class ScheduleConflictSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleConflict
        fields = ['id', 'conflict_type', 'slot_1', 'slot_2', 'description',
                  'is_resolved', 'resolution_notes']


class ScheduleSerializer(serializers.ModelSerializer):
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    level_name = serializers.CharField(source='level.name', read_only=True)
    program_name = serializers.CharField(source='level.program.name', read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.get_full_name', read_only=True)
    conflicts_count = serializers.SerializerMethodField()
    slots_count = serializers.SerializerMethodField()

    class Meta:
        model = Schedule
        fields = ['id', 'name', 'academic_year', 'academic_year_name', 'semester',
                  'level', 'level_name', 'program_name', 'status', 'week_start',
                  'week_end', 'generated_at', 'generated_by_name',
                  'conflicts_count', 'slots_count', 'generation_log']

    def get_conflicts_count(self, obj):
        return obj.conflicts.filter(is_resolved=False).count()

    def get_slots_count(self, obj):
        return ScheduleSlot.objects.filter(
            course__academic_year=obj.academic_year,
            course__module__level=obj.level,
            status__in=['planned', 'confirmed']
        ).count()


class GenerateScheduleSerializer(serializers.Serializer):
    academic_year_id = serializers.IntegerField()
    semester = serializers.IntegerField(min_value=1, max_value=2)
    level_id = serializers.IntegerField()
    week_start = serializers.DateField()
    week_end = serializers.DateField()
    schedule_name = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if data['week_start'] >= data['week_end']:
            raise serializers.ValidationError(
                "La date de fin doit être après la date de début."
            )
        return data


# Extended serializer for detail views — returns nested objects frontend can use directly
class ScheduleSlotDetailSerializer(ScheduleSlotSerializer):
    course_info = serializers.SerializerMethodField()
    professor_info = serializers.SerializerMethodField()
    room_info = serializers.SerializerMethodField()

    class Meta(ScheduleSlotSerializer.Meta):
        fields = ScheduleSlotSerializer.Meta.fields + ['course_info', 'professor_info', 'room_info']

    def get_course_info(self, obj):
        return {
            'module_code': obj.course.module.code,
            'module_name': obj.course.module.name,
            'level': obj.course.module.level.name,
        }

    def get_professor_info(self, obj):
        return {
            'id': obj.professor.id,
            'full_name': obj.professor.user.get_full_name(),
        }

    def get_room_info(self, obj):
        return {
            'code': obj.room.code,
            'name': obj.room.name,
            'capacity': obj.room.capacity,
        }
