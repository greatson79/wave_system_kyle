# 데이터베이스 설계 문서

## 1. 개요

본 문서는 실시간 채팅 서비스의 데이터베이스 스키마 설계를 정의합니다. PostgreSQL과 Supabase를 기반으로 하며, **PRD와 Userflow에 명시된 기능만** 지원합니다.

### 설계 원칙
- **간결성**: 요구사항에 명시된 데이터만 저장
- **확장성**: 향후 확장 가능하도록 기본 구조 유지
- **성능**: 실제 사용 패턴에 맞춘 최소한의 인덱스

---

## 2. 데이터 플로우

### 2.1 인증 플로우
```
회원가입
  → Supabase Auth (auth.users)
  → user_profiles 테이블에 닉네임 저장

로그인
  → Supabase Auth 세션 생성

닉네임 수정
  → user_profiles.nickname 업데이트
```

### 2.2 채팅방 플로우
```
채팅방 생성
  → chat_rooms 테이블에 삽입

채팅방 목록 조회
  → chat_rooms 전체 조회
  → 최근 메시지 시간 기준 정렬
```

### 2.3 메시지 플로우
```
메시지 전송
  → messages 테이블에 삽입
  → message_type: 'text' | 'emoticon'
  → reply_to_message_id (선택)

메시지 목록 조회
  → messages WHERE chat_room_id
  → user_profiles JOIN (발신자 닉네임)
  → reply 정보 JOIN (답장 대상)
  → likes 정보 JOIN (좋아요 개수/내 좋아요)
```

### 2.4 좋아요 플로우
```
좋아요 추가
  → message_likes 삽입
  → UNIQUE(message_id, user_id)로 중복 방지

좋아요 취소
  → message_likes 삭제
```

### 2.5 메시지 삭제 플로우
```
메시지 삭제
  → messages DELETE (본인 확인)
  → CASCADE로 좋아요도 자동 삭제
  → 답장 대상 메시지는 SET NULL
```

---

## 3. 데이터베이스 스키마

### 3.1 사용자 프로필 (user_profiles)

Supabase Auth의 `auth.users`와 1:1 관계. 닉네임만 추가 저장.

| 컬럼명 | 타입 | 제약 조건 | 설명 |
|--------|------|-----------|------|
| id | uuid | PK, FK → auth.users(id) ON DELETE CASCADE | Supabase Auth 사용자 ID |
| nickname | varchar(20) | NOT NULL | 닉네임 (2~20자) |
| created_at | timestamptz | NOT NULL, DEFAULT NOW() | 가입 시간 |

#### 인덱스
- `PRIMARY KEY (id)`

#### 비고
- Supabase Auth 회원가입 시 트리거 또는 서비스 로직으로 자동 생성
- 닉네임은 마이페이지에서 수정 가능
- `updated_at` 제거: 요구사항에 없으며 사용되지 않음

---

### 3.2 채팅방 (chat_rooms)

모든 사용자가 접근 가능한 오픈 채팅방.

| 컬럼명 | 타입 | 제약 조건 | 설명 |
|--------|------|-----------|------|
| id | uuid | PK, DEFAULT gen_random_uuid() | 채팅방 ID |
| name | varchar(50) | NOT NULL | 채팅방 이름 (1~50자) |
| created_at | timestamptz | NOT NULL, DEFAULT NOW() | 생성 시간 |

#### 인덱스
- `PRIMARY KEY (id)`
- `INDEX idx_chat_rooms_created_at ON chat_rooms(created_at DESC)` - 목록 정렬용

#### 비고
- `created_by` 제거: PRD/Userflow에 생성자 표시 요구사항 없음
- `updated_at` 제거: 채팅방 수정 기능 없음
- 채팅방 삭제 기능 없음 (향후 확장 가능)

---

### 3.3 메시지 (messages)

텍스트 메시지와 이모티콘 메시지 저장.

| 컬럼명 | 타입 | 제약 조건 | 설명 |
|--------|------|-----------|------|
| id | uuid | PK, DEFAULT gen_random_uuid() | 메시지 ID |
| chat_room_id | uuid | NOT NULL, FK → chat_rooms(id) ON DELETE CASCADE | 채팅방 ID |
| sender_id | uuid | NOT NULL, FK → user_profiles(id) ON DELETE SET NULL | 발신자 ID |
| message_type | message_type_enum | NOT NULL | 'text' 또는 'emoticon' |
| content | text | NULL | 텍스트 메시지 내용 (1~1000자) |
| emoticon_id | varchar(50) | NULL | 이모티콘 ID |
| reply_to_message_id | uuid | NULL, FK → messages(id) ON DELETE SET NULL | 답장 대상 메시지 ID |
| created_at | timestamptz | NOT NULL, DEFAULT NOW() | 전송 시간 |

