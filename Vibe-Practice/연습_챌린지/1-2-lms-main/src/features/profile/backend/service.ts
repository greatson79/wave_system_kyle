import type { SupabaseClient } from '@supabase/supabase-js'
import type { HandlerResult } from '@/backend/http/response'
import { success, failure } from '@/backend/http/response'
import type { CreateProfileInput, ProfileResponse } from './schema'

type ProfileServiceError = 'PROFILE_NOT_FOUND' | 'CREATE_FAILED' | 'INVALID_REQUEST'

export const getProfile = async (
  supabase: SupabaseClient,
  userId: string
): Promise<HandlerResult<ProfileResponse, ProfileServiceError>> => {
  try {
    const { data, error } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', userId)
      .maybeSingle()

    if (error) {
      return failure(500, 'INVALID_REQUEST', error.message)
    }

    if (!data) {
      return failure(404, 'PROFILE_NOT_FOUND', '프로필을 찾을 수 없습니다.')
    }

    return success(data as unknown as ProfileResponse)
  } catch (err) {
    return failure(
      500,
      'INVALID_REQUEST',
      err instanceof Error ? err.message : 'Unknown error'
    )
  }
}

export const createProfile = async (
  supabase: SupabaseClient,
  userId: string,
  input: CreateProfileInput
): Promise<HandlerResult<ProfileResponse, ProfileServiceError>> => {
  try {
    const { data, error } = await supabase
      .from('profiles')
      .insert({
        id: userId,
        name: input.name,
        phone: input.phone,
        role: input.role,
        terms_agreed_at: new Date().toISOString(),
      })
      .select()
      .single()

    if (error) {
      return failure(500, 'CREATE_FAILED', error.message)
    }

    return success(data as unknown as ProfileResponse, 201)
  } catch (err) {
    return failure(
      500,
      'CREATE_FAILED',
      err instanceof Error ? err.message : 'Unknown error'
    )
  }
}
