export interface AuthSession {
  expiresAtUtc: string
  refreshExpiresAtUtc: string
  sessionId: string
  userId: number
  username: string
  roles: string[]
  permissions: string[]
}

export interface TokenResponse extends AuthSession {
  accessToken: string
  refreshToken: string
  tokenType: string
}

export interface ActiveSession {
  userId: number
  username: string
  sessionId: string
  deviceName?: string
  ipAddress?: string
  createdAtUtc: string
  lastActivityAtUtc: string
  expiresAtUtc: string
}
