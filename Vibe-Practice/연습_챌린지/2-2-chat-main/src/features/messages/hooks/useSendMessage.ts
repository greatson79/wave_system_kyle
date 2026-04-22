'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/remote/api-client';
import { queryKeys } from '@/lib/query/keys';
import { useCurrentUser } from '@/features/auth/hooks/useCurrentUser';
import type { SendMessageRequest } from '../backend/schema';
import type { Message } from '../types';

export const useSendMessage = (roomId: string) => {
  const queryClient = useQueryClient();
  const { user } = useCurrentUser();

  return useMutation({
    mutationFn: (data: SendMessageRequest) =>
      apiClient.post(`/api/chat-rooms/${roomId}/messages`, data),

    onMutate: async (newMessage) => {
      await queryClient.cancelQueries({
        queryKey: queryKeys.messages.list(roomId),
      });

      const previousMessages = queryClient.getQueryData(
        queryKeys.messages.list(roomId)
      );

      queryClient.setQueryData(
        queryKeys.messages.list(roomId),
        (old: any) => {
          if (!old) return old;

          const timestamp = Date.now();
          const optimisticMessage: Message = {
            id: `temp-${timestamp}`,
            chat_room_id: roomId,
            sender_id: user?.id || '',
            sender_nickname: user?.nickname || '',
            message_type: newMessage.message_type,
            content: newMessage.message_type === 'text' ? newMessage.content : null,
            emoticon_id: newMessage.message_type === 'emoticon' ? newMessage.emoticon_id : null,
            reply_to_message_id: newMessage.reply_to_message_id || null,
            created_at: new Date().toISOString(),
            like_count: 0,
            is_liked_by_me: false,
          };

          return {
            ...old,
            pages: old.pages.map((page: any, index: number) =>
              index === 0
                ? {
                    ...page,
                    messages: [...page.messages, optimisticMessage],
                  }
                : page
            ),
          };
        }
      );

      return { previousMessages };
    },

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.messages.list(roomId),
      });
    },

    onError: (error, variables, context) => {
      if (context?.previousMessages) {
        queryClient.setQueryData(
          queryKeys.messages.list(roomId),
          context.previousMessages
        );
      }
    },
  });
};
