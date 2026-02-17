import { createRouter, createWebHistory } from 'vue-router'
import TheLayout from '@/components/layout/TheLayout.vue'
import store from "../store"

//Login

import LoginView from '../views/auth/LoginView.vue'
import RegisterView from '../views/auth/RegisterView.vue'

//Profile
import CompleteProfile from '../views/profile/CompleteProfile.vue'

//Niveau
import NiveauxView from "../views/niveaux/NiveauxView.vue"
import CreateNiveau from "../views/niveaux/CreateNiveau.vue"

//Section
import SectionsView from "../views/sections/SectionsView.vue"
import CreateSection from "../views/sections/CreateSection.vue"

//Profs
import ProfsView from "../views/profs/ProfsView.vue"
import CreateProf from "../views/profs/CreateProf.vue"

//Classe
import ClassesView from "../views/classes/ClassesView.vue"
import CreateClasse from "../views/classes/CreateClasse.vue"

//Classe
import ElevesView from "../views/eleves/ElevesView.vue"
import CreateEleve from "../views/eleves/CreateEleve.vue"

//Domaine
import DomainesView from "../views/domaines/DomainesView.vue"
import CreateDomaine from "../views/domaines/CreateDomaine.vue"

//Discipline
import DisciplinesView from "../views/disciplines/DisciplinesView.vue"
import CreateDiscipline from "../views/disciplines/CreateDiscipline.vue"
import CompetencesView from '@/views/disciplines/competences/CompetencesView.vue'
import CreateCompetence from '@/views/disciplines/competences/CreateCompetence.vue'

//Theme
import ThemesView from "../views/themes/ThemesView.vue"
import CreateTheme from "../views/themes/CreateTheme.vue"

//Theme
import LeconsView from "../views/lecons/LeconsView.vue"
import CreateLecon from "../views/lecons/CreateLecon.vue"
import LeconPreview from "../views/lecons/LeconPreview.vue"

//Exercicies

import ExercicesView from "../views/exercices/ExercicesView.vue"
import CreateExercice from "../views/exercices/CreateExercice.vue"
import ExercicesPreview from "../views/exercices/ExercicesPreview.vue"

//cours peciaux

import CoursSpeciaux from "../views/cours-speciaux/CoursSpeciaux.vue"
import CreateCoursSpecial from "../views/cours-speciaux/CreateCoursSpecial.vue"
import ChapitresView from "../views/chapitres-csp/ChapitresView.vue"
import CreateChapitre from "../views/chapitres-csp/CreateChapitre.vue"
import ChapitrePreview from "../views/chapitres-csp/ChapitrePreview.vue"
import CreateExerciceCSP from "../views/exercices-csp/CreateExerciceCSP.vue"
import ExerciceCSP from "../views/exercices-csp/ExerciceCSP.vue"

//Epreuves types
import EpTypClasses from "../views/epreuves-types/EpTypClasses.vue"
import EpTypDomaines from "../views/epreuves-types/EpTypDomaines.vue"
import EpreuvesTypes from "../views/epreuves-types/EpreuvesTypes.vue"
import CreateEpreuveType from "../views/epreuves-types/CreateEpreuveType.vue"
import EpreuvePreview from "../views/epreuves-types/EpreuvePreview.vue"


//bibl iotheque

import BooksView from "../views/bibliotheque/BooksView.vue"
import CreateBook from "../views/bibliotheque/CreateBook.vue"
import BookPreview from "../views/bibliotheque/BookPreview.vue"

import CreateFormule from "../views/lecons/CreateFormule.vue"
import FormulePreview from "../views/lecons/FormulePreview.vue"

//Evaluation
import CreateEvaluation from "../views/evaluations/CreateEvaluation.vue"
import EvaluationsView from "../views/evaluations/EvaluationsView.vue"
import PointsEvaluation from "../views/evaluations/PointsEvaluation.vue"

//palamres
import PalmaresDiscipline from "../views/palmares/PalmaresDiscipline.vue"

//bulletins

import BulletinsView from "../views/bulletins/BulletinsView.vue"

//AI
import ChatAi from "../views/ai/ChatAi.vue"


