<script setup lang="ts">
type Unit = { code: string; description: string; customsCode: string }
type Result = { items: Unit[]; total: number; page: number; pageSize: number }
definePageMeta({ middleware: 'auth' })
const auth = useAuth()
const query = ref(''), appliedQuery = ref(''), page = ref(1), pageSize = ref(10)
const items = ref<Unit[]>([]), total = ref(0), selected = ref<string[]>([])
const busy = ref(false), error = ref(''), notice = ref(''), editing = ref(false)
const editor = ref<HTMLDialogElement>(), confirmation = ref<HTMLDialogElement>()
const form = reactive<Unit>({ code: '', description: '', customsCode: '' })
const allSelected = computed(() => items.value.length > 0 && items.value.every(x => selected.value.includes(x.code)))
const pages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))
const allowed = (action: string) => auth.hasPermission(`unit-measurement.${action}`)
const message = (e: any) => e?.data?.message || (e?.statusCode === 403 ? 'ไม่มีสิทธิ์ดำเนินการ' : 'ดำเนินการไม่สำเร็จ กรุณาตรวจสอบข้อมูลและการเชื่อมต่อ')

async function load() {
  busy.value = true; error.value = ''; selected.value = []
  try {
    let result = await auth.request<Result>('/api/ddd/unit-measurements', { query: { code: appliedQuery.value, page: page.value, pageSize: pageSize.value } })
    const lastPage = Math.max(1, Math.ceil(result.total / pageSize.value))
    if (page.value > lastPage) {
      page.value = lastPage
      result = await auth.request<Result>('/api/ddd/unit-measurements', { query: { code: appliedQuery.value, page: page.value, pageSize: pageSize.value } })
    }
    items.value = result.items; total.value = result.total
  } catch (e) { error.value = message(e); items.value = []; total.value = 0 }
  finally { busy.value = false }
}
async function search(reset = false) {
  if (reset) query.value = ''
  appliedQuery.value = query.value.trim(); page.value = 1; notice.value = ''; await load()
}
async function changePage(value: number) { page.value = value; await load() }
function openEditor(unit?: Unit) {
  editing.value = !!unit; error.value = ''; notice.value = ''
  Object.assign(form, unit || { code: '', description: '', customsCode: '' })
  editor.value?.showModal()
}
async function save() {
  if (!form.description.trim()) { error.value = 'กรุณาระบุคำอธิบายหน่วยวัด'; return }
  busy.value = true; error.value = ''
  try {
    await auth.request(`/api/ddd/unit-measurements${editing.value ? `/${encodeURIComponent(form.code)}` : ''}`, {
      method: editing.value ? 'PUT' : 'POST', body: { ...form, description: form.description.trim() }
    })
    editor.value?.close(); notice.value = 'บันทึกข้อมูลสำเร็จ'; await load()
  } catch (e) { error.value = message(e) }
  finally { busy.value = false }
}
async function remove() {
  busy.value = true; error.value = ''
  try {
    const result = await auth.request<{ deletedCount: number }>('/api/ddd/unit-measurements/delete', { method: 'POST', body: { codes: selected.value } })
    confirmation.value?.close(); notice.value = `ลบข้อมูล ${result.deletedCount} รายการแล้ว`; await load()
  } catch (e) { error.value = message(e) }
  finally { busy.value = false }
}
onMounted(() => { if (allowed('read')) void load() })
</script>

