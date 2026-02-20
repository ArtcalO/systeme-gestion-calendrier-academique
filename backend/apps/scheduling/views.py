from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import TimeSlot, ScheduleSlot, Schedule, ScheduleConflict
from .serializers import (TimeSlotSerializer, ScheduleSlotSerializer, ScheduleSerializer,
                           ScheduleConflictSerializer, GenerateScheduleSerializer)
from .engine import SchedulingEngine
from apps.users.permissions import IsAdminOrDean
from apps.academic.models import AcademicYear, Level


class TimeSlotViewSet(viewsets.ModelViewSet):
    """Gestion des créneaux horaires standard"""
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['day_of_week', 'is_active']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrDean()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'])
    def create_default_slots(self, request):
        """Crée les créneaux horaires standard pour l'ULT"""
        if not request.user.role in ['admin', 'dean']:
            return Response({'error': 'Accès refusé'}, status=status.HTTP_403_FORBIDDEN)

        default_slots = []
        days = range(1, 7)  # Lundi à Samedi

        # 4 périodes par jour: 7h-9h, 9h-11h, 14h-16h, 16h-18h
        periods = [
            ('07:00', '09:00', '1ère période matin'),
            ('09:00', '11:00', '2ème période matin'),
            ('14:00', '16:00', '1ère période après-midi'),
            ('16:00', '18:00', '2ème période après-midi'),
        ]

        from datetime import time
        created = 0
        for day in days:
            for start_str, end_str, label in periods:
                h, m = map(int, start_str.split(':'))
                eh, em = map(int, end_str.split(':'))
                slot, created_flag = TimeSlot.objects.get_or_create(
                    day_of_week=day,
                    start_time=time(h, m),
                    end_time=time(eh, em),
                    defaults={'label': label, 'is_active': True}
                )
                if created_flag:
                    created += 1

        return Response({
            'message': f"{created} créneaux créés.",
            'total': TimeSlot.objects.count(),
        })


class ScheduleSlotViewSet(viewsets.ModelViewSet):
    """Gestion des créneaux planifiés individuels"""
    queryset = ScheduleSlot.objects.select_related(
        'course', 'course__module', 'professor', 'professor__user',
        'room', 'time_slot'
    )
    serializer_class = ScheduleSlotSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['course__academic_year', 'course__module__level',
                        'professor', 'room', 'week_reference', 'status', 'slot_type']
    search_fields = ['course__module__name', 'course__module__code']
    ordering_fields = ['week_reference', 'time_slot__day_of_week', 'time_slot__start_time']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrDean()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """Vérifie les conflits avant la création manuelle d'un slot"""
        from .engine import ConflictChecker
        data = serializer.validated_data

        existing = ScheduleSlot.objects.filter(
            time_slot=data['time_slot'],
            status__in=['planned', 'confirmed'],
        ).values('room_id', 'professor_id', 'time_slot_id',
                 'course__module__level_id', 'course_id', 'course__module__code')

        checker = ConflictChecker([{
            'room_id': s['room_id'],
            'professor_id': s['professor_id'],
            'time_slot_id': s['time_slot_id'],
            'level_id': s['course__module__level_id'],
            'course_id': s['course_id'],
            'course_code': s['course__module__code'],
        } for s in existing])

        can_place, conflicts = checker.can_place(
            data['room'].id,
            data['professor'].id,
            data['time_slot'].id,
            data['course'].module.level.id,
            data['course'].id,
        )

        if not can_place:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({
                'conflicts': conflicts,
                'message': 'Ce créneau crée des conflits dans l\'emploi du temps.'
            })

        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def by_week(self, request):
        """Emploi du temps d'une semaine pour un niveau donné"""
        week = request.query_params.get('week')
        level_id = request.query_params.get('level_id')
        professor_id = request.query_params.get('professor_id')

        qs = self.queryset.filter(status__in=['planned', 'confirmed'])

        if week:
            qs = qs.filter(week_reference=week)
        if level_id:
            qs = qs.filter(course__module__level_id=level_id)
        if professor_id:
            qs = qs.filter(professor_id=professor_id)

        # Organiser par jour et créneau
        slots = ScheduleSlotSerializer(qs, many=True).data
        organized = {}
        for slot in slots:
            day = slot['time_slot_info']['day_of_week']
            if day not in organized:
                organized[day] = []
            organized[day].append(slot)

        return Response({
            'week': week,
            'level_id': level_id,
            'slots_by_day': organized,
            'total_slots': len(slots),
        })


