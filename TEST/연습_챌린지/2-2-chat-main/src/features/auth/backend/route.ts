import { Hono } from 'hono';
import { zValidator } from '@hono/zod-validator';
import type { AppEnv } from '@/backend/hono/context';
import { respond, failure } from '@/backend/http/response';
import { LoginRequestSchema, SignupRequestSchema } from './schema';
import { login, signupUser } from './service';
import { requireAuth } from '@/backend/middleware/auth';

export const authRoutes = new Hono<AppEnv>();

/**
 * POST /api/auth/signup
 * 사용자 회원가입
 */
authRoutes.post(
  '/api/auth/signup',
  zValidator('json', SignupRequestSchema),
  async (c) => {
    const logger = c.get('logger');
    const supabase = c.get('supabase');
    const data = c.req.valid('json');

    logger.info('회원가입 요청', { email: data.email });

    const result = await signupUser(supabase, data);

    return respond(c, result);
  },
);

/**
 * POST /api/auth/login
 * 사용자 로그인
 */
authRoutes.post(
  '/api/auth/login',
  zValidator('json', LoginRequestSchema),
  async (c) => {
    const { email, password } = c.req.valid('json');
    const supabase = c.get('supabase');
    const redirectedFrom = c.req.query('redirectedFrom');

    const result = await login(supabase, email, password, redirectedFrom);
    return respond(c, result);
  },
);

/**
 * POST /api/auth/logout
 * 사용자 로그아웃
 */
authRoutes.post('/api/auth/logout', requireAuth(), async (c) => {
  const supabase = c.get('supabase');
  const logger = c.get('logger');

  try {
    const { error } = await supabase.auth.signOut();

    if (error) {
      logger.error('Logout failed', error);
      return respond(c, failure(500, 'LOGOUT_FAILED', '로그아웃에 실패했습니다'));
    }

    return c.json({ success: true, message: '로그아웃이 완료되었습니다' });
  } catch (error) {
    logger.error('Logout exception', error);
    return respond(c, failure(500, 'INTERNAL_ERROR', '서버 오류가 발생했습니다'));
  }
});
