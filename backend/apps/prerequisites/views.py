from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import ModulePrerequisite, PrerequisiteGraph
from .serializers import ModulePrerequisiteSerializer, PrerequisiteGraphSerializer
from .engine import PrerequisiteAnalyzer, PrerequisiteValidator
from apps.users.permissions import IsAdminOrDean
from apps.academic.models import Module, Program, Course


class ModulePrerequisiteViewSet(viewsets.ModelViewSet):
    """
    Gestion des prérequis de modules.
    Prérequis = cours qui doit être complété avant (ou en parallèle pour coréquisits).
    """
    queryset = ModulePrerequisite.objects.select_related(
        'module', 'module__level', 'prerequisite', 'prerequisite__level'
    )
    serializer_class = ModulePrerequisiteSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['module', 'prerequisite', 'prerequisite_type',
                        'module__level__program']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrDean()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        instance = serializer.save()
        has_cycle, cycle_path = PrerequisiteValidator.detect_cycles(instance.module.id)
        if has_cycle:
            instance.delete()
            from rest_framework.exceptions import ValidationError
            raise ValidationError(
                "Cette relation crée un cycle dans les prérequis. Opération annulée."
            )

    @action(detail=False, methods=['get'])
    def by_module(self, request):
        """Prérequis d'un module spécifique avec détails de planification"""
        module_id = request.query_params.get('module_id')
        if not module_id:
            return Response({'error': 'module_id requis'}, status=400)

        try:
            module = Module.objects.get(id=module_id)
        except Module.DoesNotExist:
            return Response({'error': 'Module non trouvé'}, status=404)

        deps = PrerequisiteAnalyzer.get_module_dependencies(module)
        prereqs_qs = ModulePrerequisite.objects.filter(module=module).select_related(
            'prerequisite', 'prerequisite__level'
        )

        return Response({
            'module_id': module.id,
            'module_code': module.code,
            'module_name': module.name,
            'level': module.level.name,
            'semester': module.semester,
            'dependencies': deps,
            'prerequisites': ModulePrerequisiteSerializer(prereqs_qs, many=True).data,
            'total_strict': len(deps['strict']),
            'total_corequisites': len(deps['corequisites']),
            'total_recommended': len(deps['recommended']),
        })

    @action(detail=False, methods=['get'])
    def validate_program(self, request):
        """Vérifie la cohérence des prérequis d'un programme"""
        program_id = request.query_params.get('program_id')
        if not program_id:
            return Response({'error': 'program_id requis'}, status=400)

        try:
            program = Program.objects.get(id=program_id)
        except Program.DoesNotExist:
            return Response({'error': 'Programme non trouvé'}, status=404)

        errors = PrerequisiteValidator.validate_program_prerequisites(program)
        planning_order = PrerequisiteAnalyzer.get_planning_order(program)

        return Response({
            'program': program.name,
            'is_valid': len(errors) == 0,
            'errors': errors,
            'errors_count': len(errors),
            'recommended_planning_order': planning_order,
        })

    @action(detail=False, methods=['get'])
    def graph(self, request):
        """Graphe de prérequis pour visualisation d'un programme"""
        program_id = request.query_params.get('program_id')
        if not program_id:
            return Response({'error': 'program_id requis'}, status=400)

        try:
            program = Program.objects.get(id=program_id)
        except Program.DoesNotExist:
            return Response({'error': 'Programme non trouvé'}, status=404)

        graph_data = PrerequisiteValidator.generate_graph_data(program)
        errors = PrerequisiteValidator.validate_program_prerequisites(program)

        return Response({
            'program_id': program.id,
            'program_name': program.name,
            'graph': graph_data,
            'is_valid': len(errors) == 0,
            'validation_errors': errors,
        })

    @action(detail=False, methods=['post'])
    def check_course_scheduling(self, request):
        """
        Vérifie si un cours peut être planifié selon ses prérequis.
        POST body: { course_id, academic_year_id (optionnel) }
        """
        course_id = request.data.get('course_id')
        academic_year_id = request.data.get('academic_year_id')

        if not course_id:
            return Response({'error': 'course_id requis'}, status=400)

        try:
            course = Course.objects.select_related('module__level').get(id=course_id)
        except Course.DoesNotExist:
            return Response({'error': 'Cours non trouvé'}, status=404)

        from apps.academic.models import AcademicYear
        academic_year = None
        if academic_year_id:
            try:
                academic_year = AcademicYear.objects.get(id=academic_year_id)
            except AcademicYear.DoesNotExist:
                pass

        result = PrerequisiteAnalyzer.can_schedule_course(course, academic_year)
        deps = PrerequisiteAnalyzer.get_module_dependencies(course.module)

        return Response({
            'course_id': course.id,
            'module_code': course.module.code,
            'module_name': course.module.name,
            'scheduling_check': result,
            'dependencies': deps,
        })

    @action(detail=False, methods=['get'])
    def planning_order(self, request):
        """Ordre de planification recommandé pour un programme"""
        program_id = request.query_params.get('program_id')
        if not program_id:
            return Response({'error': 'program_id requis'}, status=400)

        try:
            program = Program.objects.get(id=program_id)
        except Program.DoesNotExist:
            return Response({'error': 'Programme non trouvé'}, status=404)

        order = PrerequisiteAnalyzer.get_planning_order(program)
        return Response({
            'program_id': program.id,
            'program_name': program.name,
            'planning_order': order,
            'total_modules': len(order),
        })
