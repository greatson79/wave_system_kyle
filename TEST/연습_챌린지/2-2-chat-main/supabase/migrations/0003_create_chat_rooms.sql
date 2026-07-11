-- 채팅방 테이블 생성
-- 모든 사용자가 접근 가능한 오픈 채팅방

BEGIN;

-- 테이블 생성
CREATE TABLE IF NOT EXISTS chat_rooms (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name varchar(50) NOT NULL,
  created_at timestamptz NOT NULL DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_chat_rooms_created_at
  ON chat_rooms(created_at DESC);

-- RLS 비활성화 (프로젝트 가이드라인)
ALTER TABLE chat_rooms DISABLE ROW LEVEL SECURITY;

-- 코멘트 추가
COMMENT ON TABLE chat_rooms IS '채팅방 정보';
COMMENT ON COLUMN chat_rooms.id IS '채팅방 ID';
COMMENT ON COLUMN chat_rooms.name IS '채팅방 이름 (1~50자)';
COMMENT ON COLUMN chat_rooms.created_at IS '생성 시간';

EXCEPTION
  WHEN OTHERS THEN
    RAISE NOTICE 'Error creating chat_rooms table: %', SQLERRM;
    ROLLBACK;

COMMIT;
