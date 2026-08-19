<template>
  <el-dialog :title="year ? 'Modifier l\'année' : 'Nouvelle année académique'" v-model="visible" width="500px" @close="$emit('close')">
    <el-form :model="form" :rules="rules" ref="formRef" label-width="160px">
      <el-form-item label="Nom" prop="name">
        <el-input v-model="form.name" placeholder="ex: 2024-2025" />
      </el-form-item>
      <el-form-item label="Date de début" prop="start_date">
        <el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" placeholder="Début" style="width:100%" />
      </el-form-item>
      <el-form-item label="Date de fin" prop="end_date">
        <el-date-picker v-model="form.end_date" type="date" value-format="YYYY-MM-DD" placeholder="Fin" style="width:100%" />
      </el-form-item>
      <el-form-item label="Année courante">
        <el-switch v-model="form.is_current" />
        <span class="hint">Une seule année peut être courante</span>
      </el-form-item>
      <el-form-item label="Inscriptions ouvertes">
        <el-switch v-model="form.is_enrollment_open" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="$emit('close')">Annuler</el-button>
      <el-button type="primary" :loading="saving" @click="save">Enregistrer</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import axios from '@/plugins/axios'
import { ElMessage } from 'element-plus'

const props = defineProps({ year: { type: Object, default: null } })
const emit = defineEmits(['close', 'saved'])
const visible = ref(true)
const formRef = ref()
const saving = ref(false)

const form = ref({ name: '', start_date: '', end_date: '', is_current: false, is_enrollment_open: false })

const rules = {
  name: [{ required: true, message: 'Nom requis' }],
  start_date: [{ required: true }], end_date: [{ required: true }],
}

watch(() => props.year, (y) => {
  if (y) form.value = { name: y.name, start_date: y.start_date, end_date: y.end_date,
    is_current: y.is_current, is_enrollment_open: y.is_enrollment_open }
}, { immediate: true })

async function save() {
  await formRef.value.validate()
  saving.value = true
  try {
    if (props.year) {
      await axios.patch(`/academic/academic-years/${props.year.id}/`, form.value)
    } else {
      await axios.post('/academic/academic-years/', form.value)
    }
    ElMessage.success('Année enregistrée')
    emit('saved')
  } finally {
    saving.value = false
  }
}
</script>
<style scoped>
.hint { margin-left: 10px; font-size: 12px; color: #909399; }
</style>
