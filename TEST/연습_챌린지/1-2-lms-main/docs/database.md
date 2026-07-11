# Database Schema & Data Flow

## 1. 데이터플로우 요약

```
[Supabase Auth]
    ↓
[profiles] ← role, name, phone
    ↓
┌─────────────┬─────────────┐
│   Learner   │ Instructor  │
└─────────────┴─────────────┘
       ↓             ↓
[enrollments]  [courses] (draft/published/archived)
       ↓             ↓
       └──→ [assignments] (draft/published/closed)
                   ↓
            [submissions] ← text, link, status
                   ↓
            [grading/feedback]
```

### 주요 흐름

1. **인증 → 프로필 생성**: Supabase Auth → `profiles` 테이블에 역할(learner/instructor) 저장
2. **코스 개설**: Instructor → `courses` 생성 (draft → published)
3. **과제 생성**: Instructor → `assignments` 생성 (코스 연결)
4. **수강 신청**: Learner → `enrollments` 레코드 생성
5. **과제 제출**: Learner → `submissions` 레코드 생성 (text + link)
6. **채점**: Instructor → `submissions` 업데이트 (점수 + 피드백)

---

## 2. 데이터베이스 스키마

### 2.1 사용자 및 프로필

#### `profiles`
사용자 기본 정보 및 역할 관리

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PK, FK → auth.users | Supabase Auth 사용자 ID |
| role | text | NOT NULL, CHECK IN ('learner', 'instructor', 'operator') | 사용자 역할 |
| name | text | NOT NULL | 이름 |
| phone | text | NOT NULL | 휴대폰번호 |
| terms_agreed_at | timestamptz | NOT NULL | 약관 동의 일시 |
| created_at | timestamptz | NOT NULL, DEFAULT now() | 생성 일시 |
| updated_at | timestamptz | NOT NULL, DEFAULT now() | 수정 일시 |

**인덱스**
- `idx_profiles_role` ON `role`

---

### 2.2 메타데이터

#### `categories`
코스 카테고리

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PK, DEFAULT gen_random_uuid() | 카테고리 ID |
| name | text | NOT NULL, UNIQUE | 카테고리 이름 |
| is_active | boolean | NOT NULL, DEFAULT true | 활성 여부 |
| created_at | timestamptz | NOT NULL, DEFAULT now() | 생성 일시 |
| updated_at | timestamptz | NOT NULL, DEFAULT now() | 수정 일시 |

#### `difficulty_levels`
난이도 레벨

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PK, DEFAULT gen_random_uuid() | 난이도 ID |
| name | text | NOT NULL, UNIQUE | 난이도 이름 (예: Beginner, Intermediate, Advanced) |
| level | integer | NOT NULL, UNIQUE | 정렬용 레벨 (1, 2, 3...) |
| is_active | boolean | NOT NULL, DEFAULT true | 활성 여부 |
| created_at | timestamptz | NOT NULL, DEFAULT now() | 생성 일시 |
| updated_at | timestamptz | NOT NULL, DEFAULT now() | 수정 일시 |

**인덱스**
- `idx_difficulty_levels_level` ON `level`

---

### 2.3 코스 관리

#### `courses`
코스 정보

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PK, DEFAULT gen_random_uuid() | 코스 ID |
| instructor_id | uuid | NOT NULL, FK → profiles(id) | 강사 ID |
| category_id | uuid | NOT NULL, FK → categories(id) | 카테고리 ID |
| difficulty_id | uuid | NOT NULL, FK → difficulty_levels(id) | 난이도 ID |
| title | text | NOT NULL | 코스 제목 |
| description | text | NOT NULL | 코스 소개 |
| curriculum | text | | 커리큘럼 (텍스트 또는 JSON) |
| enrollments_count | integer | NOT NULL, DEFAULT 0 | 수강생 수 (카운트 캐시) |
| status | text | NOT NULL, DEFAULT 'draft', CHECK IN ('draft', 'published', 'archived') | 코스 상태 |
| created_at | timestamptz | NOT NULL, DEFAULT now() | 생성 일시 |
| updated_at | timestamptz | NOT NULL, DEFAULT now() | 수정 일시 |

**인덱스**
- `idx_courses_instructor_id` ON `instructor_id`
- `idx_courses_status` ON `status`
- `idx_courses_category_id` ON `category_id`
- `idx_courses_difficulty_id` ON `difficulty_id`
- `idx_courses_created_at` ON `created_at` (정렬용)
- `idx_courses_enrollments_count` ON `enrollments_count` (인기순 정렬용)

**정책**
- Instructor만 본인 코스 생성/수정 가능
- `published` 상태만 Learner에게 노출

---

### 2.4 수강 관리

#### `enrollments`
수강 신청 정보

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PK, DEFAULT gen_random_uuid() | 수강 ID |
| learner_id | uuid | NOT NULL, FK → profiles(id) | 학습자 ID |
| course_id | uuid | NOT NULL, FK → courses(id) | 코스 ID |
| enrolled_at | timestamptz | NOT NULL, DEFAULT now() | 수강 신청 일시 |
| cancelled_at | timestamptz | | 수강 취소 일시 |
| created_at | timestamptz | NOT NULL, DEFAULT now() | 생성 일시 |
| updated_at | timestamptz | NOT NULL, DEFAULT now() | 수정 일시 |