const routes= [
    {
      path: '/',
      name: 'layout',
      component: TheLayout,
      children: [
        {
          path: 'profile',
          children: [
            {
              path: '',
              name: 'profile',
              component: CompleteProfile,
            },
            {
              path: 'complete/:id',
              name: 'completeProfile',
              component: CompleteProfile,
            },
          ]
        },
        {
          path: 'niveaux',
          children: [
            {
              path: '',
              name: 'niveaux',
              component: NiveauxView,
            },
            {
              path: 'create',
              name: 'createNiveau',
              component: CreateNiveau,
            },
            {
              path: 'modify/:id',
              name: 'modifyNiveau',
              component: CreateNiveau,
            },
          ]
        },
        {
          path: 'chat-ai',
          children: [
            {
              path: '',
              name: 'chatAi',
              component: ChatAi,
            },
          ]
        },
        {
          path: 'sections',
          children: [
            {
              path: '',
              name: 'sections',
              component: SectionsView,
            },
            {
              path: 'create',
              name: 'createSection',
              component: CreateSection,
            },
            {
              path: 'modify/:id',
              name: 'modifyClasse',
              component: CreateSection,
            },
          ]
        },
        {
          path: 'profs',
          children: [
            {
              path: '',
              name: 'profs',
              component: ProfsView,
            },
            {
              path: 'create',
              name: 'createProf',
              component: CreateProf,
            },
            {
              path: 'modify/:id',
              name: 'modifyProf',
              component: CreateProf,
            },
          ]
        },
        {
          path: 'classes',
          children: [
            {
              path: '',
              name: 'classes',
              component: ClassesView,
            },
            {
              path: 'create',
              name: 'createClasse',
              component: CreateClasse,
            },
            {
              path: 'modify/:id',
              name: 'modifyClasse',
              component: CreateClasse,
            },
          ]
        },
        {
          path: 'eleves',
          children: [
            {
              path: '',
              name: 'eleves',
              component: ElevesView,
            },
            {
              path: 'create',
              name: 'createEleve',
              component: CreateEleve,
            },
            {
              path: ':id_classe/class-students',
              name: 'elevesClasse',
              component: ElevesView,
            },
            {
              path: 'modify/:id_eleve',
              name: 'modifyEleve',
              component: CreateEleve,
            },
          ]
        },
        {
          path: 'domaines',
          children: [
            {
              path: ':id_classe/classe',
              name: 'domainesClasse',
              component: DomainesView,
            },
            {
              path: '',
              name: 'domaines',
              component: DomainesView,
            },
            {
              path: 'create',
              name: 'createDomaine',
              component: CreateDomaine,
            },
            {
              path: 'modify/:id',
              name: 'modifyDomaine',
              component: CreateDomaine,
            },
          ]
        },
        {
          path: 'disciplines',
          children: [
            {
              path: ':id_domaine/domaine',
              name: 'disciplinesDomaine',
              component: DisciplinesView,
            },
            {
              path: '',
              name: 'disciplines',
              component: DisciplinesView,
            },
            {
              path: 'create',
              name: 'createDiscipline',
              component: CreateDiscipline,
            },
            {
              path: 'modify/:id',
              name: 'modifyDiscipline',
              component: CreateDiscipline,
            },
            {
              path: 'competences/:id_discipline',
              name: 'competencesDiscipline',
              component: CompetencesView,
            },
            {
              path: 'competences/:id_discipline/create',
              name: 'createCompetenceDiscipline',
              component: CreateCompetence,
            },
          ]
        },
        {
          path: 'palmares',
          children: [
            {
              path: '',
              name: 'palmares',
              component: PalmaresDiscipline,
            },
            {
              path: ':id_discipline/discipline',
              name: 'palmaresDiscipline',
              component: PalmaresDiscipline,
            },
          ]
        },
        {
          path: 'bulletins',
          children: [
            {
              path: '',
              name: 'bulletins',
              component: BulletinsView,
            }
          ]
        },
        {
          path: 'evaluations',
          children: [
            {
              path: ':id_discipline/',
              name: 'evaluationsView',
              component: EvaluationsView,
            },
            {
              path: '',
              name: 'evaluations',
              component: EvaluationsView,
            },
            {
              path: ':id_discipline/create',
              name: 'createEvaluation',
              component: CreateEvaluation,
            },
            {
              path: 'modify/:id_evaluation',
              name: 'modifyEvaluation',
              component: CreateEvaluation,
            },
            {
              path: ':id_evaluation/points',
              name: 'pointsEvaluations',
              component: PointsEvaluation,
            },
          ]
        },
        {
          path: 'themes',
          children: [
            {
              path: ':id_discipline/themes',
              name: 'themesDiscipline',
              component: ThemesView,
            },
            {
              path: '',
              name: 'themes',
              component: ThemesView,
            },
            {
              path: 'create',
              name: 'createTheme',
              component: CreateTheme,
            },
            {
              path: 'modify/:id',
              name: 'modifyTheme',
              component: CreateTheme,
            },
          ]
        },
        {
          path: 'lecons',
          children: [
            {
              path: ':id_theme/lecons',
              name: 'leconsTheme',
              component: LeconsView,
            },
            {
              path: '',
              name: 'lecons',
              component: LeconsView,
            },
            {
              path: 'create',
              name: 'createLecon',
              component: CreateLecon,
            },
            {
              path: 'modify/:id',
              name: 'modifyLecon',
              component: CreateLecon,
            },
            {
              path: 'preview/:id',
              name: 'leconPreview',
              component: LeconPreview,
            },
          ]
        },
        {
          path: 'exercices',
          children: [
            {
              path: 'lecons/:id',
              name: 'exercicesView',
              component: ExercicesView,
            },
            {
              path: 'create/:id',
              name: 'createExercice',
              component: CreateExercice,
            },
            {
              path: 'preview/:id',
              name: 'exercicesPreview',
              component: ExercicesPreview,
            },
          ]
        },
        {
          path: 'cours-peciaux',
          children: [
            {
              path: '',
              name: 'coursSpeciaux',
              component: CoursSpeciaux,
            },
            {
              path: 'create',
              name: 'createCoursSpecial',
              component: CreateCoursSpecial,
            },
          ]
        },
        {
          path: 'chapitres-csp',
          children: [
            {
              path: ':id',
              name: 'chapitres',
              component: ChapitresView,
            },
            {
              path: ':id/create',
              name: 'createChapitre',
              component: CreateChapitre,
            },
            {
              path: ':id/preivew',
              name: 'chapitrePreview',
              component: ChapitrePreview,
            },
          ]
        },
        {
          path: 'formules',
          children: [
            {
              path: ':id_lecon/create',
              name: 'createFormule',
              component: CreateFormule,
            },
            {
              path: ':id_lecon/preivew',
              name: 'formulePreview',
              component: FormulePreview,
            },
            {
              path: ':id_formule/update',
              name: 'updateFormule',
              component: CreateFormule,
            },

          ]
        },
        {
          path: 'exercices-csp',
          children: [
            {
              path: ':id',
              name: 'exerciceCSP',
              component: ExerciceCSP,
            },
            {
              path: ':id/create',
              name: 'createExerciceCSP',
              component: CreateExerciceCSP,
            },
          ]
        },
        {
          path: 'bibliotheque',
          children: [
            {
              path: '',
              name: 'booksView',
              component: BooksView,
            },
            {
              path: 'create',
              name: 'createBook',
              component: CreateBook,
            },
            {
              path: ':id/modify',
              name: 'modifyBook',
              component: CreateBook,
            },
            {
              path: ':id/preview',
              name: 'bookPreview',
              component: BookPreview,
            },
          ]
        },
        {
          path: 'epreuves-types',
          children: [
            {
              path: '',
              name: 'epTypClasses',
              component: EpTypClasses,
            },
            {
              path: ':id_classe/domaines',
              name: 'epTypDomaines',
              component: EpTypDomaines,
            },
            {
              path: ':id_domaine/epreuves',
              name: 'epreuvesTypes',
              component: EpreuvesTypes,
            },
            {
              path: ':id_discipline/creer',
              name: 'createEpreuveType',
              component: CreateEpreuveType,
            },
            {
              path: ':id_epreuve/preview',
              name: 'epreuvePreview',
              component: EpreuvePreview,
            },
          ]
        },

      ],
      meta: { requiresAuth: true },
    },    
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { requiresAuth: false },
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: { requiresAuth: false },
    },
    
  ]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach((to) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!store.state.user?.access)
      return { name: 'login' }
  }
})

export default router
