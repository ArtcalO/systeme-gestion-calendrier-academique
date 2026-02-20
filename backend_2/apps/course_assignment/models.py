"""
Module d'Attribution des Cours - SGCA ULT
Gestion équitable et transparente de la charge d'enseignement
"""
from django.db import models


class CourseAssignment(models.Model):
    """Attribution d'un cours à un professeur"""

    class Status(models.TextChoices):
        PROPOSED = 'proposed', 'Proposée (par algorithme)'
        PENDING = 'pending', 'En attente de confirmation'
        CONFIRMED = 'confirmed', 'Confirmée'
        DECLINED = 'declined', 'Refusée par le professeur'
        CANCELLED = 'cancelled', 'Annulée'

    class AssignmentMethod(models.TextChoices):
        AUTOMATIC = 'automatic', 'Attribution automatique (algorithme)'
        MANUAL = 'manual', 'Attribution manuelle'
        PROFESSOR_REQUEST = 'prof_request', 'Demande du professeur'

    course = models.ForeignKey('academic.Course', on_delete=models.CASCADE,
                                related_name='assignments')
    professor = models.ForeignKey('users.Professor', on_delete=models.CASCADE,
                                   related_name='assignments')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PROPOSED)
    assignment_method = models.CharField(max_length=20, choices=AssignmentMethod.choices,
                                          default=AssignmentMethod.AUTOMATIC)
    assigned_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True,
                                     related_name='course_assignments_made')
    assigned_date = models.DateTimeField(auto_now_add=True)
    confirmed_date = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(default=0.0,
                               verbose_name="Score de compatibilité (0-100)")
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Attribution de cours"
        verbose_name_plural = "Attributions de cours"
        unique_together = ['course', 'professor']
        ordering = ['-assigned_date']

    def __str__(self):
        return f"{self.professor} ← {self.course} [{self.get_status_display()}]"


class TeachingLoadReport(models.Model):
    """
    Rapport de charge d'enseignement par semestre.
    Généré automatiquement pour la transparence.
    """
    professor = models.ForeignKey('users.Professor', on_delete=models.CASCADE,
                                   related_name='load_reports')
    academic_year = models.ForeignKey('academic.AcademicYear', on_delete=models.CASCADE)
    semester = models.PositiveIntegerField()
    total_weekly_hours = models.PositiveIntegerField(default=0)
    total_courses = models.PositiveIntegerField(default=0)
    load_percentage = models.FloatField(default=0.0,
                                         verbose_name="% de la charge max")
    generated_at = models.DateTimeField(auto_now=True)
    details = models.JSONField(default=dict)

    class Meta:
        verbose_name = "Rapport de charge"
        verbose_name_plural = "Rapports de charge"
        unique_together = ['professor', 'academic_year', 'semester']
        ordering = ['-academic_year', 'semester', 'professor']

    def __str__(self):
        return (f"{self.professor} - {self.academic_year} S{self.semester}: "
                f"{self.total_weekly_hours}h ({self.load_percentage:.1f}%)")


class AssignmentAlgorithmRun(models.Model):
    """Journalisation des exécutions de l'algorithme d'attribution"""

    class AlgorithmStatus(models.TextChoices):
        RUNNING = 'running', 'En cours'
        COMPLETED = 'completed', 'Terminé'
        FAILED = 'failed', 'Échoué'
        PARTIAL = 'partial', 'Partiel (certains cours non assignés)'

    academic_year = models.ForeignKey('academic.AcademicYear', on_delete=models.CASCADE)
    semester = models.PositiveIntegerField(null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=AlgorithmStatus.choices,
                               default=AlgorithmStatus.RUNNING)
    run_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    courses_total = models.PositiveIntegerField(default=0)
    courses_assigned = models.PositiveIntegerField(default=0)
    courses_unassigned = models.PositiveIntegerField(default=0)
    execution_time_ms = models.PositiveIntegerField(default=0)
    algorithm_log = models.JSONField(default=list)
    error_message = models.TextField(blank=True)

    class Meta:
        verbose_name = "Exécution algorithme attribution"
        verbose_name_plural = "Exécutions algorithme attribution"
        ordering = ['-started_at']

    def __str__(self):
        return (f"Run #{self.id} - {self.academic_year} "
                f"[{self.get_status_display()}] "
                f"{self.courses_assigned}/{self.courses_total} cours")
