'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import { queryKeys } from '@/lib/query/keys';
import { toast } from '@/hooks/use-toast';
import type { UpdateNicknameRequest } from '../lib/dto';
import type { UserProfile } from '../types';

export const useUpdateNickname = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: UpdateNicknameRequest) => {
      const response = await apiClient.patch('/api/users/me', data);
      return response.data as UserProfile;
    },
    onSuccess: (data) => {
      queryClient.setQueryData(queryKeys.users.me(), data);
      toast({
        title: '닉네임이 변경되었습니다',
      });
    },
    onError: (error: unknown) => {
      const message = extractApiErrorMessage(error, '닉네임 변경에 실패했습니다');
      toast({
        title: message,
        variant: 'destructive',
      });
    },
  });
};
