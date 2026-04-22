-- 메시지 좋아요 테이블 생성
-- 사용자당 메시지 1회 제한 (복합 PK로 중복 방지)

BEGIN;

-- 테이블 생성
CREATE TABLE IF NOT EXISTS message_likes (
  message_id uuid NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
  user_id uuid NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
  created_at timestamptz NOT NULL DEFAULT NOW(),

  -- 복합 PK로 중복 방지 및 조회 최적화
  PRIMARY KEY (message_id, user_id)
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_message_likes_user_id
  ON message_likes(user_id);

-- RLS 비활성화 (프로젝트 가이드라인)
ALTER TABLE message_likes DISABLE ROW LEVEL SECURITY;

-- 코멘트 추가
COMMENT ON TABLE message_likes IS '메시지 좋아요';
COMMENT ON COLUMN message_likes.message_id IS '메시지 ID';
COMMENT ON COLUMN message_likes.user_id IS '사용자 ID';
COMMENT ON COLUMN message_likes.created_at IS '좋아요 시간';

EXCEPTION
  WHEN OTHERS THEN
    RAISE NOTICE 'Error creating message_likes table: %', SQLERRM;
    ROLLBACK;

COMMIT;
