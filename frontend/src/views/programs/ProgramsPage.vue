<template>
  <div class="programs-page">
    <div class="page-header">
      <div>
        <h2>Programmes</h2>
        <p class="subtitle">Gestion des programmes d'études</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="openModal()">Nouveau programme</el-button>
    </div>

    <el-card shadow="never" class="filter-card">
      <el-row :gutter="16">
        <el-col :xs="24" :sm="8">
          <el-input v-model="filters.search" placeholder="Nom, code..." clearable @input="load" />
        </el-col>
        <el-col :xs="24" :sm="6">
          <el-select v-model="filters.department" placeholder="Département" clearable @change="load" style="width:100%">
            <el-option v-for="d in departments" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="5">
          <el-select v-model="filters.program_type" placeholder="Type" clearable @change="load" style="width:100%">
            <el-option value="licence" label="Licence" />
            <el-option value="master" label="Master" />
            <el-option value="doctorat" label="Doctorat" />
            <el-option value="graduat" label="Graduat" />
            <el-option value="certificat" label="Certificat" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="5">
          <el-select v-model="filters.is_active" placeholder="Statut" clearable @change="load" style="width:100%">
            <el-option :value="true" label="Actif" />
            <el-option :value="false" label="Inactif" />
          </el-select>
        </el-col>
      </el-row>
    </el-card>

    <el-card shadow="never" class="mt-3">
      <el-table :data="programs" v-loading="loading" style="width:100%" stripe>
        <el-table-column label="Code" width="100">
          <template #default="{ row }">
            <el-tag type="primary" size="small">{{ row.code }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="Programme" min-width="200" />
        <el-table-column label="Type" width="110">
          <template #default="{ row }">
            <el-tag :type="typeColor(row.program_type)" size="small">{{ typeLabel(row.program_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Département" min-width="160">
          <template #default="{ row }">{{ row.department_name || '—' }}</template>
        </el-table-column>
        <el-table-column label="Faculté" min-width="140">
          <template #default="{ row }">{{ row.faculty_name || '—' }}</template>
        </el-table-column>
        <el-table-column label="Durée" width="80" align="center">
          <template #default="{ row }">{{ row.duration_years }} ans</template>
        </el-table-column>
        <el-table-column label="Niveaux" width="80" align="center">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ (row.levels || []).length }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Statut" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? 'Actif' : 'Inactif' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="100" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-button text type="primary" :icon="Edit" size="small" @click="openModal(row)" />
              <el-button text type="danger" :icon="Delete" size="small" @click="handleDelete(row)" />
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-row">
        <el-pagination v-model:current-page="page" :total="total" layout="total, prev, pager, next" @change="load" />
      </div>
    </el-card>

    <!-- Modal -->
    <el-dialog v-model="showModal" :title="editItem ? 'Modifier programme' : 'Nouveau programme'" width="560px">
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <el-row :gutter="16">
          <el-col :span="16">
            <el-form-item label="Nom" prop="name">
              <el-input v-model="form.name" placeholder="ex: Licence en Informatique" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Code" prop="code">
              <el-input v-model="form.code" placeholder="ex: L-INFO" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Type de programme" prop="program_type">
              <el-select v-model="form.program_type" style="width:100%">
                <el-option value="licence" label="Licence" />
                <el-option value="master" label="Master" />
                <el-option value="doctorat" label="Doctorat" />
                <el-option value="graduat" label="Graduat" />
                <el-option value="certificat" label="Certificat" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Durée (années)" prop="duration_years">
              <el-input-number v-model="form.duration_years" :min="1" :max="10" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Département">
          <el-select v-model="form.department" style="width:100%" placeholder="Sélectionner (optionnel)" clearable>
            <el-option v-for="d in departments" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Faculté">
          <el-select v-model="form.faculty" style="width:100%" placeholder="Sélectionner (optionnel)" clearable>
            <el-option v-for="f in faculties" :key="f.id" :label="f.name" :value="f.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item>
          <el-switch v-model="form.is_active" active-text="Programme actif" />
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
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import axios from '@/plugins/axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const saving = ref(false)
const programs = ref([])
const departments = ref([])
const faculties = ref([])
const total = ref(0)
const page = ref(1)
const filters = ref({ search: '', department: '', program_type: '', is_active: '' })
const showModal = ref(false)
const editItem = ref(null)
const formRef = ref(null)
const form = reactive({ name: '', code: '', program_type: 'licence', duration_years: 3, department: null, faculty: null, description: '', is_active: true })
const rules = {
  name: [{ required: true, message: 'Nom requis', trigger: 'blur' }],
  code: [{ required: true, message: 'Code requis', trigger: 'blur' }],
  program_type: [{ required: true, message: 'Type requis', trigger: 'change' }],
}

const typeMap = { licence: 'Licence', master: 'Master', doctorat: 'Doctorat', graduat: 'Graduat', certificat: 'Certificat' }
const typeColors = { licence: 'primary', master: 'success', doctorat: 'danger', graduat: 'warning', certificat: 'info' }
function typeLabel(t) { return typeMap[t] || t }
function typeColor(t) { return typeColors[t] || 'info' }

async function load() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: 20 }
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.department) params.department = filters.value.department
    if (filters.value.program_type) params.program_type = filters.value.program_type
    if (filters.value.is_active !== '') params.is_active = filters.value.is_active
    const res = await axios.get('/academic/programs/', { params })
    const d = res.data
    programs.value = d.results || d
    total.value = d.count || programs.value.length
  } finally { loading.value = false }
}

function openModal(item = null) {
  editItem.value = item
  if (item) Object.assign(form, { name: item.name, code: item.code, program_type: item.program_type, duration_years: item.duration_years, department: item.department, faculty: item.faculty, description: item.description || '', is_active: item.is_active })
  else Object.assign(form, { name: '', code: '', program_type: 'licence', duration_years: 3, department: null, faculty: null, description: '', is_active: true })
  showModal.value = true
}

async function save() {
  await formRef.value.validate()
  saving.value = true
  try {
    if (editItem.value) await axios.patch(`/academic/programs/${editItem.value.id}/`, form)
    else await axios.post('/academic/programs/', form)
    ElMessage.success('Enregistré')
    showModal.value = false
    load()
  } finally { saving.value = false }
}

async function handleDelete(row) {
  await ElMessageBox.confirm('Supprimer ce programme ?', 'Confirmation', { type: 'warning' })
  await axios.delete(`/academic/programs/${row.id}/`)
  ElMessage.success('Supprimé')
  load()
}

onMounted(async () => {
  load()
  const [dRes, fRes] = await Promise.all([
    axios.get('/academic/departments/', { params: { page_size: 100 } }),
    axios.get('/academic/faculties/', { params: { page_size: 100 } })
  ])
  departments.value = dRes.data.results || dRes.data
  faculties.value = fRes.data.results || fRes.data
})
</script>

<style scoped>
.programs-page { max-width: 1200px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.page-header h2 { font-size: 22px; font-weight: 700; color: #1e2a3a; }
.subtitle { color: #909399; font-size: 13px; }
.filter-card, .mt-3 { margin-top: 16px; }
.pagination-row { display: flex; justify-content: flex-end; margin-top: 16px; }
</style>
