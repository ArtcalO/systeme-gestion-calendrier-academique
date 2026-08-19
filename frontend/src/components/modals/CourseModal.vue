<template>
  <el-dialog
    :title="course ? 'Modifier le cours' : 'Nouveau cours'"
    v-model="visible"
    width="560px"
    @close="$emit('close')"
  >
    <el-form :model="form" :rules="rules" ref="formRef" label-width="140px">
      <el-form-item label="Module" prop="module">
        <el-select v-model="form.module" filterable placeholder="Sélectionner un module" style="width:100%">
          <el-option v-for="m in modules" :key="m.id" :label="`${m.code} - ${m.name}`" :value="m.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="Année académique" prop="academic_year">
        <el-select v-model="form.academic_year" placeholder="Sélectionner" style="width:100%">
          <el-option v-for="y in academicYears" :key="y.id" :label="y.name" :value="y.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="Semestre" prop="semester">
        <el-select v-model="form.semester" style="width:100%">
          <el-option :value="1" label="Semestre 1" />
          <el-option :value="2" label="Semestre 2" />
        </el-select>
      </el-form-item>
      <el-form-item label="Heures/semaine" prop="weekly_hours">
        <el-input-number v-model="form.weekly_hours" :min="1" :max="20" />
      </el-form-item>
      <el-form-item label="Statut" prop="status">
        <el-select v-model="form.status" style="width:100%">
          <el-option value="draft" label="Brouillon" />
          <el-option value="scheduled" label="Planifié" />
          <el-option value="ongoing" label="En cours" />
          <el-option value="completed" label="Terminé" />
          <el-option value="cancelled" label="Annulé" />
        </el-select>
      </el-form-item>
      <el-form-item label="Notes">
        <el-input v-model="form.notes" type="textarea" :rows="2" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="$emit('close')">Annuler</el-button>
      <el-button type="primary" :loading="saving" @click="save">Enregistrer</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import axios from '@/plugins/axios'
import { ElMessage } from 'element-plus'

const props = defineProps({
  course: { type: Object, default: null },
  academicYears: { type: Array, default: () => [] },
})
const emit = defineEmits(['close', 'saved'])

const visible = ref(true)
const formRef = ref()
const saving = ref(false)
const modules = ref([])

const form = ref({
  module: null, academic_year: null, semester: 1,
  weekly_hours: 3, status: 'draft', notes: ''
})

const rules = {
  module: [{ required: true, message: 'Module requis' }],
  academic_year: [{ required: true, message: 'Année requise' }],
  semester: [{ required: true, message: 'Semestre requis' }],
  weekly_hours: [{ required: true, message: 'Heures requises' }],
}

watch(() => props.course, (c) => {
  if (c) {
    form.value = { module: c.module, academic_year: c.academic_year, semester: c.semester,
      weekly_hours: c.weekly_hours, status: c.status, notes: c.notes || '' }
  }
}, { immediate: true })

async function save() {
  await formRef.value.validate()
  saving.value = true
  try {
    if (props.course) {
      await axios.patch(`/academic/courses/${props.course.id}/`, form.value)
    } else {
      await axios.post('/academic/courses/', form.value)
    }
    ElMessage.success('Enregistré avec succès')
    emit('saved')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  const res = await axios.get('/academic/modules/', { params: { page_size: 500 } })
  modules.value = res.data.results || res.data
})
</script>
