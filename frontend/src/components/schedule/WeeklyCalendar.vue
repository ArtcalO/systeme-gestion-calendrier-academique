<template>
  <div class="weekly-calendar">
    <!-- Controls -->
    <div class="calendar-controls no-print">
      <el-select v-model="currentWeek" placeholder="Semaine" @change="load" style="width:200px">
        <el-option v-for="w in availableWeeks" :key="w.value" :label="w.label" :value="w.value" />
      </el-select>
      <el-button-group>
        <el-button :icon="ArrowLeft" @click="prevWeek" :disabled="weekIndex <= 0" />
        <el-button :icon="ArrowRight" @click="nextWeek" :disabled="weekIndex >= availableWeeks.length - 1" />
      </el-button-group>
      <el-button :icon="Printer" type="primary" plain @click="print">Imprimer</el-button>
      <el-tag v-if="currentWeek" type="info">
        {{ weekRange }}
      </el-tag>
    </div>

    <!-- Calendar grid -->
    <div id="weekly-print-area" v-loading="loading">
      <div class="print-header">
        <h3>{{ scheduleInfo?.schedule_name || 'Emploi du temps' }}</h3>
        <p>{{ scheduleInfo?.level }} — {{ scheduleInfo?.academic_year }} — {{ weekRange }}</p>
      </div>

      <div class="weekly-grid">
        <!-- Time column -->
        <div class="time-col">
          <div class="day-header">Horaire</div>
          <div v-for="slot in timeSlots" :key="slot.id" class="time-cell">
            {{ slot.start_time }} – {{ slot.end_time }}
          </div>
        </div>

        <!-- Day columns -->
        <div v-for="day in days" :key="day.num" class="day-col">
          <div class="day-header">{{ day.name }}</div>
          <div v-for="slot in timeSlots" :key="slot.id" class="time-cell cell-slot">
            <div v-if="getCellCourse(day.num, slot)" class="course-block"
                 :style="{ background: slotColor(getCellCourse(day.num, slot).slot_type) }">
              <div class="cb-code">{{ getCellCourse(day.num, slot).course_code }}</div>
              <div class="cb-name">{{ getCellCourse(day.num, slot).course_name }}</div>
              <div class="cb-info">
                <el-icon :size="11"><UserFilled /></el-icon> {{ getCellCourse(day.num, slot).professor }}
              </div>
              <div class="cb-info">
                <el-icon :size="11"><OfficeBuilding /></el-icon> {{ getCellCourse(day.num, slot).room }}
              </div>
              <el-tag size="small" class="cb-type no-print" :type="typeTag(getCellCourse(day.num, slot).slot_type)">
                {{ slotTypeLabel(getCellCourse(day.num, slot).slot_type) }}
              </el-tag>
            </div>
            <div v-else class="empty-cell"></div>
          </div>
        </div>
      </div>

      <div v-if="!loading && totalSlots === 0" class="no-data">
        Aucun cours planifié pour cette semaine
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ArrowLeft, ArrowRight, Printer, UserFilled, OfficeBuilding } from '@element-plus/icons-vue'
import axios from '@/plugins/axios'

const props = defineProps({ scheduleId: { type: [Number, String], required: true } })

const loading = ref(false)
const scheduleInfo = ref(null)
const currentWeek = ref('')
const availableWeeks = ref([])
const slotsData = ref({})
const weekIndex = ref(0)

const days = [
  { num: 1, name: 'Lundi' }, { num: 2, name: 'Mardi' }, { num: 3, name: 'Mercredi' },
  { num: 4, name: 'Jeudi' }, { num: 5, name: 'Vendredi' }, { num: 6, name: 'Samedi' },
]

const timeSlots = [
  { id: 1, start_time: '07:00', end_time: '09:00' },
  { id: 2, start_time: '09:00', end_time: '11:00' },
  { id: 3, start_time: '14:00', end_time: '16:00' },
  { id: 4, start_time: '16:00', end_time: '18:00' },
]

const totalSlots = computed(() => Object.values(slotsData.value).flat().length)

const weekRange = computed(() => {
  if (!currentWeek.value) return ''
  const [year, wk] = currentWeek.value.split('-W')
  const mon = getMonday(Number(year), Number(wk))
  const sat = new Date(mon); sat.setDate(sat.getDate() + 5)
  return `${fmtDate(mon)} — ${fmtDate(sat)}`
})

