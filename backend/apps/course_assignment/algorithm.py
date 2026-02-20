"""
Algorithme d'Attribution Équilibrée des Cours - SGCA ULT
Implémente un algorithme de score pondéré pour une attribution équitable et transparente
"""
import time
from django.utils import timezone
from .models import CourseAssignment, TeachingLoadReport, AssignmentAlgorithmRun
from apps.academic.models import Course, AcademicYear
from apps.users.models import Professor


class CourseAssignmentEngine:
    """
    Moteur d'attribution équitable des cours aux professeurs.

    Algorithme de score pondéré:
    1. Score de spécialité (40%) - le professeur enseigne dans ce domaine
    2. Score de disponibilité (30%) - charge actuelle vs charge max
    3. Score de grade (20%) - adéquation grade/niveau du cours
    4. Score d'équité (10%) - favorise les professeurs moins chargés
    """

    WEIGHT_SPECIALTY = 0.40
    WEIGHT_AVAILABILITY = 0.30
    WEIGHT_GRADE = 0.20
    WEIGHT_EQUITY = 0.10

    # Adéquation grade/niveau du cours (L1/L2 → assistant ok, M2 → prof ordinaire préféré)
    GRADE_LEVEL_MATRIX = {
        'assistant': {'1': 1.0, '2': 0.8, '3': 0.6, '4': 0.4, '5': 0.2},
        'chef_travaux': {'1': 1.0, '2': 1.0, '3': 0.8, '4': 0.6, '5': 0.4},
        'charge_cours': {'1': 1.0, '2': 1.0, '3': 1.0, '4': 0.8, '5': 0.6},
        'maitre_assistant': {'1': 0.8, '2': 1.0, '3': 1.0, '4': 1.0, '5': 0.8},
        'prof_associe': {'1': 0.6, '2': 0.8, '3': 1.0, '4': 1.0, '5': 1.0},
        'prof_ordinaire': {'1': 0.4, '2': 0.6, '3': 0.8, '4': 1.0, '5': 1.0},
    }

    def __init__(self, academic_year, semester=None, run_by=None):
        self.academic_year = academic_year
        self.semester = semester
        self.run_by = run_by
        self.log = []
        self.algorithm_run = None

    def run(self):
        """Point d'entrée principal de l'algorithme d'attribution"""
        start_time = time.time()

        # Créer le log d'exécution
        self.algorithm_run = AssignmentAlgorithmRun.objects.create(
            academic_year=self.academic_year,
            semester=self.semester,
            run_by=self.run_by,
            status='running'
        )

        try:
            result = self._execute()
            elapsed_ms = int((time.time() - start_time) * 1000)

            self.algorithm_run.status = (
                'completed' if result['unassigned_count'] == 0 else 'partial'
            )
            self.algorithm_run.courses_total = result['total_courses']
            self.algorithm_run.courses_assigned = result['assigned_count']
            self.algorithm_run.courses_unassigned = result['unassigned_count']
            self.algorithm_run.execution_time_ms = elapsed_ms
            self.algorithm_run.algorithm_log = self.log
            self.algorithm_run.completed_at = timezone.now()
            self.algorithm_run.save()

            self._generate_load_reports()
            return result

        except Exception as e:
            self.algorithm_run.status = 'failed'
            self.algorithm_run.error_message = str(e)
            self.algorithm_run.completed_at = timezone.now()
            self.algorithm_run.save()
            raise

    def _execute(self):
        """Exécution de l'algorithme d'attribution"""
        # Récupérer les cours non assignés
        courses_qs = Course.objects.filter(
            academic_year=self.academic_year,
            status__in=['draft', 'scheduled']
        ).select_related('module', 'module__subject', 'module__level')

        if self.semester:
            courses_qs = courses_qs.filter(semester=self.semester)

        # Exclure les cours déjà confirmés
        assigned_course_ids = CourseAssignment.objects.filter(
            course__academic_year=self.academic_year,
            status='confirmed'
        ).values_list('course_id', flat=True)

        courses = list(courses_qs.exclude(id__in=assigned_course_ids))

        # Récupérer les professeurs disponibles
        professors = list(
            Professor.objects.filter(is_available=True)
            .select_related('user')
            .prefetch_related('specialities')
        )

        self._log(f"Démarrage: {len(courses)} cours à assigner, {len(professors)} professeurs disponibles")

        # Trier les cours par nombre de candidats éligibles (les plus contraints en premier)
        courses_with_candidates = []
        for course in courses:
            candidates = self._get_candidates(course, professors)
            courses_with_candidates.append((course, candidates))

        courses_with_candidates.sort(key=lambda x: len(x[1]))

        # Attribution par ordre de contrainte décroissante
        assigned = []
        unassigned = []
        professor_loads = {p.id: p.get_current_load() for p in professors}

        for course, candidates in courses_with_candidates:
            if not candidates:
                self._log(f"⚠ Aucun candidat pour: {course.module.code}", level='warning')
                unassigned.append(course)
                continue

            # Calculer les scores pour ce cours
            scored_candidates = []
            for professor in candidates:
                score = self._calculate_score(course, professor, professor_loads)
                scored_candidates.append((professor, score))

            # Trier par score décroissant
            scored_candidates.sort(key=lambda x: x[1]['total'], reverse=True)

            best_professor, best_score = scored_candidates[0]

            # Créer ou mettre à jour l'attribution
            assignment, created = CourseAssignment.objects.update_or_create(
                course=course,
                defaults={
                    'professor': best_professor,
                    'status': 'proposed',
                    'assignment_method': 'automatic',
                    'assigned_by': self.run_by,
                    'score': best_score['total'],
                    'notes': self._format_score_explanation(best_score),
                }
            )

            # Mettre à jour la charge en mémoire
            professor_loads[best_professor.id] = (
                professor_loads.get(best_professor.id, 0) + course.weekly_hours
            )

            assigned.append({
                'course': course.module.code,
                'professor': best_professor.user.get_full_name(),
                'score': best_score['total'],
            })

            self._log(
                f"✓ {course.module.code} → {best_professor.user.get_full_name()} "
                f"(score: {best_score['total']:.1f})"
            )

        self._log(f"Résultat: {len(assigned)} cours assignés, {len(unassigned)} non assignés")

        return {
            'total_courses': len(courses),
            'assigned_count': len(assigned),
            'unassigned_count': len(unassigned),
            'assignments': assigned,
            'unassigned_courses': [c.module.code for c in unassigned],
            'algorithm_run_id': self.algorithm_run.id,
        }

    def _get_candidates(self, course, professors):
        """Filtre les professeurs pouvant enseigner un cours"""
        candidates = []
        course_module = course.module

        for professor in professors:
            # Vérifier la capacité disponible
            current_load = professor.get_current_load()
            if current_load + course.weekly_hours > professor.max_weekly_hours:
                continue

            # Au moins une spécialité compatible (ou accepter tous si aucune restriction)
            specialities = professor.specialities.all()
            if specialities.exists():
                has_relevant_speciality = specialities.filter(
                    id=course_module.subject_id
                ).exists()
                # Un professeur peut quand même être candidat sans spécialité exacte
                # mais sera pénalisé dans le score
            candidates.append(professor)

        return candidates

    def _calculate_score(self, course, professor, professor_loads):
        """
        Calcule le score de compatibilité entre un cours et un professeur.
        Retourne un dict avec les composantes du score.
        """
        # Score de spécialité (0-100)
        specialty_score = self._calculate_specialty_score(course, professor)

        # Score de disponibilité (0-100)
        availability_score = self._calculate_availability_score(
            course, professor, professor_loads
        )

        # Score de grade (0-100)
        grade_score = self._calculate_grade_score(course, professor)

        # Score d'équité (0-100) - favorise les professeurs moins sollicités
        equity_score = self._calculate_equity_score(professor, professor_loads)

        total = (
            specialty_score * self.WEIGHT_SPECIALTY +
            availability_score * self.WEIGHT_AVAILABILITY +
            grade_score * self.WEIGHT_GRADE +
            equity_score * self.WEIGHT_EQUITY
        )

        return {
            'total': round(total, 2),
            'specialty': round(specialty_score, 2),
            'availability': round(availability_score, 2),
            'grade': round(grade_score, 2),
            'equity': round(equity_score, 2),
        }

    def _calculate_specialty_score(self, course, professor):
        """Score basé sur les spécialités du professeur"""
        specialities = professor.specialities.all()
        if not specialities.exists():
            return 50.0  # Score neutre si pas de spécialité définie

        if specialities.filter(id=course.module.subject_id).exists():
            return 100.0

        # Vérifier les spécialités liées (même département)
        if course.module.subject and specialities.filter(
            modules__level__program__department=course.module.level.program.department
        ).exists():
            return 60.0

        return 20.0  # Spécialité non pertinente

    def _calculate_availability_score(self, course, professor, professor_loads):
        """Score basé sur la disponibilité horaire"""
        current_load = professor_loads.get(professor.id, 0)
        max_load = professor.max_weekly_hours
        remaining = max_load - current_load

        if remaining <= 0:
            return 0.0
        if remaining >= course.weekly_hours * 2:
            return 100.0

        return (remaining / max_load) * 100

    def _calculate_grade_score(self, course, professor):
        """Score basé sur l'adéquation entre le grade et le niveau du cours"""
        grade = professor.grade
        level_year = str(course.module.level.year_number)

        matrix = self.GRADE_LEVEL_MATRIX.get(grade, {})
        # Utiliser le niveau le plus proche si exact pas disponible
        score_multiplier = matrix.get(level_year, matrix.get('3', 0.7))
        return score_multiplier * 100

    def _calculate_equity_score(self, professor, professor_loads):
        """Score d'équité: favorise les professeurs ayant moins de cours"""
        current_load = professor_loads.get(professor.id, 0)
        max_load = professor.max_weekly_hours

        if max_load == 0:
            return 0.0

        # Plus la charge est faible, plus le score d'équité est élevé
        load_ratio = current_load / max_load
        return (1 - load_ratio) * 100

    def _generate_load_reports(self):
        """Génère les rapports de charge pour tous les professeurs"""
        professors = Professor.objects.filter(is_available=True)

        for professor in professors:
            assignments = CourseAssignment.objects.filter(
                professor=professor,
                course__academic_year=self.academic_year,
                status__in=['proposed', 'confirmed']
            ).select_related('course', 'course__module')

            if self.semester:
                assignments = assignments.filter(course__semester=self.semester)

            total_hours = sum(a.course.weekly_hours for a in assignments)
            load_pct = (total_hours / professor.max_weekly_hours * 100
                        if professor.max_weekly_hours > 0 else 0)

            details = {
                'courses': [
                    {
                        'code': a.course.module.code,
                        'name': a.course.module.name,
                        'hours': a.course.weekly_hours,
                        'status': a.status,
                        'score': a.score,
                    }
                    for a in assignments
                ]
            }

            TeachingLoadReport.objects.update_or_create(
                professor=professor,
                academic_year=self.academic_year,
                semester=self.semester or 0,
                defaults={
                    'total_weekly_hours': total_hours,
                    'total_courses': assignments.count(),
                    'load_percentage': load_pct,
                    'details': details,
                }
            )

    def _format_score_explanation(self, score):
        return (
            f"Score total: {score['total']}/100 | "
            f"Spécialité: {score['specialty']:.0f}% | "
            f"Disponibilité: {score['availability']:.0f}% | "
            f"Grade: {score['grade']:.0f}% | "
            f"Équité: {score['equity']:.0f}%"
        )

    def _log(self, message, level='info'):
        entry = {'level': level, 'message': message, 'timestamp': str(timezone.now())}
        self.log.append(entry)
