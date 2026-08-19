<template>
  <div class="timeslots-page">
    <div class="page-header">
      <div>
        <h2>Créneaux horaires</h2>
        <p class="subtitle">Configuration des plages horaires de l'université</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="openModal()">Nouveau créneau</el-button>
    </div>

    <!-- Visual grid view -->
    <el-card shadow="never" class="mb-3">
      <template #header>
        <div class="card-header-row">
          <span class="card-title">Grille horaire</span>
          <el-radio-group v-model="viewMode" size="small">
            <el-radio-button label="grid">Grille</el-radio-button>
            <el-radio-button label="table">Tableau</el-radio-button>
          </el-radio-group>
        </div>
      </template>

      <div v-if="viewMode === 'grid'" class="timetable-grid">
        <div class="grid-header">
          <div class="time-col"></div>
          <div v-for="day in days" :key="day.value" class="day-col">{{ day.label }}</div>
        </div>
        <div v-for="hour in timeRows" :key="hour" class="grid-row">
          <div class="time-col">{{ hour }}</div>
          <div v-for="day in days" :key="day.value" class="day-cell">
            <div v-for="slot in getSlotsForDayHour(day.value, hour)" :key="slot.id"
              class="slot-pill" :class="{ inactive: !slot.is_active }"
              @click="openModal(slot)">
              {{ formatTime(slot.start_time) }}–{{ formatTime(slot.end_time) }}
              <span v-if="slot.label" class="slot-label">{{ slot.label }}</span>
            </div>
          </div>
        </div>
      </div>

      <el-table v-else :data="slots" v-loading="loading" style="width:100%" stripe>
        <el-table-column label="Jour" width="110">
          <template #default="{ row }">{{ dayLabel(row.day_of_week) }}</template>
        </el-table-column>
        <el-table-column label="Début" width="90">
          <template #default="{ row }">{{ formatTime(row.start_time) }}</template>
        </el-table-column>
        <el-table-column label="Fin" width="90">
          <template #default="{ row }">{{ formatTime(row.end_time) }}</template>
        </el-table-column>
        <el-table-column prop="label" label="Libellé" min-width="180" />
        <el-table-column label="Actif" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? 'Oui' : 'Non' }}
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
    </el-card>

    <!-- Modal -->
    <el-dialog v-model="showModal" :title="editItem ? 'Modifier créneau' : 'Nouveau créneau'" width="460px">
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <el-form-item label="Jour" prop="day_of_week">
          <el-select v-model="form.day_of_week" style="width:100%">
            <el-option v-for="d in days" :key="d.value" :label="d.label" :value="d.value" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Heure de début" prop="start_time">
              <el-time-picker v-model="form.start_time" format="HH:mm" value-format="HH:mm:ss" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Heure de fin" prop="end_time">
              <el-time-picker v-model="form.end_time" format="HH:mm" value-format="HH:mm:ss" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Libellé">
          <el-input v-model="form.label" placeholder="ex: Matin 1ère période" />
        </el-form-item>
        <el-form-item>
          <el-switch v-model="form.is_active" active-text="Créneau actif" />
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
import { ref, reactive, computed, onMounted } from 'vue'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import axios from '@/plugins/axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const saving = ref(false)
const slots = ref([])
const showModal = ref(false)
const editItem = ref(null)
const viewMode = ref('grid')
const formRef = ref(null)
const form = reactive({ day_of_week: 1, start_time: '08:00:00', end_time: '10:00:00', label: '', is_active: true })
const rules = {
  day_of_week: [{ required: true, trigger: 'change' }],
  start_time: [{ required: true, message: 'Heure de début requise', trigger: 'change' }],
  end_time: [{ required: true, message: 'Heure de fin requise', trigger: 'change' }]
}

const days = [
  { value: 1, label: 'Lundi' }, { value: 2, label: 'Mardi' }, { value: 3, label: 'Mercredi' },
  { value: 4, label: 'Jeudi' }, { value: 5, label: 'Vendredi' }, { value: 6, label: 'Samedi' }
]
const timeRows = ['07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00']

function dayLabel(v) { return days.find(d => d.value === v)?.label || v }
function formatTime(t) { return t ? t.slice(0, 5) : '' }

function getSlotsForDayHour(day, hour) {
  return slots.value.filter(s => {
    if (s.day_of_week !== day) return false
    const slotHour = s.start_time?.slice(0, 5)
    return slotHour === hour
  })
}

async function load() {
  loading.value = true
  try {
    const res = await axios.get('/scheduling/time-slots/', { params: { page_size: 200 } })
    slots.value = res.data.results || res.data
  } finally { loading.value = false }
}

function openModal(item = null) {
  editItem.value = item
  if (item) Object.assign(form, { day_of_week: item.day_of_week, start_time: item.start_time, end_time: item.end_time, label: item.label || '', is_active: item.is_active })
  else Object.assign(form, { day_of_week: 1, start_time: '08:00:00', end_time: '10:00:00', label: '', is_active: true })
  showModal.value = true
}

async function save() {
  await formRef.value.validate()
  saving.value = true
  try {
    if (editItem.value) await axios.patch(`/scheduling/time-slots/${editItem.value.id}/`, form)
    else await axios.post('/scheduling/time-slots/', form)
    ElMessage.success('Enregistré')
    showModal.value = false
    load()
  } finally { saving.value = false }
}

async function handleDelete(row) {
  await ElMessageBox.confirm('Supprimer ce créneau ?', 'Confirmation', { type: 'warning' })
  await axios.delete(`/scheduling/time-slots/${row.id}/`)
  ElMessage.success('Supprimé')
  load()
}

onMounted(load)
</script>

<style scoped>
.timeslots-page { max-width: 1200px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.page-header h2 { font-size: 22px; font-weight: 700; color: #1e2a3a; }
.subtitle { color: #909399; font-size: 13px; }
.mb-3 { margin-bottom: 16px; }
.card-header-row { display: flex; justify-content: space-between; align-items: center; }
.card-title { font-weight: 600; }

.timetable-grid { overflow-x: auto; }
.grid-header, .grid-row { display: grid; grid-template-columns: 60px repeat(6, 1fr); }
.grid-header { background: #f5f7fa; font-weight: 600; font-size: 13px; }
.grid-header > div, .grid-row > div { padding: 8px 6px; border: 1px solid #e8ecef; min-height: 44px; }
.time-col { font-size: 11px; color: #909399; text-align: center; background: #fafafa; }
.day-col { text-align: center; color: #1e2a3a; }
.day-cell { background: #fff; vertical-align: top; }
.slot-pill {
  background: #ecf5ff; color: #409eff; border-radius: 4px;
  padding: 3px 6px; margin: 2px; font-size: 11px; cursor: pointer;
  border: 1px solid #d9ecff;
}
.slot-pill:hover { background: #d9ecff; }
.slot-pill.inactive { background: #f5f5f5; color: #c0c4cc; border-color: #e4e7ed; }
.slot-label { display: block; font-size: 10px; color: #6b9fd4; }
</style>
