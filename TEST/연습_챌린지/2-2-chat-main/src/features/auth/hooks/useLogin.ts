'use client';

import { useMutation } from '@tanstack/react-query';
import { useRouter, useSearchParams } from 'next/navigation';
import { getSupabaseBrowserClient } from '@/lib/supabase/browser-client';
import { useCurrentUser } from './useCurrentUser';
import type { LoginRequest } from '@/features/auth/lib/dto';

export function useLogin() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { refresh } = useCurrentUser();

  return useMutation({
    mutationFn: async (data: LoginRequest) => {
      const supabase = getSupabaseBrowserClient();

      const { data: authData, error } = await supabase.auth.signInWithPassword({
        email: data.email,
        password: data.password,
      });

      if (error) {
        // 사용자 친화적인 에러 메시지로 변환
        if (error.message.includes('Invalid login credentials')) {
          throw new Error('이메일 또는 비밀번호가 올바르지 않습니다.');
        }
        throw new Error(error.message || '로그인에 실패했습니다.');
      }

      return authData;
    },
    onSuccess: async () => {
      // 사용자 정보 갱신
      await refresh();

      // 리다이렉트
      const redirectedFrom = searchParams.get('redirectedFrom');
      router.replace(redirectedFrom || '/');
    },
    onError: (error) => {
      console.error('Login failed:', error);
    },
  });
}
