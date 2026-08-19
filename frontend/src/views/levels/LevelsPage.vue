<template>
  <div class="levels-page">
    <div class="page-header">
      <div>
        <h2>Niveaux</h2>
        <p class="subtitle">Gestion des niveaux d'étude par programme</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="openModal()">Nouveau niveau</el-button>
    </div>

    <el-card shadow="never" class="filter-card">
      <el-row :gutter="16">
        <el-col :xs="24" :sm="10">
          <el-select v-model="filters.program" placeholder="Filtrer par programme" clearable @change="load" style="width:100%">
            <el-option v-for="p in programs" :key="p.id" :label="`${p.code} — ${p.name}`" :value="p.id" />
          </el-select>
        </el-col>
      </el-row>
    </el-card>

    <el-card shadow="never" class="mt-3">
      <el-table :data="levels" v-loading="loading" style="width:100%" stripe>
        <el-table-column label="Niveau" width="100">
          <template #default="{ row }">
            <el-tag type="primary" size="default">{{ row.name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Année" width="80" align="center">
          <template #default="{ row }">
            <span class="year-badge">{{ row.year_number }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Programme" min-width="220">
          <template #default="{ row }">{{ row.program_name || '—' }}</template>
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

    <el-dialog v-model="showModal" :title="editItem ? 'Modifier niveau' : 'Nouveau niveau'" width="480px">
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <el-form-item label="Programme" prop="program">
          <el-select v-model="form.program" style="width:100%" placeholder="Sélectionner">
            <el-option v-for="p in programs" :key="p.id" :label="`${p.code} — ${p.name}`" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="14">
            <el-form-item label="Nom du niveau" prop="name">
              <el-input v-model="form.name" placeholder="ex: L1, L2, M1..." />
            </el-form-item>
          </el-col>
          <el-col :span="10">
            <el-form-item label="Numéro d'année" prop="year_number">
              <el-input-number v-model="form.year_number" :min="1" :max="10" style="width:100%" />
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
const levels = ref([])
const programs = ref([])
const total = ref(0)
const page = ref(1)
const filters = ref({ program: '' })
const showModal = ref(false)
const editItem = ref(null)
const formRef = ref(null)
const form = reactive({ name: '', year_number: 1, program: '', description: '' })
const rules = {
  name: [{ required: true, message: 'Nom requis', trigger: 'blur' }],
  year_number: [{ required: true, message: 'Numéro requis', trigger: 'blur' }],
  program: [{ required: true, message: 'Programme requis', trigger: 'change' }]
}

async function load() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: 20 }
    if (filters.value.program) params.program = filters.value.program
    const res = await axios.get('/academic/levels/', { params })
    const d = res.data
    levels.value = d.results || d
    total.value = d.count || levels.value.length
  } finally { loading.value = false }
}

function openModal(item = null) {
  editItem.value = item
  if (item) Object.assign(form, { name: item.name, year_number: item.year_number, program: item.program, description: item.description || '' })
  else Object.assign(form, { name: '', year_number: 1, program: '', description: '' })
  showModal.value = true
}

async function save() {
  await formRef.value.validate()
  saving.value = true
  try {
    if (editItem.value) await axios.patch(`/academic/levels/${editItem.value.id}/`, form)
    else await axios.post('/academic/levels/', form)
    ElMessage.success('Enregistré')
    showModal.value = false
    load()
  } finally { saving.value = false }
}

async function handleDelete(row) {
  await ElMessageBox.confirm('Supprimer ce niveau ?', 'Confirmation', { type: 'warning' })
  await axios.delete(`/academic/levels/${row.id}/`)
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
.levels-page { max-width: 1200px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.page-header h2 { font-size: 22px; font-weight: 700; color: #1e2a3a; }
.subtitle { color: #909399; font-size: 13px; }
.filter-card, .mt-3 { margin-top: 16px; }
.pagination-row { display: flex; justify-content: flex-end; margin-top: 16px; }
.year-badge { font-weight: 700; color: #409EFF; font-size: 16px; }
</style>
