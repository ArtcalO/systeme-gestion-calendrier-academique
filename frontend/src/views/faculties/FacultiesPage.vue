<template>
  <div class="faculties-page">
    <div class="page-header">
      <div>
        <h2>Facultés</h2>
        <p class="subtitle">Gestion des facultés de l'université</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="openModal()">Nouvelle faculté</el-button>
    </div>

    <el-card shadow="never" class="filter-card">
      <el-row :gutter="16">
        <el-col :xs="24" :sm="10">
          <el-input v-model="filters.search" placeholder="Nom, code..." clearable @input="load" />
        </el-col>
      </el-row>
    </el-card>

    <el-card shadow="never" class="mt-3">
      <el-table :data="faculties" v-loading="loading" style="width:100%" stripe>
        <el-table-column label="Code" width="90">
          <template #default="{ row }">
            <el-tag type="primary" size="small">{{ row.code }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="Nom" min-width="220" />
        <el-table-column label="Doyen" min-width="180">
          <template #default="{ row }">{{ row.dean_name || '—' }}</template>
        </el-table-column>
        <el-table-column label="Départements" width="120" align="center">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.departments_count }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="Description" min-width="200" show-overflow-tooltip />
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
    <el-dialog v-model="showModal" :title="editItem ? 'Modifier faculté' : 'Nouvelle faculté'" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <el-row :gutter="16">
          <el-col :span="16">
            <el-form-item label="Nom" prop="name">
              <el-input v-model="form.name" placeholder="ex: Faculté des Sciences" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Code" prop="code">
              <el-input v-model="form.code" placeholder="ex: FSC" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Description">
          <el-input v-model="form.description" type="textarea" :rows="3" />
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
const faculties = ref([])
const total = ref(0)
const page = ref(1)
const filters = ref({ search: '' })
const showModal = ref(false)
const editItem = ref(null)
const formRef = ref(null)
const form = reactive({ name: '', code: '', description: '' })
const rules = {
  name: [{ required: true, message: 'Nom requis', trigger: 'blur' }],
  code: [{ required: true, message: 'Code requis', trigger: 'blur' }]
}

async function load() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: 20 }
    if (filters.value.search) params.search = filters.value.search
    const res = await axios.get('/academic/faculties/', { params })
    const d = res.data
    faculties.value = d.results || d
    total.value = d.count || faculties.value.length
  } finally { loading.value = false }
}

function openModal(item = null) {
  editItem.value = item
  if (item) { Object.assign(form, { name: item.name, code: item.code, description: item.description || '' }) }
  else { Object.assign(form, { name: '', code: '', description: '' }) }
  showModal.value = true
}

async function save() {
  await formRef.value.validate()
  saving.value = true
  try {
    if (editItem.value) await axios.patch(`/academic/faculties/${editItem.value.id}/`, form)
    else await axios.post('/academic/faculties/', form)
    ElMessage.success('Enregistré')
    showModal.value = false
    load()
  } finally { saving.value = false }
}

async function handleDelete(row) {
  await ElMessageBox.confirm('Supprimer cette faculté ?', 'Confirmation', { type: 'warning' })
  await axios.delete(`/academic/faculties/${row.id}/`)
  ElMessage.success('Supprimé')
  load()
}

onMounted(load)
</script>

<style scoped>
.faculties-page { max-width: 1200px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.page-header h2 { font-size: 22px; font-weight: 700; color: #1e2a3a; }
.subtitle { color: #909399; font-size: 13px; }
.filter-card, .mt-3 { margin-top: 16px; }
.pagination-row { display: flex; justify-content: flex-end; margin-top: 16px; }
</style>
