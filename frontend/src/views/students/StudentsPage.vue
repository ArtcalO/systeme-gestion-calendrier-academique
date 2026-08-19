<template>
  <div class="students-page">
    <div class="page-header">
      <div>
        <h2>Étudiants</h2>
        <p class="subtitle">Gestion du corps étudiant</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="openModal()">Nouvel étudiant</el-button>
    </div>

    <el-card shadow="never" class="filter-card">
      <el-row :gutter="16">
        <el-col :xs="24" :sm="8">
          <el-input v-model="filters.search" placeholder="Nom, matricule..." clearable @input="load" />
        </el-col>
        <el-col :xs="24" :sm="6">
          <el-select v-model="filters.program" placeholder="Programme" clearable @change="load" style="width:100%">
            <el-option v-for="p in programs" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="5">
          <el-select v-model="filters.status" placeholder="Statut" clearable @change="load" style="width:100%">
            <el-option value="active" label="Actif" />
            <el-option value="suspended" label="Suspendu" />
            <el-option value="graduated" label="Diplômé" />
            <el-option value="dropout" label="Abandon" />
          </el-select>
        </el-col>
      </el-row>
    </el-card>

    <el-card shadow="never" class="mt-3">
      <el-table :data="students" v-loading="loading" style="width:100%" stripe>
        <el-table-column label="Matricule" width="120">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.registration_number }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Étudiant" min-width="200">
          <template #default="{ row }">
            <div class="student-cell">
              <el-avatar :size="32" :icon="UserFilled" />
              <div>
                <div class="student-name">{{ row.user?.full_name || row.user?.username }}</div>
                <div class="student-email">{{ row.user?.email }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Programme" min-width="180">
          <template #default="{ row }">{{ row.program_name || '—' }}</template>
        </el-table-column>
        <el-table-column label="Niveau" width="90" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.level_name" size="small">{{ row.level_name }}</el-tag>
            <span v-else>—</span>
          </template>
        </el-table-column>
        <el-table-column label="Promo" width="80" align="center">
          <template #default="{ row }">{{ row.enrollment_year }}</template>
        </el-table-column>
        <el-table-column label="Statut" width="100">
          <template #default="{ row }">
            <el-tag :type="studentStatusType(row.status)" size="small">{{ studentStatusLabel(row.status) }}</el-tag>
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
    <el-dialog v-model="showModal" :title="editItem ? 'Modifier étudiant' : 'Nouvel étudiant'" width="560px">
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Prénom" prop="first_name">
              <el-input v-model="form.first_name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Nom" prop="last_name">
              <el-input v-model="form.last_name" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="14">
            <el-form-item label="Email" prop="email">
              <el-input v-model="form.email" type="email" />
            </el-form-item>
          </el-col>
          <el-col :span="10">
            <el-form-item label="Matricule" prop="registration_number">
              <el-input v-model="form.registration_number" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="14">
            <el-form-item label="Programme">
              <el-select v-model="form.program" style="width:100%" clearable>
                <el-option v-for="p in programs" :key="p.id" :label="p.name" :value="p.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="10">
            <el-form-item label="Année d'inscription">
              <el-input-number v-model="form.enrollment_year" :min="2000" :max="2100" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Statut">
          <el-select v-model="form.status" style="width:100%">
            <el-option value="active" label="Actif" />
            <el-option value="suspended" label="Suspendu" />
            <el-option value="graduated" label="Diplômé" />
            <el-option value="dropout" label="Abandon" />
          </el-select>
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
import { Plus, Edit, Delete, UserFilled } from '@element-plus/icons-vue'
import axios from '@/plugins/axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const saving = ref(false)
const students = ref([])
const programs = ref([])
const total = ref(0)
const page = ref(1)
const filters = ref({ search: '', program: '', status: '' })
const showModal = ref(false)
const editItem = ref(null)
const formRef = ref(null)
const form = reactive({ first_name: '', last_name: '', email: '', registration_number: '', program: null, enrollment_year: new Date().getFullYear(), status: 'active' })
const rules = {
  first_name: [{ required: true, message: 'Prénom requis', trigger: 'blur' }],
  last_name: [{ required: true, message: 'Nom requis', trigger: 'blur' }],
  email: [{ required: true, type: 'email', message: 'Email valide requis', trigger: 'blur' }],
  registration_number: [{ required: true, message: 'Matricule requis', trigger: 'blur' }]
}

const statusMap = { active: 'Actif', suspended: 'Suspendu', graduated: 'Diplômé', dropout: 'Abandon' }
const statusTypes = { active: 'success', suspended: 'warning', graduated: 'info', dropout: 'danger' }
function studentStatusLabel(s) { return statusMap[s] || s }
function studentStatusType(s) { return statusTypes[s] || 'info' }

async function load() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: 20 }
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.program) params.program = filters.value.program
    if (filters.value.status) params.status = filters.value.status
    const res = await axios.get('/auth/students/', { params })
    const d = res.data
    students.value = d.results || d
    total.value = d.count || students.value.length
  } finally { loading.value = false }
}

function openModal(item = null) {
  editItem.value = item
  if (item) {
    Object.assign(form, {
      first_name: item.user?.first_name || '', last_name: item.user?.last_name || '',
      email: item.user?.email || '', registration_number: item.registration_number,
      program: item.program, enrollment_year: item.enrollment_year, status: item.status
    })
  } else {
    Object.assign(form, { first_name: '', last_name: '', email: '', registration_number: '', program: null, enrollment_year: new Date().getFullYear(), status: 'active' })
  }
  showModal.value = true
}

async function save() {
  await formRef.value.validate()
  saving.value = true
  try {
    if (editItem.value) await axios.patch(`/auth/students/${editItem.value.id}/`, form)
    else await axios.post('/auth/students/', form)
    ElMessage.success('Enregistré')
    showModal.value = false
    load()
  } finally { saving.value = false }
}

async function handleDelete(row) {
  await ElMessageBox.confirm('Supprimer cet étudiant ?', 'Confirmation', { type: 'warning' })
  await axios.delete(`/auth/students/${row.id}/`)
  ElMessage.success('Supprimé')
  load()
}

onMounted(async () => {
  load()
  const res = await axios.get('/academic/programs/', { params: { page_size: 100 } })
  programs.value = res.data.results || res.data
})
</script>

<style scoped>
.students-page { max-width: 1200px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.page-header h2 { font-size: 22px; font-weight: 700; color: #1e2a3a; }
.subtitle { color: #909399; font-size: 13px; }
.filter-card, .mt-3 { margin-top: 16px; }
.student-cell { display: flex; align-items: center; gap: 10px; }
.student-name { font-weight: 600; font-size: 13px; }
.student-email { font-size: 12px; color: #909399; }
.pagination-row { display: flex; justify-content: flex-end; margin-top: 16px; }
</style>