**제약 조건**
- `UNIQUE(learner_id, course_id)` (중복 신청 방지)

**인덱스**
- `idx_enrollments_learner_id` ON `learner_id`
- `idx_enrollments_course_id` ON `course_id`
- `idx_enrollments_cancelled_at` ON `cancelled_at` (활성 수강 조회용)

**정책**
- Learner는 `published` 코스만 신청 가능
- 중복 신청 불가

---

### 2.5 과제 관리

#### `assignments`
과제 정보

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PK, DEFAULT gen_random_uuid() | 과제 ID |
| course_id | uuid | NOT NULL, FK → courses(id) | 코스 ID |
| title | text | NOT NULL | 과제 제목 |
| description | text | NOT NULL | 과제 설명 |
| due_date | timestamptz | NOT NULL | 마감일 |
| weight | decimal(5,2) | NOT NULL, CHECK (weight >= 0 AND weight <= 100) | 점수 비중 (0~100) |
| allow_late | boolean | NOT NULL, DEFAULT false | 지각 제출 허용 여부 |
| allow_resubmit | boolean | NOT NULL, DEFAULT false | 재제출 허용 여부 |
| status | text | NOT NULL, DEFAULT 'draft', CHECK IN ('draft', 'published', 'closed') | 과제 상태 |
| created_at | timestamptz | NOT NULL, DEFAULT now() | 생성 일시 |
| updated_at | timestamptz | NOT NULL, DEFAULT now() | 수정 일시 |

**인덱스**
- `idx_assignments_course_id` ON `course_id`
- `idx_assignments_status` ON `status`
- `idx_assignments_due_date` ON `due_date` (마감 임박 조회용)

**정책**
- Instructor는 본인 코스의 과제만 생성/수정 가능
- `published` 상태만 Learner에게 노출
- 마감일(`due_date`) 이후 자동 `closed` (트리거/배치 처리)

---

### 2.6 제출 및 채점

#### `submissions`
과제 제출 및 채점 정보

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PK, DEFAULT gen_random_uuid() | 제출 ID |
| assignment_id | uuid | NOT NULL, FK → assignments(id) | 과제 ID |
| learner_id | uuid | NOT NULL, FK → profiles(id) | 학습자 ID |
| submission_text | text | NOT NULL | 제출 텍스트 (필수) |
| submission_link | text | | 제출 링크 (선택, URL 형식) |
| submission_file_url | text | | 제출 파일 URL (Supabase Storage 연동용, 향후 확장) |
| is_late | boolean | NOT NULL, DEFAULT false | 지각 여부 |
| score | decimal(5,2) | CHECK (score IS NULL OR (score >= 0 AND score <= 100)) | 점수 (0~100) |
| feedback | text | | 피드백 |
| status | text | NOT NULL, DEFAULT 'submitted', CHECK IN ('submitted', 'graded', 'resubmission_required') | 제출 상태 |
| submitted_at | timestamptz | NOT NULL, DEFAULT now() | 제출 일시 |
| graded_at | timestamptz | | 채점 일시 |
| created_at | timestamptz | NOT NULL, DEFAULT now() | 생성 일시 |
| updated_at | timestamptz | NOT NULL, DEFAULT now() | 수정 일시 |

**제약 조건**
- `UNIQUE(assignment_id, learner_id)` (과제당 1개 제출, 재제출은 UPDATE)

**인덱스**
- `idx_submissions_assignment_id` ON `assignment_id`
- `idx_submissions_learner_id` ON `learner_id`
- `idx_submissions_status` ON `status` (미채점 조회용)
- `idx_submissions_is_late` ON `is_late` (지각 필터용)

**정책**
- Learner는 본인이 수강 중인(`enrollments`) 코스의 `published` 과제만 제출 가능
- 마감일 전: `is_late=false`
- 마감일 후 + `allow_late=true`: `is_late=true`
- 마감일 후 + `allow_late=false`: 제출 차단
- 재제출: `allow_resubmit=true` 시 UPDATE 가능
- 재제출 시 `submission_text`, `submission_link`, `submitted_at` 등은 갱신되지만, `is_late` 값은 재제출 시점이 아닌 최초 `assignments.due_date`를 기준으로 계산되어야 한다.
- Instructor는 본인 코스 과제의 제출물만 채점 가능

---

### 2.7 운영

#### `reports`
신고 접수 및 처리

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PK, DEFAULT gen_random_uuid() | 신고 ID |
| reporter_id | uuid | NOT NULL, FK → profiles(id) | 신고자 ID |
| target_type | text | NOT NULL, CHECK IN ('course', 'assignment', 'submission', 'user') | 신고 대상 유형 |
| target_id | uuid | NOT NULL | 신고 대상 ID |
| reason | text | NOT NULL | 신고 사유 |
| content | text | NOT NULL | 신고 내용 |
| status | text | NOT NULL, DEFAULT 'received', CHECK IN ('received', 'investigating', 'resolved') | 처리 상태 |
| action_taken | text | | 조치 내용 |
| resolved_at | timestamptz | | 처리 완료 일시 |
| created_at | timestamptz | NOT NULL, DEFAULT now() | 생성 일시 |
| updated_at | timestamptz | NOT NULL, DEFAULT now() | 수정 일시 |

