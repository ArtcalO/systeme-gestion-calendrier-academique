<template>
  <div class="algo-page">
    <div class="page-header">
      <div>
        <h2>Historique des algorithmes</h2>
        <p class="subtitle">Journal des exécutions de l'algorithme d'attribution automatique</p>
      </div>
    </div>

    <el-card shadow="never">
      <el-table :data="runs" v-loading="loading" style="width:100%" stripe>
        <el-table-column label="#" width="60" align="center">
          <template #default="{ row }">{{ row.id }}</template>
        </el-table-column>
        <el-table-column label="Année / Sem." width="130">
          <template #default="{ row }">
            <div>{{ row.academic_year_name }}</div>
            <el-tag v-if="row.semester" type="info" size="small">S{{ row.semester }}</el-tag>
            <el-tag v-else type="info" size="small">Tous</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Lancé par" width="160">
          <template #default="{ row }">{{ row.run_by_name || '—' }}</template>
        </el-table-column>
        <el-table-column label="Date" width="160">
          <template #default="{ row }">{{ formatDate(row.started_at) }}</template>
        </el-table-column>
        <el-table-column label="Résultat" width="160" align="center">
          <template #default="{ row }">
            <span class="result-text">
              <strong>{{ row.courses_assigned }}</strong> / {{ row.courses_total }} cours
            </span>
            <el-progress
              :percentage="row.success_rate"
              :color="row.success_rate === 100 ? '#67c23a' : row.success_rate > 50 ? '#e6a23c' : '#f56c6c'"
              :stroke-width="6"
              :show-text="false"
              style="margin-top: 4px"
            />
          </template>
        </el-table-column>
        <el-table-column label="Taux" width="80" align="center">
          <template #default="{ row }">{{ row.success_rate }}%</template>
        </el-table-column>
        <el-table-column label="Temps" width="90" align="center">
          <template #default="{ row }">{{ row.execution_time_ms }}ms</template>
        </el-table-column>
        <el-table-column label="Statut" width="120">
          <template #default="{ row }">
            <el-tag :type="runStatusType(row.status)" size="small">{{ runStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Détails" width="80" align="center">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="viewLog(row)">Log</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-row">
        <el-pagination v-model:current-page="page" :total="total" layout="total, prev, pager, next" @change="load" />
      </div>
    </el-card>

    <!-- Log dialog -->
    <el-dialog v-model="showLog" title="Journal d'exécution" width="640px">
      <div v-if="selectedRun">
        <el-descriptions :column="2" border size="small" class="mb-3">
          <el-descriptions-item label="Cours total">{{ selectedRun.courses_total }}</el-descriptions-item>
          <el-descriptions-item label="Cours assignés">{{ selectedRun.courses_assigned }}</el-descriptions-item>
          <el-descriptions-item label="Non assignés">{{ selectedRun.courses_unassigned }}</el-descriptions-item>
          <el-descriptions-item label="Taux de succès">{{ selectedRun.success_rate }}%</el-descriptions-item>
        </el-descriptions>
        <div v-if="selectedRun.error_message" class="error-box">
          <strong>Erreur :</strong> {{ selectedRun.error_message }}
        </div>
        <div class="log-box">
          <div v-for="(entry, i) in (selectedRun.algorithm_log || [])" :key="i" class="log-entry">
            <span class="log-level" :class="entry.level?.toLowerCase()">{{ entry.level }}</span>
            {{ entry.message }}
          </div>
          <div v-if="!selectedRun.algorithm_log?.length" class="log-empty">Aucun log disponible.</div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from '@/plugins/axios'

const loading = ref(false)
const runs = ref([])
const total = ref(0)
const page = ref(1)
const showLog = ref(false)
const selectedRun = ref(null)

const statusMap = { running: 'En cours', completed: 'Terminé', failed: 'Échoué', partial: 'Partiel' }
const statusTypes = { running: 'warning', completed: 'success', failed: 'danger', partial: 'warning' }
function runStatusLabel(s) { return statusMap[s] || s }
function runStatusType(s) { return statusTypes[s] || 'info' }
function formatDate(d) { return d ? new Date(d).toLocaleString('fr-FR') : '—' }

async function load() {
  loading.value = true
  try {
    const res = await axios.get('/assignments/algorithm-runs/', { params: { page: page.value, page_size: 20 } })
    const d = res.data
    runs.value = d.results || d
    total.value = d.count || runs.value.length
  } finally { loading.value = false }
}

function viewLog(run) {
  selectedRun.value = run
  showLog.value = true
}

onMounted(load)
</script>

<style scoped>
.algo-page { max-width: 1200px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.page-header h2 { font-size: 22px; font-weight: 700; color: #1e2a3a; }
.subtitle { color: #909399; font-size: 13px; }
.pagination-row { display: flex; justify-content: flex-end; margin-top: 16px; }
.result-text { font-size: 13px; }
.mb-3 { margin-bottom: 16px; }
.log-box { background: #1e2a3a; border-radius: 6px; padding: 12px; max-height: 300px; overflow-y: auto; }
.log-entry { font-family: monospace; font-size: 12px; color: #c0cfe0; padding: 2px 0; }
.log-level { font-weight: 700; margin-right: 6px; }
.log-level.info { color: #409eff; }
.log-level.warning { color: #e6a23c; }
.log-level.error { color: #f56c6c; }
.log-level.success { color: #67c23a; }
.log-empty { color: #4a6680; font-style: italic; font-size: 12px; }
.error-box { background: #fef0f0; border: 1px solid #fde2e2; border-radius: 6px; padding: 10px; color: #f56c6c; margin-bottom: 12px; font-size: 13px; }
</style>
