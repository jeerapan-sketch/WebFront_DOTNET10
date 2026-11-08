<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
const auth = useAuth()
const stats = computed(() => [
  { icon: 'lucide:shield-check', label: 'สิทธิ์ที่ได้รับ', value: auth.session.value?.permissions?.length || 0, tone: 'blue' },
  { icon: 'lucide:badge-check', label: 'บทบาทของคุณ', value: auth.session.value?.roles?.length || 0, tone: 'green' },
  { icon: 'lucide:clock-3', label: 'Token หมดอายุ', value: auth.session.value?.expiresAtUtc ? new Date(auth.session.value.expiresAtUtc).toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' }) : '-', tone: 'orange' }
])
</script>
<template><AppShell>
  <div class="page-heading"><div><span class="eyebrow dark">OVERVIEW</span><h1>สวัสดี, {{ auth.session.value?.username }}</h1><p>ภาพรวมการเข้าถึงและสิทธิ์ของคุณในระบบ</p></div><span class="status-pill"><i></i> เซสชันกำลังทำงาน</span></div>
  <div class="stat-grid"><article v-for="stat in stats" :key="stat.label" class="stat-card"><span :class="['stat-icon', stat.tone]"><Icon :name="stat.icon" /></span><div><p>{{ stat.label }}</p><strong>{{ stat.value }}</strong></div></article></div>
  <div class="content-grid">
    <section class="card"><div class="card-head"><div><h3>สิทธิ์ของฉัน</h3><p>สิทธิ์ที่แนบมากับ Access Token ปัจจุบัน</p></div><span class="count">{{ auth.session.value?.permissions?.length || 0 }} รายการ</span></div><div class="permission-list"><span v-for="permission in auth.session.value?.permissions" :key="permission"><Icon name="lucide:check" />{{ permission }}</span></div></section>
    <section class="card quick"><div class="card-head"><div><h3>เมนูด่วน</h3><p>ไปยังงานที่ใช้งานบ่อย</p></div></div><NuxtLink v-if="auth.hasPermission('abatement.read')" to="/abatement"><span><Icon name="lucide:file-search" /></span><div><strong>งาน Abatement</strong><small>ค้นหาและจัดการข้อมูล</small></div><Icon name="lucide:chevron-right" /></NuxtLink><NuxtLink v-if="auth.hasPermission('role.manage')" to="/permissions"><span><Icon name="lucide:shield-cog" /></span><div><strong>ตั้งค่าสิทธิ์</strong><small>กำหนดสิทธิ์ให้แต่ละ Role</small></div><Icon name="lucide:chevron-right" /></NuxtLink></section>
  </div>
</AppShell></template>
