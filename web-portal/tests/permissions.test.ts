import { describe, expect, it } from 'vitest'
import { canManageSessions, USER_MANAGE_PERMISSION } from '../utils/permissions'

describe('session management permission', () => {
  it('allows a user with user.manage to see and enter session management', () => {
    expect(canManageSessions(['abatement.read', USER_MANAGE_PERMISSION])).toBe(true)
  })

  it.each([
    { label: 'another permission', permissions: ['abatement.read'] },
    { label: 'empty permissions', permissions: [] },
    { label: 'missing permissions', permissions: undefined }
  ])('denies access for $label', ({ permissions }) => {
    expect(canManageSessions(permissions)).toBe(false)
  })

  it('matches permission names exactly', () => {
    expect(canManageSessions(['User.Manage', 'user.manage.read'])).toBe(false)
  })
})
