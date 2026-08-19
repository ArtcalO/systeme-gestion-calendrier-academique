<template>
  <div class="departments-page">
    <div class="page-header">
      <div>
        <h2>Départements</h2>
        <p class="subtitle">Gestion des départements par faculté</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="openModal()">Nouveau département</el-button>
    </div>

    <el-card shadow="never" class="filter-card">
      <el-row :gutter="16">
        <el-col :xs="24" :sm="9">
          <el-input v-model="filters.search" placeholder="Nom, code..." clearable @input="load" />
        </el-col>
        <el-col :xs="24" :sm="7">
          <el-select v-model="filters.faculty" placeholder="Faculté" clearable @change="load" style="width:100%">
            <el-option v-for="f in faculties" :key="f.id" :label="f.name" :value="f.id" />
          </el-select>
        </el-col>
      </el-row>
    </el-card>

    <el-card shadow="never" class="mt-3">
      <el-table :data="departments" v-loading="loading" style="width:100%" stripe>
        <el-table-column label="Code" width="90">
          <template #default="{ row }">
            <el-tag type="warning" size="small">{{ row.code }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="Nom" min-width="200" />
        <el-table-column label="Faculté" min-width="180">
          <template #default="{ row }">{{ row.faculty_name || '—' }}</template>
        </el-table-column>
        <el-table-column label="Chef" min-width="160">
          <template #default="{ row }">{{ row.head_name || '—' }}</template>
        </el-table-column>
        <el-table-column label="Programmes" width="110" align="center">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.programs_count }}</el-tag>
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

    <el-dialog v-model="showModal" :title="editItem ? 'Modifier département' : 'Nouveau département'" width="480px">
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <el-row :gutter="16">
          <el-col :span="16">
            <el-form-item label="Nom" prop="name">
              <el-input v-model="form.name" placeholder="ex: Informatique" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Code" prop="code">
              <el-input v-model="form.code" placeholder="ex: INFO" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Faculté" prop="faculty">
          <el-select v-model="form.faculty" style="width:100%" placeholder="Sélectionner">
            <el-option v-for="f in faculties" :key="f.id" :label="f.name" :value="f.id" />
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
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import axios from '@/plugins/axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const saving = ref(false)
const departments = ref([])
const faculties = ref([])
const total = ref(0)
const page = ref(1)
const filters = ref({ search: '', faculty: '' })
const showModal = ref(false)
const editItem = ref(null)
const formRef = ref(null)
const form = reactive({ name: '', code: '', faculty: '' })
const rules = {
  name: [{ required: true, message: 'Nom requis', trigger: 'blur' }],
  code: [{ required: true, message: 'Code requis', trigger: 'blur' }],
  faculty: [{ required: true, message: 'Faculté requise', trigger: 'change' }]
}

async function load() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: 20 }
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.faculty) params.faculty = filters.value.faculty
    const res = await axios.get('/academic/departments/', { params })
    const d = res.data
    departments.value = d.results || d
    total.value = d.count || departments.value.length
  } finally { loading.value = false }
}

function openModal(item = null) {
  editItem.value = item
  if (item) Object.assign(form, { name: item.name, code: item.code, faculty: item.faculty })
  else Object.assign(form, { name: '', code: '', faculty: '' })
  showModal.value = true
}

async function save() {
  await formRef.value.validate()
  saving.value = true
  try {
    if (editItem.value) await axios.patch(`/academic/departments/${editItem.value.id}/`, form)
    else await axios.post('/academic/departments/', form)
    ElMessage.success('Enregistré')
    showModal.value = false
    load()
  } finally { saving.value = false }
}

async function handleDelete(row) {
  await ElMessageBox.confirm('Supprimer ce département ?', 'Confirmation', { type: 'warning' })
  await axios.delete(`/academic/departments/${row.id}/`)
  ElMessage.success('Supprimé')
  load()
}

onMounted(async () => {
  load()
  const res = await axios.get('/academic/faculties/', { params: { page_size: 100 } })
  faculties.value = res.data.results || res.data
})
</script>

<style scoped>
.departments-page { max-width: 1200px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.page-header h2 { font-size: 22px; font-weight: 700; color: #1e2a3a; }
.subtitle { color: #909399; font-size: 13px; }
.filter-card, .mt-3 { margin-top: 16px; }
.pagination-row { display: flex; justify-content: flex-end; margin-top: 16px; }
</style>
