import type { TokenResponse } from '~/types/auth'
import { normalizeSession } from '~/utils/auth'
import { assertSameOrigin, backendUrl, setBrowserSession } from '../../utils/bff-auth'
import { createBrowserSessionId, saveStoredSession, toPublicSession } from '../../utils/session-store'

export default defineEventHandler(async (event) => {
  assertSameOrigin(event)
  const body = await readBody<{ Username?: string, Password?: string, DeviceName?: string }>(event)
  if (!body?.Username?.trim() || !body?.Password) {
    throw createError({ statusCode: 400, statusMessage: 'Username and password are required.' })
  }

  let response: TokenResponse
  try {
    response = await $fetch<TokenResponse>(backendUrl(event, '/api/auth/login'), {
      method: 'POST',
      body: {
        Username: body.Username,
        Password: body.Password,
        DeviceName: body.DeviceName || 'Nuxt Web Portal'
      },
      headers: { 'user-agent': getHeader(event, 'user-agent') || 'AccessFlow BFF' }
    })
  } catch (error: any) {
    const status = error?.response?.status || error?.statusCode || 502
    throw createError({
      statusCode: status === 401 ? 401 : 502,
      statusMessage: status === 401 ? 'Invalid username or password.' : 'Authentication service is unavailable.'
    })
  }
  const session = normalizeSession(response)
  if (!session) throw createError({ statusCode: 502, statusMessage: 'Invalid authentication response.' })

  const browserSessionId = createBrowserSessionId()
  await saveStoredSession(event, browserSessionId, session)
  setBrowserSession(event, browserSessionId, session)
  return toPublicSession(session)
})
