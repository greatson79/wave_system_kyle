import { Hono } from 'hono';
import { zValidator } from '@hono/zod-validator';
import type { AppEnv } from '@/backend/hono/context';
import { requireAuth } from '@/backend/middleware/auth';
import { respond, success, failure } from '@/backend/http/response';
import { CreateChatRoomRequestSchema } from './schema';
import { createChatRoom, getChatRoom, getMessages, listChatRooms } from './service';
import { ChatRoomErrorCode, chatRoomErrorMessages } from './error';

export const chatRoomRoutes = new Hono<AppEnv>();

// 채팅방 목록 조회
chatRoomRoutes.get('/api/chat-rooms', requireAuth(), async (c) => {
  const supabase = c.get('supabase');
  const logger = c.get('logger');

  try {
    const chatRooms = await listChatRooms(supabase);
    return respond(c, success({ data: chatRooms }, 200));
  } catch (error) {
    logger.error('채팅방 목록 조회 실패', { error });
    return respond(
      c,
      failure(500, 'INTERNAL_ERROR', '일시적인 오류가 발생했습니다.')
    );
  }
});

// 채팅방 생성
chatRoomRoutes.post(
  '/api/chat-rooms',
  requireAuth(),
  zValidator('json', CreateChatRoomRequestSchema),
  async (c) => {
    const data = c.req.valid('json');
    const userId = c.get('userId');
    const supabase = c.get('supabase');
    const logger = c.get('logger');

    try {
      const chatRoom = await createChatRoom(supabase, {
        name: data.name,
        userId,
      });

      logger.info('채팅방 생성 성공', { chatRoomId: chatRoom.id });

      return respond(
        c,
        success(
          {
            success: true as const,
            data: {
              id: chatRoom.id,
              name: chatRoom.name,
              created_at: chatRoom.created_at,
            },
            redirectTo: '/',
          },
          200
        )
      );
    } catch (error) {
      logger.error('채팅방 생성 실패', { error });
      return respond(
        c,
        failure(
          500,
          ChatRoomErrorCode.CREATE_FAILED,
          chatRoomErrorMessages.CHAT_ROOM_CREATE_FAILED
        )
      );
    }
  }
);

// 채팅방 정보 조회
chatRoomRoutes.get('/api/chat-rooms/:id', requireAuth(), async (c) => {
  const roomId = c.req.param('id');
  const supabase = c.get('supabase');
  const logger = c.get('logger');

  try {
    const chatRoom = await getChatRoom(supabase, roomId);

    if (!chatRoom) {
      return respond(
        c,
        failure(
          404,
          ChatRoomErrorCode.NOT_FOUND,
          chatRoomErrorMessages.CHAT_ROOM_NOT_FOUND
        )
      );
    }

    return respond(c, success(chatRoom, 200));
  } catch (error) {
    logger.error('채팅방 조회 실패', { error, roomId });
    return respond(
      c,
      failure(500, 'INTERNAL_ERROR', '채팅방 조회에 실패했습니다.')
    );
  }
});

// 메시지 목록 조회
chatRoomRoutes.get('/api/chat-rooms/:roomId/messages', requireAuth(), async (c) => {
  const roomId = c.req.param('roomId');
  const userId = c.get('userId');
  const supabase = c.get('supabase');
  const logger = c.get('logger');

  const limit = parseInt(c.req.query('limit') || '50', 10);
  const offset = parseInt(c.req.query('offset') || '0', 10);

  try {
    // 채팅방 존재 확인
    const chatRoom = await getChatRoom(supabase, roomId);
    if (!chatRoom) {
      return respond(
        c,
        failure(
          404,
          ChatRoomErrorCode.NOT_FOUND,
          chatRoomErrorMessages.CHAT_ROOM_NOT_FOUND
        )
      );
    }

    const result = await getMessages(supabase, roomId, userId, limit, offset);
    return respond(c, success(result, 200));
  } catch (error) {
    logger.error('메시지 목록 조회 실패', { error, roomId });
    return respond(
      c,
      failure(500, 'INTERNAL_ERROR', '메시지 목록 조회에 실패했습니다.')
    );
  }
});
