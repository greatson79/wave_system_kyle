import type { Hono } from 'hono';
import { failure, respond } from '@/backend/http/response';
import { getLogger, getSupabase, type AppEnv } from '@/backend/hono/context';
import { requireRole } from '@/backend/middleware/role-guard';
import {
  CreateCategoryRequestSchema,
  UpdateCategoryRequestSchema,
  CreateDifficultyRequestSchema,
  UpdateDifficultyRequestSchema,
} from './schema';
import { metadataErrorCodes } from './error';
import {
  getCategories,
  createCategory,
  updateCategory,
  getDifficulties,
  createDifficulty,
  updateDifficulty,
  getActiveCategories,
  getActiveDifficulties,
} from './service';

export const registerMetadataRoutes = (app: Hono<AppEnv>) => {
  /**
   * GET /api/operator/metadata/categories
   * 카테고리 목록 조회 (운영자 전용)
   */
  app.get('/api/operator/metadata/categories', requireRole(['operator']), async (c) => {
    const logger = getLogger(c);
    logger.info('Fetching categories list');

    const supabase = getSupabase(c);
    const result = await getCategories(supabase);

    return respond(c, result);
  });

  /**
   * POST /api/operator/metadata/categories
   * 카테고리 추가 (운영자 전용)
   */
  app.post('/api/operator/metadata/categories', requireRole(['operator']), async (c) => {
    const logger = getLogger(c);
    logger.info('Creating category');

    const body = await c.req.json();
    const parsedBody = CreateCategoryRequestSchema.safeParse(body);

    if (!parsedBody.success) {
      return respond(
        c,
        failure(
          400,
          metadataErrorCodes.invalidRequest,
          '입력값이 올바르지 않습니다.',
          parsedBody.error.format(),
        ),
      );
    }

    const supabase = getSupabase(c);
    const result = await createCategory(supabase, parsedBody.data);

    return respond(c, result);
  });

  /**
   * PATCH /api/operator/metadata/categories/:id
   * 카테고리 수정 (운영자 전용)
   */
  app.patch(
    '/api/operator/metadata/categories/:id',
    requireRole(['operator']),
    async (c) => {
      const logger = getLogger(c);
      const categoryId = c.req.param('id');

      logger.info('Updating category', { categoryId });

      const body = await c.req.json();
      const parsedBody = UpdateCategoryRequestSchema.safeParse(body);

      if (!parsedBody.success) {
        return respond(
          c,
          failure(
            400,
            metadataErrorCodes.invalidRequest,
            '입력값이 올바르지 않습니다.',
            parsedBody.error.format(),
          ),
        );
      }

      const supabase = getSupabase(c);
      const result = await updateCategory(supabase, categoryId, parsedBody.data);

      return respond(c, result);
    },
  );

  /**
   * GET /api/operator/metadata/difficulties
   * 난이도 목록 조회 (운영자 전용)
   */
  app.get('/api/operator/metadata/difficulties', requireRole(['operator']), async (c) => {
    const logger = getLogger(c);
    logger.info('Fetching difficulties list');

    const supabase = getSupabase(c);
    const result = await getDifficulties(supabase);

    return respond(c, result);
  });

  /**
   * POST /api/operator/metadata/difficulties
   * 난이도 추가 (운영자 전용)
   */
  app.post('/api/operator/metadata/difficulties', requireRole(['operator']), async (c) => {
    const logger = getLogger(c);
    logger.info('Creating difficulty');

    const body = await c.req.json();
    const parsedBody = CreateDifficultyRequestSchema.safeParse(body);

    if (!parsedBody.success) {
      return respond(
        c,
        failure(
          400,
          metadataErrorCodes.invalidRequest,
          '입력값이 올바르지 않습니다.',
          parsedBody.error.format(),
        ),
      );
    }

    const supabase = getSupabase(c);
    const result = await createDifficulty(supabase, parsedBody.data);

    return respond(c, result);
  });

  /**
   * PATCH /api/operator/metadata/difficulties/:id
   * 난이도 수정 (운영자 전용)
   */
  app.patch(
    '/api/operator/metadata/difficulties/:id',
    requireRole(['operator']),
    async (c) => {
      const logger = getLogger(c);
      const difficultyId = c.req.param('id');

      logger.info('Updating difficulty', { difficultyId });

      const body = await c.req.json();
      const parsedBody = UpdateDifficultyRequestSchema.safeParse(body);

      if (!parsedBody.success) {
        return respond(
          c,
          failure(
            400,
            metadataErrorCodes.invalidRequest,
            '입력값이 올바르지 않습니다.',
            parsedBody.error.format(),
          ),
        );
      }

      const supabase = getSupabase(c);
      const result = await updateDifficulty(supabase, difficultyId, parsedBody.data);

      return respond(c, result);
    },
  );

  /**
   * GET /api/metadata/categories
   * 활성화된 카테고리 목록 조회 (공개)
   */
  app.get('/api/metadata/categories', async (c) => {
    const logger = getLogger(c);
    logger.info('Fetching active categories (public)');

    const supabase = getSupabase(c);
    const result = await getActiveCategories(supabase);

    return respond(c, result);
  });

  /**
   * GET /api/metadata/difficulties
   * 활성화된 난이도 목록 조회 (공개)
   */
  app.get('/api/metadata/difficulties', async (c) => {
    const logger = getLogger(c);
    logger.info('Fetching active difficulties (public)');

    const supabase = getSupabase(c);
    const result = await getActiveDifficulties(supabase);

    return respond(c, result);
  });
};
