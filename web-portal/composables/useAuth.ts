import type { AuthSession } from '~/types/auth'

const STORAGE_KEY = 'accessflow.session'

export const useAuth = () => {
  const session = useState<AuthSession | null>('auth.session', () => null)
  const initialized = useState<boolean>('auth.initialized', () => false)
  const config = useRuntimeConfig()

  const removeLegacyTokens = () => {
    if (import.meta.client) localStorage.removeItem(STORAGE_KEY)
  }

  const restore = async (force = false) => {
    removeLegacyTokens()
    if (initialized.value && !force) return session.value
    try {
      const requestFetch = import.meta.server ? useRequestFetch() : $fetch
      session.value = await requestFetch<AuthSession>('/api/session/me')
    } catch {
      session.value = null
    } finally {
      initialized.value = true
    }
    return session.value
  }

  const login = async (Username: string, Password: string) => {
    const response = await $fetch<AuthSession>('/api/session/login', {
      method: 'POST', body: { Username, Password, DeviceName: 'Nuxt Web Portal' }
    })
    removeLegacyTokens()
    session.value = response
    initialized.value = true
    return response
  }

  const request = async <T>(path: string, options: Record<string, unknown> = {}) => {
    if (!initialized.value) await restore()
    if (!session.value) throw new Error('Session not found')
    try {
      return await $fetch<T>(`${config.public.apiBase}${path}`, options)
    }
    catch (error: any) {
      if (error?.status === 401 || error?.statusCode === 401) {
        session.value = null
        initialized.value = true
        await navigateTo('/login')
        throw new Error('Session expired. Please login again.')
      }
      throw error
    }
  }

  const logout = async () => {
    try { await $fetch('/api/session/logout', { method: 'POST' }) }
    finally {
      session.value = null
      initialized.value = true
      removeLegacyTokens()
    }
  }

  const heartbeat = async () => {
    if (!session.value) return
    await request<void>('/api/auth/heartbeat', { method: 'POST' })
  }

  const hasPermission = (permission: string) => session.value?.permissions?.includes(permission) ?? false

  return { session, initialized, restore, login, request, logout, heartbeat, hasPermission }
}
