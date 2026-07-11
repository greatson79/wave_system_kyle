'use client';

import React, { useEffect, useRef } from 'react';
import { useMessages } from '@/features/messages/hooks/useMessages';
import { MessageItem } from './message-item';
import { LoadingSpinner } from '@/components/common/loading-spinner';
import { EmptyState } from '@/components/common/empty-state';

type MessageListProps = {
  roomId: string;
};

export const MessageList: React.FC<MessageListProps> = ({ roomId }) => {
  const { data, isLoading, fetchNextPage, hasNextPage, isFetchingNextPage } =
    useMessages(roomId);
  const scrollRef = useRef<HTMLDivElement>(null);
  const observerTarget = useRef<HTMLDivElement>(null);

  // 무한 스크롤 Observer
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasNextPage && !isFetchingNextPage) {
          fetchNextPage();
        }
      },
      { threshold: 0.1 }
    );

    if (observerTarget.current) {
      observer.observe(observerTarget.current);
    }

    return () => observer.disconnect();
  }, [hasNextPage, isFetchingNextPage, fetchNextPage]);

  // 스크롤을 하단으로 이동 (초기 로드 시)
  useEffect(() => {
    if (scrollRef.current && data?.messages && !isLoading) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [data?.messages, isLoading]);

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (!data?.messages || data.messages.length === 0) {
    return (
      <EmptyState
        title="메시지가 없습니다"
        description="첫 메시지를 보내보세요!"
      />
    );
  }

  return (
    <div ref={scrollRef} className="flex flex-col h-full overflow-y-auto p-4 gap-3">
      {/* 무한 스크롤 감지 영역 (상단) */}
      <div ref={observerTarget} className="h-4">
        {isFetchingNextPage && (
          <div className="flex justify-center">
            <LoadingSpinner size="sm" />
          </div>
        )}
      </div>

      {/* 메시지 목록 */}
      {data.messages.map((message) => (
        <MessageItem key={message.id} message={message} roomId={roomId} />
      ))}
    </div>
  );
};
