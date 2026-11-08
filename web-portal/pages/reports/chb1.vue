<script setup lang="ts">
import type { Chb1Scope as Scope, Chb1Report as Report } from '~/types/chb1'
import { buildChb1Html } from '~/utils/chb1-html'
definePageMeta({ middleware: 'auth' })
const auth = useAuth()
const form = reactive<Scope>({ tenantId: '', warehouseId: '', invoiceNo: '', revisionId: '', processingRunId: '', schemaVersion: 5 })
const fields: { key: Exclude<keyof Scope, "schemaVersion">; label: string }[] = [
  { key: 'tenantId', label: 'Tenant' }, { key: 'warehouseId', label: 'Warehouse' },
  { key: 'invoiceNo', label: 'Invoice No (invoiceId)' }, { key: 'revisionId', label: 'Revision' },
  { key: 'processingRunId', label: 'Processing run' }
]
const report = ref<Report | null>(null), busy = ref(false), error = ref('')
const dirty = computed(() => !!report.value && ((form.schemaVersion ?? 1) !== (report.value.scope.schemaVersion ?? 1) || fields.some(f => form[f.key].trim() !== report.value!.scope[f.key])))
function fieldLabel(key: string, fallback: string) {
  if (form.schemaVersion !== 5) return fallback
  return ({ tenantId: 'องค์กร', invoiceNo: 'รหัสเอกสาร Outbound', processingRunId: 'รอบตัดเบิก' } as Record<string, string>)[key] || fallback
}
const previewHtml = computed(() => report.value ? buildChb1Html(report.value) : '')
async function message(e: any) {
  let data = e?.data
  if (data instanceof Blob) { try { data = JSON.parse(await data.text()) } catch { data = null } }
  return data?.data?.message || data?.message || (e?.statusCode === 403 ? 'ไม่มีสิทธิ์ดูรายงานนี้' : 'โหลดรายงานไม่สำเร็จ กรุณาตรวจสอบเงื่อนไขและการเชื่อมต่อ')
}
async function load() {
  busy.value = true; error.value = ''; report.value = null
  try {
    const query = Object.fromEntries(fields.map(f => [f.key, form[f.key].trim()]))
    report.value = await auth.request<Report>('/api/ddd/reports/chb1', { query: { ...query, schemaVersion: form.schemaVersion } })
  } catch (e) { error.value = await message(e) }
  finally { busy.value = false }
}
async function exportExcel() {
  if (!report.value || dirty.value) return
  busy.value = true; error.value = ''
  try {
    const blob = await auth.request<Blob>('/api/ddd/reports/chb1/excel', { query: report.value.scope, responseType: 'blob' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a'); link.href = url; link.download = 'CHB1.xlsx'
    document.body.appendChild(link); link.click(); link.remove()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  } catch (e) { error.value = await message(e) }
  finally { busy.value = false }
}
async function exportPdf() {
  if (!report.value || dirty.value) return
  busy.value = true; error.value = ''
  try {
    const blob = await $fetch<Blob>('/api/reports/chb1/pdf', { query: report.value.scope, responseType: 'blob' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a'); link.href = url; link.download = 'CHB1.pdf'
    document.body.appendChild(link); link.click(); link.remove()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  } catch (e) { error.value = await message(e) }
  finally { busy.value = false }
}
</script>

<template>
  <AppShell><PermissionGate permission="chb1.read">
    <section class="chb-page" :aria-busy="busy">
      <div class="controls">
        <h1>รายงาน CHB1</h1>
        <form @submit.prevent="load">
          <label>ข้อมูลรายงาน<select v-model.number="form.schemaVersion" :disabled="busy"><option :value="5">ผล Transfer Part ใหม่</option><option :value="1">ข้อมูลเดิม</option></select></label>
          <label v-for="field in fields" :key="field.key">{{ fieldLabel(field.key, field.label) }}<input v-model="form[field.key]" required maxlength="200" :disabled="busy"></label>
          <button :disabled="busy">{{ busy ? 'กำลังโหลด…' : 'แสดงรายงาน' }}</button>
        </form>
        <p v-if="form.schemaVersion === 5" class="field-help">ใช้รหัสเอกสาร Outbound และรอบตัดเบิกจากผล Transfer Part ที่บันทึกสำเร็จแล้ว</p>
        <p v-else class="field-help">Invoice No ใช้ค่าจากฟิลด์ invoiceId ใน MongoDB เช่น inv-demo-001</p>
        <div class="actions"><button :disabled="busy || !report || dirty" @click="exportPdf">ดาวน์โหลด PDF</button><button :disabled="busy || !report || dirty" @click="exportExcel">ดาวน์โหลด Excel</button></div>
        <p v-if="dirty" role="status">เงื่อนไขเปลี่ยนแล้ว กรุณากดแสดงรายงานอีกครั้ง</p>
        <p v-if="error" role="alert" class="error">{{ error }}</p>
      </div>
      <div v-if="report" class="paper">
        <iframe title="ตัวอย่างรายงาน CHB1" :srcdoc="previewHtml" sandbox="" class="report-preview" />
        <p class="count">{{ report.rows.length }} รายการ</p>
      </div>
      <p v-else-if="!busy && !error" class="empty">ระบุใบแจ้งหนี้และรอบข้อมูลเพื่อแสดงรายงาน</p>
    </section>
  </PermissionGate></AppShell>
</template>

<style scoped>
.chb-page{background:#fff;color:#111;padding:24px;min-width:0}.controls h1{font-size:24px;margin:0 0 18px}form{display:flex;flex-wrap:wrap;gap:12px;align-items:end}label{display:flex;flex-direction:column;gap:6px;font-size:13px}input,select{border:1px solid #aaa;border-radius:4px;padding:8px;width:190px}button{border:1px solid #326985;background:#fff;color:#194b68;border-radius:4px;padding:9px 14px;cursor:pointer}button:disabled{opacity:.45;cursor:default}.actions{display:flex;gap:10px;margin:16px 0}.error{color:#a22222}.report-preview{display:block;width:100%;height:70vh;border:1px solid #ccc}.count,.empty{color:#555;font-size:13px}.empty{padding:30px 0}
</style>
