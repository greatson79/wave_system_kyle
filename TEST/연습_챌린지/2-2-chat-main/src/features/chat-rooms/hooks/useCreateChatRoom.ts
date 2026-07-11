'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/remote/api-client';
import { queryKeys } from '@/lib/query/keys';
import type {
  CreateChatRoomRequest,
  CreateChatRoomResponse,
} from '../lib/dto';

export const useCreateChatRoom = () => {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation<CreateChatRoomResponse, Error, CreateChatRoomRequest>({
    mutationFn: async (data) => {
      const response = await apiClient.post<CreateChatRoomResponse>(
        '/api/chat-rooms',
        data
      );
      return response.data;
    },

    onSuccess: (response) => {
      // 채팅방 목록 캐시 무효화
      queryClient.invalidateQueries({
        queryKey: queryKeys.chatRooms.all(),
      });

      // 홈으로 리다이렉트
      router.push(response.redirectTo);
    },

    onError: (error) => {
      console.error('채팅방 생성 실패:', error);
      // 에러 처리는 컴포넌트에서 수행
    },
  });
};