class ScheduleViewSet(viewsets.ModelViewSet):
    """
    Gestion des emplois du temps complets.
    Inclut la génération automatique via l'algorithme.
    """
    queryset = Schedule.objects.select_related('academic_year', 'level', 'generated_by')
    serializer_class = ScheduleSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['academic_year', 'semester', 'level', 'status']
    search_fields = ['name']

    def get_permissions(self):
        if self.action in ['generate', 'publish', 'destroy']:
            return [IsAdminOrDean()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'], permission_classes=[IsAdminOrDean])
    def generate(self, request):
        """
        Génère automatiquement un emploi du temps sans conflits.
        Endpoint principal de la fonctionnalité 1 du SGCA.
        """
        serializer = GenerateScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        try:
            academic_year = AcademicYear.objects.get(id=d['academic_year_id'])
            level = Level.objects.get(id=d['level_id'])
        except (AcademicYear.DoesNotExist, Level.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

        engine = SchedulingEngine(
            academic_year=academic_year,
            semester=d['semester'],
            level=level,
            week_start=d['week_start'],
            week_end=d['week_end'],
            generated_by=request.user,
        )

        schedule, stats = engine.generate(
            schedule_name=d.get('schedule_name', '')
        )

        return Response({
            'message': f"Emploi du temps généré: {stats['placed_courses']}/{stats['total_courses']} cours planifiés.",
            'schedule': ScheduleSerializer(schedule).data,
            'stats': stats,
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrDean])
    def publish(self, request, pk=None):
        """Publie un emploi du temps (le rend visible aux étudiants et professeurs)"""
        schedule = self.get_object()

        conflicts = schedule.conflicts.filter(is_resolved=False).count()
        if conflicts > 0:
            return Response({
                'error': f"Impossible de publier: {conflicts} conflit(s) non résolu(s).",
                'conflicts_count': conflicts,
            }, status=status.HTTP_400_BAD_REQUEST)

        schedule.status = 'published'
        schedule.save()
        return Response({
            'message': 'Emploi du temps publié avec succès.',
            'schedule': ScheduleSerializer(schedule).data,
        })

    @action(detail=True, methods=['get'])
    def conflicts(self, request, pk=None):
        """Conflits détectés dans un emploi du temps"""
        schedule = self.get_object()
        conflicts = schedule.conflicts.all()
        return Response({
            'schedule_id': schedule.id,
            'total_conflicts': conflicts.count(),
            'unresolved': conflicts.filter(is_resolved=False).count(),
            'conflicts': ScheduleConflictSerializer(conflicts, many=True).data,
        })

    @action(detail=True, methods=['get'])
    def detail_view(self, request, pk=None):
        """Vue détaillée avec tous les créneaux"""
        schedule = self.get_object()
        slots = ScheduleSlot.objects.filter(
            course__academic_year=schedule.academic_year,
            course__module__level=schedule.level,
            status__in=['planned', 'confirmed']
        ).select_related(
            'course__module', 'professor__user', 'room', 'time_slot'
        ).order_by('time_slot__day_of_week', 'time_slot__start_time')

        return Response({
            'schedule': ScheduleSerializer(schedule).data,
            'slots': ScheduleSlotSerializer(slots, many=True).data,
            'conflicts': ScheduleConflictSerializer(
                schedule.conflicts.filter(is_resolved=False), many=True
            ).data,
        })


class ScheduleConflictViewSet(viewsets.ReadOnlyModelViewSet):
    """Consultation et résolution des conflits d'horaires"""
    queryset = ScheduleConflict.objects.select_related('slot_1', 'slot_2', 'schedule')
    serializer_class = ScheduleConflictSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['schedule', 'conflict_type', 'is_resolved']
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrDean])
    def resolve(self, request, pk=None):
        """Marque un conflit comme résolu"""
        conflict = self.get_object()
        conflict.is_resolved = True
        conflict.resolution_notes = request.data.get('resolution_notes', '')
        conflict.save()
        return Response({'message': 'Conflit marqué comme résolu.'})
