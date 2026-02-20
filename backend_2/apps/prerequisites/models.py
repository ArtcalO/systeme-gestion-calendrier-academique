"""
Module de Gestion des Prérequis - SGCA ULT
Contrôle automatique de la progression pédagogique des étudiants
"""
from django.db import models
from apps.academic.models import Module


class ModulePrerequisite(models.Model):
    """
    Définit les relations de prérequis entre modules.
    Un étudiant doit valider les prérequis avant de s'inscrire au module cible.
    """

    class PrerequisiteType(models.TextChoices):
        STRICT = 'strict', 'Strict (obligatoire, note ≥ 10/20)'
        RECOMMENDED = 'recommended', 'Recommandé (conseillé)'
        COREQUISITE = 'coreq', 'Coréquisit (peut être suivi en parallèle)'

    module = models.ForeignKey(Module, on_delete=models.CASCADE,
                                related_name='prerequisites',
                                verbose_name="Module cible")
    prerequisite = models.ForeignKey(Module, on_delete=models.CASCADE,
                                      related_name='required_for',
                                      verbose_name="Module prérequis")
    prerequisite_type = models.CharField(max_length=20, choices=PrerequisiteType.choices,
                                          default=PrerequisiteType.STRICT)
    minimum_grade = models.DecimalField(max_digits=4, decimal_places=2, default=10.00,
                                         verbose_name="Note minimale requise")
    description = models.TextField(blank=True,
                                    verbose_name="Justification pédagogique")

    class Meta:
        verbose_name = "Prérequis de module"
        verbose_name_plural = "Prérequis de modules"
        unique_together = ['module', 'prerequisite']
        ordering = ['module', 'prerequisite_type']

    def __str__(self):
        return f"{self.prerequisite.code} → {self.module.code} ({self.get_prerequisite_type_display()})"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.module == self.prerequisite:
            raise ValidationError("Un module ne peut pas être son propre prérequis.")
        # Vérifier les cycles
        if self._would_create_cycle():
            raise ValidationError("Cette relation créerait un cycle dans les prérequis.")

    def _would_create_cycle(self):
        """Détecte si l'ajout de cette relation créerait un cycle"""
        visited = set()
        def has_path(from_mod, to_mod):
            if from_mod.id in visited:
                return False
            visited.add(from_mod.id)
            for prereq in ModulePrerequisite.objects.filter(module=from_mod):
                if prereq.prerequisite == to_mod:
                    return True
                if has_path(prereq.prerequisite, to_mod):
                    return True
            return False
        return has_path(self.prerequisite, self.module)


class EnrollmentRequest(models.Model):
    """
    Demande d'inscription d'un étudiant à un cours.
    Le système vérifie automatiquement les prérequis.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'En attente de vérification'
        APPROVED = 'approved', 'Approuvée'
        REJECTED = 'rejected', 'Rejetée (prérequis manquants)'
        WAIVED = 'waived', 'Dispensée (dérogation accordée)'

    student = models.ForeignKey('users.Student', on_delete=models.CASCADE,
                                 related_name='enrollment_requests')
    course = models.ForeignKey('academic.Course', on_delete=models.CASCADE,
                                related_name='enrollment_requests')
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    processed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL,
                                      null=True, blank=True,
                                      related_name='processed_enrollments')
    processed_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    waiver_reason = models.TextField(blank=True)

    class Meta:
        verbose_name = "Demande d'inscription"
        verbose_name_plural = "Demandes d'inscription"
        unique_together = ['student', 'course']
        ordering = ['-request_date']

    def __str__(self):
        return f"{self.student} → {self.course} [{self.get_status_display()}]"


class PrerequisiteCheckResult(models.Model):
    """Résultat détaillé de la vérification des prérequis pour une demande d'inscription"""
    enrollment_request = models.OneToOneField(
        EnrollmentRequest, on_delete=models.CASCADE,
        related_name='check_result'
    )
    checked_at = models.DateTimeField(auto_now_add=True)
    all_prerequisites_met = models.BooleanField(default=False)
    missing_prerequisites = models.JSONField(default=list,
                                              verbose_name="Prérequis manquants")
    met_prerequisites = models.JSONField(default=list,
                                          verbose_name="Prérequis satisfaits")
    warnings = models.JSONField(default=list,
                                 verbose_name="Avertissements (recommandés non satisfaits)")
    summary = models.TextField(blank=True)

    class Meta:
        verbose_name = "Résultat vérification prérequis"
        verbose_name_plural = "Résultats vérifications prérequis"

    def __str__(self):
        status = "✓" if self.all_prerequisites_met else "✗"
        return f"{status} {self.enrollment_request}"
