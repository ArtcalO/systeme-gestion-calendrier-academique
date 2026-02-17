# api/algorithms/scheduler.py
import pulp
from datetime import datetime, timedelta
from collections import defaultdict

class TimetableScheduler:
    def __init__(self):
        self.problem = None
        
    def generate_schedule(self, modules, rooms, teachers, time_slots, constraints):
        """Génère un emploi du temps optimal avec Pulp"""
        
        # Créer le problème d'optimisation
        self.problem = pulp.LpProblem("Timetable_Scheduling", pulp.LpMinimize)
        
        # Variables de décision
        assignments = pulp.LpVariable.dicts(
            'Assign',
            [(m.id, r.id, t.id, ts.id) 
             for m in modules 
             for r in rooms 
             for t in teachers 
             for ts in time_slots],
            cat='Binary'
        )
        
        # Fonction objectif: minimiser les conflits et maximiser la satisfaction
        objective = pulp.lpSum([
            self._calculate_cost(assignments, m, r, t, ts, constraints)
            for m in modules for r in rooms 
            for t in teachers for ts in time_slots
        ])
        
        self.problem += objective
        
        # Contraintes
        self._add_hard_constraints(assignments, modules, rooms, teachers, time_slots)
        self._add_soft_constraints(assignments, constraints)
        
        # Résolution
        solver = pulp.PULP_CBC_CMD(msg=False)
        self.problem.solve(solver)
        
        return self._extract_schedule(assignments)
    
    def _calculate_cost(self, assignment, module, room, teacher, time_slot, constraints):
        """Calcule le coût d'une assignation"""
        cost = 0
        
        # Vérifier capacité salle
        if room.capacity < module.expected_students:
            cost += 1000
            
        # Vérifier disponibilité professeur
        if not self._is_teacher_available(teacher, time_slot):
            cost += 500
            
        # Appliquer les poids des contraintes
        for constraint in constraints:
            if not self._satisfies_constraint(module, room, teacher, time_slot, constraint):
                if constraint.is_hard:
                    cost += 10000
                else:
                    cost += constraint.weight * 10
                    
        return cost * assignment
    
    def _add_hard_constraints(self, assignments, modules, rooms, teachers, time_slots):
        """Ajoute les contraintes obligatoires"""
        
        # Chaque module doit être assigné exactement une fois
        for module in modules:
            self.problem += pulp.lpSum([
                assignments[(module.id, room.id, teacher.id, ts.id)]
                for room in rooms
                for teacher in teachers
                for ts in time_slots
            ]) == 1, f"Module_{module.id}_assigned_once"
        
        # Pas deux modules dans la même salle au même moment
        for room in rooms:
            for ts in time_slots:
                self.problem += pulp.lpSum([
                    assignments[(module.id, room.id, teacher.id, ts.id)]
                    for module in modules
                    for teacher in teachers
                ]) <= 1, f"Room_{room.id}_Time_{ts.id}_unique"