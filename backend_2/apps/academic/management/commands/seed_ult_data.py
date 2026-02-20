"""
Commande de seeding pour l'ULT - Données initiales de démonstration
Usage: python manage.py seed_ult_data
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, time


class Command(BaseCommand):
    help = 'Initialise les données de démonstration pour le SGCA-ULT'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset', action='store_true',
            help='Supprime toutes les données avant de re-créer'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('🚀 Initialisation SGCA-ULT...'))

        if options['reset']:
            self._reset_data()

        self._create_users()
        self._create_academic_structure()
        self._create_rooms()
        self._create_time_slots()
        self._create_academic_year()
        self._create_professors()
        self._create_modules()
        self._create_prerequisites()

        self.stdout.write(self.style.SUCCESS('✅ Données initialisées avec succès!'))
        self.stdout.write('\n📋 Comptes créés:')
        self.stdout.write('   Admin:     admin / admin123')
        self.stdout.write('   Doyen:     doyen_sci / doyen123')
        self.stdout.write('   Prof 1:    prof_math / prof123')
        self.stdout.write('   Étudiant:  etud001 / etud123\n')

    def _reset_data(self):
        from apps.users.models import User
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write('  Données supprimées.')

    def _create_users(self):
        from apps.users.models import User
        self.stdout.write('  Création des utilisateurs...')

        User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@ult.ac.cd',
                'first_name': 'Super',
                'last_name': 'Admin',
                'role': 'admin',
                'employee_id': 'ADM001',
                'is_staff': True,
                'is_superuser': True,
            }
        )[0].set_password('admin123')

        # Forcer le mot de passe
        admin = User.objects.get(username='admin')
        admin.set_password('admin123')
        admin.save()

        for username, data in [
            ('doyen_sci', {
                'email': 'doyen@ult.ac.cd', 'first_name': 'Jean-Pierre',
                'last_name': 'Kabila', 'role': 'dean', 'employee_id': 'DEAN001'
            }),
            ('prof_math', {
                'email': 'math@ult.ac.cd', 'first_name': 'Marie',
                'last_name': 'Mutombo', 'role': 'professor', 'employee_id': 'PROF001'
            }),
            ('prof_info', {
                'email': 'info@ult.ac.cd', 'first_name': 'Pierre',
                'last_name': 'Mwamba', 'role': 'professor', 'employee_id': 'PROF002'
            }),
            ('prof_eco', {
                'email': 'eco@ult.ac.cd', 'first_name': 'Alice',
                'last_name': 'Nkusu', 'role': 'professor', 'employee_id': 'PROF003'
            }),
            ('etud001', {
                'email': 'etud1@ult.ac.cd', 'first_name': 'Joël',
                'last_name': 'Banza', 'role': 'student', 'employee_id': None
            }),
        ]:
            user, _ = User.objects.get_or_create(username=username, defaults=data)
            user.set_password(username.split('_')[-1] + '123' if '_' in username else 'etud123')
            user.save()

        self.stdout.write(self.style.SUCCESS('  ✓ Utilisateurs créés'))

    def _create_academic_structure(self):
        from apps.academic.models import Faculty, Department, Program, Level, Subject
        from apps.users.models import User
        self.stdout.write('  Création de la structure académique...')

        doyen = User.objects.filter(role='dean').first()

        # Facultés
        fac_sci, _ = Faculty.objects.get_or_create(
            code='FSI',
            defaults={'name': 'Faculté des Sciences Informatiques', 'dean': doyen}
        )
        fac_eco, _ = Faculty.objects.get_or_create(
            code='FSEG',
            defaults={'name': 'Faculté des Sciences Économiques et de Gestion'}
        )

        # Départements
        dept_info, _ = Department.objects.get_or_create(
            code='INFO',
            defaults={'name': 'Département Informatique', 'faculty': fac_sci}
        )
        dept_math, _ = Department.objects.get_or_create(
            code='MATH',
            defaults={'name': 'Département Mathématiques', 'faculty': fac_sci}
        )
        dept_gestion, _ = Department.objects.get_or_create(
            code='GEST',
            defaults={'name': 'Département Gestion', 'faculty': fac_eco}
        )

        # Programmes
        prog_lic_info, _ = Program.objects.get_or_create(
            code='LIC-INFO',
            defaults={
                'name': 'Licence en Informatique',
                'department': dept_info,
                'program_type': 'licence',
                'duration_years': 3,
            }
        )
        prog_lic_gestion, _ = Program.objects.get_or_create(
            code='LIC-GEST',
            defaults={
                'name': 'Licence en Gestion',
                'department': dept_gestion,
                'program_type': 'licence',
                'duration_years': 3,
            }
        )

        # Niveaux
        for year in range(1, 4):
            Level.objects.get_or_create(
                program=prog_lic_info,
                year_number=year,
                defaults={'name': f'L{year} Informatique'}
            )
            Level.objects.get_or_create(
                program=prog_lic_gestion,
                year_number=year,
                defaults={'name': f'L{year} Gestion'}
            )

        # Matières
        for code, name in [
            ('MATH', 'Mathématiques'), ('INFO', 'Informatique'),
            ('ECO', 'Économie'), ('STAT', 'Statistiques'),
            ('BD', 'Bases de Données'), ('ALGO', 'Algorithmique'),
            ('COMPTA', 'Comptabilité'), ('DROIT', 'Droit'),
            ('PROG', 'Programmation'), ('RESEAU', 'Réseaux'),
        ]:
            Subject.objects.get_or_create(code=code, defaults={'name': name})

        self.stdout.write(self.style.SUCCESS('  ✓ Structure académique créée'))

    def _create_rooms(self):
        from apps.academic.models import Room
        self.stdout.write('  Création des salles...')

        rooms = [
            ('AMP-A', 'Amphithéâtre A', 'amphi', 300, 'Bâtiment Principal', True, False),
            ('AMP-B', 'Amphithéâtre B', 'amphi', 200, 'Bâtiment Principal', True, False),
            ('S101', 'Salle 101', 'salle', 60, 'Bâtiment A', True, False),
            ('S102', 'Salle 102', 'salle', 60, 'Bâtiment A', True, False),
            ('S201', 'Salle 201', 'salle', 50, 'Bâtiment B', True, False),
            ('S202', 'Salle 202', 'salle', 50, 'Bâtiment B', True, False),
            ('LINFO1', 'Labo Info 1', 'labo_info', 40, 'Bâtiment C', True, True),
            ('LINFO2', 'Labo Info 2', 'labo_info', 40, 'Bâtiment C', True, True),
        ]

        for code, name, rtype, cap, building, projector, computers in rooms:
            Room.objects.get_or_create(
                code=code,
                defaults={
                    'name': name, 'room_type': rtype, 'capacity': cap,
                    'building': building, 'has_projector': projector,
                    'has_computers': computers, 'is_available': True
                }
            )

        self.stdout.write(self.style.SUCCESS('  ✓ Salles créées'))

    def _create_time_slots(self):
        from apps.scheduling.models import TimeSlot
        self.stdout.write('  Création des créneaux horaires...')

        periods = [
            (time(7, 0), time(9, 0), '1ère période matin'),
            (time(9, 0), time(11, 0), '2ème période matin'),
            (time(14, 0), time(16, 0), '1ère période après-midi'),
            (time(16, 0), time(18, 0), '2ème période après-midi'),
        ]

        for day in range(1, 7):
            for start, end, label in periods:
                TimeSlot.objects.get_or_create(
                    day_of_week=day, start_time=start, end_time=end,
                    defaults={'label': label, 'is_active': True}
                )

        self.stdout.write(self.style.SUCCESS('  ✓ Créneaux horaires créés'))

    def _create_academic_year(self):
        from apps.academic.models import AcademicYear
        self.stdout.write('  Création de l\'année académique...')

        AcademicYear.objects.get_or_create(
            name='2024-2025',
            defaults={
                'start_date': date(2024, 9, 1),
                'end_date': date(2025, 6, 30),
                'is_current': True,
                'is_enrollment_open': True,
            }
        )

        self.stdout.write(self.style.SUCCESS('  ✓ Année académique 2024-2025 créée'))

    def _create_professors(self):
        from apps.users.models import User, Professor
        from apps.academic.models import Department, Subject
        self.stdout.write('  Création des profils professeurs...')

        dept_info = Department.objects.filter(code='INFO').first()
        dept_math = Department.objects.filter(code='MATH').first()
        dept_gestion = Department.objects.filter(code='GEST').first()

        subj_math = Subject.objects.filter(code='MATH').first()
        subj_info = Subject.objects.filter(code='INFO').first()
        subj_eco = Subject.objects.filter(code='ECO').first()
        subj_prog = Subject.objects.filter(code='PROG').first()
        subj_algo = Subject.objects.filter(code='ALGO').first()

        prof_configs = [
            ('prof_math', 'maitre_assistant', dept_math, [subj_math], 15),
            ('prof_info', 'charge_cours', dept_info, [subj_info, subj_prog, subj_algo], 18),
            ('prof_eco', 'chef_travaux', dept_gestion, [subj_eco], 12),
        ]

        for username, grade, dept, specialities, max_hours in prof_configs:
            user = User.objects.filter(username=username).first()
            if user:
                prof, _ = Professor.objects.get_or_create(
                    user=user,
                    defaults={
                        'grade': grade,
                        'department': dept,
                        'max_weekly_hours': max_hours,
                        'is_available': True,
                    }
                )
                if specialities:
                    for s in specialities:
                        if s:
                            prof.specialities.add(s)

        self.stdout.write(self.style.SUCCESS('  ✓ Profils professeurs créés'))

    def _create_modules(self):
        from apps.academic.models import Level, Subject, Module, AcademicYear, Course
        self.stdout.write('  Création des modules...')

        # L1 Informatique - Semestre 1
        l1_info = Level.objects.filter(program__code='LIC-INFO', year_number=1).first()
        l2_info = Level.objects.filter(program__code='LIC-INFO', year_number=2).first()

        if not l1_info:
            return

        math_subj = Subject.objects.filter(code='MATH').first()
        info_subj = Subject.objects.filter(code='INFO').first()
        algo_subj = Subject.objects.filter(code='ALGO').first()
        prog_subj = Subject.objects.filter(code='PROG').first()

        modules_l1 = [
            ('MATH101', 'Mathématiques I', math_subj, 1, 4, 4),
            ('INFO101', 'Introduction à l\'Informatique', info_subj, 1, 3, 3),
            ('ALGO101', 'Algorithmique I', algo_subj, 1, 4, 4),
            ('MATH102', 'Mathématiques II', math_subj, 2, 4, 4),
            ('PROG101', 'Programmation I (Python)', prog_subj, 2, 4, 4),
            ('ALGO102', 'Algorithmique II', algo_subj, 2, 4, 4),
        ]

        for code, name, subj, sem, credits, hours in modules_l1:
            Module.objects.get_or_create(
                code=code,
                defaults={
                    'name': name, 'subject': subj, 'level': l1_info,
                    'semester': sem, 'credits': credits, 'weekly_hours': hours,
                    'is_mandatory': True,
                }
            )

        if l2_info:
            bd_subj = Subject.objects.filter(code='BD').first()
            modules_l2 = [
                ('PROG201', 'Programmation II (Java)', prog_subj, 1, 4, 4),
                ('BD201', 'Bases de Données', bd_subj, 1, 4, 4),
                ('ALGO201', 'Algorithmique Avancée', algo_subj, 2, 4, 4),
            ]
            for code, name, subj, sem, credits, hours in modules_l2:
                Module.objects.get_or_create(
                    code=code,
                    defaults={
                        'name': name, 'subject': subj, 'level': l2_info,
                        'semester': sem, 'credits': credits, 'weekly_hours': hours,
                        'is_mandatory': True,
                    }
                )

        # Créer les cours pour l'année 2024-2025
        year = AcademicYear.objects.filter(is_current=True).first()
        if year:
            for module in Module.objects.filter(level__program__code='LIC-INFO'):
                Course.objects.get_or_create(
                    module=module,
                    academic_year=year,
                    semester=module.semester,
                    defaults={
                        'weekly_hours': module.weekly_hours,
                        'expected_students': 45,
                        'status': 'draft',
                    }
                )

        self.stdout.write(self.style.SUCCESS('  ✓ Modules et cours créés'))

    def _create_prerequisites(self):
        from apps.academic.models import Module
        from apps.prerequisites.models import ModulePrerequisite
        self.stdout.write('  Création des prérequis...')

        prereq_map = [
            ('MATH102', 'MATH101'),   # Maths II requiert Maths I
            ('ALGO102', 'ALGO101'),   # Algo II requiert Algo I
            ('PROG101', 'ALGO101'),   # Prog I requiert Algo I
            ('PROG201', 'PROG101'),   # Prog II requiert Prog I
            ('BD201', 'MATH101'),     # BD requiert Maths I (recommandé)
            ('ALGO201', 'ALGO102'),   # Algo Avancée requiert Algo II
            ('ALGO201', 'PROG101'),   # Algo Avancée requiert Prog I
        ]

        for target_code, prereq_code in prereq_map:
            target = Module.objects.filter(code=target_code).first()
            prereq = Module.objects.filter(code=prereq_code).first()
            if target and prereq:
                ModulePrerequisite.objects.get_or_create(
                    module=target,
                    prerequisite=prereq,
                    defaults={
                        'prerequisite_type': 'strict',
                        'minimum_grade': 10.0,
                    }
                )

        self.stdout.write(self.style.SUCCESS('  ✓ Prérequis configurés'))
        self.stdout.write(f'     {ModulePrerequisite.objects.count()} relations créées')
