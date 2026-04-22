import type { Hono } from 'hono';
import { respond, type ErrorResult } from '@/backend/http/response';
import { getLogger, getSupabase, type AppEnv } from '@/backend/hono/context';
import { getConcertList, getConcertDetail } from './service';
import { concertErrorCodes, type ConcertServiceError } from './error';
import { ConcertIdParamSchema } from './schema';

export const registerConcertRoutes = (app: Hono<AppEnv>) => {
  /**
   * GET /api/concerts
   * 예약 가능한 콘서트 목록 조회
   */
  app.get('/api/concerts', async (c) => {
    const supabase = getSupabase(c);
    const logger = getLogger(c);

    const result = await getConcertList(supabase);

    if (!result.ok) {
      const errorResult = result as ErrorResult<ConcertServiceError, unknown>;

      if (errorResult.error.code === concertErrorCodes.fetchError) {
        logger.error('Failed to fetch concerts', errorResult.error.message);
      }

      return respond(c, result);
    }

    return respond(c, result);
  });

  /**
   * GET /api/concerts/:concertId
   * 콘서트 상세 정보 조회
   */
  app.get('/api/concerts/:concertId', async (c) => {
    const concertId = c.req.param('concertId');

    // 1. Path Parameter 검증
    const parsedParams = ConcertIdParamSchema.safeParse({ concertId });

    if (!parsedParams.success) {
      return respond(
        c,
        {
          ok: false,
          status: 400,
          error: {
            code: concertErrorCodes.invalidId,
            message: 'The provided concert ID is invalid.',
            details: parsedParams.error.format(),
          },
        },
      );
    }

    // 2. Service 호출
    const supabase = getSupabase(c);
    const logger = getLogger(c);

    const result = await getConcertDetail(supabase, parsedParams.data.concertId);

    // 3. 에러 핸들링
    if (!result.ok) {
      const errorResult = result as ErrorResult<ConcertServiceError, unknown>;

      if (errorResult.error.code === concertErrorCodes.notFound) {
        logger.warn('Concert not found', { concertId });
      } else if (errorResult.error.code === concertErrorCodes.fetchError) {
        logger.error('Failed to fetch concert detail', errorResult.error.message);
      }

      return respond(c, result);
    }

    // 4. 성공 응답
    return respond(c, result);
  });
};
