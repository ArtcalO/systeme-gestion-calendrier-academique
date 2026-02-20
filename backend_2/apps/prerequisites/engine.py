"""
Moteur de vérification des prérequis - SGCA ULT
Algorithme de contrôle automatique de la conformité académique
"""
from django.utils import timezone
from .models import ModulePrerequisite, EnrollmentRequest, PrerequisiteCheckResult
from apps.academic.models import StudentModuleResult


class PrerequisiteEngine:
    """
    Moteur principal de vérification des prérequis.
    Implémente la logique de contrôle de la progression pédagogique.
    """

    def __init__(self, student):
        self.student = student
        self.completed_modules = self._get_completed_modules()
        self.in_progress_modules = self._get_in_progress_modules()

    def _get_completed_modules(self):
        """Récupère tous les modules validés par l'étudiant avec leurs notes"""
        results = StudentModuleResult.objects.filter(
            student=self.student, is_validated=True
        ).select_related('module')
        return {r.module_id: r for r in results}

    def _get_in_progress_modules(self):
        """Récupère les modules en cours (inscrits cette année)"""
        requests = EnrollmentRequest.objects.filter(
            student=self.student, status='approved'
        ).select_related('course__module')
        return {req.course.module_id for req in requests}

    def check_prerequisites_for_module(self, module):
        """
        Vérifie si l'étudiant peut s'inscrire à un module donné.
        Retourne un dictionnaire avec les résultats détaillés.
        """
        prerequisites = ModulePrerequisite.objects.filter(
            module=module
        ).select_related('prerequisite')

        result = {
            'can_enroll': True,
            'missing': [],
            'met': [],
            'warnings': [],
            'corequisites': [],
        }

        for prereq in prerequisites:
            prereq_module = prereq.prerequisite
            check = self._check_single_prerequisite(prereq)

            if prereq.prerequisite_type == ModulePrerequisite.PrerequisiteType.STRICT:
                if check['satisfied']:
                    result['met'].append({
                        'module_code': prereq_module.code,
                        'module_name': prereq_module.name,
                        'grade': check['grade'],
                        'required_grade': float(prereq.minimum_grade),
                    })
                else:
                    result['can_enroll'] = False
                    result['missing'].append({
                        'module_code': prereq_module.code,
                        'module_name': prereq_module.name,
                        'grade': check['grade'],
                        'required_grade': float(prereq.minimum_grade),
                        'reason': check['reason'],
                    })

            elif prereq.prerequisite_type == ModulePrerequisite.PrerequisiteType.RECOMMENDED:
                if not check['satisfied']:
                    result['warnings'].append({
                        'module_code': prereq_module.code,
                        'module_name': prereq_module.name,
                        'message': f"Module recommandé non suivi: {prereq_module.name}",
                    })
                else:
                    result['met'].append({
                        'module_code': prereq_module.code,
                        'module_name': prereq_module.name,
                        'grade': check['grade'],
                        'type': 'recommended',
                    })

            elif prereq.prerequisite_type == ModulePrerequisite.PrerequisiteType.COREQUISITE:
                if prereq_module.id in self.in_progress_modules or \
                   prereq_module.id in self.completed_modules:
                    result['corequisites'].append({
                        'module_code': prereq_module.code,
                        'module_name': prereq_module.name,
                        'status': 'met',
                    })
                else:
                    result['can_enroll'] = False
                    result['missing'].append({
                        'module_code': prereq_module.code,
                        'module_name': prereq_module.name,
                        'required_grade': float(prereq.minimum_grade),
                        'reason': "Coréquisit non inscrit simultanément",
                    })

        return result

    def _check_single_prerequisite(self, prereq_relation):
        """Vérifie un prérequis individuel"""
        prereq_module = prereq_relation.prerequisite
        module_id = prereq_module.id

        if module_id not in self.completed_modules:
            return {
                'satisfied': False,
                'grade': None,
                'reason': f"Module '{prereq_module.name}' non encore validé"
            }

        result = self.completed_modules[module_id]
        if result.grade is not None and result.grade < prereq_relation.minimum_grade:
            return {
                'satisfied': False,
                'grade': float(result.grade),
                'reason': f"Note insuffisante: {result.grade}/20 (min: {prereq_relation.minimum_grade}/20)"
            }

        return {
            'satisfied': True,
            'grade': float(result.grade) if result.grade else None,
            'reason': None
        }

    def process_enrollment_request(self, enrollment_request):
        """
        Traite une demande d'inscription en vérifiant automatiquement les prérequis.
        Crée un PrerequisiteCheckResult détaillé.
        """
        module = enrollment_request.course.module
        check = self.check_prerequisites_for_module(module)

        # Créer ou mettre à jour le résultat de vérification
        check_result, _ = PrerequisiteCheckResult.objects.update_or_create(
            enrollment_request=enrollment_request,
            defaults={
                'all_prerequisites_met': check['can_enroll'],
                'missing_prerequisites': check['missing'],
                'met_prerequisites': check['met'],
                'warnings': check['warnings'],
                'summary': self._generate_summary(check, module),
            }
        )

        # Mettre à jour le statut de la demande
        if check['can_enroll']:
            enrollment_request.status = EnrollmentRequest.Status.APPROVED
        else:
            enrollment_request.status = EnrollmentRequest.Status.REJECTED
            enrollment_request.rejection_reason = self._format_rejection_reason(check['missing'])

        enrollment_request.processed_date = timezone.now()
        enrollment_request.save()

        return check_result

    def get_eligible_modules(self, level=None, semester=None):
        """
        Retourne la liste des modules pour lesquels l'étudiant est éligible.
        """
        from apps.academic.models import Module
        qs = Module.objects.prefetch_related('prerequisites')

        if level:
            qs = qs.filter(level=level)
        if semester:
            qs = qs.filter(semester=semester)

        eligible = []
        ineligible = []

        for module in qs:
            check = self.check_prerequisites_for_module(module)
            item = {
                'module': {
                    'id': module.id,
                    'code': module.code,
                    'name': module.name,
                    'credits': module.credits,
                    'weekly_hours': module.weekly_hours,
                },
                'check': check,
            }
            if check['can_enroll']:
                eligible.append(item)
            else:
                ineligible.append(item)

        return {'eligible': eligible, 'ineligible': ineligible}

    def _generate_summary(self, check, module):
        if check['can_enroll']:
            return (f"Inscription autorisée pour '{module.name}'. "
                    f"{len(check['met'])} prérequis satisfaits. "
                    f"{len(check['warnings'])} recommandations non suivies.")
        else:
            missing_names = [m['module_name'] for m in check['missing']]
            return (f"Inscription refusée pour '{module.name}'. "
                    f"Prérequis manquants: {', '.join(missing_names)}.")

    def _format_rejection_reason(self, missing):
        if not missing:
            return ""
        reasons = []
        for m in missing:
            reasons.append(f"• {m['module_code']} - {m['module_name']}: {m['reason']}")
        return "\n".join(reasons)


