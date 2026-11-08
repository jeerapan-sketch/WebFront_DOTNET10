import { requireAuthorizedSession } from '../../utils/bff-auth'
import { toPublicSession } from '../../utils/session-store'

export default defineEventHandler(async (event) => {
  setHeader(event, 'cache-control', 'no-store')
  const { session } = await requireAuthorizedSession(event)
  return toPublicSession(session)
})
