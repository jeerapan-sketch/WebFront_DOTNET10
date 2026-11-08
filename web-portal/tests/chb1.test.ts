import { describe, expect, it } from 'vitest'
import { buildChb1Html, escapeReportText, formatChb1Value } from '../utils/chb1-html'
import { renderChb1Pdf } from '../server/utils/chb1-pdf'
import type { Chb1Report } from '../types/chb1'
import { readFile, writeFile } from 'node:fs/promises'

const report: Chb1Report = {
  scope: { tenantId: 'DEMO', warehouseId: 'OSW', invoiceNo: 'inv-demo-001', revisionId: 'v1', processingRunId: 'run1' },
  companyName: 'บริษัทตัวอย่าง', title: 'PART ISSUE FOR SHIPPING', warnings: [],
  columns: [{ key: 'partNo', label: 'PART NO', width: 20, format: 'text' }, { key: 'totalThb', label: 'TOTAL (THB)', width: 20, format: 'money' }],
  rows: [{ partNo: '00001', totalThb: 1306.47 }, { partNo: '00002', totalThb: 783.88 }],
  totals: { partNo: 'Total', totalThb: 2090.35 }
}

describe('CHB1 HTML/CSS', () => {
  it('preserves identifiers, Thai business dates, decimal precision and missing values', () => {
    expect(formatChb1Value('001', 'text')).toBe('001')
    expect(formatChb1Value('2026-09-01', 'date')).toBe('01/09/2026')
    expect(formatChb1Value(2090.35, 'money')).toBe('2,090.35')
    expect(formatChb1Value(7.5, 'weight')).toBe('7.500')
    expect(formatChb1Value(.1234567891, 'fx')).toBe('0.1234567891')
    expect(formatChb1Value(null, 'money')).toBe('')
  })
  it('uses grouped integers, two decimal money and three decimal weights including zero and rounding', () => {
    expect(formatChb1Value(1234567, 'quantity')).toBe('1,234,567')
    expect(formatChb1Value(1234.5, 'quantity')).toBe('1,235')
    expect(formatChb1Value(-1234.5, 'quantity')).toBe('-1,235')
    expect(formatChb1Value(0, 'quantity')).toBe('0')
    expect(formatChb1Value(1234.565, 'money')).toBe('1,234.57')
    expect(formatChb1Value(0, 'money')).toBe('0.00')
    expect(formatChb1Value(1234.5678, 'weight')).toBe('1,234.568')
    expect(formatChb1Value(0, 'weight')).toBe('0.000')
  })
  it('escapes source values and creates no active source content', () => {
    const html = buildChb1Html({ ...report, companyName: '<img src="http://internal" onerror="alert(1)">', warnings: ['<script>bad</script>'] })
    expect(html).not.toContain('<img')
    expect(html).not.toContain('<script>')
    expect(html).toContain('&lt;img')
    expect(escapeReportText("<&'\" >")).toBe('&lt;&amp;&#39;&quot; &gt;')
    expect(html).toContain("default-src 'none'")
  })
  it('repeats the heading on printed pages and renders Total only once after all data', () => {
    const html = buildChb1Html(report)
    expect(html).toContain('thead{display:table-header-group}')
    expect(html).toContain('size:A3 landscape')
    expect(html.match(/class="total"/g)).toHaveLength(1)
    expect(html.indexOf('00002')).toBeLessThan(html.indexOf('class="total"'))
    expect(html).toContain('2,090.35')
  })
})

// Opt in on hosts with Chromium: CHB1_TEST_CHROME=<path> npm test -- tests/chb1.test.ts
it.skipIf(!process.env.CHB1_TEST_CHROME)('renders a real PDF using Puppeteer', async () => {
  const input: Chb1Report = process.env.CHB1_TEST_REPORT
    ? JSON.parse(await readFile(process.env.CHB1_TEST_REPORT, 'utf8')) : report
  const pdf = await renderChb1Pdf(input, process.env.CHB1_TEST_CHROME!)
  expect(Buffer.from(pdf).subarray(0, 5).toString()).toBe('%PDF-')
  if (process.env.CHB1_TEST_PDF) await writeFile(process.env.CHB1_TEST_PDF, pdf)
}, 90000)
