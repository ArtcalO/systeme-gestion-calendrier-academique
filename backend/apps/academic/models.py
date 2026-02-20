"""
Modèles académiques pour le SGCA-ULT
Gère : Facultés, Départements, Programmes, Niveaux, Modules, Salles, Années académiques
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Faculty(models.Model):
    """Faculté de l'université"""
    name = models.CharField(max_length=200, verbose_name="Nom de la faculté")
    code = models.CharField(max_length=10, unique=True, verbose_name="Code")
    dean = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True,
                              limit_choices_to={'role': 'dean'}, related_name='managed_faculty')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Faculté"
        verbose_name_plural = "Facultés"
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"


class Department(models.Model):
    """Département au sein d'une faculté"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10, unique=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='departments')
    head = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='headed_department')

    class Meta:
        verbose_name = "Département"
        verbose_name_plural = "Départements"
        ordering = ['faculty', 'name']

    def __str__(self):
        return f"{self.code} - {self.name}"


class Program(models.Model):
    """Programme d'études (ex: Licence en Informatique)"""

    class ProgramType(models.TextChoices):
        LICENCE = 'licence', 'Licence'
        MASTER = 'master', 'Master'
        DOCTORAT = 'doctorat', 'Doctorat'
        GRADUAT = 'graduat', 'Graduat'
        CERTIFICAT = 'certificat', 'Certificat'

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='programs')
    program_type = models.CharField(max_length=20, choices=ProgramType.choices)
    duration_years = models.PositiveIntegerField(default=3,
                                                  verbose_name="Durée en années")
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Programme"
        verbose_name_plural = "Programmes"
        ordering = ['department', 'name']

    def __str__(self):
        return f"{self.code} - {self.name} ({self.get_program_type_display()})"


class Level(models.Model):
    """Niveau d'étude (ex: L1, L2, L3, M1, M2)"""
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='levels')
    name = models.CharField(max_length=50, verbose_name="Nom du niveau (ex: L1)")
    year_number = models.PositiveIntegerField(verbose_name="Numéro d'année")
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Niveau"
        verbose_name_plural = "Niveaux"
        unique_together = ['program', 'year_number']
        ordering = ['program', 'year_number']

    def __str__(self):
        return f"{self.program.code} - {self.name}"


class Subject(models.Model):
    """Matière/Domaine (ex: Mathématiques, Informatique, Droit...)"""
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Matière/Domaine"
        verbose_name_plural = "Matières/Domaines"
        ordering = ['name']

    def __str__(self):
        return self.name


class Module(models.Model):
    """Module/Cours enseigné dans un programme"""

    class ModuleType(models.TextChoices):
        COURS = 'cours', 'Cours Magistral'
        TP = 'tp', 'Travaux Pratiques'
        TD = 'td', 'Travaux Dirigés'
        SEMINAIRE = 'seminaire', 'Séminaire'
        STAGE = 'stage', 'Stage'
        PROJET = 'projet', 'Projet'

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True,
                                 related_name='modules')
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='modules')
    module_type = models.CharField(max_length=20, choices=ModuleType.choices, default=ModuleType.COURS)
    credits = models.PositiveIntegerField(default=3, verbose_name="Crédits ECTS")
    weekly_hours = models.PositiveIntegerField(default=3, verbose_name="Heures/semaine")
    semester = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(2)],
        verbose_name="Semestre (1 ou 2)"
    )
    is_mandatory = models.BooleanField(default=True, verbose_name="Obligatoire")
    description = models.TextField(blank=True)
    learning_objectives = models.TextField(blank=True, verbose_name="Objectifs pédagogiques")

    class Meta:
        verbose_name = "Module"
        verbose_name_plural = "Modules"
        ordering = ['level', 'semester', 'name']

    def __str__(self):
        return f"{self.code} - {self.name} ({self.level})"


class AcademicYear(models.Model):
    """Année académique"""
    name = models.CharField(max_length=20, unique=True, verbose_name="ex: 2024-2025")
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    is_enrollment_open = models.BooleanField(default=False,
                                              verbose_name="Inscriptions ouvertes")

    class Meta:
        verbose_name = "Année académique"
        verbose_name_plural = "Années académiques"
        ordering = ['-start_date']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Une seule année courante à la fois
        if self.is_current:
            AcademicYear.objects.filter(is_current=True).exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_current(cls):
        return cls.objects.filter(is_current=True).first()


class Course(models.Model):
    """Cours planifié pour une année académique donnée"""

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Brouillon'
        SCHEDULED = 'scheduled', 'Planifié'
        ONGOING = 'ongoing', 'En cours'
        COMPLETED = 'completed', 'Terminé'
        CANCELLED = 'cancelled', 'Annulé'

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='courses')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE,
                                       related_name='courses')
    semester = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(2)]
    )
    weekly_hours = models.PositiveIntegerField(
        verbose_name="Heures hebdomadaires allouées"
    )
    expected_students = models.PositiveIntegerField(default=0,
                                                     verbose_name="Étudiants inscrits prévus")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Cours"
        verbose_name_plural = "Cours"
        unique_together = ['module', 'academic_year', 'semester']
        ordering = ['academic_year', 'semester', 'module']

    def __str__(self):
        return f"{self.module.name} - {self.academic_year} S{self.semester}"


class Room(models.Model):
    """Salle de cours ou laboratoire"""

    class RoomType(models.TextChoices):
        AMPHITHEATRE = 'amphi', 'Amphithéâtre'
        SALLE_COURS = 'salle', 'Salle de cours'
        LABO_INFO = 'labo_info', 'Laboratoire Informatique'
        LABO_SCIENCE = 'labo_science', 'Laboratoire Sciences'
        SALLE_TP = 'salle_tp', 'Salle TP'
        SALLE_CONF = 'conf', 'Salle de conférence'

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    capacity = models.PositiveIntegerField(verbose_name="Capacité")
    room_type = models.CharField(max_length=20, choices=RoomType.choices)
    building = models.CharField(max_length=100, blank=True)
    floor = models.IntegerField(default=0)
    has_projector = models.BooleanField(default=False)
    has_computers = models.BooleanField(default=False)
    has_internet = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Salle"
        verbose_name_plural = "Salles"
        ordering = ['building', 'name']

    def __str__(self):
        return f"{self.code} - {self.name} (cap. {self.capacity})"


class StudentModuleResult(models.Model):
    """Résultats d'un étudiant pour un module"""
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE,
                                 related_name='module_results')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='student_results')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    semester = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(2)])
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                 verbose_name="Note /20")
    is_validated = models.BooleanField(default=False, verbose_name="Module validé")
    attempts = models.PositiveIntegerField(default=1, verbose_name="Nombre de tentatives")
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Résultat module"
        verbose_name_plural = "Résultats modules"
        unique_together = ['student', 'module', 'academic_year', 'semester']
        ordering = ['student', '-academic_year', 'semester']

    def __str__(self):
        return f"{self.student} - {self.module.code}: {self.grade}/20"

    def save(self, *args, **kwargs):
        if self.grade is not None:
            self.is_validated = self.grade >= 10
        super().save(*args, **kwargs)
