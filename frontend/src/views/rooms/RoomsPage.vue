<template>
  <div class="rooms-page">
    <div class="page-header">
      <div>
        <h2>Salles</h2>
        <p class="subtitle">Gestion des salles et laboratoires</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="openModal()">Nouvelle salle</el-button>
    </div>

    <el-card shadow="never" class="filter-card">
      <el-row :gutter="16">
        <el-col :xs="24" :sm="8">
          <el-input v-model="filters.search" placeholder="Nom, code..." clearable @input="load" />
        </el-col>
        <el-col :xs="24" :sm="6">
          <el-select v-model="filters.room_type" placeholder="Type de salle" clearable @change="load" style="width:100%">
            <el-option value="amphi" label="Amphithéâtre" />
            <el-option value="salle" label="Salle de cours" />
            <el-option value="labo_info" label="Labo Informatique" />
            <el-option value="labo_science" label="Labo Sciences" />
            <el-option value="salle_tp" label="Salle TP" />
            <el-option value="conf" label="Salle de conférence" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="4">
          <el-select v-model="filters.available" placeholder="Disponibilité" clearable @change="load" style="width:100%">
            <el-option :value="true" label="Disponible" />
            <el-option :value="false" label="Indisponible" />
          </el-select>
        </el-col>
      </el-row>
    </el-card>

    <el-row :gutter="16" class="mt-3">
      <el-col v-for="room in rooms" :key="room.id" :xs="24" :sm="12" :md="8" :lg="6">
        <el-card shadow="hover" class="room-card">
          <div class="room-header">
            <el-icon :size="28" :color="roomTypeColor(room.room_type)">
              <OfficeBuilding />
            </el-icon>
            <div>
              <div class="room-code">{{ room.code }}</div>
              <el-tag :type="room.is_available ? 'success' : 'danger'" size="small">
                {{ room.is_available ? 'Disponible' : 'Indisponible' }}
              </el-tag>
            </div>
          </div>
          <div class="room-name">{{ room.name }}</div>
          <div class="room-meta">
            <span><el-icon><Location /></el-icon> {{ room.building || 'N/A' }}, Ét. {{ room.floor }}</span>
            <span class="capacity">{{ room.capacity }} places</span>
          </div>
          <div class="room-type">{{ roomTypeLabel(room.room_type) }}</div>
          <div class="room-features">
            <el-tag v-if="room.has_projector" size="small" type="info">Vidéo</el-tag>
            <el-tag v-if="room.has_computers" size="small" type="info">Ordinateurs</el-tag>
            <el-tag v-if="room.has_internet" size="small" type="info">Internet</el-tag>
          </div>
          <div class="room-actions">
            <el-button text type="primary" :icon="Edit" size="small" @click="openModal(room)">Modifier</el-button>
            <el-button text type="danger" :icon="Delete" size="small" @click="handleDelete(room)">Supprimer</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-empty v-if="!loading && rooms.length === 0" description="Aucune salle trouvée" class="mt-4" />

    <div class="pagination-row">
      <el-pagination v-model:current-page="page" :total="total" layout="total, prev, pager, next" @change="load" />
    </div>

    <RoomModal v-if="showModal" :room="editRoom" @close="showModal = false" @saved="onSaved" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus, Edit, Delete, OfficeBuilding, Location } from '@element-plus/icons-vue'
import axios from '@/plugins/axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import RoomModal from '@/components/modals/RoomModal.vue'

const loading = ref(false)
const rooms = ref([])
const total = ref(0)
const page = ref(1)
const filters = ref({ search: '', room_type: '', available: '' })
const showModal = ref(false)
const editRoom = ref(null)

const typeLabels = { amphi: 'Amphithéâtre', salle: 'Salle de cours', labo_info: 'Labo Info',
  labo_science: 'Labo Sciences', salle_tp: 'Salle TP', conf: 'Conférence' }
const typeColors = { amphi: '#409EFF', salle: '#67C23A', labo_info: '#E6A23C', labo_science: '#9B59B6', salle_tp: '#F56C6C', conf: '#1ABC9C' }
function roomTypeLabel(t) { return typeLabels[t] || t }
function roomTypeColor(t) { return typeColors[t] || '#909399' }

async function load() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: 20 }
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.room_type) params.room_type = filters.value.room_type
    if (filters.value.available !== '') params.is_available = filters.value.available
    const res = await axios.get('/academic/rooms/', { params })
    const d = res.data
    rooms.value = d.results || d
    total.value = d.count || rooms.value.length
  } finally {
    loading.value = false
  }
}

function openModal(room = null) { editRoom.value = room; showModal.value = true }

async function handleDelete(row) {
  await ElMessageBox.confirm('Supprimer cette salle ?', 'Confirmation', { type: 'warning' })
  await axios.delete(`/academic/rooms/${row.id}/`)
  ElMessage.success('Salle supprimée')
  load()
}

function onSaved() { showModal.value = false; load() }
onMounted(load)
</script>

<style scoped>
.rooms-page { max-width: 1400px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.page-header h2 { font-size: 22px; font-weight: 700; color: #1e2a3a; }
.subtitle { color: #909399; font-size: 13px; }
.filter-card, .mt-3, .mt-4 { margin-top: 16px; }
.room-card { margin-bottom: 16px; transition: transform .15s; }
.room-card:hover { transform: translateY(-2px); }
.room-header { display: flex; align-items: flex-start; gap: 12px; margin-bottom: 10px; }
.room-code { font-weight: 700; font-size: 16px; color: #1e2a3a; }
.room-name { font-size: 14px; color: #303133; margin-bottom: 6px; }
.room-meta { display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #909399; margin-bottom: 4px; }
.capacity { font-weight: 600; color: #409EFF; }
.room-type { font-size: 12px; color: #606266; margin-bottom: 8px; }
.room-features { display: flex; gap: 4px; flex-wrap: wrap; margin-bottom: 10px; min-height: 22px; }
.room-actions { display: flex; gap: 4px; border-top: 1px solid #f0f0f0; padding-top: 8px; }
.pagination-row { display: flex; justify-content: flex-end; margin-top: 16px; }
</style>
