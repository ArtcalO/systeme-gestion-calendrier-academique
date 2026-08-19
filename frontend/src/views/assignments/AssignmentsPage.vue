<template>
  <div class="assignments-page">
    <div class="page-header">
      <div>
        <h2>Attributions de cours</h2>
        <p class="subtitle">Gestion et suivi des attributions professeurs ↔ cours</p>
      </div>
      <div class="header-actions">
        <el-button type="success" :icon="MagicStick" @click="showAlgoModal = true">
          Lancer l'algorithme
        </el-button>
        <el-button type="primary" :icon="Plus" @click="openModal()">Attribution manuelle</el-button>
      </div>
    </div>

    <!-- Stats bar -->
    <el-row :gutter="16" class="stats-row">
      <el-col :xs="12" :sm="6">
        <el-card shadow="never" class="stat-card">
          <div class="stat-value">{{ stats.total }}</div>
          <div class="stat-label">Total</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="never" class="stat-card confirmed">
          <div class="stat-value">{{ stats.confirmed }}</div>
          <div class="stat-label">Confirmées</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="never" class="stat-card pending">
          <div class="stat-value">{{ stats.pending }}</div>
          <div class="stat-label">En attente</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="never" class="stat-card proposed">
          <div class="stat-value">{{ stats.proposed }}</div>
          <div class="stat-label">Proposées</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Filters -->
    <el-card shadow="never" class="filter-card">
      <el-row :gutter="16">
        <el-col :xs="24" :sm="7">
          <el-input v-model="filters.search" placeholder="Cours, professeur..." clearable @input="load" />
        </el-col>
        <el-col :xs="24" :sm="5">
          <el-select v-model="filters.academic_year" placeholder="Année" clearable @change="load" style="width:100%">
            <el-option v-for="y in academicYears" :key="y.id" :label="y.name" :value="y.id" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="4">
          <el-select v-model="filters.semester" placeholder="Semestre" clearable @change="load" style="width:100%">
            <el-option :value="1" label="Semestre 1" />
            <el-option :value="2" label="Semestre 2" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="5">
          <el-select v-model="filters.status" placeholder="Statut" clearable @change="load" style="width:100%">
            <el-option value="proposed" label="Proposée" />
            <el-option value="pending" label="En attente" />
            <el-option value="confirmed" label="Confirmée" />
            <el-option value="declined" label="Refusée" />
            <el-option value="cancelled" label="Annulée" />
          </el-select>
        </el-col>
      </el-row>
    </el-card>

    <el-card shadow="never" class="mt-3">
      <el-table :data="assignments" v-loading="loading" style="width:100%" stripe>
        <el-table-column label="Cours" min-width="200">
          <template #default="{ row }">
            <div class="course-cell">
              <span class="course-code">{{ row.course_code }}</span>
              <span class="course-name">{{ row.course_name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Professeur" min-width="180">
          <template #default="{ row }">
            <div>
              <div class="prof-name">{{ row.professor_name }}</div>
              <div class="prof-grade">{{ row.professor_grade }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Année / Sem." width="120" align="center">
          <template #default="{ row }">
            <div class="small-text">{{ row.academic_year }}</div>
            <el-tag type="info" size="small">S{{ row.semester }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="H/sem." width="80" align="center">
          <template #default="{ row }">{{ row.weekly_hours }}h</template>
        </el-table-column>
        <el-table-column label="Score" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="scoreType(row.score)" size="small">{{ row.score?.toFixed(0) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Méthode" width="100">
          <template #default="{ row }">
            <el-tag :type="methodType(row.assignment_method)" size="small">
              {{ methodLabel(row.assignment_method) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Statut" width="120">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="130" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-button v-if="row.status === 'proposed' || row.status === 'pending'"
                text type="success" size="small" @click="confirmAssignment(row)">Confirmer</el-button>
              <el-button v-if="row.status !== 'cancelled' && row.status !== 'declined'"
                text type="danger" size="small" @click="cancelAssignment(row)">Annuler</el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-row">
        <el-pagination v-model:current-page="page" :total="total" layout="total, prev, pager, next" @change="load" />
      </div>
    </el-card>

    <!-- Algorithm Modal -->
    <el-dialog v-model="showAlgoModal" title="Lancer l'algorithme d'attribution" width="480px">
      <el-alert type="info" :closable="false" class="mb-3">
        L'algorithme attribuera automatiquement les cours aux professeurs selon leurs spécialités, disponibilités et charge maximale.
      </el-alert>
      <el-form :model="algoForm" label-position="top">
        <el-form-item label="Année académique" required>
          <el-select v-model="algoForm.academic_year_id" style="width:100%">
            <el-option v-for="y in academicYears" :key="y.id" :label="y.name" :value="y.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Semestre (optionnel)">
          <el-select v-model="algoForm.semester" clearable style="width:100%">
            <el-option :value="1" label="Semestre 1" />
            <el-option :value="2" label="Semestre 2" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-switch v-model="algoForm.dry_run" active-text="Mode simulation (sans sauvegarde)" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAlgoModal = false">Annuler</el-button>
        <el-button type="success" :loading="algoRunning" @click="runAlgorithm">
          {{ algoForm.dry_run ? 'Simuler' : 'Lancer' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- Algorithm Result -->
    <el-dialog v-model="showAlgoResult" title="Résultat de l'attribution" width="500px">
      <div v-if="algoResult" class="algo-result">
        <el-result
          :icon="algoResult.result?.courses_unassigned > 0 ? 'warning' : 'success'"
          :title="`${algoResult.result?.assigned_count || 0} / ${algoResult.result?.total_courses || 0} cours assignés`"
        />
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="Temps d'exécution">{{ algoResult.result?.execution_time_ms }}ms</el-descriptions-item>
          <el-descriptions-item label="Non assignés">{{ algoResult.result?.courses_unassigned || 0 }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button type="primary" @click="showAlgoResult = false; load()">Fermer</el-button>
      </template>
    </el-dialog>

    <!-- Manual Assignment Modal -->
    <el-dialog v-model="showModal" title="Attribution manuelle" width="480px">
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <el-form-item label="Cours" prop="course">
          <el-select v-model="form.course" style="width:100%" filterable placeholder="Rechercher un cours...">
            <el-option v-for="c in courses" :key="c.id" :label="`${c.module_code} — ${c.module_name}`" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Professeur" prop="professor">
          <el-select v-model="form.professor" style="width:100%" filterable placeholder="Rechercher un professeur...">
            <el-option v-for="p in professors" :key="p.id" :label="p.user?.full_name || p.user?.username" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Notes">
          <el-input v-model="form.notes" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showModal = false">Annuler</el-button>
        <el-button type="primary" :loading="saving" @click="save">Enregistrer</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus, MagicStick } from '@element-plus/icons-vue'
import axios from '@/plugins/axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const saving = ref(false)
const algoRunning = ref(false)
const assignments = ref([])
const academicYears = ref([])
const courses = ref([])
const professors = ref([])
const total = ref(0)
const page = ref(1)
const filters = ref({ search: '', academic_year: '', semester: '', status: '' })
const stats = ref({ total: 0, confirmed: 0, pending: 0, proposed: 0 })
const showModal = ref(false)
const showAlgoModal = ref(false)
const showAlgoResult = ref(false)
const algoResult = ref(null)
const formRef = ref(null)
const form = reactive({ course: '', professor: '', notes: '' })
const algoForm = reactive({ academic_year_id: '', semester: null, dry_run: false })
const rules = {
  course: [{ required: true, message: 'Cours requis', trigger: 'change' }],
  professor: [{ required: true, message: 'Professeur requis', trigger: 'change' }]
}

const statusMap = { proposed: 'Proposée', pending: 'En attente', confirmed: 'Confirmée', declined: 'Refusée', cancelled: 'Annulée' }
const statusTypes = { proposed: 'info', pending: 'warning', confirmed: 'success', declined: 'danger', cancelled: '' }
const methodMap = { automatic: 'Auto', manual: 'Manuel', prof_request: 'Demande' }
const methodTypes = { automatic: 'info', manual: 'primary', prof_request: 'warning' }

function statusLabel(s) { return statusMap[s] || s }
function statusType(s) { return statusTypes[s] || 'info' }
function methodLabel(m) { return methodMap[m] || m }
function methodType(m) { return methodTypes[m] || 'info' }
function scoreType(s) { return s >= 70 ? 'success' : s >= 40 ? 'warning' : 'danger' }

async function load() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: 20 }
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.academic_year) params['course__academic_year'] = filters.value.academic_year
    if (filters.value.semester) params['course__semester'] = filters.value.semester
    const res = await axios.get('/assignments/', { params })
    const d = res.data
    assignments.value = d.results || d
    total.value = d.count || assignments.value.length
    computeStats()
  } finally { loading.value = false }
}

function computeStats() {
  stats.value = {
    total: total.value,
    confirmed: assignments.value.filter(a => a.status === 'confirmed').length,
    pending: assignments.value.filter(a => a.status === 'pending').length,
    proposed: assignments.value.filter(a => a.status === 'proposed').length
  }
}

function openModal() {
  Object.assign(form, { course: '', professor: '', notes: '' })
  showModal.value = true
}

async function save() {
  await formRef.value.validate()
  saving.value = true
  try {
    await axios.post('/assignments/', form)
    ElMessage.success('Attribution créée')
    showModal.value = false
    load()
  } finally { saving.value = false }
}

async function confirmAssignment(row) {
  await axios.post(`/assignments/${row.id}/confirm/`)
  ElMessage.success('Attribution confirmée')
  load()
}

async function cancelAssignment(row) {
  await ElMessageBox.confirm('Annuler cette attribution ?', 'Confirmation', { type: 'warning' })
  await axios.post(`/assignments/${row.id}/cancel/`)
  ElMessage.success('Attribution annulée')
  load()
}

async function runAlgorithm() {
  if (!algoForm.academic_year_id) { ElMessage.warning('Sélectionnez une année académique'); return }
  algoRunning.value = true
  try {
    const res = await axios.post('/assignments/run_algorithm/', algoForm)
    algoResult.value = res.data
    showAlgoModal.value = false
    showAlgoResult.value = true
  } catch (e) {
    ElMessage.error(e.response?.data?.error || 'Erreur lors de l\'exécution')
  } finally { algoRunning.value = false }
}

onMounted(async () => {
  load()
  const [yearsRes, coursesRes, profsRes] = await Promise.all([
    axios.get('/academic/academic-years/', { params: { page_size: 50 } }),
    axios.get('/academic/courses/', { params: { page_size: 200 } }),
    axios.get('/auth/professors/', { params: { page_size: 200 } })
  ])
  academicYears.value = yearsRes.data.results || yearsRes.data
  courses.value = coursesRes.data.results || coursesRes.data
  professors.value = profsRes.data.results || profsRes.data
  if (academicYears.value.length) algoForm.academic_year_id = academicYears.value.find(y => y.is_current)?.id || academicYears.value[0].id
})
</script>

<style scoped>
.assignments-page { max-width: 1400px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.page-header h2 { font-size: 22px; font-weight: 700; color: #1e2a3a; }
.subtitle { color: #909399; font-size: 13px; }
.header-actions { display: flex; gap: 10px; }
.stats-row { margin-bottom: 16px; }
.stat-card { text-align: center; padding: 8px 0; }
.stat-card.confirmed :deep(.el-card__body) { border-left: 3px solid #67c23a; }
.stat-card.pending :deep(.el-card__body) { border-left: 3px solid #e6a23c; }
.stat-card.proposed :deep(.el-card__body) { border-left: 3px solid #409eff; }
.stat-value { font-size: 28px; font-weight: 700; color: #1e2a3a; }
.stat-label { font-size: 12px; color: #909399; margin-top: 2px; }
.filter-card, .mt-3 { margin-top: 16px; }
.course-cell { display: flex; flex-direction: column; }
.course-code { font-size: 11px; color: #409eff; font-weight: 600; }
.course-name { font-size: 13px; font-weight: 500; }
.prof-name { font-weight: 600; font-size: 13px; }
.prof-grade { font-size: 11px; color: #909399; }
.small-text { font-size: 11px; color: #909399; }
.pagination-row { display: flex; justify-content: flex-end; margin-top: 16px; }
.mb-3 { margin-bottom: 16px; }
.algo-result { text-align: center; }
</style>
