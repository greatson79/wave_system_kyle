'use client';

import { use } from 'react';
import { useRouter } from 'next/navigation';
import { ChatRoomProvider } from '@/features/chat-rooms/context/chat-room-context';
import { useChatRoom } from '@/features/chat-rooms/hooks/useChatRoom';
import { useMessages } from '@/features/messages/hooks/useMessages';
import { ChatRoomHeader } from '@/features/chat-rooms/components/chat-room-header';
import { MessageList } from '@/features/chat-rooms/components/message-list';
import { MessageInput } from '@/features/chat-rooms/components/message-input';
import { DeleteModeFooter } from '@/features/chat-rooms/components/delete-mode-footer';
import { EmoticonPicker } from '@/features/chat-rooms/components/emoticon-picker';
import { useChatRoomContext } from '@/features/chat-rooms/context/chat-room-context';
import { LoadingSpinner } from '@/components/common/loading-spinner';
import { ErrorMessage } from '@/components/common/error-message';
import { useToast } from '@/hooks/use-toast';
import { useEffect } from 'react';

type PageProps = {
  params: Promise<{
    id: string;
  }>;
};

function ChatRoomDetailContent({ roomId }: { roomId: string }) {
  const router = useRouter();
  const { toast } = useToast();
  const { state } = useChatRoomContext();

  const { data: chatRoom, isLoading, error } = useChatRoom(roomId);
  const messagesQuery = useMessages(roomId);

  // 에러 처리
  useEffect(() => {
    if (error) {
      toast({
        title: '오류',
        description: '채팅방을 찾을 수 없습니다.',
        variant: 'destructive',
      });
      router.push('/');
    }
  }, [error, router, toast]);

  if (isLoading || !chatRoom) {
    return <LoadingSpinner />;
  }

  if (messagesQuery.isError) {
    return (
      <ErrorMessage
        message="메시지를 불러올 수 없습니다."
        onRetry={() => messagesQuery.refetch()}
      />
    );
  }

  return (
    <div className="flex flex-col h-screen">
      {/* 헤더 */}
      <ChatRoomHeader roomName={chatRoom.name} />

      {/* 메시지 목록 */}
      <div className="flex-1 overflow-hidden">
        <MessageList roomId={roomId} />
      </div>

      {/* 하단 입력창 또는 삭제 모드 버튼 */}
      {state.deleteMode.isActive ? (
        <DeleteModeFooter roomId={roomId} />
      ) : (
        <MessageInput roomId={roomId} />
      )}

      {/* 이모티콘 선택 팝업 */}
      {state.emoticonPickerOpen && <EmoticonPicker roomId={roomId} />}
    </div>
  );
}

export default function ChatRoomDetailPage({ params }: PageProps) {
  const { id: roomId } = use(params);

  return (
    <ChatRoomProvider>
      <ChatRoomDetailContent roomId={roomId} />
    </ChatRoomProvider>
  );
}
