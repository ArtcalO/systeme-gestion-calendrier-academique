# SGCA-ULT — Système de Gestion du Calendrier Académique

Université de Lubumbashi — Application complète de planification académique.

---

## 🚀 Démarrage rapide

### Option 1 — Docker Compose (recommandé)

```bash
docker-compose up --build
```

- Frontend : http://localhost:3000
- Backend API : http://localhost:8000
- Docs API : http://localhost:8000/api/docs/

### Option 2 — Manuel

**Backend :**
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # puis éditer .env
python manage.py migrate
python manage.py seed_ult_data   # données de test
python manage.py runserver
```

**Frontend :**
```bash
cd frontend
npm install
npm run dev
```

---

## 📋 Fonctionnalités

### 📅 Calendrier académique
| Fonctionnalité | Description |
|---|---|
| Génération automatique | Algorithme de placement sans conflits salle/prof |
| Vue hebdomadaire | Grille navigable semaine par semaine |
| Vue annuelle | Toutes les semaines du semestre |
| **Impression** | Bouton imprimer → PDF navigateur (hebdo + annuel) |
| Export iCal | Fichier `.ics` compatible Google Calendar, Outlook |
| Détection conflits | Salle, professeur, niveau — avec résolution manuelle |

### 🔗 Prérequis (amélioré)
| Type | Signification |
|---|---|
| **Strict** | Le cours A doit être complété AVANT que B soit planifié |
| **Coréquisit** | A et B peuvent être planifiés EN PARALLÈLE (même semestre) |
| **Recommandé** | Conseillé de faire A avant B |

**Outils :**
- Graphe de dépendances par programme (visualisation par semestre)
- Validation (détection de cycles, incohérences de niveaux)
- Ordre de planification recommandé (tri topologique)
- Vérification si un cours peut être planifié selon ses prérequis

### 👥 Gestion académique
- Années académiques, Facultés, Départements, Programmes, Niveaux
- Modules (cours magistral, TP, TD, séminaire, stage, projet)
- Cours planifiés par année/semestre
- Professeurs avec grade, spécialités, charge horaire
- Salles avec capacité, équipements, disponibilité

---

## 🏗️ Architecture

```
sgca-ult/
├── backend/                    # Django REST Framework
│   ├── apps/
│   │   ├── academic/           # Modèles académiques
│   │   ├── prerequisites/      # Prérequis (amélioré)
│   │   ├── scheduling/         # Emplois du temps (amélioré)
│   │   ├── course_assignment/  # Assignation cours-professeurs
│   │   └── users/              # Auth JWT
│   └── sgca_project/           # Config Django
│
└── frontend/                   # Vue 3 + Element Plus
    └── src/
        ├── plugins/axios.js    # HTTP client global (JWT auto)
        ├── reusables/mixins.js # Composables réutilisables
        ├── store/auth.js       # Pinia — authentification
        ├── router/             # Vue Router 4
        ├── views/              # Pages (une par fonctionnalité)
        └── components/         # Modals + composants calendrier
```

---

## 🔑 Comptes par défaut (après seed_ult_data)

| Rôle | Username | Mot de passe |
|---|---|---|
| Admin | `admin` | `admin123` |
| Doyen | `doyen_fst` | `password123` |
| Professeur | `prof_pierre` | `password123` |

---

## 📡 API Endpoints principaux

```
POST   /api/v1/auth/login/
GET    /api/v1/auth/users/me/

# Académique
GET    /api/v1/academic/modules/
GET    /api/v1/academic/courses/
GET    /api/v1/academic/rooms/

# Prérequis
GET    /api/v1/prerequisites/module-prerequisites/
GET    /api/v1/prerequisites/module-prerequisites/graph/?program_id=1
GET    /api/v1/prerequisites/module-prerequisites/planning_order/?program_id=1
POST   /api/v1/prerequisites/module-prerequisites/check_course_scheduling/

# Calendrier
POST   /api/v1/scheduling/schedules/generate/
GET    /api/v1/scheduling/schedules/{id}/weekly_view/?week=2024-W35
GET    /api/v1/scheduling/schedules/{id}/annual_view/
GET    /api/v1/scheduling/schedules/{id}/export_ical/
```

Documentation complète : http://localhost:8000/api/docs/
