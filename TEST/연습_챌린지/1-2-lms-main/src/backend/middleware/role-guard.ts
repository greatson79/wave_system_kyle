import type { Context, Next } from 'hono';
import type { AppEnv } from '@/backend/hono/context';
import { getSupabase, getLogger } from '@/backend/hono/context';
import { failure, respond } from '@/backend/http/response';

/**
 * 특정 역할만 접근 가능하도록 제한하는 미들웨어
 */
export const requireRole = (allowedRoles: string[]) => {
  return async (c: Context<AppEnv>, next: Next) => {
    const logger = getLogger(c);
    const userId = c.req.header('x-user-id');

    if (!userId) {
      logger.warn('Unauthorized access attempt: no user id');
      return respond(
        c,
        failure(401, 'UNAUTHORIZED', '인증이 필요합니다.'),
      );
    }

    const supabase = getSupabase(c);

    const { data: profile, error } = await supabase
      .from('profiles')
      .select('id, role')
      .eq('id', userId)
      .single();

    if (error || !profile) {
      logger.warn('Unauthorized access attempt: profile not found', { userId });
      return respond(
        c,
        failure(401, 'UNAUTHORIZED', '인증에 실패했습니다.'),
      );
    }

    if (!allowedRoles.includes(profile.role)) {
      logger.warn('Forbidden access attempt: insufficient role', {
        userId,
        userRole: profile.role,
        requiredRoles: allowedRoles,
      });
      return respond(
        c,
        failure(403, 'FORBIDDEN', '권한이 없습니다.'),
      );
    }

    await next();
  };
};
