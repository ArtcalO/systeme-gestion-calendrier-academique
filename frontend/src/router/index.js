import { createRouter, createWebHistory } from 'vue-router'
import TheLayout from '@/components/layout/TheLayout.vue'
import store from "../store"

//Login

import LoginView from '../views/auth/LoginView.vue'


//Profs

import ProfsView from '@/views/profs/ProfsView.vue'
import CreateProf from '@/views/profs/CreateProf.vue'

import AcademicYear from '@/views/academic-year/AcademicYear.vue'


const routes= [
    {
      path: '/',
      name: 'layout',
      component: TheLayout,
      children: [
        {
          path: 'professors',
          children: [
            {
              path: '',
              name: 'professors',
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
          path: 'academic-year',
          children: [
            {
              path: '',
              name: 'academicYear',
              component: AcademicYear,
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
