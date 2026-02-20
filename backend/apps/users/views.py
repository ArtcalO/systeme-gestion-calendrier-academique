from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import User, Professor, Student
from .serializers import (
    CustomTokenObtainPairSerializer, UserSerializer, UserCreateSerializer,
    ProfessorSerializer, StudentSerializer, ChangePasswordSerializer
)
from .permissions import IsAdminOrDean, IsSelfOrAdmin


class CustomTokenObtainPairView(TokenObtainPairView):
    """Connexion avec JWT enrichi (rôle, nom complet)"""
    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    """Gestion des utilisateurs"""
    queryset = User.objects.all().order_by('last_name')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'is_active']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'employee_id']
    ordering_fields = ['last_name', 'date_joined', 'role']

    def get_serializer_class(self):
        if self.action in ['create', 'register']:
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'register']:
            return [IsAdminOrDean()]
        if self.action in ['update', 'partial_update']:
            return [IsSelfOrAdmin()]
        if self.action == 'destroy':
            return [IsAdminOrDean()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Profil de l'utilisateur connecté"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request):
        """Changer son mot de passe"""
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response({'message': 'Mot de passe modifié avec succès.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfessorViewSet(viewsets.ModelViewSet):
    """Gestion des professeurs"""
    queryset = Professor.objects.select_related('user', 'department').prefetch_related('specialities')
    serializer_class = ProfessorSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['grade', 'department', 'is_available']
    search_fields = ['user__first_name', 'user__last_name', 'user__employee_id']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrDean()]
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=['get'])
    def workload(self, request, pk=None):
        """Charge horaire détaillée d'un professeur"""
        professor = self.get_object()
        from apps.course_assignment.models import CourseAssignment
        assignments = CourseAssignment.objects.filter(
            professor=professor, status='confirmed'
        ).select_related('course', 'course__module')

        data = {
            'professor': ProfessorSerializer(professor).data,
            'total_weekly_hours': professor.get_current_load(),
            'max_weekly_hours': professor.max_weekly_hours,
            'remaining_capacity': professor.max_weekly_hours - professor.get_current_load(),
            'assignments': [
                {
                    'course': a.course.module.name,
                    'weekly_hours': a.course.weekly_hours,
                    'academic_year': a.course.academic_year,
                    'semester': a.course.semester,
                }
                for a in assignments
            ]
        }
        return Response(data)

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Professeurs disponibles avec capacité restante"""
        professors = Professor.objects.filter(is_available=True)
        data = []
        for p in professors:
            load = p.get_current_load()
            if load < p.max_weekly_hours:
                data.append({
                    'id': p.id,
                    'name': p.user.get_full_name(),
                    'grade': p.get_grade_display(),
                    'current_load': load,
                    'remaining_capacity': p.max_weekly_hours - load,
                    'specialities': [s.name for s in p.specialities.all()],
                })
        return Response(data)


class StudentViewSet(viewsets.ModelViewSet):
    """Gestion des étudiants"""
    queryset = Student.objects.select_related('user', 'program', 'current_level')
    serializer_class = StudentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['program', 'current_level', 'status', 'enrollment_year']
    search_fields = ['user__first_name', 'user__last_name', 'registration_number']

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [IsAdminOrDean()]
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=['get'])
    def academic_history(self, request, pk=None):
        """Historique académique d'un étudiant"""
        student = self.get_object()
        from apps.academic.models import StudentModuleResult
        results = StudentModuleResult.objects.filter(
            student=student
        ).select_related('module').order_by('-academic_year', 'semester')

        from apps.academic.serializers import StudentModuleResultSerializer
        return Response({
            'student': StudentSerializer(student).data,
            'results': StudentModuleResultSerializer(results, many=True).data,
            'completed_count': results.filter(is_validated=True).count(),
            'failed_count': results.filter(is_validated=False).count(),
        })