**인덱스**
- `idx_reports_reporter_id` ON `reporter_id`
- `idx_reports_target_type` ON `target_type`
- `idx_reports_status` ON `status`

**정책**
- 운영자(`role=operator`)만 조회/처리 가능

---

## 3. 주요 비즈니스 룰 (데이터베이스 관점)

### 3.1 코스 Archive 시 과제 상태 동기화
`courses` 테이블의 `status`가 `archived`로 변경될 때, 해당 `course_id`를 참조하는 `assignments` 중 `status`가 `published`인 모든 과제를 `closed`로 업데이트하는 로직이 필요하다. (애플리케이션 또는 트리거로 구현)

```sql
-- 코스 Archive 시 과제 자동 Close
UPDATE assignments
SET status = 'closed'
WHERE course_id = ? AND status = 'published';
```

### 3.2 과제 제출 시 지각 여부 판단
```sql
-- 제출 시점에서 is_late 계산
is_late = (NOW() > assignments.due_date)

-- 제출 가능 여부
IF is_late = true AND assignments.allow_late = false THEN
  RAISE EXCEPTION '마감일이 지나 제출할 수 없습니다.';
END IF;
```

### 3.3 재제출 가능 여부
```sql
-- 재제출 요청 시
IF assignments.allow_resubmit = false THEN
  RAISE EXCEPTION '재제출이 허용되지 않습니다.';
END IF;

-- 제출물 status 업데이트
UPDATE submissions SET status = 'resubmission_required' WHERE id = ?;
```

### 3.4 코스 총점 계산
```sql
-- 과제별 점수 × 비중 합산
SELECT
  course_id,
  SUM(score * weight / 100) AS total_score
FROM submissions s
JOIN assignments a ON s.assignment_id = a.id
WHERE learner_id = ? AND status = 'graded'
GROUP BY course_id;
```

### 3.5 진행률 계산
```sql
-- 완료 과제 수 / 전체 과제 수
SELECT
  course_id,
  COUNT(CASE WHEN status IN ('graded', 'resubmission_required') THEN 1 END) AS completed,
  COUNT(*) AS total,
  ROUND(COUNT(CASE WHEN status IN ('graded', 'resubmission_required') THEN 1 END) * 100.0 / COUNT(*), 2) AS progress_rate
FROM submissions s
JOIN assignments a ON s.assignment_id = a.id
WHERE learner_id = ?
GROUP BY course_id;
```

### 3.6 채점 대기 수 (Instructor)
```sql
SELECT COUNT(*)
FROM submissions s
JOIN assignments a ON s.assignment_id = a.id
JOIN courses c ON a.course_id = c.id
WHERE c.instructor_id = ? AND s.status = 'submitted';
```

---

## 4. 트리거 및 자동화

### 4.1 `updated_at` 자동 갱신
모든 테이블에 적용

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 각 테이블마다 트리거 생성
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON profiles
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- (다른 테이블도 동일)
```

### 4.2 마감일 이후 자동 `closed` (선택)
```sql
-- 주기적 배치 또는 트리거
UPDATE assignments
SET status = 'closed'
WHERE status = 'published' AND due_date < NOW();
```

---

## 5. 데이터 무결성 체크리스트

- [x] 사용자 역할(`role`)은 `learner`, `instructor`, `operator`만 허용
- [x] 코스 상태(`status`)는 `draft`, `published`, `archived`만 허용
- [x] 과제 상태(`status`)는 `draft`, `published`, `closed`만 허용
- [x] 제출 상태(`status`)는 `submitted`, `graded`, `resubmission_required`만 허용
- [x] 점수(`score`, `weight`)는 0~100 범위 내
- [x] 수강 신청 중복 방지(`UNIQUE(learner_id, course_id)`)
- [x] 과제 제출 중복 방지(`UNIQUE(assignment_id, learner_id)`)
- [x] 외래키 제약(`FK`)을 통한 참조 무결성
- [x] `NOT NULL` 제약을 통한 필수 필드 보장

---

## 6. 확장 고려사항 (현재 미포함)

- **알림**: `notifications` 테이블 (과제 마감 알림, 채점 완료 알림 등)
- **댓글/Q&A**: `comments` 테이블 (과제/코스별 질문/답변)
- **평점/리뷰**: `reviews` 테이블 (코스 평점 및 후기)
- **파일 업로드**: `submissions` 테이블에 `submission_file_url` 컬럼을 추가하고, Supabase Storage와 연동하여 과제 파일 제출 기능 구현 (현재 컬럼은 추가되어 있으나 기능 미구현)
- **감사 로그**: `audit_logs` 테이블 (민감한 작업 이력)
