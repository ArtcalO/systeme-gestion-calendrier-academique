from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from .models import CourseAssignment, TeachingLoadReport, AssignmentAlgorithmRun
from .serializers import (CourseAssignmentSerializer, CourseAssignmentCreateSerializer,
                           TeachingLoadReportSerializer, AlgorithmRunSerializer,
                           RunAlgorithmSerializer)
from .algorithm import CourseAssignmentEngine
from apps.users.permissions import IsAdminOrDean
from apps.academic.models import AcademicYear


class CourseAssignmentViewSet(viewsets.ModelViewSet):
    """
    Gestion des attributions de cours.
    Inclut l'exécution de l'algorithme d'attribution automatique.
    """
    queryset = CourseAssignment.objects.select_related(
        'course', 'course__module', 'course__academic_year',
        'professor', 'professor__user', 'assigned_by'
    )
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'assignment_method', 'professor',
                        'course__academic_year', 'course__semester']
    search_fields = ['course__module__name', 'professor__user__last_name']
    ordering_fields = ['assigned_date', 'score', 'status']

    def get_serializer_class(self):
        if self.action == 'create':
            return CourseAssignmentCreateSerializer
        return CourseAssignmentSerializer

    def get_permissions(self):
        if self.action in ['run_algorithm', 'confirm', 'cancel']:
            return [IsAdminOrDean()]
        if self.action == 'professor_confirm':
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(
            status='proposed',
            assignment_method='manual',
            assigned_by=self.request.user,
        )

    @action(detail=False, methods=['post'], permission_classes=[IsAdminOrDean])
    def run_algorithm(self, request):
        """
        Lance l'algorithme d'attribution automatique des cours.
        Endpoint principal de la fonctionnalité 3 du SGCA.
        """
        serializer = RunAlgorithmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        academic_year_id = serializer.validated_data['academic_year_id']
        semester = serializer.validated_data.get('semester')

        try:
            academic_year = AcademicYear.objects.get(id=academic_year_id)
        except AcademicYear.DoesNotExist:
            return Response({'error': 'Année académique non trouvée'},
                            status=status.HTTP_404_NOT_FOUND)

        engine = CourseAssignmentEngine(
            academic_year=academic_year,
            semester=semester,
            run_by=request.user,
        )

        result = engine.run()

        return Response({
            'message': f"Attribution terminée: {result['assigned_count']}/{result['total_courses']} cours assignés",
            'result': result,
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrDean])
    def confirm(self, request, pk=None):
        """Confirme une attribution (administrateur)"""
        assignment = self.get_object()
        if assignment.status in ['confirmed', 'cancelled']:
            return Response(
                {'detail': f"Cette attribution est déjà '{assignment.get_status_display()}'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        assignment.status = CourseAssignment.Status.CONFIRMED
        assignment.confirmed_date = timezone.now()
        assignment.save()
        return Response(CourseAssignmentSerializer(assignment).data)

    @action(detail=True, methods=['post'])
    def professor_confirm(self, request, pk=None):
        """Le professeur confirme ou refuse une attribution"""
        assignment = self.get_object()

        # Vérifier que c'est bien le bon professeur
        if not hasattr(request.user, 'professor_profile') or \
           request.user.professor_profile != assignment.professor:
            if request.user.role not in ['admin', 'dean']:
                return Response({'detail': 'Accès refusé.'}, status=status.HTTP_403_FORBIDDEN)

        action_type = request.data.get('action')  # 'accept' ou 'decline'
        if action_type == 'accept':
            assignment.status = CourseAssignment.Status.CONFIRMED
            assignment.confirmed_date = timezone.now()
        elif action_type == 'decline':
            assignment.status = CourseAssignment.Status.DECLINED
            assignment.notes = request.data.get('reason', '')
        else:
            return Response({'error': "action doit être 'accept' ou 'decline'"},
                            status=status.HTTP_400_BAD_REQUEST)

        assignment.save()
        return Response(CourseAssignmentSerializer(assignment).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrDean])
    def cancel(self, request, pk=None):
        """Annule une attribution"""
        assignment = self.get_object()
        assignment.status = CourseAssignment.Status.CANCELLED
        assignment.notes = request.data.get('reason', 'Annulée par administrateur')
        assignment.save()
        return Response(CourseAssignmentSerializer(assignment).data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Résumé des attributions par année académique"""
        academic_year_id = request.query_params.get('academic_year_id')

        qs = CourseAssignment.objects.all()
        if academic_year_id:
            qs = qs.filter(course__academic_year_id=academic_year_id)

        total = qs.count()
        by_status = {}
        for s in CourseAssignment.Status:
            by_status[s.label] = qs.filter(status=s.value).count()

        return Response({
            'total_assignments': total,
            'by_status': by_status,
            'confirmed_rate': round(
                by_status.get('Confirmée', 0) / total * 100 if total > 0 else 0, 1
            ),
        })


class TeachingLoadReportViewSet(viewsets.ReadOnlyModelViewSet):
    """Rapports de charge d'enseignement - lecture seule"""
    queryset = TeachingLoadReport.objects.select_related(
        'professor', 'professor__user', 'academic_year'
    )
    serializer_class = TeachingLoadReportSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['professor', 'academic_year', 'semester']
    ordering_fields = ['load_percentage', 'total_weekly_hours', 'total_courses']
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def equity_analysis(self, request):
        """
        Analyse d'équité de la distribution des charges.
        Compare les charges de tous les professeurs.
        """
        academic_year_id = request.query_params.get('academic_year_id')
        qs = TeachingLoadReport.objects.select_related('professor__user')
        if academic_year_id:
            qs = qs.filter(academic_year_id=academic_year_id)

        reports = list(qs)
        if not reports:
            return Response({'detail': 'Aucun rapport disponible.'})

        loads = [r.load_percentage for r in reports]
        avg_load = sum(loads) / len(loads)
        max_load = max(loads)
        min_load = min(loads)

        # Coefficient de variation (mesure d'équité)
        if avg_load > 0:
            import math
            variance = sum((l - avg_load) ** 2 for l in loads) / len(loads)
            std_dev = math.sqrt(variance)
            coefficient_of_variation = (std_dev / avg_load) * 100
        else:
            coefficient_of_variation = 0

        overloaded = [r for r in reports if r.load_percentage > 90]
        underloaded = [r for r in reports if r.load_percentage < 30]

        return Response({
            'statistics': {
                'average_load_percentage': round(avg_load, 1),
                'max_load_percentage': round(max_load, 1),
                'min_load_percentage': round(min_load, 1),
                'coefficient_of_variation': round(coefficient_of_variation, 1),
                'equity_score': round(max(0, 100 - coefficient_of_variation), 1),
            },
            'overloaded_professors': [
                {'name': r.professor.user.get_full_name(), 'load': r.load_percentage}
                for r in overloaded
            ],
            'underloaded_professors': [
                {'name': r.professor.user.get_full_name(), 'load': r.load_percentage}
                for r in underloaded
            ],
            'all_reports': TeachingLoadReportSerializer(reports, many=True).data,
        })


class AlgorithmRunViewSet(viewsets.ReadOnlyModelViewSet):
    """Historique des exécutions de l'algorithme"""
    queryset = AssignmentAlgorithmRun.objects.select_related('academic_year', 'run_by')
    serializer_class = AlgorithmRunSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['academic_year', 'status']
    permission_classes = [IsAdminOrDean]
