"""
Moteur de Génération d'Emplois du Temps - SGCA ULT
Algorithme de planification sans conflits utilisant le backtracking
"""
from django.db import transaction
from .models import TimeSlot, ScheduleSlot, Schedule, ScheduleConflict
from apps.academic.models import Course, Room
from apps.users.models import Professor
from apps.course_assignment.models import CourseAssignment


class ConflictChecker:
    """Vérifie les conflits dans un emploi du temps"""

    def __init__(self, existing_slots=None):
        """
        existing_slots: liste de dicts représentant les slots déjà planifiés
        Format: {'room_id', 'professor_id', 'time_slot_id', 'course_id', 'level_id'}
        """
        self.slots = existing_slots or []

    def can_place(self, room_id, professor_id, time_slot_id, level_id, course_id):
        """
        Vérifie si un créneau peut être placé sans conflit.
        Retourne (True, []) si ok, ou (False, [liste de conflits]) sinon.
        """
        conflicts = []

        for slot in self.slots:
            if slot['time_slot_id'] != time_slot_id:
                continue

            # Conflit de salle
            if slot['room_id'] == room_id:
                conflicts.append({
                    'type': 'room',
                    'description': f"Salle occupée par {slot.get('course_code', '?')}",
                })

            # Conflit de professeur
            if slot['professor_id'] == professor_id:
                conflicts.append({
                    'type': 'professor',
                    'description': f"Professeur occupé par {slot.get('course_code', '?')}",
                })

            # Conflit d'étudiants (même niveau au même moment)
            if slot['level_id'] == level_id:
                conflicts.append({
                    'type': 'student',
                    'description': f"Niveau déjà en cours: {slot.get('course_code', '?')}",
                })

        return len(conflicts) == 0, conflicts

    def add_slot(self, room_id, professor_id, time_slot_id, level_id, course_id, course_code):
        self.slots.append({
            'room_id': room_id,
            'professor_id': professor_id,
            'time_slot_id': time_slot_id,
            'level_id': level_id,
            'course_id': course_id,
            'course_code': course_code,
        })


