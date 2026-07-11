'use client';

import React from 'react';
import { useChatRoomContext } from '../context/chat-room-context';
import { useSendMessage } from '@/features/messages/hooks/useSendMessage';
import { EMOTICONS } from '@/constants/emoticons';
import { Button } from '@/components/ui/button';
import { X } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

type EmoticonPickerProps = {
  roomId: string;
};

export const EmoticonPicker: React.FC<EmoticonPickerProps> = ({ roomId }) => {
  const { state, dispatch } = useChatRoomContext();
  const sendMessage = useSendMessage(roomId);
  const { toast } = useToast();

  const handleSelectEmoticon = async (emoticonId: string) => {
    try {
      await sendMessage.mutateAsync({
        message_type: 'emoticon',
        emoticon_id: emoticonId,
        reply_to_message_id: state.replyTarget?.id,
      });

      dispatch({ type: 'RESET_AFTER_SEND' });
    } catch (error) {
      toast({
        title: '오류',
        description: '이모티콘 전송에 실패했습니다.',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-end z-50">
      <div className="bg-white w-full rounded-t-2xl p-6 animate-in slide-in-from-bottom">
        {/* 헤더 */}
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">이모티콘 선택</h3>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => dispatch({ type: 'TOGGLE_EMOTICON_PICKER' })}
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        {/* 이모티콘 그리드 */}
        <div className="grid grid-cols-4 gap-4">
          {EMOTICONS.map((emoticon) => (
            <button
              key={emoticon.id}
              className="flex flex-col items-center gap-2 p-4 rounded-lg hover:bg-muted transition-colors"
              onClick={() => handleSelectEmoticon(emoticon.id)}
            >
              <span className="text-4xl">{emoticon.label}</span>
              <span className="text-xs text-muted-foreground">
                {emoticon.name}
              </span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
