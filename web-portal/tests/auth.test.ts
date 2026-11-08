import { describe, expect, it } from 'vitest'
import { normalizeSession } from '../utils/auth'

const camelCaseResponse = {
  accessToken: 'access-token',
  refreshToken: 'refresh-token',
  tokenType: 'Bearer',
  expiresAtUtc: '2026-08-14T10:00:00Z',
  refreshExpiresAtUtc: '2026-08-21T10:00:00Z',
  sessionId: 'session-1',
  userId: 3,
  username: 'user01',
  roles: ['USER'],
  permissions: ['abatement.read']
}

describe('normalizeSession', () => {
  it('accepts the camelCase response returned by the API', () => {
    expect(normalizeSession(camelCaseResponse)).toEqual(camelCaseResponse)
  })

  it('migrates a legacy PascalCase session', () => {
    const result = normalizeSession({
      AccessToken: 'access-token', RefreshToken: 'refresh-token',
      TokenType: 'Bearer', ExpiresAtUtc: '2026-08-14T10:00:00Z',
      RefreshExpiresAtUtc: '2026-08-21T10:00:00Z', SessionId: 'session-1',
      UserId: 3, Username: 'user01', Roles: ['USER'],
      Permissions: ['abatement.read']
    })

    expect(result?.username).toBe('user01')
    expect(result?.permissions).toContain('abatement.read')
  })

  it('rejects incomplete token responses', () => {
    expect(normalizeSession(null)).toBeNull()
    expect(normalizeSession({ accessToken: 'only-access-token' })).toBeNull()
  })
})
