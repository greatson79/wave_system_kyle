'use client';

import { useUserProfile } from '@/features/users/hooks/use-user-profile';

export const useUser = () => {
  const { data: user, ...rest } = useUserProfile();
  return { user, ...rest };
};
