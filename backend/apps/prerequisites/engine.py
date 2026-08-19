"""
Moteur de vérification et analyse des prérequis - SGCA ULT
Analyse des dépendances pour la planification du calendrier académique
"""
from .models import ModulePrerequisite


class PrerequisiteAnalyzer:
    """
    Analyse les dépendances de prérequis pour la planification.
    Utilisé pour valider qu'un cours peut être planifié selon ses prérequis.
    """

    @staticmethod
    def get_module_dependencies(module):
        """
        Retourne toutes les dépendances d'un module:
        - prerequisites: cours qui DOIVENT être terminés avant
        - corequisites: cours qui peuvent être suivis en parallèle
        - recommended: cours recommandés avant
        """
        prereqs = ModulePrerequisite.objects.filter(module=module).select_related('prerequisite')

        result = {
            'strict': [],
            'corequisites': [],
            'recommended': [],
        }

        for p in prereqs:
            item = {
                'id': p.prerequisite.id,
                'code': p.prerequisite.code,
                'name': p.prerequisite.name,
                'level': p.prerequisite.level.name,
                'semester': p.prerequisite.semester,
                'minimum_grade': float(p.minimum_grade),
                'description': p.description,
            }
            if p.prerequisite_type == 'strict':
                result['strict'].append(item)
            elif p.prerequisite_type == 'coreq':
                result['corequisites'].append(item)
            else:
                result['recommended'].append(item)

        return result

    @staticmethod
    def can_schedule_course(course, academic_year=None):
        """
        Vérifie si un cours peut être planifié dans une année académique donnée.
        Vérifie que les cours prérequis stricts ont été ou seront planifiés
        dans des semestres/années précédents.
        """
        from apps.academic.models import Course
        module = course.module
        prereqs = ModulePrerequisite.objects.filter(
            module=module,
            prerequisite_type='strict'
        ).select_related('prerequisite')

        result = {
            'can_schedule': True,
            'warnings': [],
            'errors': [],
            'prerequisites_status': [],
        }

        for prereq_rel in prereqs:
            prereq_module = prereq_rel.prerequisite
            status_item = {
                'module_code': prereq_module.code,
                'module_name': prereq_module.name,
                'type': 'strict',
                'status': 'unknown',
            }

            # Vérifier si le prérequis est dans un niveau/semestre antérieur logique
            if prereq_module.level.year_number > module.level.year_number:
                result['errors'].append(
                    f"Le prérequis {prereq_module.code} est dans un niveau supérieur — incohérence."
                )
                status_item['status'] = 'error'
                result['can_schedule'] = False
            elif prereq_module.level.year_number == module.level.year_number and \
                 prereq_module.semester >= course.semester:
                result['warnings'].append(
                    f"Le prérequis {prereq_module.code} est dans le même semestre ou après — vérifier la logique."
                )
                status_item['status'] = 'warning'
            else:
                # Vérifier si ce cours prérequis existe dans le planning
                if academic_year:
                    prereq_course = Course.objects.filter(
                        module=prereq_module, academic_year=academic_year
                    ).first()
                    status_item['status'] = 'scheduled' if prereq_course else 'not_scheduled'
                    if not prereq_course:
                        result['warnings'].append(
                            f"Le prérequis {prereq_module.code} n'est pas planifié cette année académique."
                        )
                else:
                    status_item['status'] = 'ok'

            result['prerequisites_status'].append(status_item)

        return result

    @staticmethod
    def get_planning_order(program):
        """
        Retourne l'ordre de planification recommandé pour les modules d'un programme,
        en tenant compte des dépendances (topological sort).
        """
        from apps.academic.models import Module
        modules = list(Module.objects.filter(level__program=program).select_related('level'))

        # Build dependency graph
        module_map = {m.id: m for m in modules}
        deps = {m.id: set() for m in modules}

        for prereq_rel in ModulePrerequisite.objects.filter(
            module__level__program=program,
            prerequisite_type='strict'
        ):
            if prereq_rel.module_id in deps and prereq_rel.prerequisite_id in module_map:
                deps[prereq_rel.module_id].add(prereq_rel.prerequisite_id)

        # Topological sort (Kahn's algorithm)
        in_degree = {mid: len(d) for mid, d in deps.items()}
        queue = [mid for mid, d in in_degree.items() if d == 0]
        order = []

        while queue:
            mid = queue.pop(0)
            order.append(mid)
            for other_id, other_deps in deps.items():
                if mid in other_deps:
                    other_deps.discard(mid)
                    in_degree[other_id] -= 1
                    if in_degree[other_id] == 0:
                        queue.append(other_id)

        # Build result with ordering info
        result = []
        for i, mid in enumerate(order):
            if mid in module_map:
                m = module_map[mid]
                result.append({
                    'order': i + 1,
                    'module_id': m.id,
                    'module_code': m.code,
                    'module_name': m.name,
                    'level': m.level.name,
                    'semester': m.semester,
                    'year_number': m.level.year_number,
                })

        return result


class PrerequisiteValidator:
    """Validateur statique pour la cohérence des prérequis"""

    @staticmethod
    def detect_cycles(module_id, visited=None, path=None):
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

            for prereq_rel in ModulePrerequisite.objects.filter(module=module):
                prereq = prereq_rel.prerequisite
                if prereq.level.year_number > module.level.year_number:
                    errors.append({
                        'type': 'level_inconsistency',
                        'module': module.code,
                        'prerequisite': prereq.code,
                        'message': (
                            f"Le prérequis {prereq.code} (N{prereq.level.year_number} "
                            f"S{prereq.semester}) est dans un niveau SUPÉRIEUR à "
                            f"{module.code} (N{module.level.year_number} S{module.semester})"
                        )
                    })

        return errors

    @staticmethod
    def generate_graph_data(program):
        """Génère les données de graphe pour visualisation (nodes + edges)"""
        from apps.academic.models import Module
        modules = Module.objects.filter(level__program=program).select_related('level', 'subject')

        nodes = []
        for m in modules:
            nodes.append({
                'id': m.id,
                'code': m.code,
                'name': m.name,
                'level': m.level.name,
                'year_number': m.level.year_number,
                'semester': m.semester,
                'credits': m.credits,
                'group': f"N{m.level.year_number}S{m.semester}",
            })

        edges = []
        for prereq_rel in ModulePrerequisite.objects.filter(
            module__level__program=program
        ).select_related('module', 'prerequisite'):
            edges.append({
                'id': prereq_rel.id,
                'source': prereq_rel.prerequisite_id,
                'target': prereq_rel.module_id,
                'type': prereq_rel.prerequisite_type,
                'minimum_grade': float(prereq_rel.minimum_grade),
                'description': prereq_rel.description,
            })

        return {'nodes': nodes, 'edges': edges}
