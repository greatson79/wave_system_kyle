'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/remote/api-client';
import { queryKeys } from '@/lib/query/keys';
import type { Message } from '../types';

export const useDeleteMessages = (roomId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (messageIds: string[]) =>
      apiClient.delete('/api/messages/batch', {
        data: { message_ids: messageIds },
      }),

    onMutate: async (messageIds) => {
      await queryClient.cancelQueries({
        queryKey: queryKeys.messages.list(roomId),
      });

      const previousMessages = queryClient.getQueryData(
        queryKeys.messages.list(roomId)
      );

      // 낙관적 업데이트: 메시지 제거
      queryClient.setQueryData(
        queryKeys.messages.list(roomId),
        (old: any) => {
          if (!old) return old;

          return {
            ...old,
            pages: old.pages.map((page: any) => ({
              ...page,
              messages: page.messages.filter(
                (msg: Message) => !messageIds.includes(msg.id)
              ),
            })),
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
