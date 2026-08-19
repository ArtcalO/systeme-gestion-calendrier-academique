import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from '@/plugins/axios'
import { ElMessage } from 'element-plus'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const token = ref(localStorage.getItem('access_token') || null)

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => ['admin', 'dean', 'staff'].includes(user.value?.role))
  const isProfessor = computed(() => user.value?.role === 'professor')

  async function login(username, password) {
    const res = await axios.post('/auth/login/', { username, password })
    token.value = res.data.access
    localStorage.setItem('access_token', res.data.access)
    localStorage.setItem('refresh_token', res.data.refresh)

    // Fetch user profile
    const meRes = await axios.get('/auth/users/me/')
    user.value = meRes.data
    localStorage.setItem('user', JSON.stringify(meRes.data))
    return user.value
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  return { user, token, isAuthenticated, isAdmin, isProfessor, login, logout }
})
