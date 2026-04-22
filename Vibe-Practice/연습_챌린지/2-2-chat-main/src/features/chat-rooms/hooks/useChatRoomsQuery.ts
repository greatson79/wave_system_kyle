import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/remote/api-client';
import type { ChatRoom } from '../types';
import { ChatRoomListResponseSchema } from '../lib/dto';

export const useChatRoomsQuery = () => {
  return useQuery({
    queryKey: ['chat-rooms'],
    queryFn: async () => {
      const response = await apiClient.get('/api/chat-rooms');
      const parsed = ChatRoomListResponseSchema.parse(response.data);
      return parsed.data;
    },
    staleTime: 1000 * 60,
    retry: 1,
  });
};
