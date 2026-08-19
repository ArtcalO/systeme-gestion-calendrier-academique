<template>
  <div class="years-page">
    <div class="page-header">
      <div>
        <h2>Années académiques</h2>
        <p class="subtitle">Gestion des années universitaires</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="openModal()">Nouvelle année</el-button>
    </div>

    <el-row :gutter="20" class="mt-3">
      <el-col v-for="yr in years" :key="yr.id" :xs="24" :sm="12" :md="8">
        <el-card shadow="hover" class="year-card" :class="{ 'current-year': yr.is_current }">
          <div class="year-badge" v-if="yr.is_current">
            <el-tag type="success" size="small">Courante</el-tag>
          </div>
          <div class="year-name">{{ yr.name }}</div>
          <div class="year-dates">
            <el-icon><Calendar /></el-icon>
            {{ formatDate(yr.start_date) }} — {{ formatDate(yr.end_date) }}
          </div>
          <el-divider />
          <div class="year-stats">
            <div class="stat">
              <div class="stat-val">{{ yr.courses_count }}</div>
              <div class="stat-lbl">Cours</div>
            </div>
          </div>
          <div class="year-footer">
            <el-tag :type="yr.is_enrollment_open ? 'success' : 'info'" size="small">
              {{ yr.is_enrollment_open ? 'Inscriptions ouvertes' : 'Inscriptions fermées' }}
            </el-tag>
            <div class="year-actions">
              <el-button text type="primary" :icon="Edit" size="small" @click="openModal(yr)" />
              <el-button text type="danger" :icon="Delete" size="small" @click="handleDelete(yr)" />
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="8">
        <div class="add-year-card" @click="openModal()">
          <el-icon :size="32" color="#c0c4cc"><Plus /></el-icon>
          <span>Nouvelle année académique</span>
        </div>
      </el-col>
    </el-row>

    <AcademicYearModal v-if="showModal" :year="editYear" @close="showModal = false" @saved="onSaved" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus, Edit, Delete, Calendar } from '@element-plus/icons-vue'
import { useDateHelpers } from '@/reusables/mixins'
import axios from '@/plugins/axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import AcademicYearModal from '@/components/modals/AcademicYearModal.vue'

const { formatDate } = useDateHelpers()
const loading = ref(false)
const years = ref([])
const showModal = ref(false)
const editYear = ref(null)

async function load() {
  loading.value = true
  try {
    const res = await axios.get('/academic/academic-years/')
    years.value = res.data.results || res.data
  } finally {
    loading.value = false
  }
}

function openModal(yr = null) { editYear.value = yr; showModal.value = true }

async function handleDelete(yr) {
  await ElMessageBox.confirm(`Supprimer l'année ${yr.name} ?`, 'Confirmation', { type: 'warning' })
  await axios.delete(`/academic/academic-years/${yr.id}/`)
  ElMessage.success('Supprimé')
  load()
}

function onSaved() { showModal.value = false; load() }
onMounted(load)
</script>

<style scoped>
.years-page { max-width: 1100px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.page-header h2 { font-size: 22px; font-weight: 700; color: #1e2a3a; }
.subtitle { color: #909399; font-size: 13px; }
.mt-3 { margin-top: 16px; }
.year-card { margin-bottom: 20px; position: relative; transition: transform .15s; }
.year-card:hover { transform: translateY(-2px); }
.current-year { border: 2px solid #67C23A; }
.year-badge { position: absolute; top: -1px; right: 12px; }
.year-name { font-size: 28px; font-weight: 700; color: #409EFF; text-align: center; margin: 12px 0 8px; }
.year-dates { display: flex; align-items: center; gap: 6px; justify-content: center; color: #606266; font-size: 14px; }
.year-stats { display: flex; justify-content: center; gap: 32px; }
.stat { text-align: center; }
.stat-val { font-size: 24px; font-weight: 700; color: #303133; }
.stat-lbl { font-size: 12px; color: #909399; }
.year-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 4px; }
.year-actions { display: flex; gap: 4px; }
.add-year-card {
  border: 2px dashed #dcdfe6; border-radius: 8px;
  min-height: 200px; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 8px;
  cursor: pointer; color: #c0c4cc; font-size: 14px;
  margin-bottom: 20px; transition: all .15s;
}
.add-year-card:hover { border-color: #409EFF; color: #409EFF; }
</style>
