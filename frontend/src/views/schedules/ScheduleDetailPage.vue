<template>
  <div class="schedule-detail" v-loading="loading">
    <div class="page-header">
      <div class="header-left">
        <el-button :icon="ArrowLeft" text @click="$router.back()">Retour</el-button>
        <div>
          <h2>{{ schedule?.name || 'Calendrier' }}</h2>
          <div class="header-meta" v-if="schedule">
            <el-tag :type="schedTag(schedule.status).type">{{ schedTag(schedule.status).label }}</el-tag>
            <span>{{ schedule.level?.name }}</span>
            <span>{{ schedule.academic_year?.name }}</span>
            <span>Semestre {{ schedule.semester }}</span>
          </div>
        </div>
      </div>
      <div class="header-actions" v-if="schedule">
        <el-button v-if="schedule.status === 'draft'" type="success" :icon="Upload" @click="publish">Publier</el-button>
        <el-button :icon="Download" @click="exportIcal">Export iCal</el-button>
      </div>
    </div>

    <!-- Tabs -->
    <el-tabs v-model="activeTab" class="mt-3">
      <el-tab-pane label="Vue hebdomadaire" name="weekly">
        <el-card shadow="never">
          <WeeklyCalendar v-if="scheduleId" :schedule-id="scheduleId" />
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="Vue annuelle" name="annual">
        <el-card shadow="never">
          <AnnualCalendar v-if="scheduleId" :schedule-id="scheduleId" />
        </el-card>
      </el-tab-pane>

      <el-tab-pane name="conflicts">
        <template #label>
          <span>Conflits
            <el-badge v-if="conflictCount > 0" :value="conflictCount" type="danger" class="ml-1" />
          </span>
        </template>
        <el-card shadow="never">
          <el-empty v-if="conflicts.length === 0" description="Aucun conflit détecté" />
          <div v-else>
            <el-alert type="warning" :title="`${conflictCount} conflit(s) non résolu(s)`" show-icon :closable="false" class="mb-3" />
            <el-table :data="conflicts" stripe>
              <el-table-column label="Type" width="220">
                <template #default="{ row }">
                  <el-tag type="danger" size="small">{{ row.conflict_type }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="description" label="Description" min-width="300" />
              <el-table-column label="Résolu" width="100" align="center">
                <template #default="{ row }">
                  <el-icon v-if="row.is_resolved" color="#67C23A"><CircleCheck /></el-icon>
                  <el-icon v-else color="#F56C6C"><CircleClose /></el-icon>
                </template>
              </el-table-column>
              <el-table-column label="Action" width="120">
                <template #default="{ row }">
                  <el-button v-if="!row.is_resolved" text type="primary" size="small" @click="resolveConflict(row)">
                    Résoudre
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="Tous les créneaux" name="slots">
        <el-card shadow="never">
          <el-table :data="allSlots" stripe style="width:100%">
            <el-table-column prop="week_reference" label="Semaine" width="110" />
            <el-table-column label="Jour / Heure" min-width="160">
              <template #default="{ row }">
                {{ row.time_slot_info?.day_name }} {{ row.time_slot_info?.start_time }}–{{ row.time_slot_info?.end_time }}
              </template>
            </el-table-column>
            <el-table-column label="Module" min-width="200">
              <template #default="{ row }">
                <strong>{{ row.course_info?.module_code }}</strong> {{ row.course_info?.module_name }}
              </template>
            </el-table-column>
            <el-table-column label="Professeur" min-width="160">
              <template #default="{ row }">{{ row.professor_info?.full_name }}</template>
            </el-table-column>
            <el-table-column label="Salle" width="100">
              <template #default="{ row }">{{ row.room_info?.code }}</template>
            </el-table-column>
            <el-table-column label="Type" width="110">
              <template #default="{ row }">
                <el-tag size="small">{{ row.slot_type }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Upload, Download, CircleCheck, CircleClose } from '@element-plus/icons-vue'
import { useStatusHelpers } from '@/reusables/mixins'
import axios from '@/plugins/axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import WeeklyCalendar from '@/components/schedule/WeeklyCalendar.vue'
import AnnualCalendar from '@/components/schedule/AnnualCalendar.vue'

const route = useRoute()
const router = useRouter()
const { scheduleStatusTag: schedTag } = useStatusHelpers()

const loading = ref(false)
const schedule = ref(null)
const conflicts = ref([])
const allSlots = ref([])
const activeTab = ref('weekly')
const scheduleId = computed(() => route.params.id)
const conflictCount = computed(() => conflicts.value.filter(c => !c.is_resolved).length)

async function load() {
  loading.value = true
  try {
    const [schedRes, detailRes] = await Promise.all([
      axios.get(`/scheduling/schedules/${scheduleId.value}/`),
      axios.get(`/scheduling/schedules/${scheduleId.value}/detail_view/`),
    ])
    schedule.value = schedRes.data
    conflicts.value = detailRes.data.conflicts || []
    allSlots.value = detailRes.data.slots || []
  } finally {
    loading.value = false
  }
}

async function publish() {
  await axios.post(`/scheduling/schedules/${scheduleId.value}/publish/`)
  ElMessage.success('Calendrier publié')
  load()
}

function exportIcal() {
  window.open(`/api/v1/scheduling/schedules/${scheduleId.value}/export_ical/`, '_blank')
}

async function resolveConflict(conflict) {
  const { value: notes } = await ElMessageBox.prompt('Notes de résolution (optionnel)', 'Résoudre le conflit', {
    confirmButtonText: 'Marquer comme résolu', cancelButtonText: 'Annuler', inputPlaceholder: 'Explication...'
  })
  await axios.post(`/scheduling/conflicts/${conflict.id}/resolve/`, { resolution_notes: notes || '' })
  ElMessage.success('Conflit résolu')
  load()
}

onMounted(load)
</script>

<style scoped>
.schedule-detail { max-width: 1400px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.header-left { display: flex; align-items: flex-start; gap: 12px; }
.header-left h2 { font-size: 22px; font-weight: 700; color: #1e2a3a; margin: 0; }
.header-meta { display: flex; align-items: center; gap: 10px; margin-top: 6px; font-size: 13px; color: #606266; }
.header-actions { display: flex; gap: 10px; }
.mt-3 { margin-top: 16px; }
.mb-3 { margin-bottom: 16px; }
.ml-1 { margin-left: 4px; }
</style>
