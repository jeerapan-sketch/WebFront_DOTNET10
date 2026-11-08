<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const auth = useAuth()
const step = ref(1)
const file = ref<File | null>(null)
const dragging = ref(false)
const checking = ref(false)
const fileInput = ref<HTMLInputElement>()

const formatRows = [
  { row: 2, employeeId: 'EMP-00124', name: 'สมชาย ใจดี', department: 'FIN', amount: '12,500.00', status: 'ผ่าน', detail: 'รูปแบบข้อมูลถูกต้อง' },
  { row: 3, employeeId: 'EMP-00125', name: 'กมลวรรณ สุขใจ', department: 'HR', amount: '8,750.00', status: 'ผ่าน', detail: 'รูปแบบข้อมูลถูกต้อง' },
  { row: 4, employeeId: 'EMP00126', name: 'วิชัย พูนผล', department: 'OPS', amount: '-1,200.00', status: 'ผิดพลาด', detail: 'Employee ID และ Amount ไม่ถูกต้อง' },
  { row: 5, employeeId: 'EMP-00127', name: '', department: 'IT', amount: '9,450.00', status: 'คำเตือน', detail: 'ไม่พบชื่อพนักงาน' },
  { row: 6, employeeId: 'EMP-00128', name: 'ปิยะพร รุ่งเรือง', department: 'FIN', amount: '15,900.00', status: 'ผ่าน', detail: 'รูปแบบข้อมูลถูกต้อง' }
]

const oracleRows = [
  { employeeId: 'EMP-00124', name: 'สมชาย ใจดี', source: 'FIN', oracle: 'FIN', status: 'ตรงกัน', detail: 'พร้อมนำเข้า' },
  { employeeId: 'EMP-00125', name: 'กมลวรรณ สุขใจ', source: 'HR', oracle: 'HR', status: 'ตรงกัน', detail: 'พร้อมนำเข้า' },
  { employeeId: 'EMP-00127', name: '-', source: 'IT', oracle: 'IT', status: 'ไม่พบข้อมูล', detail: 'ไม่พบ Employee ID ใน Oracle' },
  { employeeId: 'EMP-00128', name: 'ปิยะพร รุ่งเรือง', source: 'FIN', oracle: 'ACC', status: 'ไม่ตรงกัน', detail: 'Department ไม่ตรงกับ Oracle' }
]

const chooseFile = () => fileInput.value?.click()
const selectFile = (selected?: File) => {
  if (!selected) return
  file.value = selected
  step.value = 1
}
const onDrop = (event: DragEvent) => {
  dragging.value = false
  selectFile(event.dataTransfer?.files?.[0])
}
const runFormatCheck = async () => {
  checking.value = true
  await new Promise(resolve => setTimeout(resolve, 650))
  checking.value = false
  step.value = 2
}
const runOracleCheck = async () => {
  checking.value = true
  await new Promise(resolve => setTimeout(resolve, 650))
  checking.value = false
  step.value = 3
}
const fileSize = computed(() => file.value ? `${(file.value.size / 1024 / 1024).toFixed(2)} MB` : '-')
</script>

