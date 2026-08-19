<template>
  <el-dialog :title="professor ? 'Modifier le professeur' : 'Nouveau professeur'" v-model="visible" width="620px" @close="$emit('close')">
    <el-form :model="form" :rules="rules" ref="formRef" label-width="150px">
      <el-divider content-position="left">Compte utilisateur</el-divider>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="Prénom" prop="first_name" label-width="100px">
            <el-input v-model="form.first_name" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Nom" prop="last_name" label-width="100px">
            <el-input v-model="form.last_name" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="Email" prop="email">
        <el-input v-model="form.email" type="email" />
      </el-form-item>
      <el-form-item v-if="!professor" label="Mot de passe" prop="password">
        <el-input v-model="form.password" type="password" show-password />
      </el-form-item>

      <el-divider content-position="left">Profil professeur</el-divider>
      <el-form-item label="Grade" prop="grade">
        <el-select v-model="form.grade" style="width:100%">
          <el-option value="assistant" label="Assistant" />
          <el-option value="chef_travaux" label="Chef de Travaux" />
          <el-option value="charge_cours" label="Chargé de Cours" />
          <el-option value="maitre_assistant" label="Maître-Assistant" />
          <el-option value="prof_associe" label="Professeur Associé" />
          <el-option value="prof_ordinaire" label="Professeur Ordinaire" />
        </el-select>
      </el-form-item>
      <el-form-item label="Département" prop="department">
        <el-select v-model="form.department" placeholder="Sélectionner" style="width:100%">
          <el-option v-for="d in departments" :key="d.id" :label="d.name" :value="d.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="H max/semaine">
        <el-input-number v-model="form.max_weekly_hours" :min="1" :max="40" />
      </el-form-item>
      <el-form-item label="Disponible">
        <el-switch v-model="form.is_available" />
      </el-form-item>
      <el-form-item label="Bio">
        <el-input v-model="form.bio" type="textarea" :rows="2" />
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

const props = defineProps({ professor: Object, departments: { type: Array, default: () => [] } })
const emit = defineEmits(['close', 'saved'])
const visible = ref(true)
const formRef = ref()
const saving = ref(false)

const form = ref({
  first_name: '', last_name: '', email: '', password: '',
  grade: 'charge_cours', department: null, max_weekly_hours: 15, is_available: true, bio: ''
})

const rules = {
  first_name: [{ required: true }], last_name: [{ required: true }],
  email: [{ required: true, type: 'email' }], grade: [{ required: true }],
  password: [{ required: !props.professor, min: 6, message: 'Min 6 caractères' }],
}

watch(() => props.professor, (p) => {
  if (p) form.value = {
    first_name: p.user?.first_name || '', last_name: p.user?.last_name || '',
    email: p.user?.email || '', password: '',
    grade: p.grade, department: p.department, max_weekly_hours: p.max_weekly_hours, is_available: p.is_available, bio: p.bio || ''
  }
}, { immediate: true })

async function save() {
  await formRef.value.validate()
  saving.value = true
  try {
    if (props.professor) {
      await axios.patch(`/auth/professors/${props.professor.id}/`, form.value)
    } else {
      await axios.post('/auth/professors/', { ...form.value, role: 'professor' })
    }
    ElMessage.success('Professeur enregistré')
    emit('saved')
  } finally {
    saving.value = false
  }
}
</script>
