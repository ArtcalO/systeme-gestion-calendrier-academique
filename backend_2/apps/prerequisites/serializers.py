from rest_framework import serializers
from .models import ModulePrerequisite, EnrollmentRequest, PrerequisiteCheckResult


class ModulePrerequisiteSerializer(serializers.ModelSerializer):
    module_name = serializers.CharField(source='module.name', read_only=True)
    module_code = serializers.CharField(source='module.code', read_only=True)
    prerequisite_name = serializers.CharField(source='prerequisite.name', read_only=True)
    prerequisite_code = serializers.CharField(source='prerequisite.code', read_only=True)

    class Meta:
        model = ModulePrerequisite
        fields = ['id', 'module', 'module_name', 'module_code',
                  'prerequisite', 'prerequisite_name', 'prerequisite_code',
                  'prerequisite_type', 'minimum_grade', 'description']

    def validate(self, data):
        if data.get('module') == data.get('prerequisite'):
            raise serializers.ValidationError(
                "Un module ne peut pas être son propre prérequis."
            )
        return data


class PrerequisiteCheckResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrerequisiteCheckResult
        fields = ['id', 'checked_at', 'all_prerequisites_met', 'missing_prerequisites',
                  'met_prerequisites', 'warnings', 'summary']


class EnrollmentRequestSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    course_name = serializers.CharField(source='course.module.name', read_only=True)
    course_year = serializers.CharField(source='course.academic_year.name', read_only=True)
    check_result = PrerequisiteCheckResultSerializer(read_only=True)
    processed_by_name = serializers.CharField(source='processed_by.get_full_name', read_only=True)

    class Meta:
        model = EnrollmentRequest
        fields = ['id', 'student', 'student_name', 'course', 'course_name', 'course_year',
                  'request_date', 'status', 'processed_by', 'processed_by_name',
                  'processed_date', 'rejection_reason', 'waiver_reason', 'check_result']
        read_only_fields = ['status', 'processed_by', 'processed_date', 'rejection_reason']


class EnrollmentRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnrollmentRequest
        fields = ['student', 'course']


class WaiverSerializer(serializers.Serializer):
    waiver_reason = serializers.CharField(min_length=20,
                                           help_text="Justification de la dérogation (min 20 chars)")
