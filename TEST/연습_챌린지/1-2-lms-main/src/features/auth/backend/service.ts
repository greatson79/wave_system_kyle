import type { SupabaseClient } from '@supabase/supabase-js';
import {
  failure,
  success,
  type HandlerResult,
} from '@/backend/http/response';
import {
  authErrorCodes,
  type AuthServiceError,
} from '@/features/auth/backend/error';
import type { SignupRequest, SignupResponse } from './schema';
import { normalizePhoneNumber } from '@/lib/validators/phone';

const PROFILES_TABLE = 'profiles';
const TERMS_AGREEMENTS_TABLE = 'terms_agreements';

export const signupUser = async (
  client: SupabaseClient,
  request: SignupRequest,
): Promise<HandlerResult<SignupResponse, AuthServiceError, unknown>> => {
  const { email, password, role, name, phone, termsAgreed } = request;

  const normalizedPhone = normalizePhoneNumber(phone);

  const { data: authData, error: authError } =
    await client.auth.admin.createUser({
      email,
      password,
      email_confirm: true,
    });

  if (authError) {
    if (
      authError.message.includes('already registered') ||
      authError.message.includes('already exists')
    ) {
      return failure(
        409,
        authErrorCodes.emailAlreadyExists,
        '이미 가입된 이메일입니다.',
      );
    }

    return failure(
      500,
      authErrorCodes.authCreationFailed,
      authError.message || '계정 생성에 실패했습니다.',
    );
  }

  if (!authData.user) {
    return failure(
      500,
      authErrorCodes.authCreationFailed,
      '계정 생성에 실패했습니다.',
    );
  }

  const userId = authData.user.id;
  const termsAgreedAt = new Date().toISOString();

  const { error: profileError } = await client
    .from(PROFILES_TABLE)
    .insert({
      id: userId,
      email,
      role,
      name,
      phone: normalizedPhone,
      terms_agreed_at: termsAgreedAt,
    });

  if (profileError) {
    return failure(
      500,
      authErrorCodes.profileCreationFailed,
      '프로필 생성에 실패했습니다.',
      profileError.message,
    );
  }

  const termsToInsert = [];
  if (termsAgreed.service) {
    termsToInsert.push({
      user_id: userId,
      terms_type: 'service',
      agreed_at: termsAgreedAt,
    });
  }
  if (termsAgreed.privacy) {
    termsToInsert.push({
      user_id: userId,
      terms_type: 'privacy',
      agreed_at: termsAgreedAt,
    });
  }

  if (termsToInsert.length > 0) {
    const { error: termsError } = await client
      .from(TERMS_AGREEMENTS_TABLE)
      .insert(termsToInsert);

    if (termsError) {
      return failure(
        500,
        authErrorCodes.termsRecordFailed,
        '약관 동의 이력 저장에 실패했습니다.',
        termsError.message,
      );
    }
  }

  const redirectTo = role === 'learner' ? '/courses' : '/instructor/dashboard';

  return success(
    {
      userId,
      role,
      redirectTo,
    },
    201,
  );
};
