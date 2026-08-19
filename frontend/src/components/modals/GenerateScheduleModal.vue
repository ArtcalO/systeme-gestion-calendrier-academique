<template>
  <el-dialog title="Générer un calendrier" v-model="visible" width="580px" @close="$emit('close')">
    <el-form :model="form" :rules="rules" ref="formRef" label-width="160px">
      <el-form-item label="Nom du calendrier" prop="schedule_name">
        <el-input v-model="form.schedule_name" placeholder="ex: Emploi du temps L2 S1 2024-25" />
      </el-form-item>
      <el-form-item label="Année académique" prop="academic_year_id">
        <el-select v-model="form.academic_year_id" placeholder="Sélectionner" style="width:100%" @change="onYearChange">
          <el-option v-for="y in academicYears" :key="y.id" :label="y.name" :value="y.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="Semestre" prop="semester">
        <el-radio-group v-model="form.semester">
          <el-radio :value="1">Semestre 1</el-radio>
          <el-radio :value="2">Semestre 2</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="Niveau / Promotion" prop="level_id">
        <el-select v-model="form.level_id" placeholder="Sélectionner un niveau" style="width:100%" filterable>
          <el-option-group v-for="prog in programsWithLevels" :key="prog.id" :label="prog.name">
            <el-option v-for="lv in prog.levels" :key="lv.id" :label="lv.name" :value="lv.id" />
          </el-option-group>
        </el-select>
      </el-form-item>
      <el-form-item label="Début de période" prop="week_start">
        <el-date-picker v-model="form.week_start" type="date" placeholder="Date de début" value-format="YYYY-MM-DD" style="width:100%" />
      </el-form-item>
      <el-form-item label="Fin de période" prop="week_end">
        <el-date-picker v-model="form.week_end" type="date" placeholder="Date de fin" value-format="YYYY-MM-DD" style="width:100%" />
      </el-form-item>
    </el-form>

    <el-alert v-if="result" :type="result.success ? 'success' : 'error'" :closable="false" class="mt-3">
      <template #title>{{ result.message }}</template>
      <div v-if="result.stats" class="stats-grid">
        <div><strong>{{ result.stats.placed_courses }}</strong> cours placés</div>
        <div><strong>{{ result.stats.total_courses }}</strong> cours total</div>
        <div><strong>{{ result.stats.conflicts }}</strong> conflits</div>
        <div><strong>{{ result.stats.unplaced_courses }}</strong> non placés</div>
      </div>
    </el-alert>

    <template #footer>
      <el-button @click="$emit('close')">Fermer</el-button>
      <el-button type="primary" :loading="generating" @click="generate" :disabled="!!result">
        <el-icon><MagicStick /></el-icon> Générer
      </el-button>
      <el-button v-if="result?.success" type="success" @click="viewSchedule">
        Voir le calendrier
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { MagicStick } from '@element-plus/icons-vue'
import axios from '@/plugins/axios'

const props = defineProps({ academicYears: { type: Array, default: () => [] } })
const emit = defineEmits(['close', 'generated'])
const router = useRouter()

const visible = ref(true)
const formRef = ref()
const generating = ref(false)
const result = ref(null)
const programsWithLevels = ref([])
const generatedScheduleId = ref(null)

const form = ref({
  schedule_name: '', academic_year_id: null, semester: 1,
  level_id: null, week_start: '', week_end: ''
})

const rules = {
  schedule_name: [{ required: true, message: 'Nom requis' }],
  academic_year_id: [{ required: true, message: 'Année requise' }],
  level_id: [{ required: true, message: 'Niveau requis' }],
  week_start: [{ required: true, message: 'Date de début requise' }],
  week_end: [{ required: true, message: 'Date de fin requise' }],
}

async function generate() {
  await formRef.value.validate()
  generating.value = true
  result.value = null
  try {
    const res = await axios.post('/scheduling/schedules/generate/', form.value)
    generatedScheduleId.value = res.data.schedule?.id
    result.value = { success: true, message: res.data.message, stats: res.data.stats }
    emit('generated')
  } catch (e) {
    result.value = { success: false, message: e.response?.data?.error || 'Erreur lors de la génération' }
  } finally {
    generating.value = false
  }
}

function viewSchedule() {
  if (generatedScheduleId.value) {
    router.push(`/schedules/${generatedScheduleId.value}`)
    emit('close')
  }
}

async function loadPrograms() {
  const res = await axios.get('/academic/programs/', { params: { page_size: 100 } })
  programsWithLevels.value = (res.data.results || res.data).filter(p => p.levels?.length > 0)
}

onMounted(loadPrograms)
</script>

<style scoped>
.mt-3 { margin-top: 16px; }
.stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 4px 16px; margin-top: 8px; font-size: 13px; }
</style>
