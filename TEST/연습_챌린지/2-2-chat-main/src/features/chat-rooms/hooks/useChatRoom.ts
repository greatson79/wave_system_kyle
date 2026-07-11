'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/remote/api-client';
import { queryKeys } from '@/lib/query/keys';
import type { ChatRoom } from '../types';

export const useChatRoom = (roomId: string) => {
  return useQuery({
    queryKey: queryKeys.chatRooms.detail(roomId),
    queryFn: async () => {
      const response = await apiClient.get<ChatRoom>(`/api/chat-rooms/${roomId}`);
      return response.data;
    },
    staleTime: 1000 * 60 * 5, // 5분
    gcTime: 1000 * 60 * 10, // 10분
    retry: 1,
  });
};
