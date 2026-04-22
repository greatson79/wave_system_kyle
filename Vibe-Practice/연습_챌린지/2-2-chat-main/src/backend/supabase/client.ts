import { createClient } from '@supabase/supabase-js';
import { createServerClient } from '@supabase/ssr';
import type { SupabaseClient } from '@supabase/supabase-js';
import type { CookieOptions } from '@supabase/ssr';

export type ServiceClientConfig = {
  url: string;
  serviceRoleKey: string;
};

export const createServiceClient = ({
  url,
  serviceRoleKey,
}: ServiceClientConfig): SupabaseClient =>
  createClient(url, serviceRoleKey, {
    auth: {
      persistSession: false,
    },
  });

export type SSRClientConfig = {
  url: string;
  anonKey: string;
  getCookie: (name: string) => string | undefined;
  setCookie: (name: string, value: string, options: CookieOptions) => void;
};

/**
 * SSR용 Supabase 클라이언트 생성
 * 쿠키에서 세션 정보를 읽어 인증 처리
 */
export const createSSRClient = ({
  url,
  anonKey,
  getCookie,
  setCookie,
}: SSRClientConfig): SupabaseClient => {
  return createServerClient(url, anonKey, {
    cookies: {
      get(name: string) {
        return getCookie(name);
      },
      set(name: string, value: string, options: CookieOptions) {
        setCookie(name, value, options);
      },
      remove(name: string, options: CookieOptions) {
        setCookie(name, '', { ...options, maxAge: 0 });
      },
    },
  });
};
