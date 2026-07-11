'use client';

import React, { useState } from 'react';
import type { Message } from '@/features/messages/types';
import { useChatRoomContext } from '../context/chat-room-context';
import { useToggleLike } from '@/features/messages/hooks/useToggleLike';
import { useCurrentUser } from '@/features/auth/hooks/useCurrentUser';
import { formatMessageTime } from '@/lib/utils/date';
import { getEmoticonById } from '@/constants/emoticons';
import { Heart, MoreVertical, Reply, Trash } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

type MessageItemProps = {
  message: Message;
  roomId: string;
};

export const MessageItem: React.FC<MessageItemProps> = ({ message, roomId }) => {
  const { state, dispatch } = useChatRoomContext();
  const { user } = useCurrentUser();
  const toggleLike = useToggleLike(roomId);
  const isMyMessage = user?.id === message.sender_id;
  const isSelected = state.deleteMode.selectedMessageIds.includes(message.id);

  const emoticon =
    message.message_type === 'emoticon' && message.emoticon_id
      ? getEmoticonById(message.emoticon_id)
      : null;

  const handleLikeClick = () => {
    if (isMyMessage) return; // 본인 메시지는 좋아요 불가

    toggleLike.mutate({
      messageId: message.id,
      isLiked: message.is_liked_by_me,
    });
  };

  const handleReply = () => {
    dispatch({ type: 'SET_REPLY_TARGET', payload: message });
  };

  const handleDelete = () => {
    dispatch({ type: 'ENTER_DELETE_MODE', payload: message.id });
  };

  return (
    <div
      className={cn('flex gap-2', isMyMessage ? 'flex-row-reverse' : 'flex-row')}
    >
      {/* 삭제 모드: 체크박스 (내 메시지만) */}
      {state.deleteMode.isActive && isMyMessage && (
        <div className="flex items-end pb-1">
          <Checkbox
            checked={isSelected}
            onCheckedChange={() =>
              dispatch({ type: 'TOGGLE_MESSAGE_SELECTION', payload: message.id })
            }
          />
        </div>
      )}

      {/* 메시지 본문 */}
      <div
        className={cn(
          'flex flex-col gap-1 max-w-[70%]',
          isMyMessage ? 'items-end' : 'items-start'
        )}
      >
        {/* 발신자 닉네임 (남의 메시지만) */}
        {!isMyMessage && (
          <span className="text-xs text-muted-foreground px-2">
            {message.sender_nickname}
          </span>
        )}

        {/* 답장 정보 (있는 경우) */}
        {message.reply_to && (
          <div className="px-3 py-1 bg-muted rounded text-xs text-muted-foreground">
            <span className="font-semibold">{message.reply_to.sender_nickname}</span>
            <span className="mx-1">›</span>
            <span>
              {message.reply_to.message_type === 'text'
                ? message.reply_to.content
                : getEmoticonById(message.reply_to.emoticon_id || '')?.label}
            </span>
          </div>
        )}

        {/* 메시지 내용 */}
        <div
          className={cn(
            'px-4 py-2 rounded-2xl',
            isMyMessage ? 'bg-yellow-300 text-black' : 'bg-white border text-black'
          )}
        >
          {message.message_type === 'text' ? (
            <p className="text-sm whitespace-pre-wrap break-words">{message.content}</p>
          ) : (
            <span className="text-4xl">{emoticon?.label}</span>
          )}
        </div>

        {/* 메시지 하단 정보 (좋아요, 시간, 메뉴) */}
        <div
          className={cn(
            'flex items-center gap-2 px-2',
            isMyMessage ? 'flex-row-reverse' : 'flex-row'
          )}
        >
          {/* 좋아요 */}
          {(message.like_count > 0 || !isMyMessage) && (
            <button
              onClick={handleLikeClick}
              disabled={isMyMessage}
              className="flex items-center gap-1 text-xs disabled:cursor-not-allowed"
            >
              <Heart
                className={cn(
                  'h-3 w-3',
                  message.is_liked_by_me
                    ? 'fill-pink-500 text-pink-500'
                    : 'text-gray-400'
                )}
              />
              {message.like_count > 0 && (
                <span className="text-muted-foreground">{message.like_count}</span>
              )}
            </button>
          )}

          {/* 시간 */}
          <span className="text-xs text-muted-foreground">
            {formatMessageTime(message.created_at)}
          </span>

          {/* 메뉴 버튼 (일반 모드) */}
          {!state.deleteMode.isActive && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="h-5 w-5">
                  <MoreVertical className="h-3 w-3" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align={isMyMessage ? 'end' : 'start'}>
                {!isMyMessage && (
                  <DropdownMenuItem onClick={handleReply}>
                    <Reply className="mr-2 h-4 w-4" />
                    답장
                  </DropdownMenuItem>
                )}
                {isMyMessage && (
                  <DropdownMenuItem onClick={handleDelete} className="text-destructive">
                    <Trash className="mr-2 h-4 w-4" />
                    삭제
                  </DropdownMenuItem>
                )}
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>
      </div>
    </div>
  );
};
