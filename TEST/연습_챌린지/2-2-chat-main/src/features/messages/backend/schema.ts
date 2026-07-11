import { z } from 'zod';

export const MessageTypeEnum = z.enum(['text', 'emoticon']);

// 텍스트 메시지 전송
export const SendTextMessageSchema = z.object({
  message_type: z.literal('text'),
  content: z.string().min(1).max(1000),
  reply_to_message_id: z.string().uuid().optional(),
});

// 이모티콘 메시지 전송
export const SendEmoticonMessageSchema = z.object({
  message_type: z.literal('emoticon'),
  emoticon_id: z.string(),
  reply_to_message_id: z.string().uuid().optional(),
});

// 메시지 전송 (Union)
export const SendMessageRequestSchema = z.discriminatedUnion('message_type', [
  SendTextMessageSchema,
  SendEmoticonMessageSchema,
]);

// 메시지 일괄 삭제
export const BatchDeleteMessagesSchema = z.object({
  message_ids: z
    .array(z.string().uuid())
    .min(1, '삭제할 메시지를 선택해주세요'),
});

export type SendTextMessage = z.infer<typeof SendTextMessageSchema>;
export type SendEmoticonMessage = z.infer<typeof SendEmoticonMessageSchema>;
export type SendMessageRequest = z.infer<typeof SendMessageRequestSchema>;
export type BatchDeleteMessages = z.infer<typeof BatchDeleteMessagesSchema>;
