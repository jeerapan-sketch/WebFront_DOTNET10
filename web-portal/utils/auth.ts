import type { TokenResponse } from '~/types/auth'

export const normalizeSession = (value: any): TokenResponse | null => {
  if (!value) return null

  const normalized: TokenResponse = {
    accessToken: value.accessToken ?? value.AccessToken,
    refreshToken: value.refreshToken ?? value.RefreshToken,
    tokenType: value.tokenType ?? value.TokenType ?? 'Bearer',
    expiresAtUtc: value.expiresAtUtc ?? value.ExpiresAtUtc,
    refreshExpiresAtUtc: value.refreshExpiresAtUtc ?? value.RefreshExpiresAtUtc,
    sessionId: value.sessionId ?? value.SessionId,
    userId: value.userId ?? value.UserId,
    username: value.username ?? value.Username,
    roles: value.roles ?? value.Roles ?? [],
    permissions: value.permissions ?? value.Permissions ?? []
  }

  return normalized.accessToken && normalized.refreshToken ? normalized : null
}
