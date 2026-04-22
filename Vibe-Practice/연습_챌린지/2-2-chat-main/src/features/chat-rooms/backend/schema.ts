import { z } from 'zod';
import { MessageTypeEnum } from '@/features/messages/backend/schema';

export const CreateChatRoomRequestSchema = z.object({
  name: z
    .string()
    .min(1, '채팅방 이름을 입력해주세요')
    .max(50, '채팅방 이름은 최대 50자입니다'),
});

export const CreateChatRoomResponseSchema = z.object({
  success: z.literal(true),
  data: z.object({
    id: z.string(),
    name: z.string(),
    created_at: z.string(),
  }),
  redirectTo: z.string(),
});

export const ChatRoomListResponseSchema = z.object({
  data: z.array(
    z.object({
      id: z.string().uuid(),
      name: z.string(),
      created_at: z.string(),
      last_message_content: z.string().nullable(),
      last_message_type: MessageTypeEnum.nullable(),
      last_message_emoticon_id: z.string().nullable(),
      last_message_time: z.string().nullable(),
      last_message_sender: z.string().nullable(),
    })
  ),
});

export type CreateChatRoomRequest = z.infer<
  typeof CreateChatRoomRequestSchema
>;
export type CreateChatRoomResponse = z.infer<
  typeof CreateChatRoomResponseSchema
>;
export type ChatRoomListResponse = z.infer<typeof ChatRoomListResponseSchema>;
