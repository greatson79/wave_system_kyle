import type { MiddlewareHandler } from 'hono';
import type { AppEnv } from '@/backend/hono/context';

export const requireAuth = (): MiddlewareHandler<AppEnv> => {
  return async (c, next) => {
    const supabase = c.get('supabase');
    const { data, error } = await supabase.auth.getUser();

    if (error || !data.user) {
      return c.json(
        {
          error: {
            code: 'UNAUTHORIZED',
            message: '인증이 필요합니다.',
          },
        },
        401
      );
    }

    c.set('userId', data.user.id);
    await next();
  };
};
