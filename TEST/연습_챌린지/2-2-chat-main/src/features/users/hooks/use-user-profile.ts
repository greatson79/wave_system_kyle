'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/remote/api-client';
import { queryKeys } from '@/lib/query/keys';
import type { UserProfile } from '../types';

export const useUserProfile = () => {
  return useQuery({
    queryKey: queryKeys.users.me(),
    queryFn: async () => {
      const response = await apiClient.get('/api/users/me');
      return response.data as UserProfile;
    },
    staleTime: 1000 * 60 * 5, // 5분
    refetchOnWindowFocus: false,
  });
};
