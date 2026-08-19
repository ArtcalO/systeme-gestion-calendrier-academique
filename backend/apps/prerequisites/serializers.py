from rest_framework import serializers
from .models import ModulePrerequisite, PrerequisiteGraph
from apps.academic.models import Module


class ModulePrerequisiteSerializer(serializers.ModelSerializer):
    module_name = serializers.CharField(source='module.name', read_only=True)
    module_code = serializers.CharField(source='module.code', read_only=True)
    module_level = serializers.CharField(source='module.level.name', read_only=True)
    module_semester = serializers.IntegerField(source='module.semester', read_only=True)
    prerequisite_name = serializers.CharField(source='prerequisite.name', read_only=True)
    prerequisite_code = serializers.CharField(source='prerequisite.code', read_only=True)
    prerequisite_level = serializers.CharField(source='prerequisite.level.name', read_only=True)
    prerequisite_semester = serializers.IntegerField(source='prerequisite.semester', read_only=True)

    class Meta:
        model = ModulePrerequisite
        fields = [
            'id', 'module', 'module_name', 'module_code', 'module_level', 'module_semester',
            'prerequisite', 'prerequisite_name', 'prerequisite_code',
            'prerequisite_level', 'prerequisite_semester',
            'prerequisite_type', 'minimum_grade', 'description'
        ]

    def validate(self, data):
        if data.get('module') == data.get('prerequisite'):
            raise serializers.ValidationError("Un module ne peut pas être son propre prérequis.")
        return data


class PrerequisiteGraphSerializer(serializers.ModelSerializer):
    program_name = serializers.CharField(source='program.name', read_only=True)

    class Meta:
        model = PrerequisiteGraph
        fields = ['id', 'program', 'program_name', 'generated_at', 'graph_data',
                  'is_valid', 'validation_errors']
