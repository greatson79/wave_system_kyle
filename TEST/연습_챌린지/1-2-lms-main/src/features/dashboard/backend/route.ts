import type { Hono } from 'hono';
import { failure, respond } from '@/backend/http/response';
import {
  getLogger,
  getSupabase,
  type AppEnv,
} from '@/backend/hono/context';
import { getLearnerDashboard, getInstructorDashboard } from './service';
import { dashboardErrorCodes } from './error';

export const registerDashboardRoutes = (app: Hono<AppEnv>) => {
  app.get('/api/dashboard/learner', async (c) => {
    const logger = getLogger(c);
    logger.info('Get learner dashboard request received at /api/dashboard/learner');

    // --- 디버깅 로그 추가 ---
    const userId = c.req.header('x-user-id');
    logger.info('[Dashboard Route] x-user-id header:', userId || 'NOT FOUND');
    logger.info('[Dashboard Route] All headers:', Object.fromEntries(c.req.raw.headers.entries()));
    // -----------------------

    if (!userId) {
      logger.error('[Dashboard Route] Permission denied - x-user-id header missing');
      return respond(
        c,
        failure(401, dashboardErrorCodes.permissionDenied, '인증이 필요합니다.'),
      );
    }

    const supabase = getSupabase(c);
    const result = await getLearnerDashboard(supabase, userId);

    return respond(c, result);
  });

  app.get('/api/dashboard/instructor', async (c) => {
    const logger = getLogger(c);
    logger.info('Get instructor dashboard request received at /api/dashboard/instructor');

    const userId = c.req.header('x-user-id');

    if (!userId) {
      logger.error('[Dashboard Route] Permission denied - x-user-id header missing');
      return respond(
        c,
        failure(401, dashboardErrorCodes.permissionDenied, '인증이 필요합니다.'),
      );
    }

    const supabase = getSupabase(c);
    const result = await getInstructorDashboard(supabase, userId);

    return respond(c, result);
  });
};
