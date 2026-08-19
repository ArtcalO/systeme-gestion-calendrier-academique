<template>
  <div class="modules-page">
    <div class="page-header">
      <div>
        <h2>Modules / Cours</h2>
        <p class="subtitle">Catalogue des modules par programme et niveau</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="openModal()">Nouveau module</el-button>
    </div>

    <el-card shadow="never" class="filter-card">
      <el-row :gutter="16">
        <el-col :xs="24" :sm="6">
          <el-select v-model="filters.program" placeholder="Programme" clearable @change="onProgramChange" style="width:100%">
            <el-option v-for="p in programs" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="6">
          <el-select v-model="filters.level" placeholder="Niveau" clearable @change="load" style="width:100%">
            <el-option v-for="l in levels" :key="l.id" :label="l.name" :value="l.id" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="6">
          <el-select v-model="filters.semester" placeholder="Semestre" clearable @change="load" style="width:100%">
            <el-option :value="1" label="Semestre 1" />
            <el-option :value="2" label="Semestre 2" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="6">
          <el-input v-model="filters.search" placeholder="Rechercher..." clearable @input="load" />
        </el-col>
      </el-row>
    </el-card>

    <el-card shadow="never" class="mt-3">
      <el-table :data="modules" v-loading="loading" style="width:100%" stripe>
        <el-table-column prop="code" label="Code" width="100" />
        <el-table-column prop="name" label="Nom du module" min-width="200" show-overflow-tooltip />
        <el-table-column prop="level_name" label="Niveau" width="100" />
        <el-table-column prop="semester" label="Sem." width="70" align="center" />
        <el-table-column prop="credits" label="Crédits" width="80" align="center" />
        <el-table-column prop="weekly_hours" label="H/sem" width="80" align="center" />
        <el-table-column label="Type" width="120">
          <template #default="{ row }">
            <el-tag size="small" type="info">{{ moduleTypeLabel(row.module_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Prérequis" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.has_prerequisites" type="warning" size="small">
              {{ row.prerequisites_list?.length || '?' }}
            </el-tag>
            <span v-else class="text-muted">—</span>
          </template>
        </el-table-column>
        <el-table-column label="Oblig." width="80" align="center">
          <template #default="{ row }">
            <el-icon v-if="row.is_mandatory" color="#67C23A"><CircleCheck /></el-icon>
            <el-icon v-else color="#C0C4CC"><Remove /></el-icon>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="120" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-button text type="primary" :icon="Edit" size="small" @click="openModal(row)" />
              <el-button text type="warning" :icon="Share" size="small" @click="viewPrereqs(row)" title="Voir prérequis" />
              <el-button text type="danger" :icon="Delete" size="small" @click="handleDelete(row)" />
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-row">
        <el-pagination v-model:current-page="page" :total="total" layout="total, prev, pager, next" @change="load" />
      </div>
    </el-card>

    <!-- Prereq drawer -->
    <el-drawer v-model="showPrereqDrawer" :title="`Prérequis de : ${selectedModule?.name}`" size="500px">
      <div v-if="prereqDetail" class="prereq-drawer">
        <el-descriptions :column="1" border size="small" class="mb-3">
          <el-descriptions-item label="Module">{{ prereqDetail.module_code }} — {{ prereqDetail.module_name }}</el-descriptions-item>
          <el-descriptions-item label="Niveau">{{ prereqDetail.level }} · Semestre {{ prereqDetail.semester }}</el-descriptions-item>
        </el-descriptions>

        <div v-if="prereqDetail.dependencies.strict.length">
          <el-divider content-position="left">
            <el-tag type="danger">Stricts — à compléter AVANT</el-tag>
          </el-divider>
          <el-card v-for="p in prereqDetail.dependencies.strict" :key="p.id" shadow="never" class="prereq-item">
            <strong>{{ p.code }}</strong> — {{ p.name }}
            <br><small>{{ p.level }} S{{ p.semester }} · Note min: {{ p.minimum_grade }}/20</small>
          </el-card>
        </div>

        <div v-if="prereqDetail.dependencies.corequisites.length">
          <el-divider content-position="left">
            <el-tag type="warning">Coréquisits — suivre EN PARALLÈLE</el-tag>
          </el-divider>
          <el-card v-for="p in prereqDetail.dependencies.corequisites" :key="p.id" shadow="never" class="prereq-item">
            <strong>{{ p.code }}</strong> — {{ p.name }}
            <br><small>{{ p.level }} S{{ p.semester }}</small>
          </el-card>
        </div>

        <div v-if="prereqDetail.dependencies.recommended.length">
          <el-divider content-position="left">
            <el-tag type="info">Recommandés</el-tag>
          </el-divider>
          <el-card v-for="p in prereqDetail.dependencies.recommended" :key="p.id" shadow="never" class="prereq-item">
            <strong>{{ p.code }}</strong> — {{ p.name }}
          </el-card>
        </div>

        <el-empty v-if="!prereqDetail.dependencies.strict.length && !prereqDetail.dependencies.corequisites.length && !prereqDetail.dependencies.recommended.length"
          description="Aucun prérequis défini pour ce module" />
      </div>
    </el-drawer>

    <!-- Module Modal -->
    <ModuleModal
      v-if="showModal"
      :module="editModule"
      :programs="programs"
      @close="showModal = false"
      @saved="onSaved"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus, Edit, Delete, Share, CircleCheck, Remove } from '@element-plus/icons-vue'
import axios from '@/plugins/axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import ModuleModal from '@/components/modals/ModuleModal.vue'

const loading = ref(false)
const modules = ref([])
const programs = ref([])
const levels = ref([])
const total = ref(0)
const page = ref(1)
const filters = ref({ program: '', level: '', semester: '', search: '' })
const showModal = ref(false)
const editModule = ref(null)
const showPrereqDrawer = ref(false)
const selectedModule = ref(null)
const prereqDetail = ref(null)

const moduleTypeMap = {
  cours: 'Cours Magistral', tp: 'TP', td: 'TD',
  seminaire: 'Séminaire', stage: 'Stage', projet: 'Projet'
}
function moduleTypeLabel(t) { return moduleTypeMap[t] || t }

async function load() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: 25 }
    if (filters.value.level) params.level = filters.value.level
    if (filters.value.semester) params.semester = filters.value.semester
    if (filters.value.search) params.search = filters.value.search
    const res = await axios.get('/academic/modules/', { params })
    const d = res.data
    modules.value = d.results || d
    total.value = d.count || modules.value.length
  } finally {
    loading.value = false
  }
}

