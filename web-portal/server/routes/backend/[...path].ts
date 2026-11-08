import { assertSameOrigin, backendUrl, clearBrowserSession, requireAuthorizedSession } from '../../utils/bff-auth'
import { deleteStoredSession } from '../../utils/session-store'

const blockedTokenPaths = new Set(['api/auth/login', 'api/auth/refresh'])
const excludedRequestHeaders = new Set([
  'authorization', 'cookie', 'host', 'content-length', 'connection',
  'transfer-encoding', 'upgrade', 'proxy-authorization'
])

const forwardHeaders = (event: Parameters<typeof getRequestHeaders>[0]) => Object.fromEntries(
  Object.entries(getRequestHeaders(event))
    .filter(([name]) => !excludedRequestHeaders.has(name.toLowerCase()))
    .map(([name, value]) => [name, Array.isArray(value) ? value.join(', ') : value])
    .filter((entry): entry is [string, string] => typeof entry[1] === 'string')
)

export default defineEventHandler(async (event) => {
  setHeader(event, 'cache-control', 'no-store')
  const path = event.context.params?.path?.replace(/^\/+/, '')
  if (!path) throw createError({ statusCode: 400, statusMessage: 'API path is required.' })
  if (blockedTokenPaths.has(path.toLowerCase())) {
    throw createError({ statusCode: 404, statusMessage: 'Route not found.' })
  }

  assertSameOrigin(event)
  const method = getMethod(event).toUpperCase()
  const query = getRequestURL(event).search
  const body = ['GET', 'HEAD'].includes(method) ? undefined : await readRawBody(event, false)

  const invoke = async (forceRefresh = false) => {
    const authorized = await requireAuthorizedSession(event, forceRefresh)
    const response = await $fetch.raw(backendUrl(event, `/${path}${query}`), {
      method: method as any,
      body,
      headers: {
        ...forwardHeaders(event),
        Authorization: `Bearer ${authorized.session.accessToken}`
      },
      ignoreResponseError: true
    })
    return { authorized, response }
  }

  let result = await invoke()
  if (result.response.status === 401) {
    try {
      result = await invoke(true)
    } catch {
      await deleteStoredSession(event, result.authorized.id)
      clearBrowserSession(event)
      throw createError({ statusCode: 401, statusMessage: 'Session expired.' })
    }
  }

  if (result.response.status === 401) {
    await deleteStoredSession(event, result.authorized.id)
    clearBrowserSession(event)
  }

  setResponseStatus(event, result.response.status, result.response.statusText)
  const contentType = result.response.headers.get('content-type')
  if (contentType) setHeader(event, 'content-type', contentType)
  return result.response._data
})
