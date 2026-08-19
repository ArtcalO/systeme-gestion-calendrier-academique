<template>
  <div class="load-page">
    <div class="page-header">
      <div>
        <h2>Charge d'enseignement</h2>
        <p class="subtitle">Analyse et équité de la charge horaire des professeurs</p>
      </div>
      <el-select v-model="selectedYear" placeholder="Année académique" @change="loadData" style="width:200px">
        <el-option v-for="y in academicYears" :key="y.id" :label="y.name" :value="y.id" />
      </el-select>
    </div>

    <!-- Equity stats -->
    <el-row :gutter="16" class="stats-row" v-if="equity">
      <el-col :xs="12" :sm="6">
        <el-card shadow="never" class="stat-card">
          <div class="stat-value primary">{{ equity.statistics?.average_load_percentage }}%</div>
          <div class="stat-label">Charge moyenne</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="never" class="stat-card">
          <div class="stat-value success">{{ equity.statistics?.equity_score }}</div>
          <div class="stat-label">Score d'équité /100</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="never" class="stat-card">
          <div class="stat-value danger">{{ equity.statistics?.max_load_percentage }}%</div>
          <div class="stat-label">Charge maximale</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="never" class="stat-card">
          <div class="stat-value warning">{{ equity.overloaded_professors?.length }}</div>
          <div class="stat-label">Surchargés (&gt;90%)</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Alerts -->
    <el-alert v-if="equity?.overloaded_professors?.length" type="error" class="mt-2" :closable="false"
      :title="`${equity.overloaded_professors.length} professeur(s) surchargés : ${equity.overloaded_professors.map(p => p.name).join(', ')}`" />
    <el-alert v-if="equity?.underloaded_professors?.length" type="warning" class="mt-2" :closable="false"
      :title="`${equity.underloaded_professors.length} professeur(s) sous-chargés (<30%) : ${equity.underloaded_professors.map(p => p.name).join(', ')}`" />

    <!-- Filter by semester -->
    <el-card shadow="never" class="filter-card">
      <el-radio-group v-model="selectedSemester" @change="loadReports">
        <el-radio-button :label="null">Tous</el-radio-button>
        <el-radio-button :label="1">Semestre 1</el-radio-button>
        <el-radio-button :label="2">Semestre 2</el-radio-button>
      </el-radio-group>
    </el-card>

    <!-- Reports table -->
    <el-card shadow="never" class="mt-3">
      <el-table :data="reports" v-loading="loading" style="width:100%" stripe>
        <el-table-column label="Professeur" min-width="200">
          <template #default="{ row }">
            <div>
              <div class="prof-name">{{ row.professor_name }}</div>
              <div class="prof-grade">{{ row.professor_grade }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Sem." width="70" align="center">
          <template #default="{ row }">S{{ row.semester }}</template>
        </el-table-column>
        <el-table-column label="Cours" width="70" align="center">
          <template #default="{ row }">{{ row.total_courses }}</template>
        </el-table-column>
        <el-table-column label="H/sem." width="80" align="center">
          <template #default="{ row }">{{ row.total_weekly_hours }}h</template>
        </el-table-column>
        <el-table-column label="H max" width="80" align="center">
          <template #default="{ row }">{{ row.max_weekly_hours }}h</template>
        </el-table-column>
        <el-table-column label="Charge" min-width="200">
          <template #default="{ row }">
            <div class="load-bar-wrap">
              <el-progress
                :percentage="Math.min(row.load_percentage, 100)"
                :color="loadColor(row.load_percentage)"
                :stroke-width="14"
                :show-text="false"
              />
              <span class="load-pct" :style="{ color: loadColor(row.load_percentage) }">
                {{ row.load_percentage?.toFixed(1) }}%
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="État" width="110">
          <template #default="{ row }">
            <el-tag :type="loadTagType(row.load_percentage)" size="small">
              {{ loadTagLabel(row.load_percentage) }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-row">
        <el-pagination v-model:current-page="page" :total="total" layout="total, prev, pager, next" @change="loadReports" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from '@/plugins/axios'

const loading = ref(false)
const reports = ref([])
const academicYears = ref([])
const equity = ref(null)
const selectedYear = ref('')
const selectedSemester = ref(null)
const total = ref(0)
const page = ref(1)

function loadColor(pct) {
  if (pct > 90) return '#f56c6c'
  if (pct > 70) return '#e6a23c'
  if (pct > 30) return '#67c23a'
  return '#909399'
}
function loadTagType(pct) {
  if (pct > 90) return 'danger'
  if (pct > 70) return 'warning'
  if (pct > 30) return 'success'
  return 'info'
}
function loadTagLabel(pct) {
  if (pct > 90) return 'Surchargé'
  if (pct > 70) return 'Élevée'
  if (pct > 30) return 'Normal'
  return 'Sous-chargé'
}

async function loadData() {
  if (!selectedYear.value) return
  await Promise.all([loadReports(), loadEquity()])
}

async function loadReports() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: 20 }
    if (selectedYear.value) params.academic_year = selectedYear.value
    if (selectedSemester.value) params.semester = selectedSemester.value
    const res = await axios.get('/assignments/load-reports/', { params })
    const d = res.data
    reports.value = d.results || d
    total.value = d.count || reports.value.length
  } finally { loading.value = false }
}

async function loadEquity() {
  try {
    const res = await axios.get('/assignments/load-reports/equity_analysis/', {
      params: { academic_year_id: selectedYear.value }
    })
    equity.value = res.data
  } catch {}
}

onMounted(async () => {
  const res = await axios.get('/academic/academic-years/', { params: { page_size: 50 } })
  academicYears.value = res.data.results || res.data
  const current = academicYears.value.find(y => y.is_current) || academicYears.value[0]
  if (current) { selectedYear.value = current.id; loadData() }
})
</script>

<style scoped>
.load-page { max-width: 1200px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.page-header h2 { font-size: 22px; font-weight: 700; color: #1e2a3a; }
.subtitle { color: #909399; font-size: 13px; }
.stats-row { margin-bottom: 8px; }
.stat-card { text-align: center; }
.stat-value { font-size: 26px; font-weight: 700; }
.stat-value.primary { color: #409eff; }
.stat-value.success { color: #67c23a; }
.stat-value.danger { color: #f56c6c; }
.stat-value.warning { color: #e6a23c; }
.stat-label { font-size: 12px; color: #909399; margin-top: 2px; }
.filter-card, .mt-3, .mt-2 { margin-top: 16px; }
.prof-name { font-weight: 600; font-size: 13px; }
.prof-grade { font-size: 11px; color: #909399; }
.load-bar-wrap { display: flex; align-items: center; gap: 8px; }
.load-pct { font-size: 12px; font-weight: 600; min-width: 42px; }
.pagination-row { display: flex; justify-content: flex-end; margin-top: 16px; }
</style>