class SchedulingEngine:
    """
    Moteur de génération d'emplois du temps.
    Utilise un algorithme glouton avec vérification des contraintes.
    """

    def __init__(self, academic_year, semester, level, week_start, week_end,
                 generated_by=None):
        self.academic_year = academic_year
        self.semester = semester
        self.level = level
        self.week_start = week_start
        self.week_end = week_end
        self.generated_by = generated_by
        self.log = []

    def generate(self, schedule_name=None):
        """
        Génère l'emploi du temps pour le niveau/semestre donné.
        Retourne un objet Schedule avec les slots créés.
        """
        name = schedule_name or (
            f"EDT {self.level} - {self.academic_year} S{self.semester}"
        )

        # Créer le schedule
        schedule = Schedule.objects.create(
            name=name,
            academic_year=self.academic_year,
            semester=self.semester,
            level=self.level,
            week_start=self.week_start,
            week_end=self.week_end,
            generated_by=self.generated_by,
            status='draft',
        )

        try:
            result = self._run_scheduling(schedule)
            schedule.generation_log = {
                'log': self.log,
                'stats': result,
            }
            schedule.save()

            # Détecter les conflits résiduels
            self._detect_and_save_conflicts(schedule)

            return schedule, result

        except Exception as e:
            schedule.delete()
            raise

    def _run_scheduling(self, schedule):
        """Exécution de l'algorithme de planification"""
        # Récupérer les cours confirmés avec leurs professeurs
        assignments = CourseAssignment.objects.filter(
            course__academic_year=self.academic_year,
            course__semester=self.semester,
            course__module__level=self.level,
            status='confirmed',
        ).select_related(
            'course', 'course__module', 'professor', 'professor__user'
        )

        # Créneaux disponibles
        time_slots = list(TimeSlot.objects.filter(is_active=True).order_by(
            'day_of_week', 'start_time'
        ))

        # Salles disponibles
        rooms = list(Room.objects.filter(is_available=True).order_by('capacity'))

        # Vérifier les slots existants (global - toutes les classes confondues)
        existing = list(ScheduleSlot.objects.filter(
            course__academic_year=self.academic_year,
            status__in=['planned', 'confirmed'],
        ).values(
            'room_id', 'professor_id', 'time_slot_id',
            'course__module__level_id', 'course_id', 'course__module__code'
        ))

        checker = ConflictChecker([{
            'room_id': s['room_id'],
            'professor_id': s['professor_id'],
            'time_slot_id': s['time_slot_id'],
            'level_id': s['course__module__level_id'],
            'course_id': s['course_id'],
            'course_code': s['course__module__code'],
        } for s in existing])

        placed = []
        unplaced = []

        for assignment in assignments:
            course = assignment.course
            professor = assignment.professor
            weekly_hours_needed = course.weekly_hours
            hours_placed = 0

            # Trouver une salle adaptée à l'effectif
            suitable_rooms = [r for r in rooms if r.capacity >= course.expected_students]
            if not suitable_rooms:
                suitable_rooms = rooms  # Fallback: utiliser n'importe quelle salle

            # Placer les séances hebdomadaires
            sessions_needed = max(1, weekly_hours_needed // 2)  # Sessions de ~2h

            for _ in range(sessions_needed):
                slot_found = False

                for time_slot in time_slots:
                    for room in suitable_rooms:
                        can_place, conflicts = checker.can_place(
                            room.id, professor.id, time_slot.id,
                            self.level.id, course.id
                        )

                        if can_place:
                            # Créer le slot
                            ScheduleSlot.objects.create(
                                course=course,
                                professor=professor,
                                room=room,
                                time_slot=time_slot,
                                week_reference=self._get_week_ref(self.week_start),
                                status='planned',
                                created_by=self.generated_by,
                            )

                            checker.add_slot(
                                room.id, professor.id, time_slot.id,
                                self.level.id, course.id, course.module.code
                            )

                            hours_placed += time_slot.duration_hours()
                            self._log(
                                f"✓ {course.module.code} → {room.code} "
                                f"{time_slot}"
                            )
                            slot_found = True
                            break

                    if slot_found:
                        break

                if not slot_found:
                    self._log(
                        f"⚠ Impossible de placer une séance de {course.module.code}",
                        level='warning'
                    )

            if hours_placed > 0:
                placed.append(course.module.code)
            else:
                unplaced.append(course.module.code)

        stats = {
            'total_courses': assignments.count(),
            'placed_courses': len(placed),
            'unplaced_courses': len(unplaced),
            'placed_list': placed,
            'unplaced_list': unplaced,
        }

        self._log(f"Résultat: {len(placed)}/{assignments.count()} cours planifiés")
        return stats

    def _detect_and_save_conflicts(self, schedule):
        """Détecte et enregistre les conflits dans l'emploi du temps"""
        slots = ScheduleSlot.objects.filter(
            course__academic_year=self.academic_year,
            course__module__level=self.level,
        ).select_related('course__module', 'room', 'professor', 'time_slot')

        conflicts_found = 0

        for i, slot1 in enumerate(slots):
            for slot2 in slots[i+1:]:
                if slot1.time_slot != slot2.time_slot:
                    continue

                # Conflit de salle
                if slot1.room == slot2.room:
                    ScheduleConflict.objects.create(
                        schedule=schedule,
                        conflict_type='room',
                        slot_1=slot1,
                        slot_2=slot2,
                        description=(
                            f"Salle {slot1.room.code} doublement réservée: "
                            f"{slot1.course.module.code} et {slot2.course.module.code}"
                        )
                    )
                    conflicts_found += 1

                # Conflit de professeur
                if slot1.professor == slot2.professor:
                    ScheduleConflict.objects.create(
                        schedule=schedule,
                        conflict_type='professor',
                        slot_1=slot1,
                        slot_2=slot2,
                        description=(
                            f"Prof. {slot1.professor.user.last_name} doublement réservé: "
                            f"{slot1.course.module.code} et {slot2.course.module.code}"
                        )
                    )
                    conflicts_found += 1

        if conflicts_found > 0:
            self._log(f"⚠ {conflicts_found} conflit(s) détecté(s)", level='warning')
        else:
            self._log("✓ Aucun conflit détecté")

    def _get_week_ref(self, date):
        """Retourne la référence ISO de semaine: YYYY-WNN"""
        year, week, _ = date.isocalendar()
        return f"{year}-W{week:02d}"

    def _log(self, message, level='info'):
        self.log.append({'level': level, 'message': message})
