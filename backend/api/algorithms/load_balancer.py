from api.models.academic import Module
from api.models.teacher import TeacherSpecialization, ClassAssignment
from collections import defaultdict
import numpy as np

class TeachingLoadBalancer:
    def __init__(self):
        self.teacher_loads = defaultdict(int)
        
    def balance_assignment(self, modules, teachers, academic_year):
        """Répartit équitablement la charge d'enseignement"""
        
        # Calculer la charge actuelle
        current_assignments = ClassAssignment.objects.filter(
            academic_year=academic_year,
            status='confirmed'
        )
        
        for assignment in current_assignments:
            self.teacher_loads[assignment.teacher_id] += assignment.assigned_hours
        
        # Trier les modules par difficulté/spécialité
        prioritized_modules = self._prioritize_modules(modules)
        
        # Assigner les modules
        assignments = []
        for module in prioritized_modules:
            teacher = self._select_optimal_teacher(module, teachers)
            if teacher:
                assignments.append({
                    'module': module,
                    'teacher': teacher,
                    'hours': module.hours_per_week
                })
                self.teacher_loads[teacher.id] += module.hours_per_week
        
        return assignments
    
    def _prioritize_modules(self, modules):
        """Priorise les modules selon leur complexité"""
        return sorted(modules, 
                     key=lambda m: (m.credits, m.hours_per_week),
                     reverse=True)
    
    def _select_optimal_teacher(self, module, teachers):
        """Sélectionne le professeur optimal pour un module"""
        
        suitable_teachers = []
        
        for teacher in teachers:
            # Vérifier spécialisation
            specialization = TeacherSpecialization.objects.filter(
                teacher=teacher,
                module=module
            ).first()
            
            if not specialization or specialization.proficiency_level in ['basic']:
                continue
            
            # Vérifier charge actuelle
            current_load = self.teacher_loads.get(teacher.id, 0)
            if current_load + module.hours_per_week > teacher.max_weekly_hours:
                continue
            
            # Calculer score
            score = self._calculate_teacher_score(teacher, module, specialization, current_load)
            suitable_teachers.append((teacher, score))
        
        if not suitable_teachers:
            return None
            
        # Retourner le professeur avec le meilleur score
        suitable_teachers.sort(key=lambda x: x[1], reverse=True)
        return suitable_teachers[0][0]
    
    def _calculate_teacher_score(self, teacher, module, specialization, current_load):
        """Calcule un score pour l'assignation"""
        score = 0
        
        # Spécialisation
        proficiency_scores = {'expert': 10, 'proficient': 7, 'capable': 4, 'basic': 1}
        score += proficiency_scores.get(specialization.proficiency_level, 0)
        
        # Équilibrage de charge (préférer les moins chargés)
        load_ratio = current_load / teacher.max_weekly_hours
        score += (1 - load_ratio) * 5
        
        # Expérience
        score += min(specialization.years_experience, 10) * 0.5
        
        return score