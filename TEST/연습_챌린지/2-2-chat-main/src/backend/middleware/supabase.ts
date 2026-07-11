import { createMiddleware } from 'hono/factory';
import { getCookie, setCookie } from 'hono/cookie';
import type { CookieOptions } from '@supabase/ssr';
import {
  contextKeys,
  type AppEnv,
} from '@/backend/hono/context';
import { createSSRClient } from '@/backend/supabase/client';

export const withSupabase = () =>
  createMiddleware<AppEnv>(async (c, next) => {
    const config = c.get(
      contextKeys.config,
    ) as AppEnv['Variables']['config'] | undefined;

    if (!config) {
      throw new Error('Application configuration is not available.');
    }

    // SSR 클라이언트 생성 (쿠키 기반 인증)
    const client = createSSRClient({
      url: config.supabase.url,
      anonKey: config.supabase.anonKey,
      getCookie: (name: string) => getCookie(c, name),
      setCookie: (name: string, value: string, options: CookieOptions) => {
        setCookie(c, name, value, {
          path: options.path,
          domain: options.domain,
          maxAge: options.maxAge,
          expires: options.expires ? new Date(options.expires) : undefined,
          httpOnly: options.httpOnly,
          secure: options.secure,
          sameSite: options.sameSite as 'Strict' | 'Lax' | 'None' | undefined,
        });
      },
    });

    c.set(contextKeys.supabase, client);

    await next();
  });
