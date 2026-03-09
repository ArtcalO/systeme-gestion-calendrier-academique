from rest_framework import serializers
from .models import (Faculty, Department, Program, Level, Subject, Module,
                     AcademicYear, Course, Room, StudentModuleResult)


class FacultySerializer(serializers.ModelSerializer):
    dean_name = serializers.CharField(source='dean.get_full_name', read_only=True)
    departments_count = serializers.SerializerMethodField()

    class Meta:
        model = Faculty
        fields = ['id', 'name', 'code', 'dean', 'dean_name', 'description',
                  'departments_count', 'created_at']

    def get_departments_count(self, obj):
        return obj.departments.count()


class DepartmentSerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)
    head_name = serializers.CharField(source='head.get_full_name', read_only=True)
    programs_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'faculty', 'faculty_name', 'head',
                  'head_name', 'programs_count']

    def get_programs_count(self, obj):
        return obj.programs.count()


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'description']


class LevelSerializer(serializers.ModelSerializer):
    program_name = serializers.CharField(source='program.name', read_only=True)

    class Meta:
        model = Level
        fields = ['id', 'name', 'year_number', 'program', 'program_name', 'description']


class ModuleSerializer(serializers.ModelSerializer):
    level_name = serializers.CharField(source='level.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    program_name = serializers.CharField(source='level.program.name', read_only=True)
    prerequisites_list = serializers.SerializerMethodField()
    has_prerequisites = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = ['id', 'code', 'name', 'subject', 'subject_name', 'level', 'level_name',
                  'program_name', 'module_type', 'credits', 'weekly_hours', 'semester',
                  'is_mandatory', 'description', 'learning_objectives',
                  'prerequisites_list', 'has_prerequisites']

    def get_prerequisites_list(self, obj):
        return list(obj.prerequisites.values('id', 'description', 'prerequisite'))

    def get_has_prerequisites(self, obj):
        return obj.prerequisites.exists()


class ProgramSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    faculty_name = serializers.CharField(source='department.faculty.name', read_only=True)
    levels = LevelSerializer(many=True, read_only=True)
    students_count = serializers.SerializerMethodField()

    class Meta:
        model = Program
        fields = ['id', 'name', 'code', 'department', 'department_name', 'faculty_name',
                  'program_type', 'duration_years', 'is_active', 'description',
                  'levels', 'students_count']

    def get_students_count(self, obj):
        return obj.students.filter(status='active').count()


class AcademicYearSerializer(serializers.ModelSerializer):
    courses_count = serializers.SerializerMethodField()

    class Meta:
        model = AcademicYear
        fields = ['id', 'name', 'start_date', 'end_date', 'is_current',
                  'is_enrollment_open', 'courses_count']

    def get_courses_count(self, obj):
        return obj.courses.count()


class CourseSerializer(serializers.ModelSerializer):
    module_name = serializers.CharField(source='module.name', read_only=True)
    module_code = serializers.CharField(source='module.code', read_only=True)
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    assigned_professor = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'module', 'module_name', 'module_code', 'academic_year',
                  'academic_year_name', 'semester', 'weekly_hours', 'expected_students',
                  'status', 'notes', 'assigned_professor']

    def get_assigned_professor(self, obj):
        assignment = obj.assignments.filter(status='confirmed').first()
        if assignment:
            return {
                'id': assignment.professor.id,
                'name': assignment.professor.user.get_full_name(),
                'grade': assignment.professor.get_grade_display(),
            }
        return None


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name', 'code', 'capacity', 'room_type', 'building',
                  'floor', 'has_projector', 'has_computers', 'has_internet',
                  'is_available', 'notes']


class StudentModuleResultSerializer(serializers.ModelSerializer):
    module_name = serializers.CharField(source='module.name', read_only=True)
    module_code = serializers.CharField(source='module.code', read_only=True)
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)

    class Meta:
        model = StudentModuleResult
        fields = ['id', 'student', 'module', 'module_name', 'module_code',
                  'academic_year', 'academic_year_name', 'semester', 'grade',
                  'is_validated', 'attempts', 'notes']
