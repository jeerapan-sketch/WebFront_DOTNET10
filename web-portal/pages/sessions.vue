<script setup lang="ts">
import type { ActiveSession } from '~/types/auth'

definePageMeta({ middleware: ['auth', 'user-manage'] })
const auth = useAuth()
const sessions = ref<ActiveSession[]>([])
const loading = ref(true), refreshing = ref(false), revokingId = ref(''), error = ref('')
const now = ref(Date.now())
let clock: ReturnType<typeof setInterval> | undefined

const currentSessionId = computed(() => auth.session.value?.sessionId || '')
const isExpired = (value?: string) => !value || Date.parse(value) <= now.value
const activeCount = computed(() => sessions.value.filter(item => !isExpired(item.expiresAtUtc)).length)
const dateTime = (value?: string) => value ? new Date(value).toLocaleString('th-TH', { dateStyle: 'medium', timeStyle: 'medium' }) : '-'
const shortId = (value: string) => `${value.slice(0, 10)}…${value.slice(-8)}`
const remaining = (value?: string) => {
  if (!value) return '-'
  const seconds = Math.max(0, Math.floor((Date.parse(value) - now.value) / 1000))
  if (!seconds) return 'หมดอายุแล้ว'
  const days = Math.floor(seconds / 86400), hours = Math.floor(seconds % 86400 / 3600)
  const minutes = Math.floor(seconds % 3600 / 60), secs = seconds % 60
  if (days) return `${days} วัน ${hours} ชม.`
  if (hours) return `${hours} ชม. ${minutes} นาที`
  return `${minutes}:${String(secs).padStart(2, '0')} นาที`
}

const loadSessions = async (manual = false) => {
  if (manual) refreshing.value = true
  error.value = ''
  try { sessions.value = await auth.request<ActiveSession[]>('/api/auth/sessions') }
  catch (cause: any) { error.value = cause?.data?.message || cause?.message || 'ไม่สามารถโหลดข้อมูลเซสชันได้' }
  finally { loading.value = false; refreshing.value = false }
}

const revoke = async (item: ActiveSession) => {
  const current = item.sessionId === currentSessionId.value
  const prompt = current ? 'เพิกถอนเซสชันปัจจุบันและออกจากระบบทันทีหรือไม่?' : `เพิกถอนเซสชันของ ${item.username || item.deviceName || 'ผู้ใช้นี้'} หรือไม่?`
  if (!window.confirm(prompt)) return
  revokingId.value = item.sessionId
  error.value = ''
  try {
    await auth.request(`/api/auth/users/${item.userId}/sessions/${encodeURIComponent(item.sessionId)}`, { method: 'DELETE' })
    sessions.value = sessions.value.filter(session => session.sessionId !== item.sessionId)
    if (current) await auth.logout()
  } catch (cause: any) { error.value = cause?.data?.message || cause?.message || 'ไม่สามารถเพิกถอนเซสชันได้' }
  finally { revokingId.value = '' }
}

onMounted(async () => { clock = setInterval(() => { now.value = Date.now() }, 1000); await loadSessions() })
onBeforeUnmount(() => { if (clock) clearInterval(clock) })
</script>

