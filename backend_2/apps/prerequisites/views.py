from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import ModulePrerequisite, EnrollmentRequest, PrerequisiteCheckResult
from .serializers import (ModulePrerequisiteSerializer, EnrollmentRequestSerializer,
                           EnrollmentRequestCreateSerializer, WaiverSerializer)
from .engine import PrerequisiteEngine, PrerequisiteValidator
from apps.users.permissions import IsAdminOrDean
from apps.academic.models import Module, Program
from apps.users.models import Student


class ModulePrerequisiteViewSet(viewsets.ModelViewSet):
    """
    Gestion des prérequis de modules.
    Permet de définir les relations pédagogiques entre modules.
    """
    queryset = ModulePrerequisite.objects.select_related('module', 'prerequisite')
    serializer_class = ModulePrerequisiteSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['module', 'prerequisite', 'prerequisite_type']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrDean()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        instance = serializer.save()
        # Vérifier les cycles après création
        has_cycle, cycle_path = PrerequisiteValidator.detect_cycles(instance.module.id)
        if has_cycle:
            instance.delete()
            from rest_framework.exceptions import ValidationError
            raise ValidationError(
                "Cette relation crée un cycle dans les prérequis. Opération annulée."
            )

    @action(detail=False, methods=['get'])
    def validate_program(self, request):
        """Vérifie la cohérence des prérequis d'un programme entier"""
        program_id = request.query_params.get('program_id')
        if not program_id:
            return Response({'error': 'program_id requis'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            program = Program.objects.get(id=program_id)
        except Program.DoesNotExist:
            return Response({'error': 'Programme non trouvé'}, status=status.HTTP_404_NOT_FOUND)

        errors = PrerequisiteValidator.validate_program_prerequisites(program)
        return Response({
            'program': program.name,
            'is_valid': len(errors) == 0,
            'errors': errors,
            'errors_count': len(errors),
        })


class EnrollmentRequestViewSet(viewsets.ModelViewSet):
    """
    Gestion des demandes d'inscription avec vérification automatique des prérequis.
    """
    queryset = EnrollmentRequest.objects.select_related(
        'student', 'student__user', 'course', 'course__module', 'course__academic_year'
    ).prefetch_related('check_result')
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['student', 'course', 'status']

    def get_serializer_class(self):
        if self.action == 'create':
            return EnrollmentRequestCreateSerializer
        return EnrollmentRequestSerializer

    def get_permissions(self):
        if self.action in ['grant_waiver', 'destroy']:
            return [IsAdminOrDean()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """Crée la demande et vérifie automatiquement les prérequis"""
        enrollment_request = serializer.save()
        engine = PrerequisiteEngine(enrollment_request.student)
        engine.process_enrollment_request(enrollment_request)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Retourner la réponse avec les détails complets
        enrollment = serializer.instance
        return Response(
            EnrollmentRequestSerializer(enrollment).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrDean])
    def grant_waiver(self, request, pk=None):
        """
        Accorde une dérogation pour un étudiant ne satisfaisant pas les prérequis.
        Réservé aux administrateurs/doyens.
        """
        enrollment = self.get_object()
        serializer = WaiverSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if enrollment.status == EnrollmentRequest.Status.APPROVED:
            return Response({'detail': "Cette inscription est déjà approuvée."},
                            status=status.HTTP_400_BAD_REQUEST)

        enrollment.status = EnrollmentRequest.Status.WAIVED
        enrollment.waiver_reason = serializer.validated_data['waiver_reason']
        enrollment.processed_by = request.user
        enrollment.processed_date = timezone.now()
        enrollment.save()

        return Response({
            'detail': 'Dérogation accordée avec succès.',
            'enrollment': EnrollmentRequestSerializer(enrollment).data,
        })

    @action(detail=False, methods=['post'])
    def bulk_check(self, request):
        """
        Vérifie les prérequis pour une liste de modules pour un étudiant.
        Utile pour afficher l'éligibilité du catalogue.
        """
        student_id = request.data.get('student_id')
        module_ids = request.data.get('module_ids', [])

        if not student_id:
            return Response({'error': 'student_id requis'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({'error': 'Étudiant non trouvé'}, status=status.HTTP_404_NOT_FOUND)

        engine = PrerequisiteEngine(student)
        results = []

        modules = Module.objects.filter(id__in=module_ids) if module_ids else Module.objects.all()
        for module in modules:
            check = engine.check_prerequisites_for_module(module)
            results.append({
                'module_id': module.id,
                'module_code': module.code,
                'module_name': module.name,
                'can_enroll': check['can_enroll'],
                'missing_count': len(check['missing']),
                'missing': check['missing'],
                'warnings_count': len(check['warnings']),
            })

        return Response({'student_id': student_id, 'results': results})

    @action(detail=False, methods=['get'])
    def eligible_modules(self, request):
        """Modules pour lesquels un étudiant est éligible"""
        student_id = request.query_params.get('student_id')
        level_id = request.query_params.get('level_id')
        semester = request.query_params.get('semester')

        if not student_id:
            return Response({'error': 'student_id requis'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({'error': 'Étudiant non trouvé'}, status=status.HTTP_404_NOT_FOUND)

        engine = PrerequisiteEngine(student)
        result = engine.get_eligible_modules(
            level=level_id,
            semester=int(semester) if semester else None
        )
        return Response(result)
