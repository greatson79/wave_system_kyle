export type MessageType = 'text' | 'emoticon';

export type Message = {
  id: string;
  chat_room_id: string;
  sender_id: string;
  sender_nickname: string;
  message_type: MessageType;
  content: string | null;
  emoticon_id: string | null;
  reply_to_message_id: string | null;
  created_at: string;

  // 답장 정보 (있는 경우)
  reply_to?: {
    message_id: string;
    sender_nickname: string;
    message_type: MessageType;
    content: string | null;
    emoticon_id: string | null;
  };

  // 좋아요 정보
  like_count: number;
  is_liked_by_me: boolean;
};
