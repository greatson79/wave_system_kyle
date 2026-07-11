-- 사용자 프로필 테이블 생성
-- Supabase Auth의 auth.users와 1:1 관계

BEGIN;

-- 테이블 생성
CREATE TABLE IF NOT EXISTS user_profiles (
  id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  nickname varchar(20) NOT NULL,
  created_at timestamptz NOT NULL DEFAULT NOW()
);

-- 인덱스 생성
-- PRIMARY KEY로 id 인덱스는 자동 생성됨

-- RLS 비활성화 (프로젝트 가이드라인)
ALTER TABLE user_profiles DISABLE ROW LEVEL SECURITY;

-- 코멘트 추가
COMMENT ON TABLE user_profiles IS '사용자 프로필 정보 (닉네임)';
COMMENT ON COLUMN user_profiles.id IS 'Supabase Auth 사용자 ID';
COMMENT ON COLUMN user_profiles.nickname IS '닉네임 (2~20자, 특수문자 제외)';
COMMENT ON COLUMN user_profiles.created_at IS '가입 시간';

EXCEPTION
  WHEN OTHERS THEN
    RAISE NOTICE 'Error creating user_profiles table: %', SQLERRM;
    ROLLBACK;

COMMIT;
