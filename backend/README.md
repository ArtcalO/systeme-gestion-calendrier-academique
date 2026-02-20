# SGCA - Système de Gestion du Calendrier Académique
## Université du Lac Tanganyika (ULT)

Extension intelligente de BMDSoft | Backend Django REST Framework

---

## 🎯 Fonctionnalités Principales

### 1. Optimisation de la Planification des Horaires
- Génération automatique d'emplois du temps sans conflits
- Algorithme glouton avec vérification des contraintes (salle, professeur, étudiants)
- Détection et résolution des conflits (double réservation salle, professeur occupé)
- Publication des EDT avec contrôle qualité
- Endpoint: `POST /api/v1/scheduling/schedules/generate/`

### 2. Conformité Académique par les Prérequis
- Définition de relations de prérequis (strict, recommandé, coréquisit)
- Vérification automatique lors de chaque demande d'inscription
- Détection de cycles dans le graphe des prérequis (algorithme DFS)
- Système de dérogation pour les cas exceptionnels
- Endpoint: `POST /api/v1/prerequisites/enrollment-requests/`

### 3. Attribution Équilibrée des Cours
- Algorithme de score pondéré (spécialité 40% + disponibilité 30% + grade 20% + équité 10%)
- Attribution automatique en respectant les charges maximales
- Rapports d'équité avec coefficient de variation
- Confirmation par le professeur et/ou l'administration
- Endpoint: `POST /api/v1/assignments/run_algorithm/`

---

## 📁 Structure du Projet

```
sgca/
├── manage.py
├── requirements.txt
├── .env.example
├── sgca_project/
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   └── wsgi.py
└── apps/
    ├── users/           # Auth, Professeurs, Étudiants
    ├── academic/        # Facultés, Modules, Cours, Salles
    ├── scheduling/      # Emplois du temps, Créneaux
    ├── prerequisites/   # Prérequis, Inscriptions
    └── course_assignment/ # Attribution cours, Charges
```

---

## 🚀 Installation

### 1. Prérequis
```bash
Python 3.10+
PostgreSQL 14+
Redis 6+ (pour Celery)
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Configurer l'environnement
```bash
cp .env.example .env
# Éditer .env avec vos paramètres de base de données
```

### 4. Créer la base de données
```bash
# PostgreSQL
createdb sgca_ult

# Migrations
python manage.py makemigrations
python manage.py migrate
```

### 5. Initialiser les données
```bash
python manage.py seed_ult_data
```

### 6. Lancer le serveur
```bash
python manage.py runserver
```

---

## 🔑 Comptes par défaut (après seed)

| Rôle | Username | Mot de passe |
|------|----------|--------------|
| Admin | `admin` | `admin123` |
| Doyen | `doyen_sci` | `doyen123` |
| Professeur Maths | `prof_math` | `prof123` |
| Professeur Info | `prof_info` | `prof123` |
| Étudiant | `etud001` | `etud123` |

---

## 📖 Documentation API

Après lancement, accédez à:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Admin Django**: http://localhost:8000/admin/

---

## 🔌 Endpoints Principaux

### Authentification
```
POST   /api/v1/auth/login/              # Connexion JWT
POST   /api/v1/auth/refresh/            # Rafraîchir token
GET    /api/v1/auth/users/me/           # Profil courant
```

### Structure Académique
```
GET    /api/v1/academic/faculties/
GET    /api/v1/academic/departments/
GET    /api/v1/academic/programs/
GET    /api/v1/academic/modules/
GET    /api/v1/academic/modules/{id}/prerequisite_tree/
GET    /api/v1/academic/rooms/
GET    /api/v1/academic/academic-years/current/
```

### Planification des Horaires
```
POST   /api/v1/scheduling/schedules/generate/      # ⭐ Générer EDT
GET    /api/v1/scheduling/schedules/
POST   /api/v1/scheduling/schedules/{id}/publish/  # Publier
GET    /api/v1/scheduling/slots/by_week/           # EDT hebdomadaire
POST   /api/v1/scheduling/time-slots/create_default_slots/
```

### Gestion des Prérequis
```
POST   /api/v1/prerequisites/enrollment-requests/          # ⭐ Inscription + vérif auto
POST   /api/v1/prerequisites/enrollment-requests/bulk_check/
GET    /api/v1/prerequisites/enrollment-requests/eligible_modules/
POST   /api/v1/prerequisites/enrollment-requests/{id}/grant_waiver/
GET    /api/v1/prerequisites/module-prerequisites/validate_program/
```

### Attribution des Cours
```
POST   /api/v1/assignments/run_algorithm/          # ⭐ Attribution automatique
GET    /api/v1/assignments/summary/
POST   /api/v1/assignments/{id}/confirm/
POST   /api/v1/assignments/{id}/professor_confirm/
GET    /api/v1/assignments/load-reports/equity_analysis/
```

### Professeurs
```
GET    /api/v1/auth/professors/
GET    /api/v1/auth/professors/{id}/workload/
GET    /api/v1/auth/professors/available/
```

---

## ⚙️ Workflow Complet

```
1. Admin crée la structure: Faculté → Département → Programme → Niveaux → Modules
2. Admin définit les prérequis entre modules
3. Admin crée les cours pour l'année académique courante
4. Admin lance l'algorithme d'attribution: POST /api/v1/assignments/run_algorithm/
5. Les professeurs confirment leurs attributions
6. Admin génère les emplois du temps: POST /api/v1/scheduling/schedules/generate/
7. Admin publie les EDT validés
8. Les étudiants s'inscrivent: POST /api/v1/prerequisites/enrollment-requests/
   → Vérification automatique des prérequis
   → Approbation ou rejet immédiat
```

---

## 🏗️ Architecture Technique

- **Framework**: Django 4.2 + Django REST Framework 3.14
- **Auth**: JWT via djangorestframework-simplejwt
- **DB**: PostgreSQL (SQLite pour dev)
- **Cache/Queue**: Redis + Celery
- **Docs**: drf-spectacular (OpenAPI 3.0)
- **Filtres**: django-filter

---

## 🤝 Intégration avec BMDSoft

Le SGCA est conçu comme une extension de BMDSoft. Pour l'intégration:

1. **Import de données**: Utilisez l'admin Django ou les endpoints API pour importer les données existantes de BMDSoft
2. **Authentification unifiée**: Configurez le `AUTH_USER_MODEL` pour pointer vers votre système existant ou synchronisez les utilisateurs
3. **Webhooks**: Ajoutez des signaux Django (`post_save`) pour notifier BMDSoft des changements


pip install -r requirements.txt
cp .env.example .env   # configurer DB
python manage.py makemigrations users academic scheduling prerequisites course_assignment
python manage.py migrate
python manage.py seed_ult_data
python manage.py runserver
