export const USER_MANAGE_PERMISSION = 'user.manage'

export const canManageSessions = (permissions?: readonly string[] | null) =>
  permissions?.includes(USER_MANAGE_PERMISSION) ?? false
