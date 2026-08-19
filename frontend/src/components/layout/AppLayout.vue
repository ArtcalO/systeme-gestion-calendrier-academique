<template>
  <el-container class="app-layout">
    <!-- Sidebar -->
    <el-aside :width="collapsed ? '64px' : '250px'" class="sidebar">
      <div class="sidebar-header">
        <el-icon v-if="collapsed" :size="28" color="#409EFF"><School /></el-icon>
        <template v-else>
          <el-icon :size="22" color="#409EFF"><School /></el-icon>
          <span class="logo-text">SGCA-ULT</span>
        </template>
      </div>

      <el-menu
        :default-active="$route.path"
        router
        :collapse="collapsed"
        background-color="#1e2a3a"
        text-color="#c0cfe0"
        active-text-color="#409EFF"
        class="sidebar-menu"
        :unique-opened="true"
      >
        <!-- Dashboard -->
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <template #title>Tableau de bord</template>
        </el-menu-item>

        <!-- Structure académique -->
        <el-sub-menu index="structure">
          <template #title>
            <el-icon><School /></el-icon>
            <span>Structure académique</span>
          </template>
          <el-menu-item index="/faculties">
            <el-icon><OfficeBuilding /></el-icon>
            <template #title>Facultés</template>
          </el-menu-item>
          <el-menu-item index="/departments">
            <el-icon><Grid /></el-icon>
            <template #title>Départements</template>
          </el-menu-item>
          <el-menu-item index="/programs">
            <el-icon><Notebook /></el-icon>
            <template #title>Programmes</template>
          </el-menu-item>
          <el-menu-item index="/levels">
            <el-icon><DataLine /></el-icon>
            <template #title>Niveaux</template>
          </el-menu-item>
          <el-menu-item index="/subjects">
            <el-icon><Memo /></el-icon>
            <template #title>Matières / Domaines</template>
          </el-menu-item>
        </el-sub-menu>

        <!-- Cours & Modules -->
        <el-sub-menu index="courses-modules">
          <template #title>
            <el-icon><Collection /></el-icon>
            <span>Cours &amp; Modules</span>
          </template>
          <el-menu-item index="/academic-years">
            <el-icon><Calendar /></el-icon>
            <template #title>Années académiques</template>
          </el-menu-item>
          <el-menu-item index="/modules">
            <el-icon><Reading /></el-icon>
            <template #title>Modules</template>
          </el-menu-item>
          <el-menu-item index="/courses">
            <el-icon><EditPen /></el-icon>
            <template #title>Planification cours</template>
          </el-menu-item>
          <el-menu-item index="/prerequisites">
            <el-icon><Share /></el-icon>
            <template #title>Prérequis</template>
          </el-menu-item>
        </el-sub-menu>

        <!-- Attributions -->
        <el-sub-menu index="assignments-group">
          <template #title>
            <el-icon><Connection /></el-icon>
            <span>Attributions</span>
          </template>
          <el-menu-item index="/assignments">
            <el-icon><List /></el-icon>
            <template #title>Attributions de cours</template>
          </el-menu-item>
          <el-menu-item index="/teaching-load">
            <el-icon><TrendCharts /></el-icon>
            <template #title>Charge d'enseignement</template>
          </el-menu-item>
          <el-menu-item index="/algorithm-runs">
            <el-icon><Timer /></el-icon>
            <template #title>Historique algorithme</template>
          </el-menu-item>
        </el-sub-menu>

        <!-- Emplois du temps -->
        <el-sub-menu index="schedules-group">
          <template #title>
            <el-icon><AlarmClock /></el-icon>
            <span>Emplois du temps</span>
          </template>
          <el-menu-item index="/schedules">
            <el-icon><Grid /></el-icon>
            <template #title>Calendriers</template>
          </el-menu-item>
          <el-menu-item index="/time-slots">
            <el-icon><Clock /></el-icon>
            <template #title>Créneaux horaires</template>
          </el-menu-item>
        </el-sub-menu>

        <!-- Ressources humaines -->
        <el-sub-menu index="resources-group">
          <template #title>
            <el-icon><UserFilled /></el-icon>
            <span>Ressources humaines</span>
          </template>
          <el-menu-item index="/professors">
            <el-icon><Avatar /></el-icon>
            <template #title>Professeurs</template>
          </el-menu-item>
          <el-menu-item index="/students">
            <el-icon><User /></el-icon>
            <template #title>Étudiants</template>
          </el-menu-item>
        </el-sub-menu>

        <!-- Ressources physiques -->
        <el-menu-item index="/rooms">
          <el-icon><House /></el-icon>
          <template #title>Salles</template>
        </el-menu-item>

      </el-menu>
    </el-aside>

    <!-- Main -->
    <el-container>
      <el-header class="app-header">
        <div class="header-left">
          <el-button text @click="collapsed = !collapsed" :icon="collapsed ? 'Expand' : 'Fold'" />
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">Accueil</el-breadcrumb-item>
            <el-breadcrumb-item v-if="pageTitle">{{ pageTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-tag v-if="currentYear" type="success" size="small" class="mr-2">
            {{ currentYear }}
          </el-tag>
          <el-dropdown @command="handleCommand">
            <div class="user-info">
              <el-avatar :size="32" :icon="UserFilled" />
              <span class="user-name">{{ auth.user?.first_name || auth.user?.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">
                  <el-icon><SwitchButton /></el-icon> Déconnexion
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="app-main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import axios from '@/plugins/axios'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const collapsed = ref(false)
const currentYear = ref('')

const pageTitles = {
  '/dashboard': 'Tableau de bord',
  '/faculties': 'Facultés',
  '/departments': 'Départements',
  '/programs': 'Programmes',
  '/levels': 'Niveaux',
  '/subjects': 'Matières / Domaines',
  '/academic-years': 'Années académiques',
  '/modules': 'Modules',
  '/courses': 'Planification des cours',
  '/prerequisites': 'Prérequis',
  '/assignments': 'Attributions de cours',
  '/teaching-load': "Charge d'enseignement",
  '/algorithm-runs': 'Historique algorithme',
  '/schedules': 'Calendriers',
  '/time-slots': 'Créneaux horaires',
  '/professors': 'Professeurs',
  '/students': 'Étudiants',
  '/rooms': 'Salles',
}

const pageTitle = computed(() => pageTitles[route.path] || route.meta?.title || '')

onMounted(async () => {
  try {
    const res = await axios.get('/academic/academic-years/', { params: { is_current: true } })
    const yr = res.data.results?.[0] || res.data?.[0]
    if (yr) currentYear.value = yr.name
  } catch {}
})

function handleCommand(cmd) {
  if (cmd === 'logout') {
    auth.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.app-layout { height: 100vh; }

.sidebar {
  background: #1e2a3a;
  transition: width 0.3s;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 0 16px;
  border-bottom: 1px solid #2d3e50;
  flex-shrink: 0;
}

.logo-text {
  color: #fff;
  font-weight: 700;
  font-size: 16px;
  letter-spacing: 1px;
}

.sidebar-menu {
  flex: 1;
  border-right: none;
  overflow-y: auto;
  overflow-x: hidden;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 250px;
}

/* Sub-menu dark styling */
:deep(.el-sub-menu__title) {
  color: #c0cfe0 !important;
  font-size: 13px;
}
:deep(.el-sub-menu__title:hover),
:deep(.el-sub-menu__title:focus) {
  background-color: #253447 !important;
}
:deep(.el-menu--inline) {
  background-color: #172232 !important;
}
:deep(.el-menu--inline .el-menu-item) {
  background-color: #172232 !important;
  padding-left: 44px !important;
  font-size: 13px;
}
:deep(.el-menu--inline .el-menu-item:hover) {
  background-color: #1e2d3d !important;
}
:deep(.el-menu-item-group__title) {
  padding: 10px 20px 4px !important;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: #3a566e !important;
}

.app-header {
  height: 60px;
  background: #fff;
  border-bottom: 1px solid #e8ecef;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0,0,0,.06);
  flex-shrink: 0;
}

.header-left { display: flex; align-items: center; gap: 12px; }
.header-right { display: flex; align-items: center; gap: 12px; }

.user-info {
  display: flex; align-items: center; gap: 8px;
  cursor: pointer; padding: 4px 8px; border-radius: 6px;
}
.user-info:hover { background: #f5f7fa; }
.user-name { font-size: 14px; color: #303133; }

.app-main {
  background: #f4f6f9;
  padding: 24px;
  overflow-y: auto;
}

.mr-2 { margin-right: 8px; }

.fade-enter-active, .fade-leave-active { transition: opacity .15s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
