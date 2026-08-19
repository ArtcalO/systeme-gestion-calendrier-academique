<template>
  <div class="prereq-page">
    <div class="page-header">
      <div>
        <h2>Gestion des prérequis</h2>
        <p class="subtitle">Définissez les dépendances entre modules pour la planification</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="showModal = true">Ajouter un prérequis</el-button>
    </div>

    <!-- Tabs: List / Graph / Validation -->
    <el-tabs v-model="activeTab" class="mt-3">
      <el-tab-pane label="Liste des prérequis" name="list">
        <el-card shadow="never">
          <!-- Filters -->
          <el-row :gutter="16" class="mb-3">
            <el-col :xs="24" :sm="8">
              <el-select v-model="filters.program" placeholder="Filtrer par programme" clearable @change="loadPrereqs" style="width:100%">
                <el-option v-for="p in programs" :key="p.id" :label="p.name" :value="p.id" />
              </el-select>
            </el-col>
            <el-col :xs="24" :sm="8">
              <el-select v-model="filters.type" placeholder="Type de prérequis" clearable @change="loadPrereqs" style="width:100%">
                <el-option value="strict" label="Strict (avant)" />
                <el-option value="coreq" label="Coréquisit (parallèle)" />
                <el-option value="recommended" label="Recommandé" />
              </el-select>
            </el-col>
          </el-row>

          <el-table :data="prerequisites" v-loading="loading" style="width:100%" stripe>
            <el-table-column label="Module prérequis" min-width="200">
              <template #default="{ row }">
                <div class="module-cell">
                  <span class="code">{{ row.prerequisite_code }}</span>
                  <span class="name">{{ row.prerequisite_name }}</span>
                  <el-tag size="small" type="info">{{ row.prerequisite_level }} S{{ row.prerequisite_semester }}</el-tag>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="" width="60" align="center">
              <template #default="{ row }">
                <el-icon :color="prereqTag(row.prerequisite_type).type === 'danger' ? '#F56C6C' : '#E6A23C'">
                  <Right />
                </el-icon>
              </template>
            </el-table-column>
            <el-table-column label="Module cible" min-width="200">
              <template #default="{ row }">
                <div class="module-cell">
                  <span class="code">{{ row.module_code }}</span>
                  <span class="name">{{ row.module_name }}</span>
                  <el-tag size="small" type="info">{{ row.module_level }} S{{ row.module_semester }}</el-tag>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="Type" width="180">
              <template #default="{ row }">
                <el-tag :type="prereqTag(row.prerequisite_type).type" size="small">
                  {{ prereqTag(row.prerequisite_type).label }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="minimum_grade" label="Note min." width="100" align="center">
              <template #default="{ row }">
                <span v-if="row.prerequisite_type === 'strict'">{{ row.minimum_grade }}/20</span>
                <span v-else>—</span>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="Description" min-width="160" show-overflow-tooltip />
            <el-table-column label="Actions" width="100" fixed="right">
              <template #default="{ row }">
                <el-button-group>
                  <el-button text type="primary" :icon="Edit" size="small" @click="openEdit(row)" />
                  <el-button text type="danger" :icon="Delete" size="small" @click="handleDelete(row)" />
                </el-button-group>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination-row">
            <el-pagination v-model:current-page="page" :total="total" layout="total, prev, pager, next" @change="loadPrereqs" />
          </div>
        </el-card>
      </el-tab-pane>

      <!-- Graph View -->
      <el-tab-pane label="Graphe de dépendances" name="graph">
        <el-card shadow="never">
          <div class="graph-controls">
            <el-select v-model="graphProgram" placeholder="Sélectionner un programme" @change="loadGraph" style="width:280px">
              <el-option v-for="p in programs" :key="p.id" :label="p.name" :value="p.id" />
            </el-select>
            <el-tag v-if="graphData" :type="graphData.is_valid ? 'success' : 'danger'">
              {{ graphData.is_valid ? 'Graphe valide' : `${graphData.validation_errors?.length} erreur(s)` }}
            </el-tag>
          </div>

          <div v-if="graphData" class="graph-container">
            <!-- Legend -->
            <div class="graph-legend">
              <span><span class="dot strict"></span>Strict (avant)</span>
              <span><span class="dot coreq"></span>Coréquisit (parallèle)</span>
              <span><span class="dot recommended"></span>Recommandé</span>
            </div>

            <!-- Semester grid -->
            <div class="semester-grid">
              <div v-for="group in semesterGroups" :key="group.key" class="semester-col">
                <div class="sem-header">{{ group.label }}</div>
                <div v-for="node in group.nodes" :key="node.id" class="node-card">
                  <div class="node-code">{{ node.code }}</div>
                  <div class="node-name">{{ node.name }}</div>
                </div>
              </div>
            </div>

            <!-- Edges summary -->
            <el-collapse class="mt-3">
              <el-collapse-item :title="`${graphData.graph.edges.length} relation(s) de dépendance`" name="edges">
                <el-table :data="graphData.graph.edges" size="small">
                  <el-table-column label="De (prérequis)" min-width="180">
                    <template #default="{ row }">{{ nodeLabel(row.source) }}</template>
                  </el-table-column>
                  <el-table-column label="" width="40" align="center"><template #default><el-icon><Right /></el-icon></template></el-table-column>
                  <el-table-column label="Vers (module)" min-width="180">
                    <template #default="{ row }">{{ nodeLabel(row.target) }}</template>
                  </el-table-column>
                  <el-table-column label="Type" width="140">
                    <template #default="{ row }">
                      <el-tag :type="prereqTag(row.type).type" size="small">{{ prereqTag(row.type).label }}</el-tag>
                    </template>
                  </el-table-column>
                </el-table>
              </el-collapse-item>
            </el-collapse>

            <!-- Errors -->
            <el-alert v-for="(err, i) in graphData.validation_errors" :key="i"
              :title="err.message" type="error" show-icon class="mt-2" :closable="false" />
          </div>
          <el-empty v-else description="Sélectionner un programme" />
        </el-card>
      </el-tab-pane>

      <!-- Planning Order -->
      <el-tab-pane label="Ordre de planification" name="order">
        <el-card shadow="never">
          <div class="graph-controls">
            <el-select v-model="orderProgram" placeholder="Sélectionner un programme" @change="loadOrder" style="width:280px">
              <el-option v-for="p in programs" :key="p.id" :label="p.name" :value="p.id" />
            </el-select>
          </div>
          <div v-if="planningOrder.length">
            <p class="order-hint">
              Ordre recommandé de planification des cours selon les dépendances prérequis :
            </p>
            <el-timeline>
              <el-timeline-item
                v-for="item in planningOrder"
                :key="item.module_id"
                :color="item.year_number === 1 ? '#409EFF' : item.year_number === 2 ? '#67C23A' : '#E6A23C'"
              >
                <div class="order-item">
                  <el-tag size="small" type="info">{{ item.level }} S{{ item.semester }}</el-tag>
                  <strong>{{ item.module_code }}</strong> — {{ item.module_name }}
                </div>
              </el-timeline-item>
            </el-timeline>
          </div>
          <el-empty v-else description="Sélectionner un programme" />
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- Modal -->
    <PrerequisiteModal
      v-if="showModal"
      :prereq="editPrereq"
      @close="showModal = false; editPrereq = null"
      @saved="onSaved"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Plus, Edit, Delete, Right } from '@element-plus/icons-vue'
