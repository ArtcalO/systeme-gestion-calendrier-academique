<template>
  <el-dialog :title="room ? 'Modifier la salle' : 'Nouvelle salle'" v-model="visible" width="560px" @close="$emit('close')">
    <el-form :model="form" :rules="rules" ref="formRef" label-width="140px">
      <el-form-item label="Code" prop="code">
        <el-input v-model="form.code" placeholder="ex: A101" style="width:160px" />
      </el-form-item>
      <el-form-item label="Nom" prop="name">
        <el-input v-model="form.name" placeholder="ex: Salle A101" />
      </el-form-item>
      <el-form-item label="Type" prop="room_type">
        <el-select v-model="form.room_type" style="width:100%">
          <el-option value="amphi" label="Amphithéâtre" />
          <el-option value="salle" label="Salle de cours" />
          <el-option value="labo_info" label="Laboratoire Informatique" />
          <el-option value="labo_science" label="Laboratoire Sciences" />
          <el-option value="salle_tp" label="Salle TP" />
          <el-option value="conf" label="Salle de conférence" />
        </el-select>
      </el-form-item>
      <el-form-item label="Capacité" prop="capacity">
        <el-input-number v-model="form.capacity" :min="1" :max="2000" />
        <span class="hint">personnes</span>
      </el-form-item>
      <el-row :gutter="16">
        <el-col :span="14">
          <el-form-item label="Bâtiment" label-width="140px">
            <el-input v-model="form.building" placeholder="ex: Bâtiment A" />
          </el-form-item>
        </el-col>
        <el-col :span="10">
          <el-form-item label="Étage" label-width="60px">
            <el-input-number v-model="form.floor" :min="-2" :max="20" style="width:100%" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="Équipements">
        <el-checkbox v-model="form.has_projector">Projecteur/Vidéo</el-checkbox>
        <el-checkbox v-model="form.has_computers">Ordinateurs</el-checkbox>
        <el-checkbox v-model="form.has_internet">Internet</el-checkbox>
      </el-form-item>
      <el-form-item label="Disponible">
        <el-switch v-model="form.is_available" />
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
import { ref, watch } from 'vue'
import axios from '@/plugins/axios'
import { ElMessage } from 'element-plus'

const props = defineProps({ room: { type: Object, default: null } })
const emit = defineEmits(['close', 'saved'])
const visible = ref(true)
const formRef = ref()
const saving = ref(false)

const form = ref({ code: '', name: '', room_type: 'salle', capacity: 30, building: '',
  floor: 0, has_projector: false, has_computers: false, has_internet: false, is_available: true, notes: '' })

const rules = {
  code: [{ required: true }], name: [{ required: true }],
  room_type: [{ required: true }], capacity: [{ required: true }],
}

watch(() => props.room, (r) => {
  if (r) form.value = { ...r }
}, { immediate: true })

async function save() {
  await formRef.value.validate()
  saving.value = true
  try {
    if (props.room) {
      await axios.patch(`/academic/rooms/${props.room.id}/`, form.value)
    } else {
      await axios.post('/academic/rooms/', form.value)
    }
    ElMessage.success('Salle enregistrée')
    emit('saved')
  } finally {
    saving.value = false
  }
}
</script>
<style scoped>
.hint { margin-left: 8px; color: #909399; font-size: 13px; }
</style>
