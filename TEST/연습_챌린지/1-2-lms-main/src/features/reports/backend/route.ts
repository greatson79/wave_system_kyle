import type { Hono } from 'hono';
import { failure, respond } from '@/backend/http/response';
import { getLogger, getSupabase, type AppEnv } from '@/backend/hono/context';
import { requireRole } from '@/backend/middleware/role-guard';
import {
  SubmitReportRequestSchema,
  ReportsListQuerySchema,
  UpdateReportRequestSchema,
} from './schema';
import { reportsErrorCodes } from './error';
import {
  submitReport,
  getReportsList,
  getReportDetail,
  updateReport,
} from './service';

export const registerReportsRoutes = (app: Hono<AppEnv>) => {
  /**
   * POST /api/reports
   * 신고 접수 (모든 로그인 사용자)
   */
  app.post('/api/reports', async (c) => {
    const logger = getLogger(c);
    const userId = c.req.header('x-user-id');

    if (!userId) {
      logger.warn('Unauthorized report submission: no user id');
      return respond(c, failure(401, reportsErrorCodes.unauthorized, '인증이 필요합니다.'));
    }

    const body = await c.req.json();
    const parsedBody = SubmitReportRequestSchema.safeParse(body);

    if (!parsedBody.success) {
      return respond(
        c,
        failure(
          400,
          reportsErrorCodes.invalidRequest,
          '입력값이 올바르지 않습니다.',
          parsedBody.error.format(),
        ),
      );
    }

    const supabase = getSupabase(c);
    const result = await submitReport(supabase, userId, parsedBody.data);

    return respond(c, result);
  });

  /**
   * GET /api/operator/reports
   * 신고 목록 조회 (운영자 전용)
   */
  app.get('/api/operator/reports', requireRole(['operator']), async (c) => {
    const logger = getLogger(c);
    logger.info('Fetching reports list');

    const query = c.req.query();
    const parsedQuery = ReportsListQuerySchema.safeParse(query);

    if (!parsedQuery.success) {
      return respond(
        c,
        failure(
          400,
          reportsErrorCodes.invalidRequest,
          '쿼리 파라미터가 올바르지 않습니다.',
          parsedQuery.error.format(),
        ),
      );
    }

    const supabase = getSupabase(c);
    const result = await getReportsList(supabase, parsedQuery.data);

    return respond(c, result);
  });

  /**
   * GET /api/operator/reports/:id
   * 신고 상세 조회 (운영자 전용)
   */
  app.get('/api/operator/reports/:id', requireRole(['operator']), async (c) => {
    const logger = getLogger(c);
    const reportId = c.req.param('id');

    logger.info('Fetching report detail', { reportId });

    const supabase = getSupabase(c);
    const result = await getReportDetail(supabase, reportId);

    return respond(c, result);
  });

  /**
   * PATCH /api/operator/reports/:id
   * 신고 처리 (운영자 전용)
   */
  app.patch('/api/operator/reports/:id', requireRole(['operator']), async (c) => {
    const logger = getLogger(c);
    const reportId = c.req.param('id');

    logger.info('Updating report', { reportId });

    const body = await c.req.json();
    const parsedBody = UpdateReportRequestSchema.safeParse(body);

    if (!parsedBody.success) {
      return respond(
        c,
        failure(
          400,
          reportsErrorCodes.invalidRequest,
          '입력값이 올바르지 않습니다.',
          parsedBody.error.format(),
        ),
      );
    }

    const supabase = getSupabase(c);
    const result = await updateReport(supabase, reportId, parsedBody.data);

    return respond(c, result);
  });
};
