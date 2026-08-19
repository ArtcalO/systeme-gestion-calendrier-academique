import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import 'dayjs/locale/fr'
import axios from '@/plugins/axios'

dayjs.locale('fr')

// ─── API helpers ─────────────────────────────────────────────────────────────
export function useApi() {
  async function fetchList(url, params = {}) {
    const res = await axios.get(url, { params })
    return res.data
  }

  async function fetchOne(url, id) {
    const res = await axios.get(`${url}${id}/`)
    return res.data
  }

  async function create(url, data) {
    const res = await axios.post(url, data)
    ElMessage.success('Créé avec succès')
    return res.data
  }

  async function update(url, id, data) {
    const res = await axios.patch(`${url}${id}/`, data)
    ElMessage.success('Modifié avec succès')
    return res.data
  }

  async function remove(url, id, label = 'Élément') {
    await ElMessageBox.confirm(
      `Supprimer définitivement cet élément ?`,
      'Confirmation',
      { confirmButtonText: 'Supprimer', cancelButtonText: 'Annuler', type: 'warning' }
    )
    await axios.delete(`${url}${id}/`)
    ElMessage.success(`${label} supprimé`)
    return true
  }

  return { fetchList, fetchOne, create, update, remove }
}

// ─── Date / week helpers ──────────────────────────────────────────────────────
export function useDateHelpers() {
  function formatDate(d) {
    return d ? dayjs(d).format('DD/MM/YYYY') : '—'
  }

  function formatDateTime(d) {
    return d ? dayjs(d).format('DD/MM/YYYY HH:mm') : '—'
  }

  function getISOWeek(date) {
    return dayjs(date).format('YYYY-[W]WW')
  }

  function getWeekRange(isoWeek) {
    const [year, week] = isoWeek.split('-W')
    const mon = dayjs().year(Number(year)).isoWeek(Number(week)).startOf('isoWeek')
    return {
      start: mon.format('DD/MM/YYYY'),
      end: mon.add(5, 'day').format('DD/MM/YYYY'),
    }
  }

  function weeksInRange(startDate, endDate) {
    const weeks = []
    let cur = dayjs(startDate).startOf('isoWeek')
    const end = dayjs(endDate)
    while (cur.isBefore(end) || cur.isSame(end, 'week')) {
      weeks.push(cur.format('YYYY-[W]WW'))
      cur = cur.add(1, 'week')
    }
    return weeks
  }

  return { formatDate, formatDateTime, getISOWeek, getWeekRange, weeksInRange }
}

// ─── Status / label helpers ───────────────────────────────────────────────────
export function useStatusHelpers() {
  const courseStatusMap = {
    draft: { label: 'Brouillon', type: 'info' },
    scheduled: { label: 'Planifié', type: 'success' },
    ongoing: { label: 'En cours', type: 'warning' },
    completed: { label: 'Terminé', type: '' },
    cancelled: { label: 'Annulé', type: 'danger' },
  }

  const scheduleStatusMap = {
    draft: { label: 'Brouillon', type: 'info' },
    published: { label: 'Publié', type: 'success' },
    archived: { label: 'Archivé', type: '' },
  }

  const slotTypeMap = {
    regular: { label: 'Régulier', color: '#409EFF' },
    makeup: { label: 'Rattrapage', color: '#E6A23C' },
    exam: { label: 'Examen', color: '#F56C6C' },
    midterm: { label: 'Partiel', color: '#9B59B6' },
  }

  const prereqTypeMap = {
    strict: { label: 'Strict (avant)', type: 'danger', icon: 'Lock' },
    coreq: { label: 'Coréquisit (parallèle)', type: 'warning', icon: 'Connection' },
    recommended: { label: 'Recommandé', type: 'info', icon: 'InfoFilled' },
  }

  const dayNames = ['', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']

  function courseStatusTag(s) { return courseStatusMap[s] || { label: s, type: '' } }
  function scheduleStatusTag(s) { return scheduleStatusMap[s] || { label: s, type: '' } }
  function slotTypeTag(t) { return slotTypeMap[t] || { label: t, color: '#909399' } }
  function prereqTypeTag(t) { return prereqTypeMap[t] || { label: t, type: '' } }
  function dayName(n) { return dayNames[n] || '?' }

  return { courseStatusTag, scheduleStatusTag, slotTypeTag, prereqTypeTag, dayName }
}

// ─── Print helper ─────────────────────────────────────────────────────────────
export function usePrint() {
  function printElement(elementId, title = '') {
    const el = document.getElementById(elementId)
    if (!el) return
    const w = window.open('', '_blank')
    w.document.write(`
      <html><head>
        <title>${title}</title>
        <style>
          body { font-family: Arial, sans-serif; font-size: 12px; }
          table { width: 100%; border-collapse: collapse; }
          th, td { border: 1px solid #ddd; padding: 6px 8px; text-align: left; }
          th { background: #f0f0f0; font-weight: bold; }
          .no-print { display: none !important; }
          @page { margin: 1cm; }
        </style>
      </head><body>
        <h2>${title}</h2>
        ${el.innerHTML}
      </body></html>
    `)
    w.document.close()
    w.print()
  }

  return { printElement }
}

// ─── Pagination helper ────────────────────────────────────────────────────────
export function usePagination(defaultPageSize = 20) {
  const pagination = {
    page: 1,
    pageSize: defaultPageSize,
    total: 0,
  }

  function buildParams(extra = {}) {
    return { page: pagination.page, page_size: pagination.pageSize, ...extra }
  }

  function handleResponse(data) {
    pagination.total = data.count || data.results?.length || 0
    return data.results || data
  }

  return { pagination, buildParams, handleResponse }
}
