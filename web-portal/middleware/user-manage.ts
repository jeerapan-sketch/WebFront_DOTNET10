import { canManageSessions } from '~/utils/permissions'

export default defineNuxtRouteMiddleware(async () => {
  const auth = useAuth()
  await auth.restore()
  if (!auth.session.value) return navigateTo('/login')
  if (!canManageSessions(auth.session.value.permissions)) return navigateTo('/')
})
