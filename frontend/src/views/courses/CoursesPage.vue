<template>
  <div class="courses-page">
    <div class="page-header">
      <div>
        <h2>Planification des cours</h2>
        <p class="subtitle">Gérez les cours planifiés par année académique</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="openModal()">Nouveau cours</el-button>
    </div>

    <!-- Filters -->
    <el-card shadow="never" class="filter-card">
      <el-row :gutter="16">
        <el-col :xs="24" :sm="8" :md="6">
          <el-select v-model="filters.academic_year" placeholder="Année académique" clearable @change="load" style="width:100%">
            <el-option v-for="y in academicYears" :key="y.id" :label="y.name" :value="y.id" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="8" :md="6">
          <el-select v-model="filters.semester" placeholder="Semestre" clearable @change="load" style="width:100%">
            <el-option :value="1" label="Semestre 1" />
            <el-option :value="2" label="Semestre 2" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="8" :md="6">
          <el-select v-model="filters.status" placeholder="Statut" clearable @change="load" style="width:100%">
            <el-option value="draft" label="Brouillon" />
            <el-option value="scheduled" label="Planifié" />
            <el-option value="ongoing" label="En cours" />
            <el-option value="completed" label="Terminé" />
            <el-option value="cancelled" label="Annulé" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="8" :md="6">
          <el-input v-model="filters.search" placeholder="Rechercher..." :prefix-icon="Search" clearable @input="load" />
        </el-col>
      </el-row>
    </el-card>

    <!-- Table -->
    <el-card shadow="never" class="mt-3">
      <el-table :data="courses" v-loading="loading" style="width:100%" stripe>
        <el-table-column prop="module_code" label="Code" width="100" />
        <el-table-column prop="module_name" label="Module" min-width="180" show-overflow-tooltip />
        <el-table-column prop="academic_year_name" label="Année" width="110" />
        <el-table-column prop="semester" label="Sem." width="70" align="center" />
        <el-table-column prop="weekly_hours" label="H/sem" width="80" align="center" />
        <el-table-column label="Professeur" min-width="160">
          <template #default="{ row }">
            <span v-if="row.assigned_professor">{{ row.assigned_professor.name }}</span>
            <el-tag v-else type="warning" size="small">Non assigné</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Prérequis" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.has_prerequisites" type="warning" size="small" :icon="Lock">Oui</el-tag>
            <el-tag v-else type="info" size="small">Non</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Statut" width="120">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status).type" size="small">{{ statusTag(row.status).label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="120" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-button text type="primary" :icon="Edit" size="small" @click="openModal(row)" />
              <el-button text type="danger" :icon="Delete" size="small" @click="handleDelete(row)" />
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-row">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @change="load"
        />
      </div>
    </el-card>

    <!-- Modal -->
    <CourseModal
      v-if="showModal"
      :course="editCourse"
      :academic-years="academicYears"
      @close="showModal = false"
      @saved="onSaved"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus, Edit, Delete, Search, Lock } from '@element-plus/icons-vue'
import { useStatusHelpers } from '@/reusables/mixins'
import { useApi } from '@/reusables/mixins'
import axios from '@/plugins/axios'
import CourseModal from '@/components/modals/CourseModal.vue'

const { courseStatusTag: statusTag } = useStatusHelpers()
const { remove } = useApi()

const loading = ref(false)
const courses = ref([])
const academicYears = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const showModal = ref(false)
const editCourse = ref(null)
const filters = ref({ academic_year: '', semester: '', status: '', search: '' })

async function load() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filters.value.academic_year) params.academic_year = filters.value.academic_year
    if (filters.value.semester) params.semester = filters.value.semester
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.search) params.search = filters.value.search

    const res = await axios.get('/academic/courses/', { params })
    const d = res.data
    courses.value = (d.results || d).map(c => ({
      ...c,
      has_prerequisites: false // will be enriched if needed
    }))
    total.value = d.count || courses.value.length
  } finally {
    loading.value = false
  }
}

async function loadAcademicYears() {
  const res = await axios.get('/academic/academic-years/')
  academicYears.value = res.data.results || res.data
}

function openModal(course = null) {
  editCourse.value = course
  showModal.value = true
}

async function handleDelete(row) {
  const ok = await remove('/academic/courses/', row.id, 'Cours').catch(() => false)
  if (ok) load()
}

function onSaved() {
  showModal.value = false
  load()
}

onMounted(() => { load(); loadAcademicYears() })
</script>

<style scoped>
.courses-page { max-width: 1400px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.page-header h2 { font-size: 22px; font-weight: 700; color: #1e2a3a; }
.subtitle { color: #909399; font-size: 13px; margin-top: 2px; }
.filter-card, .mt-3 { margin-top: 16px; }
.pagination-row { display: flex; justify-content: flex-end; margin-top: 16px; }
</style>
