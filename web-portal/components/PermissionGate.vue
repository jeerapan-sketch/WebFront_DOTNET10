<script setup lang="ts">
const props = defineProps<{ permission: string }>()
const auth = useAuth()
</script>
<template>
  <slot v-if="auth.hasPermission(props.permission)" />
  <div v-else class="empty-state compact"><Icon name="lucide:lock-keyhole" /><strong>ไม่มีสิทธิ์ดำเนินการ</strong><span>ต้องการสิทธิ์ {{ permission }}</span></div>
</template>