<template>
  <AppShell><PermissionGate permission="unit-measurement.read">
    <section class="unit-page" :aria-busy="busy">
      <header class="unit-heading"><div><small>02.MST-Master Data / 2.1) Master Common Menu</small><h1>Unit Measurement — DDD</h1></div><span>ZQM014P001-DDD</span></header>
      <p class="unit-success">หน้าทดลอง DDD ใช้ข้อมูลแยกจาก Unit Measurement เดิม</p><div class="unit-actions">
        <button :disabled="busy" @click="search()"><Icon name="lucide:search" /> Search</button>
        <button :disabled="busy || !allowed('create')" @click="openEditor()"><Icon name="lucide:circle-plus" /> Add</button>
        <button :disabled="busy || !allowed('delete') || !selected.length" @click="error = ''; confirmation?.showModal()"><Icon name="lucide:trash-2" /> Delete</button>
        <button :disabled="busy" @click="search(true)"><Icon name="lucide:rotate-cw" /> Reset</button>
      </div>
      <p v-if="error" role="alert" class="unit-error">{{ error }}</p>
      <p v-if="notice" role="status" class="unit-success">{{ notice }}</p>
      <form class="unit-search" @submit.prevent="search()"><label for="unit-search-code">Unit Measurement Code</label><input id="unit-search-code" v-model="query" maxlength="30" :disabled="busy"><button :disabled="busy" aria-label="Search"><Icon name="lucide:search" /></button></form>
      <div class="unit-table"><table>
        <caption class="sr-only">รายการหน่วยวัด: รหัสหน่วยวัด คำอธิบาย และรหัสหน่วยวัดกรมศุลกากร</caption>
        <thead><tr><th><input type="checkbox" aria-label="Select all on this page" :checked="allSelected" :disabled="busy || !allowed('delete') || !items.length" @change="selected = allSelected ? [] : items.map(x => x.code)"></th><th><span class="sr-only">Edit</span></th><th>Unit Measurement Code</th><th>Unit Measurement Description</th><th>Unit Measurement Customs Dept. Code</th></tr></thead>
        <tbody><tr v-for="unit in items" :key="unit.code"><td><input v-model="selected" type="checkbox" :value="unit.code" :aria-label="`Select ${unit.code}`" :disabled="busy || !allowed('delete')"></td><td><button class="unit-edit" :aria-label="`Edit ${unit.code}`" :disabled="busy || !allowed('update')" @click="openEditor(unit)"><Icon name="lucide:pencil" /></button></td><td>{{ unit.code }}</td><td>{{ unit.description }}</td><td>{{ unit.customsCode }}</td></tr>
        <tr v-if="!items.length"><td colspan="5" class="unit-empty">{{ busy ? 'กำลังโหลดข้อมูล…' : error ? 'ไม่สามารถโหลดข้อมูลได้' : 'ไม่พบข้อมูล' }}</td></tr></tbody>
      </table></div>
      <footer class="unit-pagination"><label>Show <select v-model.number="pageSize" :disabled="busy" @change="changePage(1)"><option :value="10">10</option><option :value="25">25</option><option :value="50">50</option><option :value="100">100</option></select></label><span>Showing {{ total ? (page - 1) * pageSize + 1 : 0 }} to {{ Math.min(page * pageSize, total) }} of {{ total }} entries</span><div><button :disabled="busy || page <= 1" @click="changePage(page - 1)">Previous</button><span>{{ page }} / {{ pages }}</span><button :disabled="busy || page >= pages" @click="changePage(page + 1)">Next</button></div></footer>
    </section>
    <dialog ref="editor" class="unit-dialog" @cancel="busy && $event.preventDefault()">
      <form @submit.prevent="save"><h2>{{ editing ? 'Edit' : 'Add' }} Unit Measurement</h2>
        <p v-if="error" role="alert" class="unit-error">{{ error }}</p>
        <label>Unit Measurement Code <input v-model="form.code" required maxlength="30" pattern="[A-Za-z0-9_-]+" :readonly="editing" :disabled="busy" title="ตัวอักษรภาษาอังกฤษ ตัวเลข _ หรือ -" autofocus></label>
        <label>Unit Measurement Description <input v-model="form.description" required maxlength="200" :disabled="busy"></label>
        <label>Unit Measurement Customs Dept. Code <input v-model="form.customsCode" maxlength="30" :disabled="busy"></label>
        <div class="unit-dialog-actions"><button type="button" :disabled="busy" @click="editor?.close()">Cancel</button><button type="submit" :disabled="busy">{{ busy ? 'Saving…' : 'Save' }}</button></div>
      </form>
    </dialog>
    <dialog ref="confirmation" class="unit-dialog" @cancel="busy && $event.preventDefault()"><h2>Delete Unit Measurement</h2><p>ยืนยันการลบ {{ selected.length }} รายการ?</p><p class="unit-codes">{{ selected.join(', ') }}</p><p v-if="error" role="alert" class="unit-error">{{ error }}</p><div class="unit-dialog-actions"><button :disabled="busy" @click="confirmation?.close()">Cancel</button><button :disabled="busy" @click="remove">{{ busy ? 'Deleting…' : 'Delete' }}</button></div></dialog>
  </PermissionGate></AppShell>
</template>

<style scoped>
.unit-page{background:white;border:1px solid #d6dde4;color:#244561;font-size:13px}.unit-heading{display:flex;justify-content:space-between;align-items:center;padding:20px;background:#60a6c9;color:white;gap:16px}.unit-heading h1{font-size:22px;margin:8px 0 0}.unit-heading span{font-size:12px;white-space:nowrap}.unit-actions{display:flex;gap:5px;padding:16px 18px;border-bottom:1px solid #ddd}button{display:inline-flex;align-items:center;justify-content:center;gap:4px;background:white;color:#327caf;border:1px solid #a8c4d9;border-radius:3px;padding:5px 9px;cursor:pointer}button:disabled{opacity:.45;cursor:default}button:focus-visible,input:focus-visible,select:focus-visible{outline:2px solid #1675ae;outline-offset:2px}.unit-search{display:flex;align-items:center;justify-content:center;gap:16px;padding:20px}.unit-search input{width:320px;max-width:100%}input,select{border:1px solid #c9ced3;padding:6px;color:#244561;background:white}input[readonly]{background:#eef1f4}.unit-table{overflow-x:auto;margin:0 18px}table{border-collapse:collapse;width:100%;min-width:780px}th,td{border:1px solid #ddd;padding:9px;text-align:left}th{background:#c5d1df;font-weight:500;color:#396385}th:nth-child(-n+2),td:nth-child(-n+2){width:34px;text-align:center;padding:4px}tbody tr:nth-child(odd){background:#f8f8f8}.unit-edit{border:0;background:transparent;color:#e8a000}.unit-empty{text-align:center;padding:32px}.unit-pagination{display:flex;align-items:center;gap:10px;padding:14px 18px;flex-wrap:wrap}.unit-pagination>div{margin-left:auto;display:flex;gap:12px;align-items:center}.unit-error,.unit-success{padding:10px 18px;margin:8px 0}.unit-error{background:#fff1f1;color:#b42318}.unit-success{background:#effaf1;color:#23663a}.unit-dialog{margin:auto;border:1px solid #c5d1df;border-radius:6px;padding:26px;width:520px;max-width:calc(100vw - 32px);max-height:90vh;overflow:auto;color:#244561}.unit-dialog::backdrop{background:#142b4566}.unit-dialog h2{font-size:19px;margin:0 0 20px}.unit-dialog label{display:flex;flex-direction:column;gap:8px;margin-bottom:18px;font-size:13px}.unit-dialog-actions{display:flex;justify-content:flex-end;gap:8px;margin-top:24px}.unit-codes{overflow-wrap:anywhere}.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)}@media(max-width:650px){.unit-search{flex-wrap:wrap;justify-content:flex-start}.unit-heading{align-items:flex-start;flex-direction:column}.unit-heading h1{font-size:18px}}
</style>
