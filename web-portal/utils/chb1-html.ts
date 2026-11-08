import type { Chb1Report } from '../types/chb1'

export const escapeReportText = (value: unknown) => String(value ?? '').replace(/[&<>"']/g, c => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}[c]!))

export function formatChb1Value(value: unknown, format: string): string {
  if (value == null) return ''
  if (format === 'date') {
    const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(value))
    return match ? `${match[3]}/${match[2]}/${match[1]}` : String(value)
  }
  if (typeof value !== 'number') return String(value)
  const precision: Record<string, [number, number]> = { integer: [0, 0], quantity: [0, 0], weight: [3, 3], money: [2, 2], rate: [0, 2], fx: [0, 10] }
  const [minimumFractionDigits, maximumFractionDigits] = precision[format] ?? [0, 2]
  return new Intl.NumberFormat('en-US', { minimumFractionDigits, maximumFractionDigits }).format(value)
}

// A single standalone HTML/CSS template serves both the sandboxed preview and Puppeteer PDF.
export function buildChb1Html(report: Chb1Report): string {
  const e = escapeReportText
  const columns = report.columns
  const numeric = (format: string) => !['text', 'date'].includes(format)
  const row = (values: Chb1Report['totals'], total = false) => `<tr${total ? ' class="total"' : ''}>${columns.map(c =>
    `<td class="${numeric(c.format) ? 'number' : ''}">${e(formatChb1Value(values[c.key], c.format))}</td>`).join('')}</tr>`
  const width = columns.reduce((sum, c) => sum + c.width, 0)
  return `<!DOCTYPE html><html lang="th"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src 'none'; font-src 'none'; script-src 'none'; base-uri 'none'">
<title>CHB1 — ${e(report.scope.invoiceNo)}</title><style>
@page{size:A3 landscape;margin:12mm 8mm 12mm}
*{box-sizing:border-box}body{margin:0;background:white;color:black;font-family:Arial,'Noto Sans Thai',Tahoma,sans-serif}
.sheet{width:404mm;margin:auto;padding:0}table{border-collapse:collapse;width:100%;table-layout:fixed;font-size:6pt;line-height:1.3}
col{width:auto}thead{display:table-header-group}tr{break-inside:avoid;page-break-inside:avoid}th,td{border:.5pt solid #000;padding:1.2mm .7mm;overflow-wrap:anywhere;vertical-align:middle}
th{font-size:5.8pt;text-align:center;font-weight:700}.company,.title{border:0;text-align:center;font-size:10pt;padding:1mm}.title{padding-bottom:5mm}
.invoice{font-size:7pt;text-align:left;padding:1mm}.number{text-align:right;font-variant-numeric:tabular-nums}.total{font-weight:700}
.note{font-size:7pt;margin:2mm 0}.notes{break-inside:avoid}
@media screen{body{padding:8mm;background:#e9edf1}.sheet{background:white;padding:8mm;width:420mm;box-shadow:0 1px 5px #aaa}}
</style></head><body><main class="sheet"><table aria-label="CHB1 PART ISSUE FOR SHIPPING">
<colgroup>${columns.map(c => `<col style="width:${(c.width / width * 100).toFixed(4)}%">`).join('')}</colgroup>
<thead><tr><th colspan="${columns.length}" class="company">${e(report.companyName)}</th></tr>
<tr><th colspan="${columns.length}" class="title">${e(report.title)}</th></tr>
<tr><th colspan="${columns.length}" class="invoice">Invoice No : ${e(report.scope.invoiceNo)}</th></tr>
<tr>${columns.map(c => `<th scope="col">${e(c.label)}</th>`).join('')}</tr></thead>
<tbody>${report.rows.map(r => row(r)).join('')}${row(report.totals, true)}</tbody></table>
<div class="notes">${report.warnings.map(w => `<p class="note">${e(w)}</p>`).join('')}</div></main></body></html>`
}
