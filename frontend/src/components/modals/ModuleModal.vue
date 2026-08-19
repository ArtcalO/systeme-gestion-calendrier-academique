<template>
  <el-dialog :title="module ? 'Modifier le module' : 'Nouveau module'" v-model="visible" width="600px" @close="$emit('close')">
    <el-form :model="form" :rules="rules" ref="formRef" label-width="150px">
      <el-form-item label="Code" prop="code">
        <el-input v-model="form.code" placeholder="ex: INFO301" style="width:200px" />
      </el-form-item>
      <el-form-item label="Nom" prop="name">
        <el-input v-model="form.name" placeholder="Nom complet du module" />
      </el-form-item>
      <el-form-item label="Programme" prop="program">
        <el-select v-model="form.program" placeholder="Programme" @change="onProgramChange" style="width:100%">
          <el-option v-for="p in programs" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="Niveau" prop="level">
        <el-select v-model="form.level" placeholder="Niveau" style="width:100%" :disabled="!form.program">
          <el-option v-for="l in levels" :key="l.id" :label="l.name" :value="l.id" />
        </el-select>
      </el-form-item>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="Semestre" prop="semester" label-width="150px">
            <el-select v-model="form.semester" style="width:100%">
              <el-option :value="1" label="Semestre 1" />
              <el-option :value="2" label="Semestre 2" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Type" prop="module_type" label-width="100px">
            <el-select v-model="form.module_type" style="width:100%">
              <el-option value="cours" label="Cours Magistral" />
              <el-option value="tp" label="TP" />
              <el-option value="td" label="TD" />
              <el-option value="seminaire" label="Séminaire" />
              <el-option value="stage" label="Stage" />
              <el-option value="projet" label="Projet" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="Crédits" prop="credits" label-width="150px">
            <el-input-number v-model="form.credits" :min="1" :max="30" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="H/semaine" label-width="100px">
            <el-input-number v-model="form.weekly_hours" :min="1" :max="20" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="Obligatoire">
        <el-switch v-model="form.is_mandatory" />
      </el-form-item>
      <el-form-item label="Description">
        <el-input v-model="form.description" type="textarea" :rows="2" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="$emit('close')">Annuler</el-button>
      <el-button type="primary" :loading="saving" @click="save">Enregistrer</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import axios from '@/plugins/axios'
import { ElMessage } from 'element-plus'

const props = defineProps({ module: { type: Object, default: null }, programs: { type: Array, default: () => [] } })
const emit = defineEmits(['close', 'saved'])

const visible = ref(true)
const formRef = ref()
const saving = ref(false)
const levels = ref([])

const form = ref({ code: '', name: '', program: null, level: null, semester: 1,
  module_type: 'cours', credits: 3, weekly_hours: 3, is_mandatory: true, description: '' })

const rules = {
  code: [{ required: true, message: 'Code requis' }],
  name: [{ required: true, message: 'Nom requis' }],
  level: [{ required: true, message: 'Niveau requis' }],
  semester: [{ required: true }],
}

watch(() => props.module, async (m) => {
  if (m) {
    form.value = { code: m.code, name: m.name, program: null, level: m.level,
      semester: m.semester, module_type: m.module_type, credits: m.credits,
      weekly_hours: m.weekly_hours, is_mandatory: m.is_mandatory, description: m.description || '' }
    // load levels for current level's program
    const lvRes = await axios.get(`/academic/levels/${m.level}/`)
    if (lvRes.data.program) {
      form.value.program = lvRes.data.program
      await onProgramChange()
    }
  }
}, { immediate: true })

async function onProgramChange() {
  if (!form.value.program) return
  const res = await axios.get('/academic/levels/', { params: { program: form.value.program } })
  levels.value = res.data.results || res.data
}

async function save() {
  await formRef.value.validate()
  saving.value = true
  const payload = { ...form.value }
  delete payload.program
  try {
    if (props.module) {
      await axios.patch(`/academic/modules/${props.module.id}/`, payload)
    } else {
      await axios.post('/academic/modules/', payload)
    }
    ElMessage.success('Module enregistré')
    emit('saved')
  } finally {
    saving.value = false
  }
}
</script>