#### ENUM 타입
```sql
CREATE TYPE message_type_enum AS ENUM ('text', 'emoticon');
```

#### 인덱스
- `PRIMARY KEY (id)`
- `INDEX idx_messages_chat_room_created ON messages(chat_room_id, created_at)` - 메시지 목록 조회용
- `INDEX idx_messages_sender_id ON messages(sender_id)` - 일괄 삭제 시 본인 확인용

#### 제약 조건
```sql
CHECK (
  (message_type = 'text' AND content IS NOT NULL AND emoticon_id IS NULL) OR
  (message_type = 'emoticon' AND emoticon_id IS NOT NULL AND content IS NULL)
)
```

#### 비고
- **중요**: `sender_id ON DELETE SET NULL`로 변경
  - 사용자 삭제 시 메시지는 유지하되 발신자는 NULL로 표시
  - 채팅 히스토리 보존 (CASCADE는 데이터 유실 위험)
  - UI에서 탈퇴한 사용자는 "알 수 없음" 등으로 표시
- 채팅방 삭제 시 메시지도 삭제 (CASCADE)
- 답장 대상 메시지 삭제 시 NULL로 설정 (답장 메시지는 유지)
- `reply_to` 인덱스 제거: 자주 사용되지 않음

---

### 3.4 좋아요 (message_likes)

메시지 좋아요. 사용자당 메시지 1회 제한.

| 컬럼명 | 타입 | 제약 조건 | 설명 |
|--------|------|-----------|------|
| message_id | uuid | PK, FK → messages(id) ON DELETE CASCADE | 메시지 ID |
| user_id | uuid | PK, FK → user_profiles(id) ON DELETE CASCADE | 사용자 ID |
| created_at | timestamptz | NOT NULL, DEFAULT NOW() | 좋아요 시간 |

#### 인덱스
- `PRIMARY KEY (message_id, user_id)` - 복합 PK로 중복 방지 + 조회 최적화
- `INDEX idx_message_likes_user_id ON message_likes(user_id)` - 사용자별 좋아요 조회용

#### 비고
- 별도 `id` 컬럼 제거: 복합 PK로 충분
- `(message_id, user_id)` 복합 PK로 중복 좋아요 자동 방지
- 메시지/사용자 삭제 시 좋아요도 삭제 (CASCADE)

---

## 4. ERD (개체-관계 다이어그램)

```
┌─────────────────────┐
│   auth.users        │ (Supabase Auth)
└──────────┬──────────┘
           │ 1:1
           ▼
┌─────────────────────┐
│  user_profiles      │
├─────────────────────┤
│ id (PK, FK)         │◄──────────┐
│ nickname            │           │
│ created_at          │           │
└─────────────────────┘           │
                                  │
                                  │
┌─────────────────────┐           │
│  chat_rooms         │           │
├─────────────────────┤           │
│ id (PK)             │           │
│ name                │           │
│ created_at          │           │
└──────────┬──────────┘           │
           │ 1:N                  │
           ▼                      │
┌─────────────────────────┐      │
│  messages               │      │
├─────────────────────────┤      │
│ id (PK)                 │◄─────┼──┐ self-reference
│ chat_room_id (FK)       │      │  │
│ sender_id (FK)          │──────┘  │
│ message_type            │         │
│ content                 │         │
│ emoticon_id             │         │
│ reply_to_message_id (FK)│─────────┘
│ created_at              │
└──────────┬──────────────┘
           │ 1:N
           ▼
┌─────────────────────┐
│  message_likes      │
├─────────────────────┤
│ message_id (PK, FK) │
│ user_id (PK, FK)    │──────► user_profiles.id
│ created_at          │
└─────────────────────┘
```

---

## 5. 이모티콘 관리

### 5.1 간단한 접근 (초기 버전)

