import {
  assertSameOrigin,
  backendUrl,
  clearBrowserSession,
  getBrowserSessionId,
  requireAuthorizedSession
} from '../../utils/bff-auth'
import { deleteStoredSession } from '../../utils/session-store'

export default defineEventHandler(async (event) => {
  assertSameOrigin(event)
  const browserSessionId = getBrowserSessionId(event)
  try {
    const authorized = await requireAuthorizedSession(event)
    await $fetch(backendUrl(event, '/api/auth/logout'), {
      method: 'POST',
      headers: { Authorization: `Bearer ${authorized.session.accessToken}` }
    })
  } finally {
    if (browserSessionId) await deleteStoredSession(event, browserSessionId)
    clearBrowserSession(event)
  }
  setResponseStatus(event, 204)
  return null
})
