from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import (Faculty, Department, Program, Level, Subject, Module,
                     AcademicYear, Course, Room, StudentModuleResult)
from .serializers import (FacultySerializer, DepartmentSerializer, ProgramSerializer,
                           LevelSerializer, SubjectSerializer, ModuleSerializer,
                           AcademicYearSerializer, CourseSerializer, RoomSerializer,
                           StudentModuleResultSerializer)
from apps.users.permissions import IsAdminOrDean


class FacultyViewSet(viewsets.ModelViewSet):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    filter_backends = [SearchFilter]
    search_fields = ['name', 'code']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrDean()]
        return [IsAuthenticated()]


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.select_related('faculty')
    serializer_class = DepartmentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['faculty']
    search_fields = ['name', 'code']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrDean()]
        return [IsAuthenticated()]


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name', 'code']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrDean()]
        return [IsAuthenticated()]


class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.select_related('department', 'department__faculty').prefetch_related('levels')
    serializer_class = ProgramSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['department', 'program_type', 'is_active']
    search_fields = ['name', 'code']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrDean()]
        return [IsAuthenticated()]


class LevelViewSet(viewsets.ModelViewSet):
    queryset = Level.objects.select_related('program')
    serializer_class = LevelSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['program']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrDean()]
        return [IsAuthenticated()]


class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.select_related('level', 'level__program', 'subject').prefetch_related('prerequisites')
    serializer_class = ModuleSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['level', 'semester', 'module_type', 'is_mandatory', 'subject']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'credits', 'weekly_hours', 'semester']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrDean()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['get'])
    def prerequisite_tree(self, request, pk=None):
        """Arbre complet des prérequis d'un module"""
        module = self.get_object()

        def get_tree(mod, visited=None):
            if visited is None:
                visited = set()
            if mod.id in visited:
                return None  # Éviter les cycles
            visited.add(mod.id)
            return {
                'id': mod.id,
                'code': mod.code,
                'name': mod.name,
                'credits': mod.credits,
                'prerequisites': [
                    get_tree(p, visited) for p in mod.prerequisites.all()
                    if get_tree(p, visited) is not None
                ]
            }

        return Response(get_tree(module))


class AcademicYearViewSet(viewsets.ModelViewSet):
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_current', 'is_enrollment_open']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrDean()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def current(self, request):
        """Retourne l'année académique courante"""
        year = AcademicYear.get_current()
        if year:
            return Response(AcademicYearSerializer(year).data)
        return Response({'detail': 'Aucune année académique courante définie.'},
                        status=status.HTTP_404_NOT_FOUND)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related('module', 'academic_year').prefetch_related('assignments')
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['academic_year', 'semester', 'status', 'module__level']
    search_fields = ['module__name', 'module__code']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrDean()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def unassigned(self, request):
        """Cours sans professeur assigné"""
        courses = Course.objects.filter(
            assignments__isnull=True
        ).select_related('module', 'academic_year')
        academic_year = request.query_params.get('academic_year')
        if academic_year:
            courses = courses.filter(academic_year=academic_year)
        return Response(CourseSerializer(courses, many=True).data)


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['room_type', 'is_available', 'building', 'has_projector',
                        'has_computers']
    search_fields = ['name', 'code', 'building']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrDean()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """Disponibilité d'une salle pour une semaine donnée"""
        room = self.get_object()
        week = request.query_params.get('week')  # Format: YYYY-WNN
        from apps.scheduling.models import ScheduleSlot
        slots = ScheduleSlot.objects.filter(room=room)
        if week:
            slots = slots.filter(week_reference=week)

        from apps.scheduling.serializers import ScheduleSlotSerializer
        return Response({
            'room': RoomSerializer(room).data,
            'scheduled_slots': ScheduleSlotSerializer(slots, many=True).data,
        })


class StudentModuleResultViewSet(viewsets.ModelViewSet):
    queryset = StudentModuleResult.objects.select_related('student', 'module', 'academic_year')
    serializer_class = StudentModuleResultSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['student', 'module', 'academic_year', 'semester', 'is_validated']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrDean()]
        return [IsAuthenticated()]
