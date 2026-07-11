import { NextResponse, type NextRequest } from "next/server";
import { createServerClient } from "@supabase/ssr";
import type { Database } from "@/lib/supabase/types";
import { env } from "@/constants/env";
import {
  LOGIN_PATH,
  isAuthEntryPath,
  shouldProtectPath,
} from "@/constants/auth";
import { match } from "ts-pattern";

const copyCookies = (from: NextResponse, to: NextResponse) => {
  from.cookies.getAll().forEach((cookie) => {
    to.cookies.set({
      name: cookie.name,
      value: cookie.value,
      path: cookie.path,
      expires: cookie.expires,
      httpOnly: cookie.httpOnly,
      maxAge: cookie.maxAge,
      sameSite: cookie.sameSite,
      secure: cookie.secure,
    });
  });

  return to;
};

export async function middleware(request: NextRequest) {
  const response = NextResponse.next({ request });

  // Authorization 헤더에서 토큰 추출
  const authHeader = request.headers.get('authorization');
  const token = authHeader?.replace('Bearer ', '');

  let user = null;

  if (token) {
    // Authorization 헤더가 있는 경우 (API 요청)
    const supabase = createServerClient<Database>(
      env.NEXT_PUBLIC_SUPABASE_URL,
      env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
      {
        cookies: {
          getAll() {
            return request.cookies.getAll();
          },
          setAll(cookiesToSet) {
            cookiesToSet.forEach(({ name, value, options }) => {
              request.cookies.set({ name, value, ...options });
              response.cookies.set({ name, value, ...options });
            });
          },
        },
        global: {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      }
    );

    const {
      data: { user: authUser },
    } = await supabase.auth.getUser();

    user = authUser;
  } else {
    // Authorization 헤더가 없는 경우 (페이지 요청) - 쿠키로 확인
    const supabase = createServerClient<Database>(
      env.NEXT_PUBLIC_SUPABASE_URL,
      env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
      {
        cookies: {
          getAll() {
            return request.cookies.getAll();
          },
          setAll(cookiesToSet) {
            cookiesToSet.forEach(({ name, value, options }) => {
              request.cookies.set({ name, value, ...options });
              response.cookies.set({ name, value, ...options });
            });
          },
        },
      }
    );

    const {
      data: { user: cookieUser },
    } = await supabase.auth.getUser();

    user = cookieUser;
  }

  // --- 디버깅 로그 추가 ---
  console.log('[Middleware] User:', user ? user.id : 'User not found');
  console.log('[Middleware] Path:', request.nextUrl.pathname);
  console.log('[Middleware] Auth Header:', authHeader ? 'Present' : 'Not present');
  // -----------------------

  // API 요청에 user id 헤더 추가
  if (user && request.nextUrl.pathname.startsWith('/api/')) {
    const requestHeaders = new Headers(request.headers);
    requestHeaders.set('x-user-id', user.id);

    return NextResponse.next({
      request: {
        headers: requestHeaders,
      },
    });
  }

  const decision = match({ user, pathname: request.nextUrl.pathname })
    .when(
      ({ user: currentUser, pathname }) =>
        !currentUser && shouldProtectPath(pathname),
      ({ pathname }) => {
        const loginUrl = request.nextUrl.clone();
        loginUrl.pathname = LOGIN_PATH;
        loginUrl.searchParams.set("redirectedFrom", pathname);

        return copyCookies(response, NextResponse.redirect(loginUrl));
      }
    )
    .otherwise(() => response);

  return decision;
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
