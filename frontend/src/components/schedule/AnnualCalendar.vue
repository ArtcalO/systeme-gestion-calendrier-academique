<template>
  <div class="annual-calendar">
    <div class="annual-controls no-print">
      <div class="annual-info" v-if="annualData">
        <span><strong>{{ annualData.level }}</strong></span>
        <span>{{ annualData.academic_year }} · Semestre {{ annualData.semester }}</span>
        <span>{{ annualData.total_weeks }} semaine(s)</span>
      </div>
      <div class="actions">
        <el-input v-model="search" placeholder="Rechercher un cours..." style="width:200px" clearable />
        <el-button :icon="Printer" type="primary" plain @click="print">Imprimer planning annuel</el-button>
      </div>
    </div>

    <div id="annual-print-area" v-loading="loading">
      <div class="print-header">
        <h3>Planification annuelle — {{ annualData?.schedule_name }}</h3>
        <p>{{ annualData?.level }} · {{ annualData?.academic_year }} · Semestre {{ annualData?.semester }}</p>
      </div>

      <div v-for="week in filteredWeeks" :key="week.week" class="week-block">
        <div class="week-header">
          <span class="week-label">Semaine {{ week.week.split('-W')[1] }} · {{ week.week }}</span>
          <span class="week-hours">{{ week.total_hours }}h</span>
        </div>
        <div class="week-slots">
          <div v-for="slot in week.slots" :key="slot.id" class="annual-slot"
               :style="{ borderLeftColor: dayColor(slot.day_number) }">
            <div class="slot-day">{{ slot.day }}</div>
            <div class="slot-time">{{ slot.start_time }}–{{ slot.end_time }}</div>
            <div class="slot-course">
              <strong>{{ slot.course_code }}</strong> {{ slot.course_name }}
            </div>
            <div class="slot-meta">
              <el-icon :size="11"><UserFilled /></el-icon> {{ slot.professor }}
              <el-icon :size="11" style="margin-left:8px"><OfficeBuilding /></el-icon> {{ slot.room }}
            </div>
          </div>
        </div>
      </div>

      <el-empty v-if="!loading && (!annualData || annualData.weeks?.length === 0)"
        description="Aucune donnée de planification disponible" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Printer, UserFilled, OfficeBuilding } from '@element-plus/icons-vue'
import axios from '@/plugins/axios'

const props = defineProps({ scheduleId: { type: [Number, String], required: true } })

const loading = ref(false)
const annualData = ref(null)
const search = ref('')

const dayColors = ['', '#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#9B59B6', '#1ABC9C']
function dayColor(n) { return dayColors[n] || '#909399' }

const filteredWeeks = computed(() => {
  if (!annualData.value?.weeks) return []
  if (!search.value) return annualData.value.weeks
  const q = search.value.toLowerCase()
  return annualData.value.weeks.map(w => ({
    ...w,
    slots: w.slots.filter(s =>
      s.course_name.toLowerCase().includes(q) ||
      s.course_code.toLowerCase().includes(q) ||
      s.professor.toLowerCase().includes(q)
    )
  })).filter(w => w.slots.length > 0)
})

async function load() {
  loading.value = true
  try {
    const res = await axios.get(`/scheduling/schedules/${props.scheduleId}/annual_view/`)
    annualData.value = res.data
  } finally {
    loading.value = false
  }
}

function print() {
  const el = document.getElementById('annual-print-area')
  if (!el) return
  const w = window.open('', '_blank')
  w.document.write(`
    <html><head><title>Planification annuelle</title>
    <style>
      body{font-family:Arial,sans-serif;font-size:11px;margin:16px;color:#333}
      h3{margin:0 0 4px;font-size:14px} p{color:#666;margin:0 0 16px}
      .week-block{margin-bottom:16px;break-inside:avoid}
      .week-header{display:flex;justify-content:space-between;background:#1e2a3a;color:#fff;padding:6px 12px;border-radius:4px 4px 0 0;font-weight:700}
      .week-slots{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:6px;padding:8px;border:1px solid #ddd;border-top:none}
      .annual-slot{border-left:3px solid #409EFF;padding:6px;background:#f9f9f9;border-radius:0 4px 4px 0}
      .slot-day{font-weight:700;font-size:10px;text-transform:uppercase;color:#888}
      .slot-time{font-size:10px;color:#666}
      .slot-course{font-size:11px;margin:2px 0}
      .slot-meta{font-size:10px;color:#888;display:flex;align-items:center;gap:4px}
      .no-print{display:none!important}
      @page{margin:1.5cm}
    </style></head><body>${el.innerHTML}</body></html>
  `)
  w.document.close()
  w.print()
}

onMounted(load)
</script>

<style scoped>
.annual-calendar { padding: 4px; }
.annual-controls { display: flex; justify-content: space-between; align-items: center; gap: 16px; margin-bottom: 16px; flex-wrap: wrap; }
.annual-info { display: flex; gap: 16px; align-items: center; font-size: 14px; color: #303133; }
.actions { display: flex; gap: 10px; align-items: center; }
.print-header { margin-bottom: 16px; }
.print-header h3 { font-size: 18px; font-weight: 700; color: #1e2a3a; margin: 0 0 4px; }
.print-header p { color: #606266; font-size: 13px; }
.week-block { margin-bottom: 20px; border: 1px solid #e4e7ed; border-radius: 8px; overflow: hidden; }
.week-header {
  display: flex; justify-content: space-between; align-items: center;
  background: #1e2a3a; color: #fff; padding: 8px 14px; font-weight: 700; font-size: 13px;
}
.week-hours { font-size: 12px; opacity: .8; }
.week-slots { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 8px; padding: 10px; background: #fafafa; }
.annual-slot {
  border-left: 3px solid #409EFF; padding: 8px 10px;
  background: #fff; border-radius: 0 6px 6px 0;
  box-shadow: 0 1px 3px rgba(0,0,0,.06);
}
.slot-day { font-size: 10px; font-weight: 700; text-transform: uppercase; color: #909399; margin-bottom: 2px; }
.slot-time { font-size: 11px; color: #606266; margin-bottom: 4px; }
.slot-course { font-size: 12px; color: #303133; line-height: 1.4; }
.slot-course strong { color: #1a6496; }
.slot-meta { display: flex; align-items: center; gap: 4px; font-size: 11px; color: #909399; margin-top: 4px; }
@media print { .no-print { display: none !important; } }
</style>
