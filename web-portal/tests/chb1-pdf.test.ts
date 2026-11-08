import { beforeEach, describe, expect, it, vi } from 'vitest'
import type { Chb1Report } from '../types/chb1'

const mocks = vi.hoisted(() => ({ launch: vi.fn() }))
vi.mock('puppeteer-core', () => ({ default: { launch: mocks.launch } }))
import { Chb1PdfBusyError, renderChb1Pdf } from '../server/utils/chb1-pdf'

const report: Chb1Report = {
  scope: { tenantId: 'DEMO', warehouseId: 'OSW', invoiceNo: 'inv-demo-001', revisionId: 'v1', processingRunId: 'run1' },
  companyName: 'บริษัทตัวอย่าง', title: 'PART ISSUE FOR SHIPPING', warnings: [],
  columns: [{ key: 'totalThb', label: 'TOTAL (THB)', width: 20, format: 'money' }],
  rows: [{ totalThb: 1306.47 }, { totalThb: 783.88 }], totals: { totalThb: 2090.35 }
}

function renderer() {
  const page = {
    setJavaScriptEnabled: vi.fn().mockResolvedValue(undefined),
    setRequestInterception: vi.fn().mockResolvedValue(undefined),
    on: vi.fn(), setContent: vi.fn().mockResolvedValue(undefined),
    emulateMediaType: vi.fn().mockResolvedValue(undefined),
    pdf: vi.fn().mockResolvedValue(new Uint8Array([37, 80, 68, 70, 45]))
  }
  const browser = { newPage: vi.fn().mockResolvedValue(page), close: vi.fn().mockResolvedValue(undefined) }
  mocks.launch.mockResolvedValue(browser)
  return { browser, page }
}

beforeEach(() => vi.resetAllMocks())

describe('Puppeteer lifecycle without requiring Chrome on CI', () => {
  it('rejects a missing executable before launching a browser', async () => {
    await expect(renderChb1Pdf(report, '')).rejects.toThrow('NUXT_PUPPETEER_EXECUTABLE_PATH')
    expect(mocks.launch).not.toHaveBeenCalled()
  })

  it('renders the report securely with A3 pagination and closes Chromium', async () => {
    const { browser, page } = renderer()
    const bytes = await renderChb1Pdf(report, '/usr/bin/chromium')
    expect(Buffer.from(bytes).toString()).toBe('%PDF-')
    expect(mocks.launch).toHaveBeenCalledWith(expect.objectContaining({ headless: true,
      executablePath: '/usr/bin/chromium', args: ['--disable-dev-shm-usage'] }))
    expect(page.setJavaScriptEnabled).toHaveBeenCalledWith(false)
    expect(page.setRequestInterception).toHaveBeenCalledWith(true)
    const abort = vi.fn().mockResolvedValue(undefined)
    page.on.mock.calls[0]![1]({ abort })
    expect(abort).toHaveBeenCalledOnce()
    expect(page.setContent.mock.calls[0]![0]).toContain('2,090.35')
    expect(page.emulateMediaType).toHaveBeenCalledWith('print')
    expect(page.pdf).toHaveBeenCalledWith(expect.objectContaining({ format: 'A3', landscape: true,
      displayHeaderFooter: true, headerTemplate: expect.stringContaining('totalPages') }))
    expect(browser.close).toHaveBeenCalledOnce()
  })

  it('disables the sandbox only when explicitly configured', async () => {
    renderer()
    await renderChb1Pdf(report, '/usr/bin/chromium', true)
    expect(mocks.launch.mock.calls[0]![0].args).toContain('--no-sandbox')
  })

  it.each(['newPage', 'setContent', 'pdf', 'close'] as const)('releases capacity after %s fails', async stage => {
    const { browser, page } = renderer()
    const operation = stage === 'newPage' || stage === 'close' ? browser[stage] : page[stage]
    operation.mockRejectedValueOnce(new Error(`${stage} failed`))
    await expect(renderChb1Pdf(report, '/usr/bin/chromium')).rejects.toThrow(`${stage} failed`)
    expect(browser.close).toHaveBeenCalledOnce()
    renderer()
    await expect(renderChb1Pdf(report, '/usr/bin/chromium')).resolves.toBeInstanceOf(Uint8Array)
  })

  it('recovers capacity when Chrome cannot launch', async () => {
    mocks.launch.mockRejectedValueOnce(new Error('launch failed'))
    await expect(renderChb1Pdf(report, '/bad/path')).rejects.toThrow('launch failed')
    renderer()
    await expect(renderChb1Pdf(report, '/usr/bin/chromium')).resolves.toBeInstanceOf(Uint8Array)
  })

  it('limits simultaneous browsers and accepts new work after they finish', async () => {
    const { page } = renderer()
    let finish!: (value: Uint8Array) => void
    const pending = new Promise<Uint8Array>(resolve => { finish = resolve })
    page.pdf.mockReturnValue(pending)
    const first = renderChb1Pdf(report, '/usr/bin/chromium')
    const second = renderChb1Pdf(report, '/usr/bin/chromium')
    try {
      await expect(renderChb1Pdf(report, '/usr/bin/chromium')).rejects.toBeInstanceOf(Chb1PdfBusyError)
    } finally {
      finish(new Uint8Array([37, 80, 68, 70, 45]))
      await Promise.all([first, second])
    }
    expect(mocks.launch).toHaveBeenCalledTimes(2)
    renderer()
    await expect(renderChb1Pdf(report, '/usr/bin/chromium')).resolves.toBeInstanceOf(Uint8Array)
  })
})
