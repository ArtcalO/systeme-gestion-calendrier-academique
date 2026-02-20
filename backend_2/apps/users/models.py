"""
Modèles utilisateurs pour le SGCA-ULT
Gère : Administrateurs, Professeurs, Étudiants, Doyens
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Modèle utilisateur étendu pour l'ULT"""

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrateur'
        DEAN = 'dean', 'Doyen'
        PROFESSOR = 'professor', 'Professeur'
        STUDENT = 'student', 'Étudiant'
        STAFF = 'staff', 'Personnel administratif'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    photo = models.ImageField(upload_to='users/photos/', null=True, blank=True)
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True,
                                   verbose_name="Matricule")
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    @property
    def is_professor(self):
        return self.role == self.Role.PROFESSOR

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_admin_or_dean(self):
        return self.role in [self.Role.ADMIN, self.Role.DEAN]


class Professor(models.Model):
    """Profil détaillé d'un professeur"""

    class Grade(models.TextChoices):
        ASSISTANT = 'assistant', 'Assistant'
        CHEF_TRAVAUX = 'chef_travaux', 'Chef de Travaux'
        CHARGE_COURS = 'charge_cours', 'Chargé de Cours'
        MAITRE_ASSISTANT = 'maitre_assistant', 'Maître-Assistant'
        PROFESSEUR_ASSOCIE = 'prof_associe', 'Professeur Associé'
        PROFESSEUR_ORDINAIRE = 'prof_ordinaire', 'Professeur Ordinaire'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='professor_profile')
    grade = models.CharField(max_length=30, choices=Grade.choices)
    department = models.ForeignKey('academic.Department', on_delete=models.SET_NULL,
                                   null=True, related_name='professors')
    specialities = models.ManyToManyField('academic.Subject', blank=True,
                                          related_name='specialized_professors',
                                          verbose_name="Spécialités")
    max_weekly_hours = models.PositiveIntegerField(default=15,
                                                    verbose_name="Heures max/semaine")
    is_available = models.BooleanField(default=True)
    bio = models.TextField(blank=True)

    class Meta:
        verbose_name = "Professeur"
        verbose_name_plural = "Professeurs"

    def __str__(self):
        return f"Prof. {self.user.get_full_name()} - {self.get_grade_display()}"

    def get_current_load(self, academic_year=None, semester=None):
        """Calcule la charge horaire actuelle du professeur"""
        from apps.course_assignment.models import CourseAssignment
        qs = CourseAssignment.objects.filter(professor=self, status='confirmed')
        if academic_year:
            qs = qs.filter(course__academic_year=academic_year)
        if semester:
            qs = qs.filter(course__semester=semester)
        return sum(a.course.weekly_hours for a in qs)


class Student(models.Model):
    """Profil détaillé d'un étudiant"""

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Actif'
        SUSPENDED = 'suspended', 'Suspendu'
        GRADUATED = 'graduated', 'Diplômé'
        DROPOUT = 'dropout', 'Abandon'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    registration_number = models.CharField(max_length=20, unique=True,
                                            verbose_name="Numéro d'immatriculation")
    program = models.ForeignKey('academic.Program', on_delete=models.SET_NULL,
                                null=True, related_name='students')
    current_level = models.ForeignKey('academic.Level', on_delete=models.SET_NULL,
                                      null=True, related_name='students')
    enrollment_year = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        verbose_name = "Étudiant"
        verbose_name_plural = "Étudiants"

    def __str__(self):
        return f"{self.registration_number} - {self.user.get_full_name()}"

    def get_completed_modules(self):
        """Retourne les modules validés par l'étudiant"""
        from apps.academic.models import StudentModuleResult
        return StudentModuleResult.objects.filter(
            student=self, is_validated=True
        ).values_list('module_id', flat=True)