<template>
  <AppShell>
    <div class="page-heading session-heading">
      <div><span class="eyebrow dark">SECURITY · SESSION CONTROL</span><h1>ตรวจสอบเซสชัน</h1><p>ติดตามสถานะ token, refresh session และเพิกถอนอุปกรณ์ที่ไม่รู้จัก</p></div>
      <button class="button secondary" :disabled="refreshing" @click="loadSessions(true)"><Icon name="lucide:refresh-cw" :class="{ spin: refreshing }" />ตรวจสอบอีกครั้ง</button>
    </div>

    <div class="session-summary">
      <article class="summary-card"><span><Icon name="lucide:monitor-smartphone" /></span><div><small>เซสชันที่กำลังใช้งาน</small><strong>{{ activeCount }}</strong></div></article>
      <article class="summary-card"><span class="blue"><Icon name="lucide:key-round" /></span><div><small>Access token ปัจจุบัน</small><strong>{{ remaining(auth.session.value?.expiresAtUtc) }}</strong></div></article>
      <article class="summary-card"><span class="orange"><Icon name="lucide:rotate-cw" /></span><div><small>Refresh session ปัจจุบัน</small><strong>{{ remaining(auth.session.value?.refreshExpiresAtUtc) }}</strong></div></article>
    </div>
    <div v-if="error" class="alert error session-alert">{{ error }}</div>

    <section class="card token-overview">
      <div class="section-title"><div><span class="eyebrow dark">CURRENT CREDENTIAL</span><h2>สถานะ Token ปัจจุบัน</h2></div><span class="status-pill" :class="{ expired: isExpired(auth.session.value?.expiresAtUtc) }"><i />{{ isExpired(auth.session.value?.expiresAtUtc) ? 'หมดอายุ' : 'ใช้งานได้' }}</span></div>
      <div class="token-grid">
        <div><small>Access token หมดอายุ</small><strong>{{ dateTime(auth.session.value?.expiresAtUtc) }}</strong><em>เหลือ {{ remaining(auth.session.value?.expiresAtUtc) }}</em></div>
        <div><small>Refresh token หมดอายุ</small><strong>{{ dateTime(auth.session.value?.refreshExpiresAtUtc) }}</strong><em>เหลือ {{ remaining(auth.session.value?.refreshExpiresAtUtc) }}</em></div>
        <div><small>Session ID</small><strong class="mono">{{ currentSessionId ? shortId(currentSessionId) : '-' }}</strong><em>Token จริงถูกป้องกันไว้ใน Redis</em></div>
      </div>
    </section>

    <section class="card session-section">
      <div class="section-title"><div><span class="eyebrow dark">ACTIVE DEVICES</span><h2>อุปกรณ์และเซสชัน</h2></div><span class="result-count">{{ sessions.length }} รายการ</span></div>
      <div v-if="loading" class="empty-state"><Icon name="lucide:loader-circle" class="spin" /><span>กำลังตรวจสอบเซสชัน...</span></div>
      <div v-else-if="!sessions.length" class="empty-state"><Icon name="lucide:monitor-off" /><strong>ไม่พบเซสชันที่ใช้งาน</strong></div>
      <div v-else class="session-table-wrap">
        <table class="session-table">
          <caption class="visually-hidden">รายการเซสชัน อุปกรณ์ วันหมดอายุ และการเพิกถอนการเข้าใช้งาน</caption>
          <thead><tr><th>ผู้ใช้งาน</th><th>อุปกรณ์</th><th>Session</th><th>ใช้งานล่าสุด</th><th>หมดอายุ</th><th>สถานะ</th><th /></tr></thead>
          <tbody><tr v-for="item in sessions" :key="item.sessionId" :class="{ current: item.sessionId === currentSessionId }">
            <td><div class="user-session"><span>{{ item.username?.slice(0, 2).toUpperCase() }}</span><div><strong>{{ item.username || 'Unknown user' }}</strong><small>User ID: {{ item.userId }}</small></div></div></td>
            <td><div class="device-cell"><span><Icon name="lucide:monitor" /></span><div><strong>{{ item.deviceName || 'Unknown device' }}</strong><small>{{ item.ipAddress || 'ไม่พบ IP' }}</small></div></div></td>
            <td><code>{{ shortId(item.sessionId) }}</code><small class="subline">Access token ตรวจสอบโดย server</small></td>
            <td><strong>{{ dateTime(item.lastActivityAtUtc) }}</strong><small class="subline">เริ่ม {{ dateTime(item.createdAtUtc) }}</small></td>
            <td><strong>{{ remaining(item.expiresAtUtc) }}</strong><small class="subline">{{ dateTime(item.expiresAtUtc) }}</small></td>
            <td><span class="status-pill compact" :class="{ expired: isExpired(item.expiresAtUtc) }"><i />{{ isExpired(item.expiresAtUtc) ? 'หมดอายุ' : item.sessionId === currentSessionId ? 'เครื่องนี้' : 'ใช้งานอยู่' }}</span></td>
            <td><button class="button danger revoke-button" :disabled="revokingId === item.sessionId" @click="revoke(item)"><Icon :name="revokingId === item.sessionId ? 'lucide:loader-circle' : 'lucide:log-out'" :class="{ spin: revokingId === item.sessionId }" />เพิกถอน</button></td>
          </tr></tbody>
        </table>
      </div>
    </section>
  </AppShell>
