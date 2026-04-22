import type { SupabaseClient } from '@supabase/supabase-js';
import type { ChatRoom } from '../types';
import type { Message } from '@/features/messages/types';

export type CreateChatRoomParams = {
  name: string;
  userId: string;
};

export async function createChatRoom(
  supabase: SupabaseClient,
  params: CreateChatRoomParams
): Promise<ChatRoom> {
  const { data, error } = await supabase
    .from('chat_rooms')
    .insert({
      name: params.name.trim(),
    })
    .select('id, name, created_at')
    .single();

  if (error || !data) {
    throw new Error('채팅방 생성 실패: ' + error?.message);
  }

  return data;
}

// 채팅방 정보 조회
export async function getChatRoom(
  supabase: SupabaseClient,
  roomId: string
): Promise<ChatRoom | null> {
  const { data, error } = await supabase
    .from('chat_rooms')
    .select('id, name, created_at')
    .eq('id', roomId)
    .single();

  if (error || !data) {
    return null;
  }

  return data;
}

// 메시지 목록 조회
export async function getMessages(
  supabase: SupabaseClient,
  roomId: string,
  userId: string,
  limit: number,
  offset: number
): Promise<{ messages: Message[] }> {
  // 메시지 조회 (발신자, 답장, 좋아요 정보 포함)
  const { data, error } = await supabase
    .from('messages')
    .select(`
      id,
      chat_room_id,
      sender_id,
      message_type,
      content,
      emoticon_id,
      reply_to_message_id,
      created_at,
      sender:user_profiles!sender_id(nickname),
      reply_to:messages!reply_to_message_id(
        id,
        sender_id,
        message_type,
        content,
        emoticon_id,
        sender:user_profiles!sender_id(nickname)
      ),
      likes:message_likes(user_id)
    `)
    .eq('chat_room_id', roomId)
    .order('created_at', { ascending: true })
    .range(offset, offset + limit - 1);

  if (error) {
    throw new Error('메시지 조회 실패: ' + error.message);
  }

  // 데이터 변환
  const messages: Message[] = (data || []).map((msg: any) => ({
    id: msg.id,
    chat_room_id: msg.chat_room_id,
    sender_id: msg.sender_id,
    sender_nickname: msg.sender?.nickname || '알 수 없음',
    message_type: msg.message_type,
    content: msg.content,
    emoticon_id: msg.emoticon_id,
    reply_to_message_id: msg.reply_to_message_id,
    created_at: msg.created_at,
    reply_to: msg.reply_to && msg.reply_to.id
      ? {
          message_id: msg.reply_to.id,
          sender_nickname: msg.reply_to.sender?.nickname || '알 수 없음',
          message_type: msg.reply_to.message_type,
          content: msg.reply_to.content,
          emoticon_id: msg.reply_to.emoticon_id,
        }
      : undefined,
    like_count: msg.likes?.length || 0,
    is_liked_by_me: msg.likes?.some((like: any) => like.user_id === userId) || false,
  }));

  return { messages };
}

export async function listChatRooms(
  supabase: SupabaseClient
): Promise<ChatRoom[]> {
  const { data: chatRooms, error: roomsError } = await supabase
    .from('chat_rooms')
    .select('*')
    .order('created_at', { ascending: false })
    .limit(100);

  if (roomsError) {
    throw new Error(`채팅방 목록 조회 실패: ${roomsError.message}`);
  }

  const chatRoomsWithMessages = await Promise.all(
    (chatRooms || []).map(async (room) => {
      const { data: messages } = await supabase
        .from('messages')
        .select('content, message_type, emoticon_id, created_at, sender:user_profiles(nickname)')
        .eq('chat_room_id', room.id)
        .order('created_at', { ascending: false })
        .limit(1)
        .maybeSingle();

      const sender = messages?.sender as unknown;
      const senderNickname = Array.isArray(sender) && sender.length > 0
        ? (sender[0] as { nickname: string }).nickname
        : null;

      return {
        ...room,
        last_message_content: messages?.content || null,
        last_message_type: messages?.message_type || null,
        last_message_emoticon_id: messages?.emoticon_id || null,
        last_message_time: messages?.created_at || null,
        last_message_sender: senderNickname,
      };
    })
  );

  return chatRoomsWithMessages.sort((a, b) => {
    const timeA = a.last_message_time || a.created_at;
    const timeB = b.last_message_time || b.created_at;
    return new Date(timeB).getTime() - new Date(timeA).getTime();
  });
}