이모티콘 ID는 **고정된 문자열 코드**로 관리 (별도 테이블 없음):
- 프론트엔드 상수로 정의: `const EMOTICONS = ['smile', 'heart', 'thumbsup', ...]`
- 백엔드에서도 동일한 상수로 검증
- DB에는 `emoticon_id` 문자열만 저장

### 5.2 향후 확장 (동적 관리)

필요 시 `emoticons` 테이블 추가:
```sql
CREATE TABLE emoticons (
  id varchar(50) PRIMARY KEY,
  image_url text NOT NULL,
  display_order int NOT NULL
);
```

---

## 6. 주요 쿼리 패턴

### 6.1 채팅방 목록 조회

```sql
SELECT
  cr.id,
  cr.name,
  cr.created_at,
  m.content AS last_message_content,
  m.message_type AS last_message_type,
  m.emoticon_id AS last_message_emoticon_id,
  m.created_at AS last_message_time,
  up.nickname AS last_message_sender
FROM chat_rooms cr
LEFT JOIN LATERAL (
  SELECT * FROM messages
  WHERE chat_room_id = cr.id
  ORDER BY created_at DESC
  LIMIT 1
) m ON true
LEFT JOIN user_profiles up ON m.sender_id = up.id
ORDER BY COALESCE(m.created_at, cr.created_at) DESC
LIMIT 100;
```

### 6.2 메시지 목록 조회

```sql
SELECT
  m.id,
  m.message_type,
  m.content,
  m.emoticon_id,
  m.created_at,
  m.sender_id,
  sender.nickname AS sender_nickname,
  -- 답장 정보
  reply_msg.id AS reply_to_id,
  reply_msg.content AS reply_to_content,
  reply_msg.message_type AS reply_to_type,
  reply_msg.emoticon_id AS reply_to_emoticon_id,
  reply_sender.nickname AS reply_to_sender_nickname,
  -- 좋아요 정보
  COUNT(ml.user_id) AS like_count,
  BOOL_OR(ml.user_id = $current_user_id) AS is_liked_by_me
FROM messages m
LEFT JOIN user_profiles sender ON m.sender_id = sender.id
LEFT JOIN messages reply_msg ON m.reply_to_message_id = reply_msg.id
LEFT JOIN user_profiles reply_sender ON reply_msg.sender_id = reply_sender.id
LEFT JOIN message_likes ml ON m.id = ml.message_id
WHERE m.chat_room_id = $chat_room_id
GROUP BY m.id, sender.id, reply_msg.id, reply_sender.id
ORDER BY m.created_at ASC
LIMIT 50 OFFSET $offset;
```

### 6.3 메시지 전송

```sql
-- 텍스트
INSERT INTO messages (chat_room_id, sender_id, message_type, content, reply_to_message_id)
VALUES ($1, $2, 'text', $3, $4)
RETURNING *;

-- 이모티콘
INSERT INTO messages (chat_room_id, sender_id, message_type, emoticon_id, reply_to_message_id)
VALUES ($1, $2, 'emoticon', $3, $4)
RETURNING *;
```

### 6.4 좋아요 토글

```sql
-- 추가
INSERT INTO message_likes (message_id, user_id)
VALUES ($1, $2)
ON CONFLICT DO NOTHING;

-- 삭제
DELETE FROM message_likes
WHERE message_id = $1 AND user_id = $2;
```

### 6.5 메시지 일괄 삭제

```sql
DELETE FROM messages
WHERE id = ANY($1::uuid[])
  AND sender_id = $2; -- 본인 확인
```

---

## 7. 데이터 무결성

### 7.1 외래 키 동작

| 테이블 | 외래 키 | 삭제 시 동작 | 이유 |
|--------|---------|-------------|------|
| user_profiles → auth.users | CASCADE | 사용자 삭제 시 프로필도 삭제 | Auth 삭제 = 완전 탈퇴 |
| messages → chat_rooms | CASCADE | 채팅방 삭제 시 메시지도 삭제 | 채팅방 소속 데이터 |
| messages → user_profiles (sender) | **SET NULL** | 사용자 삭제 시 발신자만 NULL | **히스토리 보존** |
| messages → messages (reply) | SET NULL | 답장 대상 삭제 시 NULL | 답장 메시지는 유지 |
| message_likes → messages | CASCADE | 메시지 삭제 시 좋아요도 삭제 | 의미 없는 데이터 |
| message_likes → user_profiles | CASCADE | 사용자 삭제 시 좋아요도 삭제 | 의미 없는 데이터 |