</template>

<style scoped>
.session-heading{align-items:flex-end}.session-summary{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px;margin:24px 0}.summary-card{background:#fff;border:1px solid #e2e8f0;border-radius:18px;padding:20px;display:flex;align-items:center;gap:16px;box-shadow:0 8px 24px rgba(15,23,42,.04)}.summary-card>span{width:46px;height:46px;border-radius:14px;background:#e8f8f0;color:#079669;display:grid;place-items:center;font-size:22px}.summary-card>span.blue{background:#eaf3ff;color:#1684e8}.summary-card>span.orange{background:#fff2e5;color:#e98019}.summary-card div{display:grid;gap:4px}.summary-card small,.token-grid small,.subline{color:#718096}.summary-card strong{font-size:22px;color:#142238}.session-alert{margin-bottom:18px}.token-overview,.session-section{margin-top:18px}.section-title{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:20px}.section-title h2{margin:4px 0 0;font-size:20px}.status-pill{display:inline-flex;align-items:center;gap:7px;color:#087f5b;background:#e8f8f0;border-radius:999px;padding:8px 12px;font-size:13px;font-weight:700;white-space:nowrap}.status-pill i{width:7px;height:7px;border-radius:50%;background:#12b981}.status-pill.expired{color:#c2413b;background:#fff0ef}.status-pill.expired i{background:#ef4444}.status-pill.compact{padding:6px 10px;font-size:12px}.token-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.token-grid>div{background:#f8fafc;border:1px solid #edf1f5;border-radius:14px;padding:16px;display:grid;gap:7px}.token-grid strong{color:#17263c}.token-grid em{font-size:12px;color:#718096;font-style:normal}.mono,code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}.result-count{color:#64748b;font-size:13px}.session-table-wrap{overflow-x:auto}.session-table{width:100%;border-collapse:collapse;min-width:1120px}.session-table th{text-align:left;color:#718096;font-size:12px;font-weight:600;padding:12px;border-bottom:1px solid #e8edf3}.session-table td{padding:15px 12px;border-bottom:1px solid #edf1f5;vertical-align:middle;font-size:13px}.session-table tr.current{background:#f7fbff}.user-session,.device-cell{display:flex;align-items:center;gap:11px}.user-session>span{width:38px;height:38px;border-radius:11px;background:#edf1fb;color:#5269a1;display:grid;place-items:center;font-weight:700}.user-session div{display:grid;gap:3px}.user-session small{font-size:11px;color:#718096}.device-cell>span{width:38px;height:38px;border-radius:11px;background:#eaf3ff;color:#1684e8;display:grid;place-items:center}.device-cell div{display:grid;gap:3px}.device-cell small,.subline{display:block;font-size:11px;margin-top:5px}.session-table code{font-size:12px;background:#f1f5f9;padding:5px 7px;border-radius:6px}.revoke-button{padding:8px 10px;font-size:12px}.button:disabled{opacity:.55;cursor:not-allowed}@media(max-width:900px){.session-summary,.token-grid{grid-template-columns:1fr}.session-heading{align-items:flex-start;gap:16px}}
</style>
