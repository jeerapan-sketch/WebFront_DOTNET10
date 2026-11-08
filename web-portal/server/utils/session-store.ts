import { randomBytes, randomUUID } from 'node:crypto'
import Redis from 'ioredis'
import type { H3Event } from 'h3'
import type { AuthSession, TokenResponse } from '~/types/auth'
import { normalizeSession } from '~/utils/auth'

interface MemoryEntry {
  value: TokenResponse
  expiresAt: number
}

const memorySessions = new Map<string, MemoryEntry>()
const memoryLocks = new Map<string, number>()
let redisClient: Redis | null = null
let redisClientUrl = ''

const sessionKey = (id: string) => `accessflow:session:${id}`
const lockKey = (id: string) => `accessflow:refresh-lock:${id}`

const getRedis = (event: H3Event) => {
  const config = useRuntimeConfig(event)
  const url = typeof config.redisUrl === 'string' ? config.redisUrl.trim() : ''
  const password = typeof config.redisPassword === 'string' ? config.redisPassword.trim() : ''
  if (!url) return null
  if (!redisClient || redisClientUrl !== url) {
    redisClient?.disconnect()
    redisClientUrl = url
    redisClient = new Redis(url, {
      password: password || undefined,
      lazyConnect: true,
      maxRetriesPerRequest: 2,
      enableReadyCheck: true
    })
    redisClient.on('error', error => console.error('Redis session store error:', error.message))
  }
  return redisClient
}

const ttlSeconds = (event: H3Event, session: TokenResponse) => {
  const refreshTtl = Math.max(
    1,
    Math.floor((Date.parse(session.refreshExpiresAtUtc) - Date.now()) / 1000)
  )
  const configuredIdleTtl = Number(useRuntimeConfig(event).sessionIdleSeconds || 600)
  const idleTtl = Math.min(86_400, Math.max(120, configuredIdleTtl))
  return Math.min(refreshTtl, idleTtl)
}

export const createBrowserSessionId = () => randomBytes(32).toString('base64url')

export const getStoredSession = async (event: H3Event, id: string) => {
  const redis = getRedis(event)
  const memoryEntry = redis ? undefined : memorySessions.get(id)
  if (memoryEntry && memoryEntry.expiresAt <= Date.now()) {
    memorySessions.delete(id)
    return null
  }
  const raw = redis
    ? await redis.get(sessionKey(id))
    : memoryEntry?.value

  if (!raw) return null
  const parsed = typeof raw === 'string' ? JSON.parse(raw) : raw
  const session = normalizeSession(parsed)
  if (!session || Date.parse(session.refreshExpiresAtUtc) <= Date.now()) {
    await deleteStoredSession(event, id)
    return null
  }
  const ttl = ttlSeconds(event, session)
  if (redis) await redis.expire(sessionKey(id), ttl)
  else memorySessions.set(id, { value: session, expiresAt: Date.now() + ttl * 1000 })
  return session
}

export const saveStoredSession = async (event: H3Event, id: string, session: TokenResponse) => {
  const ttl = ttlSeconds(event, session)
  const redis = getRedis(event)
  if (redis) await redis.set(sessionKey(id), JSON.stringify(session), 'EX', ttl)
  else memorySessions.set(id, { value: session, expiresAt: Date.now() + ttl * 1000 })
}

export const deleteStoredSession = async (event: H3Event, id: string) => {
  const redis = getRedis(event)
  if (redis) await redis.del(sessionKey(id))
  else memorySessions.delete(id)
}

export const acquireRefreshLock = async (event: H3Event, id: string) => {
  const owner = randomUUID()
  const redis = getRedis(event)
  if (redis) {
    const result = await redis.set(lockKey(id), owner, 'PX', 10_000, 'NX')
    return result === 'OK' ? owner : null
  }

  const key = lockKey(id)
  const existingExpiry = memoryLocks.get(key) || 0
  if (existingExpiry > Date.now()) return null
  memoryLocks.set(key, Date.now() + 10_000)
  return owner
}

export const releaseRefreshLock = async (event: H3Event, id: string, owner: string) => {
  const redis = getRedis(event)
  if (redis) {
    await redis.eval(
      'if redis.call("get", KEYS[1]) == ARGV[1] then return redis.call("del", KEYS[1]) else return 0 end',
      1,
      lockKey(id),
      owner
    )
  } else {
    memoryLocks.delete(lockKey(id))
  }
}

export const toPublicSession = (session: TokenResponse): AuthSession => ({
  expiresAtUtc: session.expiresAtUtc,
  refreshExpiresAtUtc: session.refreshExpiresAtUtc,
  sessionId: session.sessionId,
  userId: session.userId,
  username: session.username,
  roles: session.roles,
  permissions: session.permissions
})
