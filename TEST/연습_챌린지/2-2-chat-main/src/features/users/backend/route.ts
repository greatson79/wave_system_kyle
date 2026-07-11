import { Hono } from 'hono';
import { zValidator } from '@hono/zod-validator';
import type { AppEnv } from '@/backend/hono/context';
import { requireAuth } from '@/backend/middleware/auth';
import { respond, success, failure } from '@/backend/http/response';
import { UpdateNicknameRequestSchema } from './schema';
import { getUserProfile, updateNickname } from './service';
import { UserErrorCode, userErrorMessages } from './error';

const app = new Hono<AppEnv>();

// GET /api/users/me - 사용자 프로필 조회
app.get('/me', requireAuth(), async (c) => {
  const userId = c.get('userId');
  const supabase = c.get('supabase');

  try {
    const profile = await getUserProfile(supabase, userId);

    if (!profile) {
      return respond(
        c,
        failure(404, UserErrorCode.USER_NOT_FOUND, userErrorMessages.USER_NOT_FOUND),
      );
    }

    return c.json(profile);
  } catch (error) {
    c.get('logger').error('Get user profile failed', error);
    return respond(c, failure(500, 'INTERNAL_ERROR', '프로필 조회에 실패했습니다'));
  }
});

// PATCH /api/users/me - 닉네임 수정
app.patch(
  '/me',
  requireAuth(),
  zValidator('json', UpdateNicknameRequestSchema),
  async (c) => {
    const userId = c.get('userId');
    const supabase = c.get('supabase');
    const { nickname } = c.req.valid('json');

    try {
      const updatedProfile = await updateNickname(supabase, userId, nickname);
      return respond(c, success(updatedProfile));
    } catch (error) {
      c.get('logger').error('Update nickname failed', error);
      return respond(c, failure(500, 'INTERNAL_ERROR', '닉네임 변경에 실패했습니다'));
    }
  },
);

export default app;
