<script setup lang="ts">
import { canManageSessions } from '~/utils/permissions'

const route = useRoute()
const auth = useAuth()
const open = ref(false)
let heartbeatTimer: ReturnType<typeof setInterval> | undefined

const sendHeartbeat = () => {
  if (auth.session.value) void auth.heartbeat().catch(() => undefined)
}

onMounted(() => {
  sendHeartbeat()
  heartbeatTimer = setInterval(sendHeartbeat, 60_000)
  document.addEventListener('visibilitychange', sendHeartbeat)
})

onBeforeUnmount(() => {
  if (heartbeatTimer) clearInterval(heartbeatTimer)
  document.removeEventListener('visibilitychange', sendHeartbeat)
})

const links = computed(() => [
  { to: '/', icon: 'lucide:layout-dashboard', label: 'ภาพรวม', show: true },
  { to: '/reports/chb1', icon: 'lucide:file-spreadsheet', label: 'รายงาน CHB1', show: auth.hasPermission('chb1.read') },
  { to: '/unit-measurements', icon: 'lucide:ruler', label: 'Unit Measurement Information', show: auth.hasPermission('unit-measurement.read') },
  { to: '/unit-measurements-ddd', icon: 'lucide:ruler', label: 'Unit Measurement DDD', show: auth.hasPermission('unit-measurement.read') },
  { to: '/unit-measurements-fdd', icon: 'lucide:ruler', label: 'Unit Measurement FDD', show: auth.hasPermission('unit-measurement.read') },
  { to: '/abatement', icon: 'lucide:file-check-2', label: 'งาน Abatement', show: auth.hasPermission('abatement.read') },
  { to: '/excel-import', icon: 'lucide:file-spreadsheet', label: 'นำเข้า Excel', show: auth.hasPermission('abatement.create') },
  { to: '/permissions', icon: 'lucide:shield-check', label: 'ตั้งค่าสิทธิ์', show: auth.hasPermission('role.manage') },
  { to: '/users', icon: 'lucide:users', label: 'ผู้ใช้งาน', show: auth.hasPermission('user.manage') },
  { to: '/sessions', icon: 'lucide:monitor-smartphone', label: 'ตรวจสอบเซสชัน', show: canManageSessions(auth.session.value?.permissions) }
].filter(x => x.show))

const signOut = async () => { await auth.logout(); await navigateTo('/login') }
</script>

<template>
  <div class="app-frame">
    <aside class="sidebar" :class="{ open }">
      <div class="brand"><span class="brand-mark"><Icon name="lucide:shield-check" /></span><span>AccessFlow<small>RBAC Portal</small></span></div>
      <nav>
        <p class="nav-label">เมนูหลัก</p>
        <NuxtLink v-for="link in links" :key="link.to" :to="link.to" :class="{ active: route.path === link.to }" @click="open = false">
          <Icon :name="link.icon" /><span>{{ link.label }}</span>
        </NuxtLink>
      </nav>
      <div class="sidebar-user">
        <div class="avatar">{{ auth.session.value?.username?.slice(0, 2).toUpperCase() }}</div>
        <div><strong>{{ auth.session.value?.username }}</strong><small>{{ auth.session.value?.roles?.join(', ') }}</small></div>
        <button class="icon-button" title="ออกจากระบบ" @click="signOut"><Icon name="lucide:log-out" /></button>
      </div>
    </aside>
    <main class="main">
      <header class="topbar">
        <button class="icon-button menu-button" @click="open = !open"><Icon name="lucide:menu" /></button>
        <div class="environment"><span></span> API connected · Secure BFF</div>
        <div class="top-actions"><button class="icon-button"><Icon name="lucide:bell" /></button><div class="avatar small">{{ auth.session.value?.username?.slice(0, 2).toUpperCase() }}</div></div>
      </header>
      <div class="page"><slot /></div>
    </main>
  </div>
</template>
