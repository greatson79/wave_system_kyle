'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/remote/api-client';
import { queryKeys } from '@/lib/query/keys';
import type { Message } from '../types';

export const useToggleLike = (roomId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ messageId, isLiked }: { messageId: string; isLiked: boolean }) => {
      if (isLiked) {
        return apiClient.delete(`/api/messages/${messageId}/likes`);
      } else {
        return apiClient.post(`/api/messages/${messageId}/likes`);
      }
    },

    onMutate: async ({ messageId, isLiked }) => {
      await queryClient.cancelQueries({
        queryKey: queryKeys.messages.list(roomId),
      });

      const previousMessages = queryClient.getQueryData(
        queryKeys.messages.list(roomId)
      );

      // 낙관적 업데이트
      queryClient.setQueryData(
        queryKeys.messages.list(roomId),
        (old: any) => {
          if (!old) return old;

          return {
            ...old,
            pages: old.pages.map((page: any) => ({
              ...page,
              messages: page.messages.map((msg: Message) =>
                msg.id === messageId
                  ? {
                      ...msg,
                      like_count: isLiked ? msg.like_count - 1 : msg.like_count + 1,
                      is_liked_by_me: !isLiked,
                    }
                  : msg
              ),
            })),
          };
        }
      );

      return { previousMessages };
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
