from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.http import HttpResponse
import json
from datetime import datetime, timedelta, date
from .models import TimeSlot, ScheduleSlot, Schedule, ScheduleConflict
from .serializers import (TimeSlotSerializer, ScheduleSlotSerializer, ScheduleSerializer,
                           ScheduleConflictSerializer, GenerateScheduleSerializer)
from .engine import SchedulingEngine
from apps.users.permissions import IsAdminOrDean
from apps.academic.models import AcademicYear, Level


class TimeSlotViewSet(viewsets.ModelViewSet):
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
        if not request.user.role in ['admin', 'dean']:
            return Response({'error': 'Accès refusé'}, status=status.HTTP_403_FORBIDDEN)

        days = range(1, 7)
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
                _, created_flag = TimeSlot.objects.get_or_create(
                    day_of_week=day, start_time=time(h, m), end_time=time(eh, em),
                    defaults={'label': label, 'is_active': True}
                )
                if created_flag:
                    created += 1

        return Response({'message': f"{created} créneaux créés.", 'total': TimeSlot.objects.count()})


class ScheduleSlotViewSet(viewsets.ModelViewSet):
    queryset = ScheduleSlot.objects.select_related(
        'course', 'course__module', 'professor', 'professor__user', 'room', 'time_slot'
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
        from .engine import ConflictChecker
        data = serializer.validated_data
        existing = ScheduleSlot.objects.filter(
            time_slot=data['time_slot'], status__in=['planned', 'confirmed'],
        ).values('room_id', 'professor_id', 'time_slot_id',
                 'course__module__level_id', 'course_id', 'course__module__code')

        checker = ConflictChecker([{
            'room_id': s['room_id'], 'professor_id': s['professor_id'],
            'time_slot_id': s['time_slot_id'], 'level_id': s['course__module__level_id'],
            'course_id': s['course_id'], 'course_code': s['course__module__code'],
        } for s in existing])

        can_place, conflicts = checker.can_place(
            data['room'].id, data['professor'].id, data['time_slot'].id,
            data['course'].module.level.id, data['course'].id,
        )
        if not can_place:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'conflicts': conflicts, 'message': "Ce créneau crée des conflits."})

        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def by_week(self, request):
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

        slots = ScheduleSlotSerializer(qs, many=True).data
        organized = {}
        for slot in slots:
            day = slot['time_slot_info']['day_of_week']
            if day not in organized:
                organized[day] = []
            organized[day].append(slot)

        return Response({'week': week, 'level_id': level_id, 'slots_by_day': organized, 'total_slots': len(slots)})


