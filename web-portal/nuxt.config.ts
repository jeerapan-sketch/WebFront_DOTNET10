export default defineNuxtConfig({
  compatibilityDate: '2025-05-15',
  devtools: { enabled: true },
  modules: ['@nuxt/icon'],
  css: ['~/assets/css/main.css'],
  runtimeConfig: {
    puppeteerExecutablePath: process.env.NUXT_PUPPETEER_EXECUTABLE_PATH || '',
    puppeteerNoSandbox: process.env.NUXT_PUPPETEER_NO_SANDBOX === 'true',
    apiProxyTarget: process.env.NUXT_API_PROXY_TARGET || 'http://localhost:5109',
    redisUrl: process.env.NUXT_REDIS_URL || '',
    redisPassword: process.env.NUXT_REDIS_PASSWORD || '',
    sessionCookieName: process.env.NUXT_SESSION_COOKIE_NAME || 'accessflow.sid',
    sessionCookieSecure: process.env.NUXT_SESSION_COOKIE_SECURE === 'true',
    sessionIdleSeconds: Number(process.env.NUXT_SESSION_IDLE_SECONDS || 600),
    public: { apiBase: process.env.NUXT_PUBLIC_API_BASE || '/backend' }
  },
  app: {
    head: {
      title: 'AccessFlow · RBAC Portal',
      meta: [{ name: 'description', content: 'JWT and RBAC administration portal' }]
    }
  }
})
