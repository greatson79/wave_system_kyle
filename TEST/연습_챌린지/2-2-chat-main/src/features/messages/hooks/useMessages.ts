'use client';

import { useInfiniteQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/remote/api-client';
import { queryKeys } from '@/lib/query/keys';
import type { Message } from '../types';

type MessagesResponse = {
  messages: Message[];
};

export const useMessages = (roomId: string) => {
  return useInfiniteQuery({
    queryKey: queryKeys.messages.list(roomId),
    queryFn: async ({ pageParam = 0 }) => {
      const response = await apiClient.get<MessagesResponse>(
        `/api/chat-rooms/${roomId}/messages`,
        {
          params: { limit: 50, offset: pageParam },
        }
      );
      return response.data;
    },
    initialPageParam: 0,
    getNextPageParam: (lastPage, allPages) => {
      const totalFetched = allPages.length * 50;
      return lastPage.messages.length === 50 ? totalFetched : undefined;
    },
    staleTime: 1000 * 60, // 1분
    gcTime: 1000 * 60 * 5, // 5분
    select: (data) => ({
      pages: data.pages,
      pageParams: data.pageParams,
      messages: data.pages.flatMap((page) => page.messages),
    }),
  });
};
