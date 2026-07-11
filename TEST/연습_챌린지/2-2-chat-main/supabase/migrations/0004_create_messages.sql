-- 메시지 테이블 생성
-- 텍스트 메시지와 이모티콘 메시지 저장

BEGIN;

-- ENUM 타입 생성
DO $$ BEGIN
  CREATE TYPE message_type_enum AS ENUM ('text', 'emoticon');
EXCEPTION
  WHEN duplicate_object THEN null;
END $$;

-- 테이블 생성
CREATE TABLE IF NOT EXISTS messages (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  chat_room_id uuid NOT NULL REFERENCES chat_rooms(id) ON DELETE CASCADE,
  sender_id uuid REFERENCES user_profiles(id) ON DELETE SET NULL,
  message_type message_type_enum NOT NULL,
  content text,
  emoticon_id varchar(50),
  reply_to_message_id uuid REFERENCES messages(id) ON DELETE SET NULL,
  created_at timestamptz NOT NULL DEFAULT NOW(),

  -- 제약 조건: 메시지 타입에 따라 content 또는 emoticon_id 중 하나만 존재
  CONSTRAINT messages_content_check CHECK (
    (message_type = 'text' AND content IS NOT NULL AND emoticon_id IS NULL) OR
    (message_type = 'emoticon' AND emoticon_id IS NOT NULL AND content IS NULL)
  )
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_messages_chat_room_created
  ON messages(chat_room_id, created_at);

CREATE INDEX IF NOT EXISTS idx_messages_sender_id
  ON messages(sender_id);

-- RLS 비활성화 (프로젝트 가이드라인)
ALTER TABLE messages DISABLE ROW LEVEL SECURITY;

-- 코멘트 추가
COMMENT ON TABLE messages IS '메시지 정보 (텍스트/이모티콘)';
COMMENT ON COLUMN messages.id IS '메시지 ID';
COMMENT ON COLUMN messages.chat_room_id IS '채팅방 ID';
COMMENT ON COLUMN messages.sender_id IS '발신자 ID (탈퇴 시 NULL)';
COMMENT ON COLUMN messages.message_type IS '메시지 유형 (text/emoticon)';
COMMENT ON COLUMN messages.content IS '텍스트 메시지 내용 (1~1000자)';
COMMENT ON COLUMN messages.emoticon_id IS '이모티콘 ID';
COMMENT ON COLUMN messages.reply_to_message_id IS '답장 대상 메시지 ID';
COMMENT ON COLUMN messages.created_at IS '전송 시간';

EXCEPTION
  WHEN OTHERS THEN
    RAISE NOTICE 'Error creating messages table: %', SQLERRM;
    ROLLBACK;

COMMIT;
