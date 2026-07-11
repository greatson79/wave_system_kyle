'use client';

import React from 'react';
import Link from 'next/link';
import { Plus } from 'lucide-react';
import { useChatRoomsQuery } from '../hooks/useChatRoomsQuery';
import { ChatRoomCard } from './chat-room-card';
import { LoadingSpinner } from '@/components/common/loading-spinner';
import { ErrorMessage } from '@/components/common/error-message';
import { EmptyState } from '@/components/common/empty-state';
import { Button } from '@/components/ui/button';

export const ChatRoomList: React.FC = () => {
  const { data: chatRooms, isLoading, isError, error, refetch } = useChatRoomsQuery();

  if (isLoading) {
    return <LoadingSpinner size="lg" />;
  }

  if (isError) {
    return (
      <ErrorMessage
        message={error?.message || '채팅방 목록을 불러오는데 실패했습니다.'}
        onRetry={() => refetch()}
      />
    );
  }

  if (!chatRooms || chatRooms.length === 0) {
    return (
      <EmptyState
        title="아직 채팅방이 없습니다"
        description="첫 채팅방을 만들어보세요!"
        action={
          <Button asChild>
            <Link href="/chat-rooms/new">
              <Plus className="w-4 h-4 mr-2" />
              채팅방 추가
            </Link>
          </Button>
        }
      />
    );
  }

  return (
    <div className="space-y-3">
      {chatRooms.map((chatRoom) => (
        <ChatRoomCard key={chatRoom.id} chatRoom={chatRoom} />
      ))}
    </div>
  );
};