function getMonday(year, week) {
  const jan1 = new Date(year, 0, 1)
  const days = (week - 1) * 7
  const mon = new Date(jan1)
  mon.setDate(jan1.getDate() + days - jan1.getDay() + 1)
  return mon
}
function fmtDate(d) {
  return d.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function getCellCourse(dayNum, slot) {
  const daySlots = slotsData.value[dayNum] || []
  return daySlots.find(s => s.start_time === slot.start_time) || null
}

const slotColors = {
  regular: '#EBF5FB', makeup: '#FEF9E7', exam: '#FDEDEC', midterm: '#F3E5F5'
}
const slotTypes = {
  regular: { label: 'Régulier', type: '' },
  makeup: { label: 'Rattrapage', type: 'warning' },
  exam: { label: 'Examen', type: 'danger' },
  midterm: { label: 'Partiel', type: '' },
}
function slotColor(t) { return slotColors[t] || '#EBF5FB' }
function typeTag(t) { return slotTypes[t]?.type || '' }
function slotTypeLabel(t) { return slotTypes[t]?.label || t }

async function loadScheduleInfo() {
  const res = await axios.get(`/scheduling/schedules/${props.scheduleId}/`)
  const s = res.data
  scheduleInfo.value = {
    schedule_name: s.name, level: s.level?.name, academic_year: s.academic_year?.name,
  }
  // Build available weeks
  const annualRes = await axios.get(`/scheduling/schedules/${props.scheduleId}/annual_view/`)
  const weeks = (annualRes.data.weeks || []).map(w => ({
    value: w.week,
    label: `Semaine ${w.week.split('-W')[1]} (${w.week})`,
  }))
  availableWeeks.value = weeks
  if (weeks.length > 0) {
    currentWeek.value = weeks[0].value
    weekIndex.value = 0
    await load()
  }
}

async function load() {
  if (!currentWeek.value) return
  loading.value = true
  try {
    const res = await axios.get(`/scheduling/schedules/${props.scheduleId}/weekly_view/`, {
      params: { week: currentWeek.value }
    })
    const cal = res.data.weekly_calendar || {}
    const dayMap = { 'Lundi': 1, 'Mardi': 2, 'Mercredi': 3, 'Jeudi': 4, 'Vendredi': 5, 'Samedi': 6 }
    const newData = {}
    for (const [dayName, slots] of Object.entries(cal)) {
      const dayNum = dayMap[dayName]
      if (dayNum) newData[dayNum] = slots
    }
    slotsData.value = newData
  } finally {
    loading.value = false
  }
}

function prevWeek() {
  if (weekIndex.value > 0) {
    weekIndex.value--
    currentWeek.value = availableWeeks.value[weekIndex.value].value
    load()
  }
}

function nextWeek() {
  if (weekIndex.value < availableWeeks.value.length - 1) {
    weekIndex.value++
    currentWeek.value = availableWeeks.value[weekIndex.value].value
    load()
  }
}

function print() {
  const el = document.getElementById('weekly-print-area')
  if (!el) return
  const w = window.open('', '_blank')
  w.document.write(`
    <html><head><title>Emploi du temps</title>
    <style>
      body{font-family:Arial,sans-serif;font-size:11px;margin:16px}
      h3{margin:0 0 4px;font-size:14px}p{margin:0 0 12px;color:#666}
      .weekly-grid{display:grid;grid-template-columns:90px repeat(6,1fr);border:1px solid #ccc}
      .day-header{background:#1e2a3a;color:#fff;padding:6px;font-weight:700;text-align:center;font-size:12px}
      .time-cell{border:1px solid #eee;min-height:60px;padding:4px}
      .course-block{background:#EBF5FB;border-radius:4px;padding:4px;height:100%}
      .cb-code{font-weight:700;font-size:11px;color:#1a6496}
      .cb-name{font-size:10px;margin:2px 0}
      .cb-info{font-size:10px;color:#666}
      .no-print{display:none!important}
      @page{margin:1cm;size:A4 landscape}
    </style></head><body>
    ${el.innerHTML}
    </body></html>
  `)
  w.document.close()
  w.print()
}

onMounted(loadScheduleInfo)
</script>

<style scoped>
.weekly-calendar { padding: 4px; }
.calendar-controls { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }
.print-header { margin-bottom: 12px; }
.print-header h3 { font-size: 18px; font-weight: 700; color: #1e2a3a; margin: 0 0 4px; }
.print-header p { color: #606266; font-size: 13px; }
.weekly-grid {
  display: grid;
  grid-template-columns: 90px repeat(6, 1fr);
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  overflow: hidden;
}
.time-col, .day-col { display: flex; flex-direction: column; }
.day-header {
  background: #1e2a3a; color: #fff; padding: 10px 8px;
  font-weight: 700; text-align: center; font-size: 13px;
}
.time-cell {
  border: 1px solid #ebeef5;
  min-height: 80px;
  padding: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #909399;
}
.cell-slot { padding: 4px; }
.course-block {
  width: 100%; height: 100%; min-height: 68px;
  border-radius: 6px; padding: 6px;
  border-left: 3px solid #409EFF;
}
.cb-code { font-weight: 700; font-size: 12px; color: #1a6496; }
.cb-name { font-size: 11px; color: #303133; margin: 2px 0; line-height: 1.3; }
.cb-info { font-size: 11px; color: #606266; display: flex; align-items: center; gap: 3px; }
.cb-type { margin-top: 4px; }
.empty-cell { width: 100%; height: 68px; }
.no-data { text-align: center; color: #909399; padding: 32px; }
@media print { .no-print { display: none !important; } }
</style>
