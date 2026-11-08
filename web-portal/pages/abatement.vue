<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
const auth = useAuth()
const loading = ref(false), result = ref<any>(null), error = ref('')
const actions = [
  { permission: 'abatement.read', method: 'GET', path: '/api/permission-test/abatement/read', label: 'อ่านข้อมูล', icon: 'lucide:book-open' },
  { permission: 'abatement.create', method: 'POST', path: '/api/permission-test/abatement/create', label: 'สร้างรายการ', icon: 'lucide:plus' },
  { permission: 'abatement.update', method: 'PUT', path: '/api/permission-test/abatement/update', label: 'แก้ไขรายการ', icon: 'lucide:pencil' },
  { permission: 'abatement.approve', method: 'POST', path: '/api/permission-test/abatement/approve', label: 'อนุมัติรายการ', icon: 'lucide:badge-check' },
  { permission: 'abatement.delete', method: 'DELETE', path: '/api/permission-test/abatement/delete', label: 'ลบรายการ', icon: 'lucide:trash-2' }
]
const invoke = async (action: typeof actions[number]) => {
  loading.value = true; error.value = ''; result.value = null
  try { result.value = await auth.request(action.path, { method: action.method }) }
  catch (e: any) { error.value = `${e?.status || ''} ${e?.data?.message || e?.message || 'เรียก API ไม่สำเร็จ'}` }
  finally { loading.value = false }
}
</script>
<template><AppShell><div class="page-heading"><div><span class="eyebrow dark">OPERATIONS</span><h1>งาน Abatement</h1><p>ทดสอบการอนุญาตใช้งาน API ตามสิทธิ์ใน JWT</p></div></div>
  <section class="card"><div class="action-grid"><button v-for="action in actions" :key="action.permission" class="action-card" :disabled="!auth.hasPermission(action.permission) || loading" @click="invoke(action)"><span><Icon :name="action.icon" /></span><strong>{{ action.label }}</strong><small>{{ action.permission }}</small><em :class="auth.hasPermission(action.permission) ? 'allowed' : 'denied'"><Icon :name="auth.hasPermission(action.permission) ? 'lucide:check' : 'lucide:lock'" />{{ auth.hasPermission(action.permission) ? 'อนุญาต' : 'ไม่มีสิทธิ์' }}</em></button></div></section>
  <section v-if="result || error" class="card response"><div class="card-head"><h3>ผลการเรียก API</h3><span :class="['status-pill', error && 'danger']"><i></i>{{ error ? 'ไม่สำเร็จ' : 'สำเร็จ' }}</span></div><pre>{{ error || JSON.stringify(result, null, 2) }}</pre></section>
</AppShell></template>
