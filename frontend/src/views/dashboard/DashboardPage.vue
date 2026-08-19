<template>
  <div class="dashboard">
    <div class="page-header">
      <h2>Tableau de bord</h2>
      <span class="subtitle">Bienvenue, {{ auth.user?.first_name || auth.user?.username }}</span>
    </div>

    <!-- Stats cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="12" :sm="6" v-for="stat in stats" :key="stat.label">
        <div class="stat-card" :style="{ borderColor: stat.color }">
          <div class="stat-icon" :style="{ background: stat.color + '20', color: stat.color }">
            <el-icon :size="24"><component :is="stat.icon" /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Recent schedules + quick actions -->
    <el-row :gutter="20" class="mt-4">
      <el-col :xs="24" :md="16">
        <el-card shadow="never">
          <template #header>
            <div class="card-header-row">
              <span>Derniers emplois du temps</span>
              <el-button text type="primary" @click="$router.push('/schedules')">Voir tout</el-button>
            </div>
          </template>
          <el-table :data="recentSchedules" v-loading="loading" style="width:100%">
            <el-table-column prop="name" label="Nom" />
            <el-table-column prop="level.name" label="Niveau" width="100" />
            <el-table-column label="Statut" width="120">
              <template #default="{ row }">
                <el-tag :type="scheduleTag(row.status).type" size="small">
                  {{ scheduleTag(row.status).label }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Actions" width="100">
              <template #default="{ row }">
                <el-button text type="primary" size="small" @click="$router.push(`/schedules/${row.id}`)">
                  Ouvrir
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="8">
        <el-card shadow="never">
          <template #header><span>Actions rapides</span></template>
          <div class="quick-actions">
            <el-button type="primary" @click="$router.push('/schedules')" :icon="Grid" style="width:100%">
              Nouveau calendrier
            </el-button>
            <el-button @click="$router.push('/courses')" :icon="Reading" style="width:100%">
              Gérer les cours
            </el-button>
            <el-button @click="$router.push('/prerequisites')" :icon="Share" style="width:100%">
              Configurer prérequis
            </el-button>
            <el-button @click="$router.push('/professors')" :icon="UserFilled" style="width:100%">
              Gérer professeurs
            </el-button>
          </div>
        </el-card>

        <el-card shadow="never" class="mt-3">
          <template #header><span>Année académique courante</span></template>
          <div v-if="currentYear" class="year-info">
            <div class="year-name">{{ currentYear.name }}</div>
            <div class="year-dates">
              {{ formatDate(currentYear.start_date) }} — {{ formatDate(currentYear.end_date) }}
            </div>
            <el-tag :type="currentYear.is_enrollment_open ? 'success' : 'info'" size="small">
              {{ currentYear.is_enrollment_open ? 'Inscriptions ouvertes' : 'Inscriptions fermées' }}
            </el-tag>
          </div>
          <el-empty v-else description="Aucune année courante" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/store/auth'
import { useStatusHelpers, useDateHelpers } from '@/reusables/mixins'
import { Grid, Reading, Share, UserFilled } from '@element-plus/icons-vue'
import axios from '@/plugins/axios'

const auth = useAuthStore()
const { scheduleStatusTag: scheduleTag } = useStatusHelpers()
const { formatDate } = useDateHelpers()

const loading = ref(false)
const recentSchedules = ref([])
const currentYear = ref(null)
const stats = ref([
  { label: 'Modules', value: '—', icon: 'Collection', color: '#409EFF' },
  { label: 'Professeurs', value: '—', icon: 'UserFilled', color: '#67C23A' },
  { label: 'Salles', value: '—', icon: 'OfficeBuilding', color: '#E6A23C' },
  { label: 'Calendriers', value: '—', icon: 'Grid', color: '#9B59B6' },
])

onMounted(async () => {
  loading.value = true
  try {
    const [schedRes, yearRes, modRes, profRes, roomRes] = await Promise.allSettled([
      axios.get('/scheduling/schedules/', { params: { page_size: 5 } }),
      axios.get('/academic/academic-years/', { params: { is_current: true } }),
      axios.get('/academic/modules/', { params: { page_size: 1 } }),
      axios.get('/auth/professors/', { params: { page_size: 1 } }),
      axios.get('/academic/rooms/', { params: { page_size: 1 } }),
    ])

    if (schedRes.status === 'fulfilled') {
      const d = schedRes.value.data
      recentSchedules.value = d.results || d
      stats.value[3].value = d.count || (d.results || d).length
    }
    if (yearRes.status === 'fulfilled') {
      const d = yearRes.value.data
      currentYear.value = d.results?.[0] || d?.[0]
    }
    if (modRes.status === 'fulfilled') stats.value[0].value = modRes.value.data.count || '—'
    if (profRes.status === 'fulfilled') stats.value[1].value = profRes.value.data.count || '—'
    if (roomRes.status === 'fulfilled') stats.value[2].value = roomRes.value.data.count || '—'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.dashboard { max-width: 1400px; }
.page-header { margin-bottom: 24px; }
.page-header h2 { font-size: 22px; font-weight: 700; color: #1e2a3a; }
.subtitle { color: #909399; font-size: 14px; }
.stats-row .el-col { margin-bottom: 16px; }
.stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  border-left: 4px solid;
  box-shadow: 0 2px 8px rgba(0,0,0,.06);
}
.stat-icon { width: 48px; height: 48px; border-radius: 10px; display: flex; align-items: center; justify-content: center; }
.stat-value { font-size: 28px; font-weight: 700; color: #1e2a3a; }
.stat-label { font-size: 12px; color: #909399; margin-top: 2px; }
.mt-4 { margin-top: 20px; }
.mt-3 { margin-top: 16px; }
.card-header-row { display: flex; justify-content: space-between; align-items: center; }
.quick-actions { display: flex; flex-direction: column; gap: 10px; }
.year-info { text-align: center; padding: 8px 0; }
.year-name { font-size: 22px; font-weight: 700; color: #409EFF; }
.year-dates { color: #909399; font-size: 13px; margin: 4px 0 12px; }
</style>
