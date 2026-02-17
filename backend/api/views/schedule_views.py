from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from api.models.teacher import ClassAssignment, Teacher
from api.models.academic import Module
from api.models.schedule import TimeSlot, Room, ScheduleConstraint
from .serializers import ScheduleConstraintSerializer, TimetableSerializer
from .algorithms.scheduler import TimetableScheduler
import json

class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = ScheduleConstraint.objects.all()
    serializer_class = ScheduleConstraintSerializer
    
    @action(detail=False, methods=['post'])
    def generate_timetable(self, request):
        """Génère un emploi du temps automatiquement"""
        
        data = request.data
        academic_year_id = data.get('academic_year_id')
        semester = data.get('semester')
        
        # Récupérer les données nécessaires
        modules = Module.objects.filter(
            semester=semester,
            department_id=data.get('department_id')
        )
        
        # Générer l'emploi du temps
        scheduler = TimetableScheduler()
        schedule = scheduler.generate_schedule(
            modules=modules,
            rooms=Room.objects.all(),
            teachers=Teacher.objects.filter(status='active'),
            time_slots=TimeSlot.objects.all(),
            constraints=ScheduleConstraint.objects.filter(is_active=True)
        )
        
        # Sauvegarder dans la base de données
        with transaction.atomic():
            for assignment in schedule:
                ClassAssignment.objects.create(**assignment)
        
        return Response({
            'status': 'success',
            'schedule': schedule,
            'generated_at': datetime.now().isoformat()
        })
    
    @action(detail=False, methods=['get'])
    def get_timetable(self, request):
        """Récupère l'emploi du temps filtré"""
        
        filters = {}
        if department_id := request.query_params.get('department_id'):
            filters['module__department_id'] = department_id
        
        if teacher_id := request.query_params.get('teacher_id'):
            filters['teacher_id'] = teacher_id
        
        if semester := request.query_params.get('semester'):
            filters['semester'] = semester
            
        assignments = ClassAssignment.objects.filter(**filters)
        serializer = TimetableSerializer(assignments, many=True)
        
        return Response(serializer.data)