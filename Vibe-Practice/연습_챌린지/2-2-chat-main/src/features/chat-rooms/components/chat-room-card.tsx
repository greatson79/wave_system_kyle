'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import type { ChatRoom } from '../types';
import { formatChatRoomTime } from '@/lib/utils/date';
import { getEmoticonById } from '@/constants/emoticons';
import { Card, CardContent } from '@/components/ui/card';

type ChatRoomCardProps = {
  chatRoom: ChatRoom;
};

export const ChatRoomCard: React.FC<ChatRoomCardProps> = ({ chatRoom }) => {
  const router = useRouter();

  const handleClick = () => {
    router.push(`/chat-rooms/${chatRoom.id}`);
  };

  const getLastMessageDisplay = () => {
    if (!chatRoom.last_message_type) {
      return '채팅방이 생성되었습니다';
    }

    if (chatRoom.last_message_type === 'emoticon') {
      const emoticon = getEmoticonById(chatRoom.last_message_emoticon_id || '');
      return emoticon ? `${emoticon.label} 이모티콘` : '[이모티콘]';
    }

    const content = chatRoom.last_message_content || '';
    return content.length > 50 ? `${content.slice(0, 50)}...` : content;
  };

  const lastMessageTime = chatRoom.last_message_time || chatRoom.created_at;

  return (
    <Card
      className="cursor-pointer hover:bg-accent transition-colors"
      onClick={handleClick}
    >
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <h3 className="text-base font-semibold text-foreground truncate">
              {chatRoom.name}
            </h3>
            <p className="text-sm text-muted-foreground truncate mt-1">
              {getLastMessageDisplay()}
            </p>
          </div>
          <time className="text-xs text-muted-foreground whitespace-nowrap">
            {formatChatRoomTime(lastMessageTime)}
          </time>
        </div>
      </CardContent>
    </Card>
  );
};
