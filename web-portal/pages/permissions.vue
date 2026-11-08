<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
const roles = ref([
  { code: 'ADMIN', name: 'ผู้ดูแลระบบ', users: 1, permissions: ['abatement.read','abatement.create','abatement.update','abatement.delete','abatement.approve','role.manage','user.manage'] },
  { code: 'APPROVER', name: 'ผู้อนุมัติ', users: 1, permissions: ['abatement.read','abatement.approve'] },
  { code: 'USER', name: 'ผู้ใช้งานทั่วไป', users: 1, permissions: ['abatement.read','abatement.create','abatement.update'] }
])
const all = ['abatement.read','abatement.create','abatement.update','abatement.delete','abatement.approve','role.manage','user.manage']
const selected = ref(roles.value[0])
const saved = ref(false)
const save = () => { saved.value = true; setTimeout(() => saved.value = false, 2500) }
</script>
<template><AppShell><PermissionGate permission="role.manage">
  <div class="page-heading"><div><span class="eyebrow dark">ACCESS CONTROL</span><h1>ตั้งค่า Role และ Permission</h1><p>กำหนดขอบเขตการใช้งานให้แต่ละบทบาท</p></div><button class="button primary" @click="save"><Icon name="lucide:save" />บันทึกการเปลี่ยนแปลง</button></div>
  <div v-if="saved" class="alert warning"><Icon name="lucide:info" />บันทึกในหน้าจอตัวอย่างแล้ว — ต้องเพิ่ม Admin API เพื่อบันทึกลง Oracle</div>
  <div class="permission-layout"><section class="card role-list"><div class="card-head"><div><h3>บทบาททั้งหมด</h3><p>{{ roles.length }} บทบาทในระบบ</p></div><button class="icon-button"><Icon name="lucide:plus" /></button></div><button v-for="role in roles" :key="role.code" :class="{ active: selected.code === role.code }" @click="selected = role"><span class="role-icon"><Icon name="lucide:user-round-cog" /></span><div><strong>{{ role.name }}</strong><small>{{ role.code }} · {{ role.users }} ผู้ใช้</small></div><Icon name="lucide:chevron-right" /></button></section>
  <section class="card matrix"><div class="card-head"><div><h3>สิทธิ์ของ {{ selected.name }}</h3><p>เลือกสิทธิ์ที่บทบาทนี้สามารถดำเนินการได้</p></div><span class="role-code">{{ selected.code }}</span></div><div class="permission-table"><div class="table-head"><span>Permission</span><span>การเข้าถึง</span></div><label v-for="permission in all" :key="permission"><span><i :class="permission.split('.')[0]"><Icon :name="permission.startsWith('abatement') ? 'lucide:file-check' : permission.startsWith('role') ? 'lucide:shield' : 'lucide:users'" /></i><span><strong>{{ permission }}</strong><small>{{ permission.startsWith('abatement') ? 'Abatement workflow' : 'System administration' }}</small></span></span><input v-model="selected.permissions" type="checkbox" :value="permission"><em></em></label></div></section></div>
</PermissionGate></AppShell></template>
