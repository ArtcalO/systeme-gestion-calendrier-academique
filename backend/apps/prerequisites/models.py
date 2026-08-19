"""
Module de Gestion des Prérequis - SGCA ULT
Gestion des relations pédagogiques entre modules pour la planification du calendrier
"""
from django.db import models
from apps.academic.models import Module


class ModulePrerequisite(models.Model):
    """
    Définit les relations de prérequis entre modules.
    Un cours peut avoir des prérequis (avant) et des coréquisits (en parallèle).
    """

    class PrerequisiteType(models.TextChoices):
        STRICT = 'strict', 'Strict (obligatoire avant)'
        RECOMMENDED = 'recommended', 'Recommandé (conseillé avant)'
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
    description = models.TextField(blank=True, verbose_name="Justification pédagogique")

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
        if self._would_create_cycle():
            raise ValidationError("Cette relation créerait un cycle dans les prérequis.")

    def _would_create_cycle(self):
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


class PrerequisiteGraph(models.Model):
    """
    Snapshot du graphe de prérequis pour un programme donné.
    Utilisé pour la visualisation et la planification.
    """
    program = models.ForeignKey('academic.Program', on_delete=models.CASCADE,
                                 related_name='prerequisite_graphs')
    generated_at = models.DateTimeField(auto_now_add=True)
    graph_data = models.JSONField(default=dict,
                                   verbose_name="Données du graphe (nodes + edges)")
    is_valid = models.BooleanField(default=True)
    validation_errors = models.JSONField(default=list)

    class Meta:
        verbose_name = "Graphe de prérequis"
        ordering = ['-generated_at']

    def __str__(self):
        return f"Graphe {self.program.code} - {self.generated_at.strftime('%d/%m/%Y')}"
