import puppeteer from 'puppeteer-core'
import { buildChb1Html } from '../../utils/chb1-html'
import type { Chb1Report } from '../../types/chb1'

// Bound concurrent Chromium processes. The route returns 503 for callers to retry.
let activeRenders = 0
export class Chb1PdfBusyError extends Error {}

export async function renderChb1Pdf(report: Chb1Report, executablePath: string, noSandbox = false): Promise<Uint8Array> {
  if (activeRenders >= 2) throw new Chb1PdfBusyError('Report renderer is busy')
  if (!executablePath) throw new Error('Configure NUXT_PUPPETEER_EXECUTABLE_PATH')
  activeRenders++
  let browser: Awaited<ReturnType<typeof puppeteer.launch>> | undefined
  try {
    browser = await puppeteer.launch({ executablePath, headless: true, timeout: 30000,
      args: noSandbox ? ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'] : ['--disable-dev-shm-usage'] })
    const page = await browser.newPage()
    await page.setJavaScriptEnabled(false)
    await page.setRequestInterception(true)
    page.on('request', request => { void request.abort() })
    await page.setContent(buildChb1Html(report), { waitUntil: 'load', timeout: 30000 })
    await page.emulateMediaType('print')
    return await page.pdf({ format: 'A3', landscape: true, preferCSSPageSize: true, printBackground: true,
      displayHeaderFooter: true, headerTemplate: '<div style="width:100%;padding:0 8mm;font-size:7px;text-align:right">Page: <span class="pageNumber"></span>/<span class="totalPages"></span></div>',
      footerTemplate: '<div></div>', margin: { top: '12mm', bottom: '12mm', left: '8mm', right: '8mm' }, timeout: 60000 })
  } finally {
    try { await browser?.close() } finally { activeRenders-- }
  }
}
