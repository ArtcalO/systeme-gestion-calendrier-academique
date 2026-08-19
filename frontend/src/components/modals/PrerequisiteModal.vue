<template>
  <el-dialog
    :title="prereq ? 'Modifier le prérequis' : 'Ajouter un prérequis'"
    v-model="visible"
    width="580px"
    @close="$emit('close')"
  >
    <el-alert type="info" :closable="false" class="mb-3">
      <strong>Types de prérequis :</strong><br>
      • <strong>Strict</strong> : le module A doit être complété AVANT le module B<br>
      • <strong>Coréquisit</strong> : les modules A et B peuvent être suivis en PARALLÈLE<br>
      • <strong>Recommandé</strong> : il est conseillé de suivre A avant B
    </el-alert>

    <el-form :model="form" :rules="rules" ref="formRef" label-width="160px">
      <el-form-item label="Module prérequis" prop="prerequisite">
        <el-select v-model="form.prerequisite" filterable placeholder="Module à compléter en premier" style="width:100%">
          <el-option v-for="m in modules" :key="m.id" :label="`${m.code} — ${m.name} (${m.level_name} S${m.semester})`" :value="m.id" />
        </el-select>
      </el-form-item>

      <el-form-item label="Type de relation" prop="prerequisite_type">
        <el-radio-group v-model="form.prerequisite_type">
          <el-radio value="strict">
            <el-tag type="danger" size="small">Strict</el-tag> Avant
          </el-radio>
          <el-radio value="coreq">
            <el-tag type="warning" size="small">Coréquisit</el-tag> Parallèle
          </el-radio>
          <el-radio value="recommended">
            <el-tag type="info" size="small">Recommandé</el-tag>
          </el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="Module cible" prop="module">
        <el-select v-model="form.module" filterable placeholder="Module qui nécessite ce prérequis" style="width:100%">
          <el-option v-for="m in modules" :key="m.id" :label="`${m.code} — ${m.name} (${m.level_name} S${m.semester})`" :value="m.id" />
        </el-select>
      </el-form-item>

      <el-form-item v-if="form.prerequisite_type === 'strict'" label="Note minimale">
        <el-input-number v-model="form.minimum_grade" :min="0" :max="20" :step="0.5" />
        <span class="hint">/20</span>
      </el-form-item>

      <el-form-item label="Description">
        <el-input v-model="form.description" type="textarea" :rows="2" placeholder="Justification pédagogique..." />
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

const props = defineProps({ prereq: { type: Object, default: null } })
const emit = defineEmits(['close', 'saved'])

const visible = ref(true)
const formRef = ref()
const saving = ref(false)
const modules = ref([])

const form = ref({
  module: null, prerequisite: null,
  prerequisite_type: 'strict', minimum_grade: 10, description: ''
})

const rules = {
  module: [{ required: true, message: 'Module cible requis' }],
  prerequisite: [{ required: true, message: 'Module prérequis requis' }],
  prerequisite_type: [{ required: true }],
}

watch(() => props.prereq, (p) => {
  if (p) form.value = { module: p.module, prerequisite: p.prerequisite,
    prerequisite_type: p.prerequisite_type, minimum_grade: parseFloat(p.minimum_grade), description: p.description || '' }
}, { immediate: true })

async function save() {
  await formRef.value.validate()
  saving.value = true
  try {
    if (props.prereq) {
      await axios.patch(`/prerequisites/module-prerequisites/${props.prereq.id}/`, form.value)
    } else {
      await axios.post('/prerequisites/module-prerequisites/', form.value)
    }
    ElMessage.success('Prérequis enregistré')
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

<style scoped>
.mb-3 { margin-bottom: 16px; }
.hint { margin-left: 8px; color: #909399; }
</style>