class ScheduleViewSet(viewsets.ModelViewSet):
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
        serializer = GenerateScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        try:
            academic_year = AcademicYear.objects.get(id=d['academic_year_id'])
            level = Level.objects.get(id=d['level_id'])
        except (AcademicYear.DoesNotExist, Level.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

        engine = SchedulingEngine(
            academic_year=academic_year, semester=d['semester'], level=level,
            week_start=d['week_start'], week_end=d['week_end'], generated_by=request.user,
        )
        schedule, stats = engine.generate(schedule_name=d.get('schedule_name', ''))

        return Response({
            'message': f"Emploi du temps généré: {stats['placed_courses']}/{stats['total_courses']} cours planifiés.",
            'schedule': ScheduleSerializer(schedule).data, 'stats': stats,
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrDean])
    def publish(self, request, pk=None):
        schedule = self.get_object()
        conflicts = schedule.conflicts.filter(is_resolved=False).count()
        if conflicts > 0:
            return Response({'error': f"Impossible de publier: {conflicts} conflit(s) non résolu(s)."}, status=400)
        schedule.status = 'published'
        schedule.save()
        return Response({'message': 'Emploi du temps publié.', 'schedule': ScheduleSerializer(schedule).data})

    @action(detail=True, methods=['get'])
    def conflicts(self, request, pk=None):
        schedule = self.get_object()
        conflicts = schedule.conflicts.all()
        return Response({
            'schedule_id': schedule.id, 'total_conflicts': conflicts.count(),
            'unresolved': conflicts.filter(is_resolved=False).count(),
            'conflicts': ScheduleConflictSerializer(conflicts, many=True).data,
        })

    @action(detail=True, methods=['get'])
    def detail_view(self, request, pk=None):
        schedule = self.get_object()
        slots = ScheduleSlot.objects.filter(
            course__academic_year=schedule.academic_year,
            course__module__level=schedule.level,
            status__in=['planned', 'confirmed']
        ).select_related('course__module', 'professor__user', 'room', 'time_slot'
        ).order_by('time_slot__day_of_week', 'time_slot__start_time')

        return Response({
            'schedule': ScheduleSerializer(schedule).data,
            'slots': ScheduleSlotSerializer(slots, many=True).data,
            'conflicts': ScheduleConflictSerializer(schedule.conflicts.filter(is_resolved=False), many=True).data,
        })

    @action(detail=True, methods=['get'])
    def weekly_view(self, request, pk=None):
        """Vue hebdomadaire formatée pour affichage et impression"""
        schedule = self.get_object()
        week = request.query_params.get('week')

        slots_qs = ScheduleSlot.objects.filter(
            course__academic_year=schedule.academic_year,
            course__module__level=schedule.level,
            status__in=['planned', 'confirmed']
        ).select_related('course__module', 'professor__user', 'room', 'time_slot')

        if week:
            slots_qs = slots_qs.filter(week_reference=week)

        days = {1: 'Lundi', 2: 'Mardi', 3: 'Mercredi', 4: 'Jeudi', 5: 'Vendredi', 6: 'Samedi'}
        weekly = {d: [] for d in range(1, 7)}

        for slot in slots_qs:
            ts = slot.time_slot
            weekly[ts.day_of_week].append({
                'id': slot.id,
                'start_time': ts.start_time.strftime('%H:%M'),
                'end_time': ts.end_time.strftime('%H:%M'),
                'course_code': slot.course.module.code,
                'course_name': slot.course.module.name,
                'professor': slot.professor.user.get_full_name(),
                'room': slot.room.code,
                'slot_type': slot.slot_type,
                'status': slot.status,
                'week_reference': slot.week_reference,
            })

        for day_slots in weekly.values():
            day_slots.sort(key=lambda x: x['start_time'])

        return Response({
            'schedule_id': schedule.id,
            'schedule_name': schedule.name,
            'level': schedule.level.name,
            'academic_year': schedule.academic_year.name,
            'week': week,
            'weekly_calendar': {days[d]: weekly[d] for d in range(1, 7)},
        })

    @action(detail=True, methods=['get'])
    def annual_view(self, request, pk=None):
        """Vue annuelle - tous les créneaux organisés par semaine"""
        schedule = self.get_object()

        slots_qs = ScheduleSlot.objects.filter(
            course__academic_year=schedule.academic_year,
            course__module__level=schedule.level,
            status__in=['planned', 'confirmed']
        ).select_related('course__module', 'professor__user', 'room', 'time_slot'
        ).order_by('week_reference', 'time_slot__day_of_week', 'time_slot__start_time')

        # Group by week
        weeks_data = {}
        for slot in slots_qs:
            week = slot.week_reference
            if week not in weeks_data:
                weeks_data[week] = {'week': week, 'slots': [], 'total_hours': 0}
            ts = slot.time_slot
            duration = ts.duration_hours()
            weeks_data[week]['slots'].append({
                'id': slot.id,
                'day': ts.get_day_of_week_display(),
                'day_number': ts.day_of_week,
                'start_time': ts.start_time.strftime('%H:%M'),
                'end_time': ts.end_time.strftime('%H:%M'),
                'course_code': slot.course.module.code,
                'course_name': slot.course.module.name,
                'professor': slot.professor.user.get_full_name(),
                'room': slot.room.code,
                'duration_hours': duration,
            })
            weeks_data[week]['total_hours'] += duration

        weeks_list = sorted(weeks_data.values(), key=lambda x: x['week'])

        return Response({
            'schedule_id': schedule.id,
            'schedule_name': schedule.name,
            'level': schedule.level.name,
            'academic_year': schedule.academic_year.name,
            'semester': schedule.semester,
            'total_weeks': len(weeks_list),
            'weeks': weeks_list,
        })

    @action(detail=True, methods=['get'])
    def export_ical(self, request, pk=None):
        """Export iCal pour import dans Google Calendar, Outlook, etc."""
        schedule = self.get_object()

        slots_qs = ScheduleSlot.objects.filter(
            course__academic_year=schedule.academic_year,
            course__module__level=schedule.level,
            status__in=['planned', 'confirmed']
        ).select_related('course__module', 'professor__user', 'room', 'time_slot')

        lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//SGCA-ULT//Calendar//FR',
                 f'X-WR-CALNAME:{schedule.name}', 'CALSCALE:GREGORIAN']

        for slot in slots_qs:
            ts = slot.time_slot
            # Parse week reference like "2024-W35"
            try:
                year, week_part = slot.week_reference.split('-W')
                # Get Monday of that week
                mon = date.fromisocalendar(int(year), int(week_part), 1)
                event_date = mon + timedelta(days=ts.day_of_week - 1)
                start_dt = datetime.combine(event_date, ts.start_time)
                end_dt = datetime.combine(event_date, ts.end_time)
                dtstart = start_dt.strftime('%Y%m%dT%H%M%S')
                dtend = end_dt.strftime('%Y%m%dT%H%M%S')

                lines.extend([
                    'BEGIN:VEVENT',
                    f'UID:{slot.id}@sgca-ult',
                    f'DTSTART:{dtstart}',
                    f'DTEND:{dtend}',
                    f'SUMMARY:{slot.course.module.code} - {slot.course.module.name}',
                    f'LOCATION:{slot.room.name}',
                    f'DESCRIPTION:Prof: {slot.professor.user.get_full_name()}\\nSalle: {slot.room.code}',
                    'END:VEVENT',
                ])
            except Exception:
                continue

        lines.append('END:VCALENDAR')
        ical_content = '\r\n'.join(lines)

        response = HttpResponse(ical_content, content_type='text/calendar; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="calendrier_{schedule.id}.ics"'
        return response


class ScheduleConflictViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ScheduleConflict.objects.select_related('slot_1', 'slot_2', 'schedule')
    serializer_class = ScheduleConflictSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['schedule', 'conflict_type', 'is_resolved']
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrDean])
    def resolve(self, request, pk=None):
        conflict = self.get_object()
        conflict.is_resolved = True
        conflict.resolution_notes = request.data.get('resolution_notes', '')
        conflict.save()
        return Response({'message': 'Conflit résolu.'})
