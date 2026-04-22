import type { SupabaseClient } from '@supabase/supabase-js';
import type { HandlerResult } from '@/backend/http/response';
import { success, failure } from '@/backend/http/response';
import type { LoginResponse, SignupRequest, SignupResponse } from './schema';
import { AuthErrorCode, authErrorMessages } from './error';

/**
 * 로그인 서비스 로직
 * Supabase Auth로 로그인하고 사용자 프로필 정보를 조회합니다.
 */
export async function login(
  supabase: SupabaseClient,
  email: string,
  password: string,
  redirectedFrom?: string,
): Promise<HandlerResult<LoginResponse, AuthErrorCode>> {
  // 1. Supabase Auth 로그인
  const { data: authData, error: authError } =
    await supabase.auth.signInWithPassword({
      email,
      password,
    });

  if (authError || !authData.user) {
    return failure(
      401,
      AuthErrorCode.INVALID_CREDENTIALS,
      authErrorMessages.AUTH_INVALID_CREDENTIALS,
    );
  }

  // 2. 사용자 프로필 조회
  const { data: profile, error: profileError } = await supabase
    .from('user_profiles')
    .select('nickname')
    .eq('id', authData.user.id)
    .single();

  if (profileError || !profile) {
    return failure(
      500,
      AuthErrorCode.INTERNAL_SERVER_ERROR,
      authErrorMessages.INTERNAL_SERVER_ERROR,
    );
  }

  // 3. 응답 반환
  return success({
    success: true,
    user: {
      id: authData.user.id,
      email: authData.user.email!,
      nickname: profile.nickname,
    },
    redirectTo: redirectedFrom || '/',
  });
}

/**
 * 회원가입 서비스 로직
 * Supabase Auth로 사용자를 생성하고 user_profiles 테이블에 닉네임을 저장합니다.
 */
export async function signupUser(
  supabase: SupabaseClient,
  data: SignupRequest,
): Promise<HandlerResult<SignupResponse, AuthErrorCode | string>> {
  // 1. Supabase Auth 사용자 생성
  const { data: authData, error: authError } =
    await supabase.auth.admin.createUser({
      email: data.email,
      password: data.password,
      email_confirm: true, // 이메일 인증 스킵 (개발 환경)
    });

  if (authError) {
    // 이메일 중복 에러 처리
    if (authError.message.includes('already registered')) {
      return failure(
        409,
        AuthErrorCode.EMAIL_DUPLICATE,
        authErrorMessages.AUTH_EMAIL_DUPLICATE,
      );
    }
    return failure(500, 'SIGNUP_FAILED', authError.message);
  }

  // 2. user_profiles 테이블에 닉네임 저장
  const { error: profileError } = await supabase.from('user_profiles').insert({
    id: authData.user.id,
    nickname: data.nickname,
  });

  if (profileError) {
    // 프로필 생성 실패 (Auth 사용자는 이미 생성됨)
    // 추후 재시도 로직 또는 관리자 알림 추가 고려
    return failure(
      500,
      'PROFILE_CREATION_FAILED',
      '회원가입 중 오류가 발생했습니다. 고객센터로 문의해주세요.',
      profileError.message,
    );
  }

  // 3. 성공 응답
  return success<SignupResponse>({
    success: true,
    redirectTo: '/login',
  });
}
