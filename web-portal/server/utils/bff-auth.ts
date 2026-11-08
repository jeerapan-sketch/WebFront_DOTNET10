import type { H3Event } from 'h3'
import type { TokenResponse } from '~/types/auth'
import { normalizeSession } from '~/utils/auth'
import {
  acquireRefreshLock,
  deleteStoredSession,
  getStoredSession,
  releaseRefreshLock,
  saveStoredSession
} from './session-store'

const cookieOptions = (event: H3Event, maxAge?: number) => {
  const config = useRuntimeConfig(event)
  return {
    httpOnly: true,
    secure: config.sessionCookieSecure,
    sameSite: 'lax' as const,
    path: '/',
    ...(maxAge ? { maxAge } : {})
  }
}

export const backendUrl = (event: H3Event, path: string) => {
  const base = String(useRuntimeConfig(event).apiProxyTarget).replace(/\/$/, '')
  return `${base}${path.startsWith('/') ? path : `/${path}`}`
}

export const getBrowserSessionId = (event: H3Event) => {
  const name = String(useRuntimeConfig(event).sessionCookieName)
  return getCookie(event, name) || null
}

export const setBrowserSession = (event: H3Event, id: string, session: TokenResponse) => {
  const maxAge = Math.max(1, Math.floor((Date.parse(session.refreshExpiresAtUtc) - Date.now()) / 1000))
  setHeader(event, 'cache-control', 'no-store')
  setCookie(event, String(useRuntimeConfig(event).sessionCookieName), id, cookieOptions(event, maxAge))
}

export const clearBrowserSession = (event: H3Event) => {
  setHeader(event, 'cache-control', 'no-store')
  deleteCookie(event, String(useRuntimeConfig(event).sessionCookieName), cookieOptions(event))
}

export const assertSameOrigin = (event: H3Event) => {
  const method = getMethod(event).toUpperCase()
  if (['GET', 'HEAD', 'OPTIONS'].includes(method)) return
  const origin = getHeader(event, 'origin')
  const requestUrl = getRequestURL(event)
  let originHost = ''
  try { originHost = origin ? new URL(origin).host : '' } catch { originHost = '' }
  if (!originHost || originHost !== requestUrl.host) {
    throw createError({ statusCode: 403, statusMessage: 'Cross-site request rejected.' })
  }
}

const refreshSession = async (event: H3Event, browserSessionId: string, force = false) => {
  let current = await getStoredSession(event, browserSessionId)
  if (!current) return null
  if (!force && Date.parse(current.expiresAtUtc) > Date.now() + 30_000) return current

  const owner = await acquireRefreshLock(event, browserSessionId)
  if (!owner) {
    for (let attempt = 0; attempt < 20; attempt++) {
      await new Promise(resolve => setTimeout(resolve, 100))
      const updated = await getStoredSession(event, browserSessionId)
      if (!updated) return null
      if (updated.accessToken !== current.accessToken) return updated
    }
    throw createError({ statusCode: 503, statusMessage: 'Session refresh is busy.' })
  }

  try {
    current = await getStoredSession(event, browserSessionId)
    if (!current) return null
    if (!force && Date.parse(current.expiresAtUtc) > Date.now() + 30_000) return current

    const response = await $fetch<TokenResponse>(backendUrl(event, '/api/auth/refresh'), {
      method: 'POST',
      body: { RefreshToken: current.refreshToken },
      headers: { 'user-agent': getHeader(event, 'user-agent') || 'AccessFlow BFF' }
    })
    const refreshed = normalizeSession(response)
    if (!refreshed) throw new Error('Invalid refresh response from API.')
    await saveStoredSession(event, browserSessionId, refreshed)
    setBrowserSession(event, browserSessionId, refreshed)
    return refreshed
  } catch (error: any) {
    const status = error?.response?.status || error?.statusCode || error?.status
    if (status === 401) {
      await deleteStoredSession(event, browserSessionId)
      clearBrowserSession(event)
      throw createError({ statusCode: 401, statusMessage: 'Session expired.' })
    }
    throw createError({ statusCode: 502, statusMessage: 'Authentication service is unavailable.' })
  } finally {
    await releaseRefreshLock(event, browserSessionId, owner)
  }
}

export const requireAuthorizedSession = async (event: H3Event, forceRefresh = false) => {
  const id = getBrowserSessionId(event)
  if (!id) throw createError({ statusCode: 401, statusMessage: 'Session cookie is missing.' })
  const session = await refreshSession(event, id, forceRefresh)
  if (!session) {
    clearBrowserSession(event)
    throw createError({ statusCode: 401, statusMessage: 'Session expired.' })
  }
  return { id, session }
}
