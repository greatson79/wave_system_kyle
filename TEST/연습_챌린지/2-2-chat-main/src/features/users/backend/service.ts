import type { SupabaseClient } from '@supabase/supabase-js';
import type { UserProfile } from '../types';

export const getUserProfile = async (
  supabase: SupabaseClient,
  userId: string,
): Promise<UserProfile | null> => {
  const { data: profile, error } = await supabase
    .from('user_profiles')
    .select('id, nickname')
    .eq('id', userId)
    .single();

  if (error) {
    throw error;
  }

  // 이메일은 Supabase Auth에서 가져옴
  const { data: authUser } = await supabase.auth.getUser();

  return {
    id: profile.id,
    nickname: profile.nickname,
    email: authUser.user?.email || '',
  };
};

export const updateNickname = async (
  supabase: SupabaseClient,
  userId: string,
  nickname: string,
): Promise<UserProfile> => {
  const { data: profile, error } = await supabase
    .from('user_profiles')
    .update({ nickname })
    .eq('id', userId)
    .select('id, nickname')
    .single();

  if (error) {
    throw error;
  }

  const { data: authUser } = await supabase.auth.getUser();

  return {
    id: profile.id,
    nickname: profile.nickname,
    email: authUser.user?.email || '',
  };
};
