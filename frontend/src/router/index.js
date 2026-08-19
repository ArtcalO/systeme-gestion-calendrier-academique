import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/LoginPage.vue'),
    meta: { public: true }
  },
  {
    path: '/',
    component: () => import('@/components/layout/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', name: 'Dashboard', component: () => import('@/views/dashboard/DashboardPage.vue') },
      // Structure académique
      { path: 'faculties', name: 'Faculties', component: () => import('@/views/faculties/FacultiesPage.vue'), meta: { title: 'Facultés' } },
      { path: 'departments', name: 'Departments', component: () => import('@/views/departments/DepartmentsPage.vue'), meta: { title: 'Départements' } },
      { path: 'programs', name: 'Programs', component: () => import('@/views/programs/ProgramsPage.vue'), meta: { title: 'Programmes' } },
      { path: 'levels', name: 'Levels', component: () => import('@/views/levels/LevelsPage.vue'), meta: { title: 'Niveaux' } },
      { path: 'subjects', name: 'Subjects', component: () => import('@/views/subjects/SubjectsPage.vue'), meta: { title: 'Matières / Domaines' } },
      // Cours & Modules
      { path: 'academic-years', name: 'AcademicYears', component: () => import('@/views/academic-years/AcademicYearsPage.vue'), meta: { title: 'Années académiques' } },
      { path: 'modules', name: 'Modules', component: () => import('@/views/modules/ModulesPage.vue'), meta: { title: 'Modules' } },
      { path: 'courses', name: 'Courses', component: () => import('@/views/courses/CoursesPage.vue'), meta: { title: 'Planification cours' } },
      { path: 'prerequisites', name: 'Prerequisites', component: () => import('@/views/prerequisites/PrerequisitesPage.vue'), meta: { title: 'Prérequis' } },
      // Attributions
      { path: 'assignments', name: 'Assignments', component: () => import('@/views/assignments/AssignmentsPage.vue'), meta: { title: 'Attributions de cours' } },
      { path: 'teaching-load', name: 'TeachingLoad', component: () => import('@/views/teaching-load/TeachingLoadPage.vue'), meta: { title: 'Charge d\'enseignement' } },
      { path: 'algorithm-runs', name: 'AlgorithmRuns', component: () => import('@/views/algorithm-runs/AlgorithmRunsPage.vue'), meta: { title: 'Historique algorithme' } },
      // Emplois du temps
      { path: 'schedules', name: 'Schedules', component: () => import('@/views/schedules/SchedulesPage.vue'), meta: { title: 'Calendriers' } },
      { path: 'schedules/:id', name: 'ScheduleDetail', component: () => import('@/views/schedules/ScheduleDetailPage.vue'), meta: { title: 'Détail calendrier' } },
      { path: 'time-slots', name: 'TimeSlots', component: () => import('@/views/time-slots/TimeSlotsPage.vue'), meta: { title: 'Créneaux horaires' } },
      // Ressources humaines
      { path: 'professors', name: 'Professors', component: () => import('@/views/professors/ProfessorsPage.vue'), meta: { title: 'Professeurs' } },
      { path: 'students', name: 'Students', component: () => import('@/views/students/StudentsPage.vue'), meta: { title: 'Étudiants' } },
      { path: 'rooms', name: 'Rooms', component: () => import('@/views/rooms/RoomsPage.vue'), meta: { title: 'Salles' } },
    ]
  },
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isAuthenticated) return '/login'
  if (to.path === '/login' && auth.isAuthenticated) return '/dashboard'
})

export default router