class PrerequisiteValidator:
    """
    Validateur statique pour vérifier la cohérence des prérequis
    lors de la création/modification de la structure académique.
    """

    @staticmethod
    def detect_cycles(module_id, visited=None, path=None):
        """Algorithme DFS pour détecter les cycles dans le graphe des prérequis"""
        if visited is None:
            visited = set()
        if path is None:
            path = []

        visited.add(module_id)
        path.append(module_id)

        prerequisites = ModulePrerequisite.objects.filter(
            module_id=module_id
        ).values_list('prerequisite_id', flat=True)

        for prereq_id in prerequisites:
            if prereq_id in path:
                return True, path + [prereq_id]
            if prereq_id not in visited:
                has_cycle, cycle_path = PrerequisiteValidator.detect_cycles(
                    prereq_id, visited, path[:]
                )
                if has_cycle:
                    return True, cycle_path

        return False, []

    @staticmethod
    def validate_program_prerequisites(program):
        """
        Vérifie que tous les prérequis d'un programme sont cohérents.
        Retourne une liste d'erreurs.
        """
        errors = []
        from apps.academic.models import Module
        modules = Module.objects.filter(level__program=program)

        for module in modules:
            has_cycle, cycle_path = PrerequisiteValidator.detect_cycles(module.id)
            if has_cycle:
                errors.append({
                    'type': 'cycle',
                    'module': module.code,
                    'message': f"Cycle détecté dans les prérequis de {module.code}",
                    'path': cycle_path,
                })

            # Vérifier que les prérequis ne sont pas dans un niveau supérieur
            for prereq_rel in ModulePrerequisite.objects.filter(module=module):
                prereq = prereq_rel.prerequisite
                if prereq.level.year_number >= module.level.year_number:
                    if prereq.semester >= module.semester or \
                       prereq.level.year_number > module.level.year_number:
                        errors.append({
                            'type': 'level_inconsistency',
                            'module': module.code,
                            'prerequisite': prereq.code,
                            'message': (f"Le prérequis {prereq.code} (N{prereq.level.year_number} "
                                       f"S{prereq.semester}) ne précède pas logiquement "
                                       f"{module.code} (N{module.level.year_number} S{module.semester})")
                        })

        return errors
