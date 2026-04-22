'use client';

import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useChatRoomContext } from '../context/chat-room-context';
import { useSendMessage } from '@/features/messages/hooks/useSendMessage';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Smile, Send } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const textMessageSchema = z.object({
  content: z
    .string()
    .min(1, '메시지를 입력해주세요')
    .max(1000, '메시지는 최대 1000자까지 입력할 수 있습니다')
    .trim(),
});

type TextMessageFormData = z.infer<typeof textMessageSchema>;

type MessageInputProps = {
  roomId: string;
};

export const MessageInput: React.FC<MessageInputProps> = ({ roomId }) => {
  const { state, dispatch } = useChatRoomContext();
  const sendMessage = useSendMessage(roomId);
  const { toast } = useToast();

  const form = useForm<TextMessageFormData>({
    resolver: zodResolver(textMessageSchema),
    defaultValues: { content: '' },
  });

  const handleSubmit = form.handleSubmit(async (data) => {
    try {
      await sendMessage.mutateAsync({
        message_type: 'text',
        content: data.content,
        reply_to_message_id: state.replyTarget?.id,
      });

      form.reset();
      dispatch({ type: 'RESET_AFTER_SEND' });
    } catch (error) {
      toast({
        title: '오류',
        description: '메시지 전송에 실패했습니다.',
        variant: 'destructive',
      });
    }
  });

  return (
    <div className="border-t bg-white">
      {/* 답장 대상 미리보기 */}
      {state.replyTarget && (
        <div className="px-4 py-2 bg-muted flex items-center justify-between">
          <div className="text-sm text-muted-foreground">
            <span className="font-semibold">
              {state.replyTarget.sender_nickname}
            </span>
            <span className="mx-2">›</span>
            <span>
              {state.replyTarget.message_type === 'text'
                ? state.replyTarget.content
                : '이모티콘'}
            </span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => dispatch({ type: 'SET_REPLY_TARGET', payload: null })}
          >
            ✕
          </Button>
        </div>
      )}

      {/* 입력창 */}
      <form onSubmit={handleSubmit} className="flex items-center gap-2 p-4">
        <Button
          type="button"
          variant="ghost"
          size="icon"
          onClick={() => dispatch({ type: 'TOGGLE_EMOTICON_PICKER' })}
        >
          <Smile className="h-5 w-5" />
        </Button>

        <Input
          {...form.register('content')}
          placeholder="메시지를 입력하세요"
          className="flex-1"
        />

        <Button type="submit" size="icon" className="rounded-full">
          <Send className="h-4 w-4" />
        </Button>
      </form>

      {/* 에러 메시지 */}
      {form.formState.errors.content && (
        <p className="px-4 pb-2 text-xs text-destructive">
          {form.formState.errors.content.message}
        </p>
      )}
    </div>
  );
};
