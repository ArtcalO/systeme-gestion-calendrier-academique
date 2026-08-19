<template>
  <div class="schedules-page">
    <div class="page-header">
      <div>
        <h2>Calendriers académiques</h2>
        <p class="subtitle">Planification annuelle et hebdomadaire</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="showGenerateModal = true">Générer un calendrier</el-button>
    </div>

    <!-- Filters -->
    <el-card shadow="never" class="filter-card">
      <el-row :gutter="16">
        <el-col :xs="24" :sm="6">
          <el-select v-model="filters.academic_year" placeholder="Année académique" clearable @change="load" style="width:100%">
            <el-option v-for="y in academicYears" :key="y.id" :label="y.name" :value="y.id" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="6">
          <el-select v-model="filters.status" placeholder="Statut" clearable @change="load" style="width:100%">
            <el-option value="draft" label="Brouillon" />
            <el-option value="published" label="Publié" />
            <el-option value="archived" label="Archivé" />
          </el-select>
        </el-col>
      </el-row>
    </el-card>

    <el-row :gutter="20" class="mt-3">
      <el-col v-for="sched in schedules" :key="sched.id" :xs="24" :sm="12" :md="8" :lg="6">
        <el-card shadow="hover" class="schedule-card" @click="$router.push(`/schedules/${sched.id}`)">
          <div class="scard-header">
            <el-tag :type="schedTag(sched.status).type" size="small">{{ schedTag(sched.status).label }}</el-tag>
            <el-dropdown @click.stop trigger="click" @command="(cmd) => handleCmd(cmd, sched)">
              <el-button text :icon="MoreFilled" size="small" @click.stop />
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="view" :icon="View">Voir détails</el-dropdown-item>
                  <el-dropdown-item v-if="sched.status === 'draft'" command="publish" :icon="Upload">Publier</el-dropdown-item>
                  <el-dropdown-item command="weekly" :icon="Grid">Vue hebdomadaire</el-dropdown-item>
                  <el-dropdown-item command="annual" :icon="Calendar">Vue annuelle</el-dropdown-item>
                  <el-dropdown-item command="ical" :icon="Download">Export iCal</el-dropdown-item>
                  <el-dropdown-item divided command="delete" :icon="Delete" class="danger-item">Supprimer</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
          <div class="scard-name">{{ sched.name }}</div>
          <div class="scard-meta">
            <el-icon><Collection /></el-icon> {{ sched.level?.name || '—' }}
          </div>
          <div class="scard-meta">
            <el-icon><Calendar /></el-icon> {{ sched.academic_year?.name || '—' }} · S{{ sched.semester }}
          </div>
          <div class="scard-meta">
            <el-icon><Clock /></el-icon>
            {{ formatDate(sched.week_start) }} — {{ formatDate(sched.week_end) }}
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <div class="add-card" @click="showGenerateModal = true">
          <el-icon :size="32" color="#c0c4cc"><Plus /></el-icon>
          <span>Nouveau calendrier</span>
        </div>
      </el-col>
    </el-row>

    <el-empty v-if="!loading && schedules.length === 0" description="Aucun calendrier trouvé" class="mt-4" />

    <!-- Generate Modal -->
    <GenerateScheduleModal
      v-if="showGenerateModal"
      :academic-years="academicYears"
      @close="showGenerateModal = false"
      @generated="onGenerated"
    />

    <!-- Weekly View Dialog -->
    <el-dialog v-model="showWeekly" title="Emploi du temps hebdomadaire" width="90%" top="5vh">
      <WeeklyCalendar v-if="showWeekly && selectedSchedule" :schedule-id="selectedSchedule.id" />
    </el-dialog>

    <!-- Annual View Dialog -->
    <el-dialog v-model="showAnnual" title="Planification annuelle" width="90%" top="5vh">
      <AnnualCalendar v-if="showAnnual && selectedSchedule" :schedule-id="selectedSchedule.id" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Edit, Delete, MoreFilled, View, Upload, Grid, Calendar, Download, Clock, Collection } from '@element-plus/icons-vue'
import { useStatusHelpers, useDateHelpers } from '@/reusables/mixins'
import axios from '@/plugins/axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import GenerateScheduleModal from '@/components/modals/GenerateScheduleModal.vue'
import WeeklyCalendar from '@/components/schedule/WeeklyCalendar.vue'
import AnnualCalendar from '@/components/schedule/AnnualCalendar.vue'

const router = useRouter()
const { scheduleStatusTag: schedTag } = useStatusHelpers()
const { formatDate } = useDateHelpers()

const loading = ref(false)
const schedules = ref([])
const academicYears = ref([])
const filters = ref({ academic_year: '', status: '' })
const showGenerateModal = ref(false)
const showWeekly = ref(false)
const showAnnual = ref(false)
const selectedSchedule = ref(null)

async function load() {
  loading.value = true
  try {
    const params = {}
    if (filters.value.academic_year) params.academic_year = filters.value.academic_year
    if (filters.value.status) params.status = filters.value.status
    const res = await axios.get('/scheduling/schedules/', { params })
    schedules.value = res.data.results || res.data
  } finally {
    loading.value = false
  }
}

async function handleCmd(cmd, sched) {
  selectedSchedule.value = sched
  if (cmd === 'view') router.push(`/schedules/${sched.id}`)
  else if (cmd === 'publish') {
    await axios.post(`/scheduling/schedules/${sched.id}/publish/`)
    ElMessage.success('Calendrier publié')
    load()
  } else if (cmd === 'weekly') showWeekly.value = true
  else if (cmd === 'annual') showAnnual.value = true
  else if (cmd === 'ical') {
    window.open(`/api/v1/scheduling/schedules/${sched.id}/export_ical/`, '_blank')
  } else if (cmd === 'delete') {
    await ElMessageBox.confirm('Supprimer ce calendrier ?', 'Confirmation', { type: 'warning' })
    await axios.delete(`/scheduling/schedules/${sched.id}/`)
    ElMessage.success('Supprimé')
    load()
  }
}

function onGenerated() {
  showGenerateModal.value = false
  load()
}

onMounted(async () => {
  load()
  const res = await axios.get('/academic/academic-years/')
  academicYears.value = res.data.results || res.data
})
</script>

<style scoped>
.schedules-page { max-width: 1400px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.page-header h2 { font-size: 22px; font-weight: 700; color: #1e2a3a; }
.subtitle { color: #909399; font-size: 13px; }
.filter-card { margin-top: 0; }
.mt-3 { margin-top: 16px; }
.mt-4 { margin-top: 24px; }
.schedule-card { cursor: pointer; transition: transform .15s; margin-bottom: 16px; }
.schedule-card:hover { transform: translateY(-2px); }
.scard-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.scard-name { font-size: 15px; font-weight: 600; color: #1e2a3a; margin-bottom: 10px; line-height: 1.3; }
.scard-meta { display: flex; align-items: center; gap: 6px; font-size: 13px; color: #606266; margin-bottom: 4px; }
.add-card {
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  min-height: 160px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  color: #c0c4cc;
  font-size: 14px;
  margin-bottom: 16px;
  transition: all .15s;
}
.add-card:hover { border-color: #409EFF; color: #409EFF; }
.danger-item { color: #F56C6C !important; }
</style>
