import type { Hono } from 'hono';
import { failure, respond } from '@/backend/http/response';
import {
  getLogger,
  getSupabase,
  type AppEnv,
} from '@/backend/hono/context';
import { getCourseGrades } from './service';
import { gradesErrorCodes } from './error';

export const registerGradesRoutes = (app: Hono<AppEnv>) => {
  app.get('/api/courses/:courseId/grades', async (c) => {
    const logger = getLogger(c);
    const courseId = c.req.param('courseId');
    logger.info(`Get course grades request received for course ${courseId}`);

    const userId = c.req.header('x-user-id');
    if (!userId) {
      return respond(
        c,
        failure(401, gradesErrorCodes.unauthorized, '인증이 필요합니다.'),
      );
    }

    const supabase = getSupabase(c);
    const result = await getCourseGrades(supabase, userId, courseId);

    return respond(c, result);
  });
};
