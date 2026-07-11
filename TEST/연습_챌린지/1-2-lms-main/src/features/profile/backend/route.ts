import type { Hono } from 'hono'
import type { AppEnv } from '@/backend/hono/context'
import { respond, failure } from '@/backend/http/response'
import { getLogger, getSupabase } from '@/backend/hono/context'
import { createProfileSchema } from './schema'
import { createProfile, getProfile } from './service'

export const registerProfileRoutes = (app: Hono<AppEnv>) => {
  // GET /api/profile - 현재 사용자 프로필 조회
  app.get('/api/profile', async (c) => {
    const supabase = getSupabase(c)
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      return c.json({ error: 'Unauthorized' }, 401)
    }

    const result = await getProfile(supabase, user.id)
    return respond(c, result)
  })

  // POST /api/profile - 프로필 생성
  app.post('/api/profile', async (c) => {
    const logger = getLogger(c)
    logger.info('Create profile request received')

    const supabase = getSupabase(c)
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      return c.json({ error: 'Unauthorized' }, 401)
    }

    const body = await c.req.json()
    const parsed = createProfileSchema.safeParse(body)

    if (!parsed.success) {
      return respond(
        c,
        failure(
          400,
          'INVALID_REQUEST',
          '입력값이 올바르지 않습니다.',
          parsed.error.format(),
        ),
      )
    }

    const result = await createProfile(supabase, user.id, parsed.data)
    return respond(c, result)
  })
}
