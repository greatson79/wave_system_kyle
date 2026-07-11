import { Hono } from 'hono';
import { zValidator } from '@hono/zod-validator';
import type { AppEnv } from '@/backend/hono/context';
import { requireAuth } from '@/backend/middleware/auth';
import { respond, success, failure } from '@/backend/http/response';
import { SendMessageRequestSchema, BatchDeleteMessagesSchema } from './schema';
import { sendMessage, addLike, removeLike, deleteMessages } from './service';
import { MessageErrorCode, messageErrorMessages } from './error';

export const messageRoutes = new Hono<AppEnv>();

// 메시지 전송
messageRoutes.post(
  '/api/chat-rooms/:roomId/messages',
  requireAuth(),
  zValidator('json', SendMessageRequestSchema),
  async (c) => {
    const roomId = c.req.param('roomId');
    const userId = c.get('userId');
    const supabase = c.get('supabase');
    const logger = c.get('logger');
    const data = c.req.valid('json');

    try {
      const message = await sendMessage(supabase, {
        roomId,
        userId,
        ...data,
      });

      logger.info('메시지 전송 성공', { messageId: message.id });
      return respond(c, success(message, 201));
    } catch (error: any) {
      logger.error('메시지 전송 실패', { error, roomId });

      if (error.message.includes('채팅방을 찾을 수 없습니다')) {
        return respond(
          c,
          failure(
            404,
            MessageErrorCode.CHAT_ROOM_NOT_FOUND,
            messageErrorMessages.CHAT_ROOM_NOT_FOUND
          )
        );
      }

      return respond(
        c,
        failure(500, 'INTERNAL_ERROR', '메시지 전송에 실패했습니다.')
      );
    }
  }
);

// 좋아요 추가
messageRoutes.post('/api/messages/:messageId/likes', requireAuth(), async (c) => {
  const messageId = c.req.param('messageId');
  const userId = c.get('userId');
  const supabase = c.get('supabase');
  const logger = c.get('logger');

  try {
    await addLike(supabase, messageId, userId);
    logger.info('좋아요 추가 성공', { messageId, userId });
    return respond(c, success({ success: true }, 201));
  } catch (error: any) {
    logger.error('좋아요 추가 실패', { error, messageId });

    if (error.message.includes('본인 메시지')) {
      return respond(
        c,
        failure(400, 'LIKE_OWN_MESSAGE', '본인 메시지에는 좋아요를 할 수 없습니다.')
      );
    }

    if (error.message.includes('찾을 수 없습니다')) {
      return respond(
        c,
        failure(
          404,
          MessageErrorCode.MESSAGE_NOT_FOUND,
          messageErrorMessages.MESSAGE_NOT_FOUND
        )
      );
    }

    return respond(c, success({ success: true }, 200)); // 멱등성 처리
  }
});

// 좋아요 취소
messageRoutes.delete('/api/messages/:messageId/likes', requireAuth(), async (c) => {
  const messageId = c.req.param('messageId');
  const userId = c.get('userId');
  const supabase = c.get('supabase');
  const logger = c.get('logger');

  try {
    await removeLike(supabase, messageId, userId);
    logger.info('좋아요 취소 성공', { messageId, userId });
    return respond(c, success({ success: true }, 200));
  } catch (error) {
    logger.error('좋아요 취소 실패', { error, messageId });
    return respond(c, success({ success: true }, 200)); // 멱등성 처리
  }
});

// 메시지 일괄 삭제
messageRoutes.delete(
  '/api/messages/batch',
  requireAuth(),
  zValidator('json', BatchDeleteMessagesSchema),
  async (c) => {
    const userId = c.get('userId');
    const supabase = c.get('supabase');
    const logger = c.get('logger');
    const { message_ids } = c.req.valid('json');

    try {
      const deletedCount = await deleteMessages(supabase, message_ids, userId);
      logger.info('메시지 일괄 삭제 성공', { deletedCount });
      return respond(c, success({ deleted_count: deletedCount }, 200));
    } catch (error) {
      logger.error('메시지 삭제 실패', { error });
      return respond(
        c,
        failure(500, 'INTERNAL_ERROR', '메시지 삭제에 실패했습니다.')
      );
    }
  }
);
