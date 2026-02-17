sgca_backend/
├── core/                    # Configuration principale
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   └── urls.py
├── api/                     # Application principale
│   ├── models/
│   │   ├── academic.py     # Modèles académiques
│   │   ├── schedule.py     # Modèles d'emploi du temps
│   │   └── teacher.py      # Modèles enseignants
│   ├── serializers/
│   ├── views/
│   │   ├── schedule_views.py
│   │   ├── prerequisite_views.py
│   │   └── teacher_assignment_views.py
│   ├── algorithms/         # Algorithmes métier
│   │   ├── scheduler.py    # Générateur d'emploi du temps
│   │   ├── prerequisite_checker.py
│   │   └── load_balancer.py
│   └── tasks.py            # Tâches Celery
├── bmd_integration/        # Intégration avec BMDSoft
│   ├── adapters/
│   └── sync_services.py
└── utils/                  # Utilitaires