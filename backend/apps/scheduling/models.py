"""
Module de Planification des Horaires - SGCA ULT
Gestion des emplois du temps sans conflits
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class TimeSlot(models.Model):
    """Créneau horaire standard de l'université"""

    class DayOfWeek(models.IntegerChoices):
        MONDAY = 1, 'Lundi'
        TUESDAY = 2, 'Mardi'
        WEDNESDAY = 3, 'Mercredi'
        THURSDAY = 4, 'Jeudi'
        FRIDAY = 5, 'Vendredi'
        SATURDAY = 6, 'Samedi'

    day_of_week = models.IntegerField(choices=DayOfWeek.choices)
    start_time = models.TimeField(verbose_name="Heure de début")
    end_time = models.TimeField(verbose_name="Heure de fin")
    label = models.CharField(max_length=50, blank=True,
                              verbose_name="ex: Matin 1ère période")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Créneau horaire"
        verbose_name_plural = "Créneaux horaires"
        unique_together = ['day_of_week', 'start_time', 'end_time']
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.get_day_of_week_display()} {self.start_time:%H:%M}-{self.end_time:%H:%M}"

    def duration_hours(self):
        from datetime import datetime, date
        start = datetime.combine(date.today(), self.start_time)
        end = datetime.combine(date.today(), self.end_time)
        return (end - start).seconds / 3600


class ScheduleSlot(models.Model):
    """
    Créneau planifié dans l'emploi du temps.
    Représente une séance de cours à une date/heure/salle précise.
    """

    class SlotStatus(models.TextChoices):
        PLANNED = 'planned', 'Planifié'
        CONFIRMED = 'confirmed', 'Confirmé'
        CANCELLED = 'cancelled', 'Annulé'
        RESCHEDULED = 'rescheduled', 'Reporté'

    class SlotType(models.TextChoices):
        REGULAR = 'regular', 'Cours régulier'
        MAKEUP = 'makeup', 'Cours de rattrapage'
        EXAM = 'exam', 'Examen'
        MIDTERM = 'midterm', 'Partiel'

    course = models.ForeignKey('academic.Course', on_delete=models.CASCADE,
                                related_name='schedule_slots')
    professor = models.ForeignKey('users.Professor', on_delete=models.CASCADE,
                                   related_name='schedule_slots')
    room = models.ForeignKey('academic.Room', on_delete=models.CASCADE,
                              related_name='schedule_slots')
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE,
                                   related_name='schedule_slots')
    week_reference = models.CharField(max_length=10, verbose_name="Semaine (ex: 2024-W35)")
    slot_type = models.CharField(max_length=20, choices=SlotType.choices, default=SlotType.REGULAR)
    status = models.CharField(max_length=20, choices=SlotStatus.choices, default=SlotStatus.PLANNED)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True,
                                    related_name='created_slots')

    class Meta:
        verbose_name = "Créneau planifié"
        verbose_name_plural = "Créneaux planifiés"
        ordering = ['week_reference', 'time_slot__day_of_week', 'time_slot__start_time']

    def __str__(self):
        return (f"{self.course.module.code} | {self.professor.user.last_name} | "
                f"{self.room.code} | {self.time_slot}")


class Schedule(models.Model):
    """
    Emploi du temps complet pour un niveau/programme donné sur une période.
    Agrège plusieurs ScheduleSlots.
    """

    class ScheduleStatus(models.TextChoices):
        DRAFT = 'draft', 'Brouillon'
        PUBLISHED = 'published', 'Publié'
        ARCHIVED = 'archived', 'Archivé'

    name = models.CharField(max_length=200)
    academic_year = models.ForeignKey('academic.AcademicYear', on_delete=models.CASCADE,
                                       related_name='schedules')
    semester = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(2)])
    level = models.ForeignKey('academic.Level', on_delete=models.CASCADE,
                               related_name='schedules')
    status = models.CharField(max_length=20, choices=ScheduleStatus.choices,
                               default=ScheduleStatus.DRAFT)
    week_start = models.DateField(verbose_name="Semaine de début")
    week_end = models.DateField(verbose_name="Semaine de fin")
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True,
                                      related_name='generated_schedules')
    generation_log = models.JSONField(default=dict)

    class Meta:
        verbose_name = "Emploi du temps"
        verbose_name_plural = "Emplois du temps"
        ordering = ['-academic_year', '-generated_at']

    def __str__(self):
        return f"{self.name} - {self.level} ({self.get_status_display()})"

    def get_conflicts(self):
        """Retourne les conflits détectés dans cet emploi du temps"""
        return ScheduleConflict.objects.filter(schedule=self, is_resolved=False)


class ScheduleConflict(models.Model):
    """Conflit détecté dans un emploi du temps"""

    class ConflictType(models.TextChoices):
        ROOM_DOUBLE_BOOKING = 'room', 'Double réservation de salle'
        PROFESSOR_DOUBLE_BOOKING = 'professor', 'Double réservation professeur'
        STUDENT_OVERLAP = 'student', 'Chevauchement pour les étudiants'
        CAPACITY_EXCEEDED = 'capacity', 'Capacité salle dépassée'

    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE,
                                  related_name='conflicts')
    conflict_type = models.CharField(max_length=30, choices=ConflictType.choices)
    slot_1 = models.ForeignKey(ScheduleSlot, on_delete=models.CASCADE,
                                related_name='conflicts_as_slot1')
    slot_2 = models.ForeignKey(ScheduleSlot, on_delete=models.CASCADE,
                                null=True, blank=True, related_name='conflicts_as_slot2')
    description = models.TextField()
    is_resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Conflit d'horaire"
        verbose_name_plural = "Conflits d'horaires"

    def __str__(self):
        return f"Conflit: {self.get_conflict_type_display()} - {self.description[:50]}"
