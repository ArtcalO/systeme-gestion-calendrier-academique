from rest_framework import serializers
from .models import CourseAssignment, TeachingLoadReport, AssignmentAlgorithmRun


class CourseAssignmentSerializer(serializers.ModelSerializer):
    professor_name = serializers.CharField(source='professor.user.get_full_name', read_only=True)
    professor_grade = serializers.CharField(source='professor.get_grade_display', read_only=True)
    course_name = serializers.CharField(source='course.module.name', read_only=True)
    course_code = serializers.CharField(source='course.module.code', read_only=True)
    academic_year = serializers.CharField(source='course.academic_year.name', read_only=True)
    semester = serializers.IntegerField(source='course.semester', read_only=True)
    weekly_hours = serializers.IntegerField(source='course.weekly_hours', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.get_full_name', read_only=True)

    class Meta:
        model = CourseAssignment
        fields = ['id', 'course', 'course_name', 'course_code', 'academic_year',
                  'semester', 'weekly_hours', 'professor', 'professor_name',
                  'professor_grade', 'status', 'assignment_method', 'assigned_by',
                  'assigned_by_name', 'assigned_date', 'confirmed_date', 'score', 'notes']
        read_only_fields = ['assigned_date', 'confirmed_date', 'score']


class CourseAssignmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseAssignment
        fields = ['course', 'professor', 'notes']


class TeachingLoadReportSerializer(serializers.ModelSerializer):
    professor_name = serializers.CharField(source='professor.user.get_full_name', read_only=True)
    professor_grade = serializers.CharField(source='professor.get_grade_display', read_only=True)
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    max_weekly_hours = serializers.IntegerField(source='professor.max_weekly_hours', read_only=True)

    class Meta:
        model = TeachingLoadReport
        fields = ['id', 'professor', 'professor_name', 'professor_grade',
                  'academic_year', 'academic_year_name', 'semester',
                  'total_weekly_hours', 'max_weekly_hours', 'total_courses',
                  'load_percentage', 'generated_at', 'details']


class AlgorithmRunSerializer(serializers.ModelSerializer):
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    run_by_name = serializers.CharField(source='run_by.get_full_name', read_only=True)
    success_rate = serializers.SerializerMethodField()

    class Meta:
        model = AssignmentAlgorithmRun
        fields = ['id', 'academic_year', 'academic_year_name', 'semester',
                  'started_at', 'completed_at', 'status', 'run_by', 'run_by_name',
                  'courses_total', 'courses_assigned', 'courses_unassigned',
                  'execution_time_ms', 'success_rate', 'algorithm_log', 'error_message']

    def get_success_rate(self, obj):
        if obj.courses_total == 0:
            return 0
        return round(obj.courses_assigned / obj.courses_total * 100, 1)


class RunAlgorithmSerializer(serializers.Serializer):
    academic_year_id = serializers.IntegerField()
    semester = serializers.IntegerField(required=False, allow_null=True, min_value=1, max_value=2)
    dry_run = serializers.BooleanField(default=False,
                                        help_text="Si True, simule sans sauvegarder")