### 7.2 CHECK 제약 조건

```sql
-- messages 테이블
ALTER TABLE messages ADD CONSTRAINT messages_content_check
CHECK (
  (message_type = 'text' AND content IS NOT NULL AND emoticon_id IS NULL) OR
  (message_type = 'emoticon' AND emoticon_id IS NOT NULL AND content IS NULL)
);
```

---

## 8. 성능 최적화

### 8.1 인덱싱 전략

**최소한의 인덱스만 유지** (쓰기 성능 고려):

1. **chat_rooms.created_at**: 목록 정렬
2. **(messages.chat_room_id, created_at)**: 메시지 목록 조회 (복합 인덱스)
3. **messages.sender_id**: 일괄 삭제 시 본인 메시지 필터링
4. **(message_likes.message_id, user_id)**: 복합 PK로 중복 방지 + 조회
5. **message_likes.user_id**: 사용자별 좋아요 조회

제거된 인덱스:
- `messages.reply_to_message_id`: 사용 빈도 낮음
- `chat_rooms.created_by`: 컬럼 자체 제거

### 8.2 쿼리 최적화

- **LATERAL JOIN**: 채팅방별 최근 메시지 효율적 조회
- **GROUP BY + BOOL_OR**: 메시지별 좋아요 정보 한 번에 조회
- **페이지네이션**: 메시지 50개 단위, 채팅방 100개 제한

---

## 9. 보안

### 9.1 RLS 비활성화

프로젝트 가이드라인에 따라 **모든 테이블에서 RLS 비활성화**:

```sql
ALTER TABLE user_profiles DISABLE ROW LEVEL SECURITY;
ALTER TABLE chat_rooms DISABLE ROW LEVEL SECURITY;
ALTER TABLE messages DISABLE ROW LEVEL SECURITY;
ALTER TABLE message_likes DISABLE ROW LEVEL SECURITY;
```

### 9.2 권한 검증

**백엔드 서비스 레이어(Hono)**에서 처리:
- Supabase Auth 세션 검증 (미들웨어)
- 메시지 삭제 시 `sender_id` 확인
- XSS 방지: 입력값 sanitization

---

## 10. 마이그레이션 파일 구조

```
/supabase/migrations/
  0001_create_user_profiles.sql
  0002_create_chat_rooms.sql
  0003_create_messages.sql
  0004_create_message_likes.sql
```

### 원칙
- `CREATE TABLE IF NOT EXISTS` (멱등성)
- 외래 키 제약 조건 명시
- RLS 비활성화
- 주석 추가

---

## 11. 개선 사항 요약

### 제거된 요소 (오버엔지니어링)
1. ✂️ `updated_at` 컬럼 (user_profiles, chat_rooms): 사용되지 않음
2. ✂️ `chat_rooms.created_by`: PRD에 생성자 표시 요구사항 없음
3. ✂️ `message_likes.id`: 복합 PK로 충분
4. ✂️ `messages.reply_to_message_id` 인덱스: 사용 빈도 낮음
5. ✂️ 트리거 함수: `updated_at` 제거로 불필요

### 변경된 요소 (무결성 개선)
1. 🔧 `messages.sender_id`: CASCADE → **SET NULL** (히스토리 보존)
2. 🔧 `message_type`: varchar(20) → **ENUM** (성능/타입 안전성)
3. 🔧 `message_likes`: 별도 id → **복합 PK** (간결성)

### 추가/명확화된 요소
1. ➕ 이모티콘 관리 방식 명시 (고정 코드 vs 동적 테이블)
2. ➕ 탈퇴 사용자 처리 방침 (메시지 유지)
3. ➕ 성능 중심 인덱싱 전략

---

## 12. 향후 확장 고려사항

### Phase 2
- `emoticons` 테이블: 동적 이모티콘 관리
- `chat_room_members` 테이블: 비공개 채팅방
- `user_profiles.avatar_url`: 프로필 이미지

### Phase 3
- `message_read_status` 테이블: 읽음/안읽음
- `message_attachments` 테이블: 파일 첨부
- Supabase Realtime 구독

---

## 13. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
|------|------|--------|-----------|
| 2.0 | 2025-10-20 | Claude Code | 오버엔지니어링 제거, 무결성 개선, 간결화 |
| 1.0 | 2025-10-20 | Claude Code | 초안 작성 |

---

**문서 종료**
