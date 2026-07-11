'use client';

import React from 'react';
import { useChatRoomContext } from '../context/chat-room-context';
import { useDeleteMessages } from '@/features/messages/hooks/useDeleteMessages';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';

type DeleteModeFooterProps = {
  roomId: string;
};

export const DeleteModeFooter: React.FC<DeleteModeFooterProps> = ({
  roomId,
}) => {
  const { state, dispatch, selectedMessageCount, canDelete } = useChatRoomContext();
  const deleteMessages = useDeleteMessages(roomId);
  const { toast } = useToast();

  const handleDelete = async () => {
    try {
      await deleteMessages.mutateAsync(state.deleteMode.selectedMessageIds);

      toast({
        title: '성공',
        description: `${selectedMessageCount}개의 메시지가 삭제되었습니다.`,
      });

      dispatch({ type: 'EXIT_DELETE_MODE' });
    } catch (error) {
      toast({
        title: '오류',
        description: '메시지 삭제에 실패했습니다.',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="border-t bg-white p-4 flex items-center justify-between">
      <Button
        variant="outline"
        onClick={() => dispatch({ type: 'EXIT_DELETE_MODE' })}
      >
        취소
      </Button>
      <Button
        variant="destructive"
        disabled={!canDelete}
        onClick={handleDelete}
      >
        일괄삭제({selectedMessageCount}개)
      </Button>
    </div>
  );
};