import { useStatusHelpers } from '@/reusables/mixins'
import axios from '@/plugins/axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import PrerequisiteModal from '@/components/modals/PrerequisiteModal.vue'

const { prereqTypeTag: prereqTag } = useStatusHelpers()

const activeTab = ref('list')
const loading = ref(false)
const prerequisites = ref([])
const programs = ref([])
const total = ref(0)
const page = ref(1)
const showModal = ref(false)
const editPrereq = ref(null)
const filters = ref({ program: '', type: '' })

// Graph
const graphProgram = ref(null)
const graphData = ref(null)
const orderProgram = ref(null)
const planningOrder = ref([])

const semesterGroups = computed(() => {
  if (!graphData.value) return []
  const nodes = graphData.value.graph.nodes
  const groups = {}
  for (const n of nodes) {
    const key = n.group
    if (!groups[key]) groups[key] = { key, label: `${n.level} - Sem. ${n.semester}`, nodes: [], yearNum: n.year_number, semNum: n.semester }
    groups[key].nodes.push(n)
  }
  return Object.values(groups).sort((a, b) => a.yearNum - b.yearNum || a.semNum - b.semNum)
})

function nodeLabel(id) {
  if (!graphData.value) return id
  const n = graphData.value.graph.nodes.find(n => n.id === id)
  return n ? `${n.code} - ${n.name}` : id
}

