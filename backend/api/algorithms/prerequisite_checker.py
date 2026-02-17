from api.models.academic import Module, Prerequisite
from api.models.academic import Student, StudentModuleRegistration

class PrerequisiteChecker:
    def __init__(self, student_id):
        self.student_id = student_id
        self.errors = []
        
    def validate_registration(self, module_ids):
        """Valide si un étudiant peut s'inscrire à des modules"""
        
        student = Student.objects.get(student_id=self.student_id)
        completed_modules = self._get_completed_modules(student)
        
        for module_id in module_ids:
            module = Module.objects.get(id=module_id)
            prerequisites = Prerequisite.objects.filter(module=module)
            
            for prereq in prerequisites:
                if not self._check_prerequisite(prereq, completed_modules):
                    self.errors.append({
                        'module': module.code,
                        'prerequisite': prereq.prerequisite_module.code,
                        'message': f"Prerequisite {prereq.prerequisite_module.code} not satisfied"
                    })
        
        return len(self.errors) == 0, self.errors
    
    def _get_completed_modules(self, student):
        """Récupère les modules validés par l'étudiant"""
        return StudentModuleRegistration.objects.filter(
            student=student,
            status='completed'
        ).select_related('module')
    
    def _check_prerequisite(self, prereq, completed_modules):
        """Vérifie un prérequis spécifique"""
        for completed in completed_modules:
            if completed.module == prereq.prerequisite_module:
                if prereq.min_grade:
                    return completed.grade >= prereq.min_grade
                return True
        return False