"use client";

import { useMutation } from '@tanstack/react-query';
import { getSupabaseBrowserClient } from '@/lib/supabase/browser-client';
import { useCurrentUserContext } from '../context/current-user-context';
import { useRouter } from 'next/navigation';

export const useLogout = () => {
  const { refresh } = useCurrentUserContext();
  const router = useRouter();

  return useMutation({
    mutationFn: async () => {
      // 클라이언트에서 직접 Supabase signOut을 호출하여 쿠키를 초기화합니다
      const supabase = getSupabaseBrowserClient();
      const { error } = await supabase.auth.signOut();

      if (error) {
        throw new Error(error.message);
      }

      return { success: true };
    },
    onSuccess: async () => {
      // 현재 사용자 상태를 갱신하여 로그아웃 상태로 만듭니다
      await refresh();
      // 홈 페이지로 이동
      router.push('/');
    },
  });
};