async function loadPrereqs() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: 20 }
    if (filters.value.program) params['module__level__program'] = filters.value.program
    if (filters.value.type) params.prerequisite_type = filters.value.type
    const res = await axios.get('/prerequisites/module-prerequisites/', { params })
    const d = res.data
    prerequisites.value = d.results || d
    total.value = d.count || prerequisites.value.length
  } finally {
    loading.value = false
  }
}

async function loadPrograms() {
  const res = await axios.get('/academic/programs/', { params: { page_size: 100 } })
  programs.value = res.data.results || res.data
}

async function loadGraph() {
  if (!graphProgram.value) return
  const res = await axios.get('/prerequisites/module-prerequisites/graph/', { params: { program_id: graphProgram.value } })
  graphData.value = res.data
}

async function loadOrder() {
  if (!orderProgram.value) return
  const res = await axios.get('/prerequisites/module-prerequisites/planning_order/', { params: { program_id: orderProgram.value } })
  planningOrder.value = res.data.planning_order || []
}

function openEdit(row) {
  editPrereq.value = row
  showModal.value = true
}

async function handleDelete(row) {
  await ElMessageBox.confirm('Supprimer ce prérequis ?', 'Confirmation', { type: 'warning' })
  await axios.delete(`/prerequisites/module-prerequisites/${row.id}/`)
  ElMessage.success('Supprimé')
  loadPrereqs()
}

function onSaved() {
  showModal.value = false
  editPrereq.value = null
  loadPrereqs()
}

onMounted(() => { loadPrereqs(); loadPrograms() })
</script>

<style scoped>
.prereq-page { max-width: 1400px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.page-header h2 { font-size: 22px; font-weight: 700; color: #1e2a3a; }
.subtitle { color: #909399; font-size: 13px; }
.mt-3 { margin-top: 16px; }
.mt-2 { margin-top: 8px; }
.mb-3 { margin-bottom: 16px; }
.module-cell { display: flex; flex-direction: column; gap: 2px; }
.module-cell .code { font-weight: 600; font-size: 13px; }
.module-cell .name { color: #606266; font-size: 12px; }
.pagination-row { display: flex; justify-content: flex-end; margin-top: 16px; }
.graph-controls { display: flex; align-items: center; gap: 16px; margin-bottom: 20px; }
.graph-legend { display: flex; gap: 20px; font-size: 13px; color: #606266; margin-bottom: 16px; }
.dot { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 4px; }
.dot.strict { background: #F56C6C; }
.dot.coreq { background: #E6A23C; }
.dot.recommended { background: #909399; }
.semester-grid { display: flex; gap: 16px; overflow-x: auto; padding-bottom: 12px; }
.semester-col { min-width: 160px; }
.sem-header { background: #409EFF; color: #fff; padding: 6px 12px; border-radius: 6px 6px 0 0; font-size: 13px; font-weight: 600; text-align: center; }
.node-card { border: 1px solid #ddd; padding: 8px 10px; margin-top: 6px; border-radius: 6px; background: #fff; }
.node-code { font-weight: 600; font-size: 12px; color: #409EFF; }
.node-name { font-size: 11px; color: #606266; }
.order-hint { color: #909399; font-size: 13px; margin-bottom: 16px; }
.order-item { display: flex; align-items: center; gap: 10px; font-size: 14px; }
</style>
