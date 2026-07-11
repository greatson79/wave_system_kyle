import type { SupabaseClient } from '@supabase/supabase-js';
import type { SendMessageRequest } from './schema';

type SendMessageParams = SendMessageRequest & {
  roomId: string;
  userId: string;
};

// 메시지 전송
export async function sendMessage(
  supabase: SupabaseClient,
  params: SendMessageParams
) {
  // 채팅방 존재 확인
  const { data: room } = await supabase
    .from('chat_rooms')
    .select('id')
    .eq('id', params.roomId)
    .single();

  if (!room) {
    throw new Error('채팅방을 찾을 수 없습니다.');
  }

  // 답장 대상 확인 (선택)
  let replyToMessageId = params.reply_to_message_id || null;
  if (replyToMessageId) {
    const { data: replyMsg } = await supabase
      .from('messages')
      .select('id')
      .eq('id', replyToMessageId)
      .single();

    if (!replyMsg) {
      replyToMessageId = null; // 답장 대상 없으면 일반 메시지로 저장
    }
  }

  // 메시지 삽입
  const { data: newMessage, error } = await supabase
    .from('messages')
    .insert({
      chat_room_id: params.roomId,
      sender_id: params.userId,
      message_type: params.message_type,
      content: params.message_type === 'text' ? params.content : null,
      emoticon_id: params.message_type === 'emoticon' ? params.emoticon_id : null,
      reply_to_message_id: replyToMessageId,
    })
    .select()
    .single();

  if (error) {
    throw new Error('메시지 삽입 실패: ' + error.message);
  }

  return newMessage;
}

// 좋아요 추가
export async function addLike(
  supabase: SupabaseClient,
  messageId: string,
  userId: string
) {
  // 메시지 존재 및 본인 메시지 확인
  const { data: message } = await supabase
    .from('messages')
    .select('sender_id')
    .eq('id', messageId)
    .single();

  if (!message) {
    throw new Error('메시지를 찾을 수 없습니다.');
  }

  if (message.sender_id === userId) {
    throw new Error('본인 메시지에는 좋아요를 할 수 없습니다.');
  }

  // 좋아요 삽입 (중복 시 UNIQUE 제약으로 에러 무시)
  const { error } = await supabase
    .from('message_likes')
    .insert({ message_id: messageId, user_id: userId });

  // 중복 좋아요는 에러 무시 (멱등성)
  if (error && error.code !== '23505') {
    throw error;
  }
}

// 좋아요 취소
export async function removeLike(
  supabase: SupabaseClient,
  messageId: string,
  userId: string
) {
  await supabase
    .from('message_likes')
    .delete()
    .eq('message_id', messageId)
    .eq('user_id', userId);
}

// 메시지 일괄 삭제
export async function deleteMessages(
  supabase: SupabaseClient,
  messageIds: string[],
  userId: string
): Promise<number> {
  // 본인 메시지만 삭제
  const { data, error } = await supabase
    .from('messages')
    .delete()
    .in('id', messageIds)
    .eq('sender_id', userId)
    .select();

  if (error) {
    throw new Error('메시지 삭제 실패: ' + error.message);
  }

  return data?.length || 0;
}
