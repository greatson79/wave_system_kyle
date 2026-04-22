import type { MessageType } from '@/features/messages/types';

export type ChatRoom = {
  id: string;
  name: string;
  created_at: string;

  // 최근 메시지 정보 (목록 조회 시)
  last_message_content?: string | null;
  last_message_type?: MessageType | null;
  last_message_emoticon_id?: string | null;
  last_message_time?: string | null;
  last_message_sender?: string | null;
};
