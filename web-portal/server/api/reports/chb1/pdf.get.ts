import { backendUrl, requireAuthorizedSession } from '../../../utils/bff-auth'
import { Chb1PdfBusyError, renderChb1Pdf } from '../../../utils/chb1-pdf'
import type { Chb1Report } from '../../../../types/chb1'

export default defineEventHandler(async event => {
  setHeader(event, 'cache-control', 'no-store')
  const query = getQuery(event)
  const scope: Record<string, string> = {}
  for (const key of ['tenantId', 'warehouseId', 'invoiceNo', 'revisionId', 'processingRunId']) {
    const value = query[key]
    if (typeof value !== 'string' || !value.trim() || value.length > 200)
      throw createError({ statusCode: 400, statusMessage: 'Invalid report scope', data: { message: `กรุณาระบุ ${key}` } })
    scope[key] = value.trim()
  }
  const schemaVersion = query.schemaVersion ?? '1'
  if (schemaVersion !== '1' && schemaVersion !== '5')
    throw createError({ statusCode: 400, statusMessage: 'Invalid schemaVersion' })
  scope.schemaVersion = schemaVersion
  const fetchReport = async (force = false) => {
    const { session } = await requireAuthorizedSession(event, force)
    if (!session.permissions.includes('chb1.read')) throw createError({ statusCode: 403, statusMessage: 'Forbidden' })
    return $fetch<Chb1Report>(backendUrl(event, '/api/ddd/reports/chb1'), {
      query: scope, headers: { Authorization: `Bearer ${session.accessToken}` }, timeout: 35000
    })
  }
  let report: Chb1Report
  try {
    try { report = await fetchReport() }
    catch (error: any) {
      if (error?.statusCode === 401 || error?.status === 401) report = await fetchReport(true)
      else throw error
    }
  } catch (error: any) {
    const status = error?.statusCode || error?.status
    throw createError({ statusCode: [400, 401, 403].includes(status) ? status : 502,
      statusMessage: 'Report data unavailable', data: { message: error?.data?.message || 'ไม่สามารถโหลดข้อมูลรายงานได้' } })
  }
  const config = useRuntimeConfig(event)
  try {
    const pdf = await renderChb1Pdf(report, String(config.puppeteerExecutablePath), config.puppeteerNoSandbox === true)
    setHeader(event, 'content-type', 'application/pdf')
    setHeader(event, 'content-disposition', 'attachment; filename="CHB1.pdf"')
    return Buffer.from(pdf)
  } catch (error) {
    throw createError({ statusCode: error instanceof Chb1PdfBusyError ? 503 : 500,
      statusMessage: 'PDF generation failed', data: { message: error instanceof Chb1PdfBusyError ? 'กำลังสร้างรายงานหลายรายการ กรุณาลองใหม่' : 'สร้าง PDF ไม่สำเร็จ กรุณาตรวจสอบการตั้งค่า Chromium ที่เซิร์ฟเวอร์' } })
  }
})
