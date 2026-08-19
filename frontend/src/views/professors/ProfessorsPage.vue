<template>
  <div class="professors-page">
    <div class="page-header">
      <div>
        <h2>Professeurs</h2>
        <p class="subtitle">Gestion du corps enseignant</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="openModal()">Nouveau professeur</el-button>
    </div>

    <el-card shadow="never" class="filter-card">
      <el-row :gutter="16">
        <el-col :xs="24" :sm="8">
          <el-input v-model="filters.search" placeholder="Nom, prénom..." clearable @input="load" />
        </el-col>
        <el-col :xs="24" :sm="6">
          <el-select v-model="filters.department" placeholder="Département" clearable @change="load" style="width:100%">
            <el-option v-for="d in departments" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="6">
          <el-select v-model="filters.grade" placeholder="Grade" clearable @change="load" style="width:100%">
            <el-option value="assistant" label="Assistant" />
            <el-option value="chef_travaux" label="Chef de Travaux" />
            <el-option value="charge_cours" label="Chargé de Cours" />
            <el-option value="maitre_assistant" label="Maître-Assistant" />
            <el-option value="prof_associe" label="Professeur Associé" />
            <el-option value="prof_ordinaire" label="Professeur Ordinaire" />
          </el-select>
        </el-col>
      </el-row>
    </el-card>

    <el-card shadow="never" class="mt-3">
      <el-table :data="professors" v-loading="loading" style="width:100%" stripe>
        <el-table-column label="Professeur" min-width="200">
          <template #default="{ row }">
            <div class="prof-cell">
              <el-avatar :size="36" :icon="UserFilled" />
              <div>
                <div class="prof-name">{{ row.user?.full_name || row.user?.username }}</div>
                <div class="prof-email">{{ row.user?.email }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Grade" min-width="180">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ gradeLabel(row.grade) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Département" min-width="180">
          <template #default="{ row }">{{ row.department_name || '—' }}</template>
        </el-table-column>
        <el-table-column label="Spécialités" min-width="200">
          <template #default="{ row }">
            <el-tag v-for="s in (row.specialities_names || []).slice(0, 2)" :key="s" size="small" class="mr-1">{{ s }}</el-tag>
            <span v-if="(row.specialities_names || []).length > 2" class="text-muted">+{{ row.specialities_names.length - 2 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="H max/sem" width="100" align="center">
          <template #default="{ row }">{{ row.max_weekly_hours }}h</template>
        </el-table-column>
        <el-table-column label="Dispo." width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_available ? 'success' : 'danger'" size="small">
              {{ row.is_available ? 'Oui' : 'Non' }}
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

    <ProfessorModal v-if="showModal" :professor="editProf" :departments="departments" @close="showModal = false" @saved="onSaved" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus, Edit, Delete, UserFilled } from '@element-plus/icons-vue'
import axios from '@/plugins/axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import ProfessorModal from '@/components/modals/ProfessorModal.vue'

const loading = ref(false)
const professors = ref([])
const departments = ref([])
const total = ref(0)
const page = ref(1)
const filters = ref({ search: '', department: '', grade: '' })
const showModal = ref(false)
const editProf = ref(null)

const gradeMap = {
  assistant: 'Assistant', chef_travaux: 'Chef de Travaux', charge_cours: 'Chargé de Cours',
  maitre_assistant: 'Maître-Assistant', prof_associe: 'Professeur Associé', prof_ordinaire: 'Professeur Ordinaire'
}
function gradeLabel(g) { return gradeMap[g] || g }

async function load() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: 20 }
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.department) params.department = filters.value.department
    if (filters.value.grade) params.grade = filters.value.grade
    const res = await axios.get('/auth/professors/', { params })
    const d = res.data
    professors.value = d.results || d
    total.value = d.count || professors.value.length
  } finally {
    loading.value = false
  }
}

function openModal(prof = null) { editProf.value = prof; showModal.value = true }

async function handleDelete(row) {
  await ElMessageBox.confirm('Supprimer ce professeur ?', 'Confirmation', { type: 'warning' })
  await axios.delete(`/auth/professors/${row.id}/`)
  ElMessage.success('Supprimé')
  load()
}

function onSaved() { showModal.value = false; load() }

onMounted(async () => {
  load()
  const res = await axios.get('/academic/departments/', { params: { page_size: 100 } })
  departments.value = res.data.results || res.data
})
</script>

<style scoped>
.professors-page { max-width: 1200px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.page-header h2 { font-size: 22px; font-weight: 700; color: #1e2a3a; }
.subtitle { color: #909399; font-size: 13px; }
.filter-card, .mt-3 { margin-top: 16px; }
.prof-cell { display: flex; align-items: center; gap: 10px; }
.prof-name { font-weight: 600; font-size: 14px; }
.prof-email { font-size: 12px; color: #909399; }
.mr-1 { margin-right: 4px; }
.text-muted { color: #c0c4cc; font-size: 12px; }
.pagination-row { display: flex; justify-content: flex-end; margin-top: 16px; }
</style>
