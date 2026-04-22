import type { Hono } from 'hono';
import {
  failure,
  respond,
  type ErrorResult,
} from '@/backend/http/response';
import {
  getLogger,
  getSupabase,
  type AppEnv,
} from '@/backend/hono/context';
import { SignupRequestSchema } from '@/features/auth/backend/schema';
import { signupUser } from './service';
import {
  authErrorCodes,
  type AuthServiceError,
} from './error';

export const registerAuthRoutes = (app: Hono<AppEnv>) => {
  app.post('/api/auth/signup', async (c) => {
    const logger = getLogger(c);
    logger.info('Signup request received at /auth/signup');

    const body = await c.req.json();
    const parsedBody = SignupRequestSchema.safeParse(body);

    if (!parsedBody.success) {
      return respond(
        c,
        failure(
          400,
          authErrorCodes.invalidRequest,
          '입력값이 올바르지 않습니다.',
          parsedBody.error.format(),
        ),
      );
    }

    const supabase = getSupabase(c);

    const result = await signupUser(supabase, parsedBody.data);

    if (!result.ok) {
      const errorResult = result as ErrorResult<AuthServiceError, unknown>;

      if (
        errorResult.error.code === authErrorCodes.authCreationFailed ||
        errorResult.error.code === authErrorCodes.profileCreationFailed ||
        errorResult.error.code === authErrorCodes.termsRecordFailed
      ) {
        logger.error('Failed to signup user', errorResult.error.message);
      }

      return respond(c, result);
    }

    return respond(c, result);
  });
};
