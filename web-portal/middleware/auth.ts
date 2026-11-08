export default defineNuxtRouteMiddleware(async () => {
  const auth = useAuth()
  await auth.restore()
  if (!auth.session.value) return navigateTo('/login')
})