<template>
  <AppShell>
    <PermissionGate permission="abatement.create">
      <div class="page-heading import-heading">
        <div><span class="eyebrow dark">DATA IMPORT</span><h1>นำเข้าข้อมูลจาก Excel</h1><p>ตรวจสอบคุณภาพข้อมูลก่อนบันทึกเข้าสู่ฐานข้อมูล Oracle</p></div>
        <span class="mock-badge"><Icon name="lucide:beaker" /> Mockup Preview</span>
      </div>

      <nav class="import-steps" aria-label="ขั้นตอนนำเข้าข้อมูล">
        <button v-for="item in [{ n: 1, title: 'อัปโหลดไฟล์', caption: 'เลือกไฟล์ Excel' }, { n: 2, title: 'ตรวจสอบรูปแบบ', caption: 'Validation & Preview' }, { n: 3, title: 'ตรวจสอบ Oracle', caption: 'Database verification' }]" :key="item.n" :class="{ active: step === item.n, done: step > item.n }" :disabled="item.n > step" @click="step = item.n">
          <span><Icon v-if="step > item.n" name="lucide:check" />{{ step > item.n ? '' : item.n }}</span><div><strong>{{ item.title }}</strong><small>{{ item.caption }}</small></div><Icon v-if="item.n < 3" name="lucide:chevron-right" />
        </button>
      </nav>

      <section v-if="step === 1" class="card import-panel">
        <div class="panel-title"><div><span class="panel-icon"><Icon name="lucide:upload-cloud" /></span><div><h2>เลือกไฟล์ Excel</h2><p>รองรับไฟล์ .xlsx และ .xls ขนาดไม่เกิน 20 MB</p></div></div><a href="#" @click.prevent><Icon name="lucide:download" /> ดาวน์โหลดไฟล์ตัวอย่าง</a></div>
        <input ref="fileInput" class="hidden-input" type="file" accept=".xlsx,.xls" @change="selectFile(($event.target as HTMLInputElement).files?.[0])">
        <button class="drop-zone" :class="{ dragging, selected: file }" @click="chooseFile" @dragover.prevent="dragging = true" @dragleave.prevent="dragging = false" @drop.prevent="onDrop">
          <span class="excel-mark"><Icon name="lucide:file-spreadsheet" /></span>
          <template v-if="file"><strong>{{ file.name }}</strong><small>{{ fileSize }} · พร้อมตรวจสอบ</small><em><Icon name="lucide:refresh-cw" /> เปลี่ยนไฟล์</em></template>
          <template v-else><strong>ลากไฟล์มาวางที่นี่</strong><small>หรือเลือกไฟล์จากเครื่องของคุณ</small><em><Icon name="lucide:folder-open" /> Browse file</em></template>
        </button>
        <div class="file-requirements"><div><Icon name="lucide:sheet" /><span><strong>Sheet ที่ต้องการ</strong><small>ABATEMENT_DATA</small></span></div><div><Icon name="lucide:columns-3" /><span><strong>คอลัมน์บังคับ</strong><small>Employee ID, Name, Department, Amount</small></span></div><div><Icon name="lucide:shield-check" /><span><strong>ความปลอดภัย</strong><small>ไฟล์จะถูกตรวจสอบก่อนบันทึกเสมอ</small></span></div></div>
        <footer class="panel-actions"><span>ขั้นตอน 1 จาก 3</span><button class="button primary" :disabled="!file || checking" @click="runFormatCheck"><Icon :name="checking ? 'lucide:loader-circle' : 'lucide:scan-search'" :class="{ spin: checking }" />ตรวจสอบรูปแบบ</button></footer>
      </section>

      <section v-else-if="step === 2" class="card import-panel">
        <div class="panel-title"><div><span class="panel-icon blue"><Icon name="lucide:list-checks" /></span><div><h2>ผลการตรวจสอบรูปแบบ</h2><p>{{ file?.name || 'Abatement_August_2026.xlsx' }} · พบข้อมูลตัวอย่าง 5 แถว</p></div></div><span class="result-badge warning"><Icon name="lucide:triangle-alert" /> ต้องแก้ไข 2 รายการ</span></div>
        <div class="validation-summary"><div><small>รายการทั้งหมด</small><strong>125</strong></div><div class="pass"><small>ผ่านการตรวจสอบ</small><strong>121</strong></div><div class="warn"><small>คำเตือน</small><strong>2</strong></div><div class="fail"><small>ผิดพลาด</small><strong>2</strong></div></div>
        <div class="import-table-wrap"><table class="import-table"><caption class="visually-hidden">ผลตรวจสอบรูปแบบข้อมูล Excel แยกตามแถว</caption><thead><tr><th>แถว</th><th>Employee ID</th><th>ชื่อ–นามสกุล</th><th>Department</th><th class="right">Amount</th><th>ผลตรวจสอบ</th></tr></thead><tbody><tr v-for="row in formatRows" :key="row.row"><td>{{ row.row }}</td><td><code>{{ row.employeeId }}</code></td><td>{{ row.name || '-' }}</td><td>{{ row.department }}</td><td class="right">{{ row.amount }}</td><td><span class="row-status" :class="row.status === 'ผ่าน' ? 'pass' : row.status === 'คำเตือน' ? 'warn' : 'fail'"><Icon :name="row.status === 'ผ่าน' ? 'lucide:circle-check' : row.status === 'คำเตือน' ? 'lucide:triangle-alert' : 'lucide:circle-x'" />{{ row.status }}</span><small>{{ row.detail }}</small></td></tr></tbody></table></div>
        <footer class="panel-actions"><button class="button secondary" @click="step = 1"><Icon name="lucide:arrow-left" />ย้อนกลับ</button><div><button class="button secondary"><Icon name="lucide:download" />ดาวน์โหลดข้อผิดพลาด</button><button class="button primary" :disabled="checking" @click="runOracleCheck"><Icon :name="checking ? 'lucide:loader-circle' : 'lucide:database-search'" :class="{ spin: checking }" />ตรวจสอบกับ Oracle</button></div></footer>
      </section>

      <section v-else class="card import-panel">
        <div class="panel-title"><div><span class="panel-icon purple"><Icon name="lucide:database" /></span><div><h2>ผลตรวจสอบกับ Oracle</h2><p>เปรียบเทียบข้อมูล Master และสถานะพนักงานล่าสุด</p></div></div><span class="result-badge warning"><Icon name="lucide:shield-alert" /> พบข้อแตกต่าง 2 รายการ</span></div>
        <div class="oracle-banner"><Icon name="lucide:database-zap" /><div><strong>Oracle connection verified</strong><small>HR_MASTER · DEV · ตรวจสอบล่าสุดเมื่อสักครู่</small></div><span>Connected</span></div>
        <div class="validation-summary oracle"><div><small>ส่งตรวจสอบ</small><strong>123</strong></div><div class="pass"><small>ข้อมูลตรงกัน</small><strong>119</strong></div><div class="warn"><small>ไม่พบใน Oracle</small><strong>2</strong></div><div class="fail"><small>ข้อมูลไม่ตรงกัน</small><strong>2</strong></div></div>
        <div class="import-table-wrap"><table class="import-table"><caption class="visually-hidden">ผลเปรียบเทียบข้อมูลจาก Excel กับฐานข้อมูล Oracle</caption><thead><tr><th>Employee ID</th><th>ชื่อ–นามสกุล</th><th>Excel</th><th>Oracle</th><th>ผลเปรียบเทียบ</th><th>รายละเอียด</th></tr></thead><tbody><tr v-for="row in oracleRows" :key="row.employeeId"><td><code>{{ row.employeeId }}</code></td><td>{{ row.name }}</td><td>{{ row.source }}</td><td>{{ row.oracle }}</td><td><span class="row-status" :class="row.status === 'ตรงกัน' ? 'pass' : row.status === 'ไม่พบข้อมูล' ? 'warn' : 'fail'"><Icon :name="row.status === 'ตรงกัน' ? 'lucide:circle-check' : row.status === 'ไม่พบข้อมูล' ? 'lucide:circle-help' : 'lucide:git-compare-arrows'" />{{ row.status }}</span></td><td>{{ row.detail }}</td></tr></tbody></table></div>
        <footer class="panel-actions"><button class="button secondary" @click="step = 2"><Icon name="lucide:arrow-left" />ย้อนกลับ</button><div><button class="button secondary"><Icon name="lucide:file-down" />Export ผลตรวจสอบ</button><button class="button primary" disabled><Icon name="lucide:database-backup" />นำเข้าข้อมูล 119 รายการ</button></div></footer>
      </section>
    </PermissionGate>
  </AppShell>