async function onProgramChange() {
  levels.value = []
  filters.value.level = ''
  if (filters.value.program) {
    const res = await axios.get('/academic/levels/', { params: { program: filters.value.program } })
    levels.value = res.data.results || res.data
  }
  load()
}

async function viewPrereqs(module) {
  selectedModule.value = module
  showPrereqDrawer.value = true
  const res = await axios.get('/prerequisites/module-prerequisites/by_module/', { params: { module_id: module.id } })
  prereqDetail.value = res.data
}

function openModal(mod = null) { editModule.value = mod; showModal.value = true }

async function handleDelete(row) {
  await ElMessageBox.confirm('Supprimer ce module ?', 'Confirmation', { type: 'warning' })
  await axios.delete(`/academic/modules/${row.id}/`)
  ElMessage.success('Module supprimé')
  load()
}

function onSaved() { showModal.value = false; load() }

onMounted(async () => {
  load()
  const res = await axios.get('/academic/programs/', { params: { page_size: 100 } })
  programs.value = res.data.results || res.data
})
</script>

<style scoped>
.modules-page { max-width: 1400px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.page-header h2 { font-size: 22px; font-weight: 700; color: #1e2a3a; }
.subtitle { color: #909399; font-size: 13px; }
.filter-card, .mt-3 { margin-top: 16px; }
.mb-3 { margin-bottom: 16px; }
.pagination-row { display: flex; justify-content: flex-end; margin-top: 16px; }
.text-muted { color: #c0c4cc; }
.prereq-drawer { padding: 4px; }
.prereq-item { margin-bottom: 8px; font-size: 13px; }
.prereq-item small { color: #909399; }
</style>
