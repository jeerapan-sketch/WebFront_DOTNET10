<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
const users = [
  { id: 1, username: 'admin', name: 'System Administrator', email: 'admin@example.local', role: 'ADMIN', active: true },
  { id: 2, username: 'approver01', name: 'Test Approver', email: 'approver01@example.local', role: 'APPROVER', active: true },
  { id: 3, username: 'user01', name: 'Test User', email: 'user01@example.local', role: 'USER', active: true }
]
</script>
<template><AppShell><PermissionGate permission="user.manage"><div class="page-heading"><div><span class="eyebrow dark">USER DIRECTORY</span><h1>ผู้ใช้งาน</h1><p>จัดการบัญชี บทบาท และสถานะการเข้าใช้งาน</p></div><button class="button primary"><Icon name="lucide:user-plus" />เพิ่มผู้ใช้งาน</button></div><section class="card data-card"><div class="toolbar"><div class="search"><Icon name="lucide:search" /><input placeholder="ค้นหาชื่อหรืออีเมล"></div><button class="button secondary"><Icon name="lucide:list-filter" />ตัวกรอง</button></div><div class="data-table"><div class="data-row head"><span>ผู้ใช้งาน</span><span>บทบาท</span><span>สถานะ</span><span></span></div><div v-for="user in users" :key="user.id" class="data-row"><span class="user-cell"><span class="avatar">{{ user.username.slice(0,2).toUpperCase() }}</span><span><strong>{{ user.name }}</strong><small>{{ user.username }} · {{ user.email }}</small></span></span><span><b class="role-code">{{ user.role }}</b></span><span><b class="active-badge"><i></i>ใช้งาน</b></span><span><button class="icon-button"><Icon name="lucide:ellipsis" /></button></span></div></div></section></PermissionGate></AppShell></template>