</template>

<style scoped>
.import-heading{align-items:center}.mock-badge,.result-badge{display:inline-flex;align-items:center;gap:7px;border-radius:999px;padding:8px 12px;font-size:11px;font-weight:600;background:#eef5fc;color:#426987}.import-steps{display:grid;grid-template-columns:repeat(3,1fr);background:#fff;border:1px solid var(--line);border-radius:14px;margin-bottom:18px;box-shadow:var(--shadow);overflow:hidden}.import-steps button{border:0;background:#fff;min-height:82px;padding:15px 20px;display:flex;align-items:center;gap:12px;text-align:left;color:#98a6b4}.import-steps button>span{width:32px;height:32px;border:2px solid #d8e0e8;border-radius:50%;display:grid;place-items:center;font:600 12px Manrope,sans-serif}.import-steps button>div{display:grid;gap:2px;flex:1}.import-steps strong{font-size:13px;color:#718092}.import-steps small{font-size:10px}.import-steps button.active{background:#f5f9fd;color:var(--blue);box-shadow:inset 0 -3px var(--blue)}.import-steps button.active>span{border-color:var(--blue);background:var(--blue);color:#fff}.import-steps button.active strong,.import-steps button.done strong{color:var(--ink)}.import-steps button.done>span{border-color:var(--green);background:var(--green);color:#fff}.import-steps button>svg{color:#ccd5dd}.import-panel{padding:26px}.panel-title,.panel-title>div,.file-requirements>div,.oracle-banner{display:flex;align-items:center;gap:13px}.panel-title{justify-content:space-between;margin-bottom:23px}.panel-title h2{font-size:18px;margin:0 0 3px}.panel-title p{font-size:12px;color:var(--muted);margin:0}.panel-title>a{font-size:12px;color:var(--blue);display:flex;align-items:center;gap:6px}.panel-icon{width:45px;height:45px;border-radius:12px;background:#e9f8f1;color:var(--green);display:grid;place-items:center;font-size:21px}.panel-icon.blue{background:var(--sky);color:var(--blue)}.panel-icon.purple{background:#f3ecfb;color:#7e57aa}.hidden-input{display:none}.drop-zone{width:100%;min-height:245px;border:2px dashed #cfdce8;border-radius:14px;background:#f9fbfd;display:flex;flex-direction:column;align-items:center;justify-content:center;cursor:pointer;color:var(--ink);padding:30px}.drop-zone:hover,.drop-zone.dragging{border-color:var(--blue);background:#f2f8fe}.drop-zone.selected{border-style:solid;border-color:#9ed9c3;background:#f6fcf9}.excel-mark{width:64px;height:64px;border-radius:18px;background:#e6f6ee;color:#15845f;display:grid;place-items:center;font-size:31px;margin-bottom:15px}.drop-zone strong{font-size:16px}.drop-zone small{color:var(--muted);margin:4px 0 15px}.drop-zone em{font-style:normal;background:var(--blue);color:#fff;border-radius:8px;padding:9px 15px;display:flex;gap:7px;align-items:center;font-size:12px;font-weight:600}.file-requirements{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:17px 0}.file-requirements>div{background:#f7f9fb;border-radius:10px;padding:13px;color:var(--blue)}.file-requirements span{display:grid;gap:2px}.file-requirements strong{font-size:11px;color:var(--ink)}.file-requirements small{font-size:9px;color:var(--muted)}.panel-actions{border-top:1px solid var(--line);margin-top:22px;padding-top:18px;display:flex;align-items:center;justify-content:space-between}.panel-actions>span{font-size:11px;color:var(--muted)}.panel-actions>div{display:flex;gap:9px}.result-badge.warning{background:#fff7e8;color:#a26a19}.validation-summary{display:grid;grid-template-columns:repeat(4,1fr);gap:11px;margin-bottom:18px}.validation-summary>div{border:1px solid var(--line);border-radius:10px;padding:13px 15px;display:grid;gap:2px}.validation-summary small{font-size:10px;color:var(--muted)}.validation-summary strong{font:700 21px Manrope,sans-serif}.validation-summary .pass strong{color:var(--green)}.validation-summary .warn strong{color:var(--orange)}.validation-summary .fail strong{color:var(--red)}.import-table-wrap{overflow:auto;border:1px solid var(--line);border-radius:10px}.import-table{width:100%;border-collapse:collapse;min-width:900px}.import-table th{background:#f6f8fa;color:var(--muted);font-size:10px;text-align:left;padding:10px 12px}.import-table td{padding:12px;border-top:1px solid var(--line);font-size:11px}.import-table td small{display:block;color:var(--muted);font-size:9px;margin-top:3px}.import-table code{font-size:10px;color:#385776}.import-table .right{text-align:right}.row-status{display:inline-flex;align-items:center;gap:5px;font-size:10px;font-weight:600}.row-status.pass{color:var(--green)}.row-status.warn{color:var(--orange)}.row-status.fail{color:var(--red)}.oracle-banner{background:#f4faf7;border:1px solid #d9eee4;border-radius:10px;padding:12px 15px;color:var(--green);margin-bottom:14px}.oracle-banner>div{flex:1;display:grid}.oracle-banner strong{font-size:11px;color:var(--ink)}.oracle-banner small{font-size:9px;color:var(--muted)}.oracle-banner>span{font-size:10px;font-weight:600}@media(max-width:900px){.import-steps button{padding:12px}.import-steps button>svg,.import-steps small{display:none}.file-requirements,.validation-summary{grid-template-columns:repeat(2,1fr)}}@media(max-width:560px){.import-steps button{flex-direction:column;text-align:center}.panel-title{align-items:flex-start}.panel-title>a,.result-badge{display:none}.file-requirements,.validation-summary{grid-template-columns:1fr}.panel-actions,.panel-actions>div{align-items:stretch;flex-direction:column}.panel-actions .button{width:100%}}
</style>
