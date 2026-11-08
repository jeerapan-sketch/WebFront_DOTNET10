<script setup lang="ts">
definePageMeta({ layout: false })
const auth = useAuth()
const username = ref('user01')
const password = ref('P@ssw0rd!')
const showPassword = ref(false)
const loading = ref(false)
const error = ref('')

onMounted(async () => { await auth.restore(); if (auth.session.value) await navigateTo('/') })
const submit = async () => {
  error.value = ''; loading.value = true
  try { await auth.login(username.value, password.value); await navigateTo('/') }
  catch (e: any) { error.value = e?.data?.message || 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง' }
  finally { loading.value = false }
}
</script>

<template>
  <div class="login-page">
    <section class="login-story">
      <div class="story-content">
        <div class="brand light"><span class="brand-mark"><Icon name="lucide:shield-check" /></span><span>AccessFlow<small>RBAC Portal</small></span></div>
        <div class="story-copy"><span class="eyebrow">SECURE · SIMPLE · AUDITABLE</span><h1>จัดการสิทธิ์อย่างมั่นใจ<br>ในทุกการเข้าถึง</h1><p>ระบบบริหาร JWT, Role และ Permission ที่ออกแบบให้ทีมทำงานต่อได้อย่างปลอดภัยและตรวจสอบย้อนหลังได้</p></div>
        <div class="security-points"><span><Icon name="lucide:key-round" /> JWT Authentication</span><span><Icon name="lucide:users-round" /> Role-based access</span><span><Icon name="lucide:history" /> Session control</span></div>
      </div>
    </section>
    <section class="login-panel">
      <form class="login-card" @submit.prevent="submit">
        <div><span class="eyebrow dark">ยินดีต้อนรับ</span><h2>เข้าสู่ระบบ</h2><p>ใช้บัญชีที่ได้รับอนุญาตเพื่อดำเนินการต่อ</p></div>
        <div v-if="error" class="alert error"><Icon name="lucide:circle-alert" />{{ error }}</div>
        <label>ชื่อผู้ใช้<div class="input-wrap"><Icon name="lucide:user" /><input v-model="username" autocomplete="username" required placeholder="กรอกชื่อผู้ใช้"></div></label>
        <label>รหัสผ่าน<div class="input-wrap"><Icon name="lucide:lock-keyhole" /><input v-model="password" :type="showPassword ? 'text' : 'password'" autocomplete="current-password" required placeholder="กรอกรหัสผ่าน"><button type="button" @click="showPassword = !showPassword"><Icon :name="showPassword ? 'lucide:eye-off' : 'lucide:eye'" /></button></div></label>
        <button class="button primary full" :disabled="loading"><Icon v-if="loading" name="lucide:loader-circle" class="spin" />{{ loading ? 'กำลังตรวจสอบ...' : 'เข้าสู่ระบบ' }}<Icon v-if="!loading" name="lucide:arrow-right" /></button>
        <p class="login-foot"><Icon name="lucide:lock" /> การเชื่อมต่อได้รับการปกป้องด้วย JWT</p>
      </form>
    </section>
  </div>
</template>
