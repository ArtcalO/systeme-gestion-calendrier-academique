# SGCA-ULT Frontend — Vue.js

Système de Gestion du Calendrier Académique — Université de Lubumbashi

## Stack

- **Vue 3** + Composition API
- **Element Plus** (UI Library)
- **Pinia** (State management)
- **Vue Router 4**
- **Axios** (HTTP client, configuré globalement)
- **Vite** (Build tool)

## Structure du projet

```
src/
├── plugins/
│   └── axios.js          # Axios configuré globalement (JWT auto, refresh, erreurs)
├── reusables/
│   └── mixins.js         # Fonctions réutilisables (useApi, useDateHelpers, useStatusHelpers, usePrint...)
├── store/
│   └── auth.js           # Store Pinia : authentification JWT
├── router/
│   └── index.js          # Routes avec navigation guards
├── components/
│   ├── layout/
│   │   └── AppLayout.vue         # Layout principal (sidebar + header)
│   ├── modals/
│   │   ├── CourseModal.vue       # Modal cours
│   │   ├── ModuleModal.vue       # Modal module
│   │   ├── PrerequisiteModal.vue # Modal prérequis
│   │   ├── ProfessorModal.vue    # Modal professeur
│   │   ├── RoomModal.vue         # Modal salle
│   │   ├── AcademicYearModal.vue # Modal année académique
│   │   └── GenerateScheduleModal.vue # Modal génération de calendrier
│   └── schedule/
│       ├── WeeklyCalendar.vue    # Calendrier hebdomadaire (avec impression)
│       └── AnnualCalendar.vue    # Planning annuel (avec impression)
└── views/
    ├── auth/
    │   └── LoginPage.vue
    ├── dashboard/
    │   └── DashboardPage.vue
    ├── academic-years/
    │   └── AcademicYearsPage.vue
    ├── courses/
    │   └── CoursesPage.vue
    ├── modules/
    │   └── ModulesPage.vue
    ├── prerequisites/
    │   └── PrerequisitesPage.vue  # Liste + graphe + ordre de planification
    ├── schedules/
    │   ├── SchedulesPage.vue
    │   └── ScheduleDetailPage.vue # Vue hebdo + annuelle + conflits + créneaux
    ├── professors/
    │   └── ProfessorsPage.vue
    └── rooms/
        └── RoomsPage.vue
```

## Installation et démarrage

```bash
# Installer les dépendances
npm install

# Démarrer en développement (proxy vers backend :8000)
npm run dev

# Build production
npm run build
```

## Configuration

Le proxy Vite redirige automatiquement `/api` vers `http://localhost:8000`.

Pour la production, configurer `VITE_API_BASE_URL` ou un reverse proxy nginx.

## Fonctionnalités clés

### Prérequis
- **Liste** : tous les prérequis avec type (strict / coréquisit / recommandé)
- **Graphe** : visualisation par semestre et niveau avec validation
- **Ordre de planification** : tri topologique recommandé par programme

### Calendrier
- **Vue hebdomadaire** : grille par jour/heure, navigable semaine par semaine
- **Vue annuelle** : toutes les semaines avec recherche
- **Impression** : bouton impression natif (PDF navigateur)
- **Export iCal** : compatible Google Calendar, Outlook

### Général
- Authentification JWT avec refresh automatique
- Responsive (mobile + desktop)
- Filtres et recherche sur toutes les pages
- Notifications toast (succès / erreur)
