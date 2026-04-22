-- Migration: LMS 데이터베이스 스키마 생성
-- 모든 테이블, 인덱스, 트리거, 제약조건 포함

-- pgcrypto 확장 (gen_random_uuid 사용)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ================================================================
-- 1. 사용자 및 프로필
-- ================================================================

-- profiles 테이블: 사용자 기본 정보 및 역할 관리
CREATE TABLE IF NOT EXISTS public.profiles (
  id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  role text NOT NULL CHECK (role IN ('learner', 'instructor', 'operator')),
  name text NOT NULL,
  phone text NOT NULL,
  terms_agreed_at timestamptz NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.profiles IS 'Supabase Auth 사용자의 프로필 정보 및 역할 관리';

-- profiles 인덱스
CREATE INDEX IF NOT EXISTS idx_profiles_role ON public.profiles(role);

-- ================================================================
-- 2. 메타데이터
-- ================================================================

-- categories 테이블: 코스 카테고리
CREATE TABLE IF NOT EXISTS public.categories (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL UNIQUE,
  is_active boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.categories IS '코스 카테고리 메타데이터';

-- difficulty_levels 테이블: 난이도 레벨
CREATE TABLE IF NOT EXISTS public.difficulty_levels (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL UNIQUE,
  level integer NOT NULL UNIQUE,
  is_active boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.difficulty_levels IS '코스 난이도 레벨 메타데이터';

-- difficulty_levels 인덱스
CREATE INDEX IF NOT EXISTS idx_difficulty_levels_level ON public.difficulty_levels(level);

-- ================================================================
-- 3. 코스 관리
-- ================================================================

-- courses 테이블: 코스 정보
CREATE TABLE IF NOT EXISTS public.courses (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  instructor_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  category_id uuid NOT NULL REFERENCES public.categories(id) ON DELETE RESTRICT,
  difficulty_id uuid NOT NULL REFERENCES public.difficulty_levels(id) ON DELETE RESTRICT,
  title text NOT NULL,
  description text NOT NULL,
  curriculum text,
  enrollments_count integer NOT NULL DEFAULT 0,
  status text NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.courses IS '강사가 개설한 코스 정보';

-- courses 인덱스
CREATE INDEX IF NOT EXISTS idx_courses_instructor_id ON public.courses(instructor_id);
CREATE INDEX IF NOT EXISTS idx_courses_status ON public.courses(status);
CREATE INDEX IF NOT EXISTS idx_courses_category_id ON public.courses(category_id);
CREATE INDEX IF NOT EXISTS idx_courses_difficulty_id ON public.courses(difficulty_id);
CREATE INDEX IF NOT EXISTS idx_courses_created_at ON public.courses(created_at);
CREATE INDEX IF NOT EXISTS idx_courses_enrollments_count ON public.courses(enrollments_count);

-- ================================================================
-- 4. 수강 관리
-- ================================================================

-- enrollments 테이블: 수강 신청 정보
CREATE TABLE IF NOT EXISTS public.enrollments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  learner_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  course_id uuid NOT NULL REFERENCES public.courses(id) ON DELETE CASCADE,
  enrolled_at timestamptz NOT NULL DEFAULT now(),
  cancelled_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT unique_learner_course UNIQUE (learner_id, course_id)
);

COMMENT ON TABLE public.enrollments IS '학습자의 코스 수강 신청 정보';

-- enrollments 인덱스
CREATE INDEX IF NOT EXISTS idx_enrollments_learner_id ON public.enrollments(learner_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_course_id ON public.enrollments(course_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_cancelled_at ON public.enrollments(cancelled_at);

-- ================================================================
-- 5. 과제 관리
-- ================================================================

-- assignments 테이블: 과제 정보
CREATE TABLE IF NOT EXISTS public.assignments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  course_id uuid NOT NULL REFERENCES public.courses(id) ON DELETE CASCADE,
  title text NOT NULL,
  description text NOT NULL,
  due_date timestamptz NOT NULL,
  weight decimal(5,2) NOT NULL CHECK (weight >= 0 AND weight <= 100),
  allow_late boolean NOT NULL DEFAULT false,
  allow_resubmit boolean NOT NULL DEFAULT false,
  status text NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'closed')),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.assignments IS '코스별 과제 정보';

-- assignments 인덱스
CREATE INDEX IF NOT EXISTS idx_assignments_course_id ON public.assignments(course_id);
CREATE INDEX IF NOT EXISTS idx_assignments_status ON public.assignments(status);
CREATE INDEX IF NOT EXISTS idx_assignments_due_date ON public.assignments(due_date);

-- ================================================================
-- 6. 제출 및 채점
-- ================================================================

-- submissions 테이블: 과제 제출 및 채점 정보
CREATE TABLE IF NOT EXISTS public.submissions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  assignment_id uuid NOT NULL REFERENCES public.assignments(id) ON DELETE CASCADE,
  learner_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  submission_text text NOT NULL,
  submission_link text,
  submission_file_url text,
  is_late boolean NOT NULL DEFAULT false,
  score decimal(5,2) CHECK (score IS NULL OR (score >= 0 AND score <= 100)),
  feedback text,
  status text NOT NULL DEFAULT 'submitted' CHECK (status IN ('submitted', 'graded', 'resubmission_required')),
  submitted_at timestamptz NOT NULL DEFAULT now(),
  graded_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT unique_assignment_learner UNIQUE (assignment_id, learner_id)
);

COMMENT ON TABLE public.submissions IS '학습자의 과제 제출 및 강사의 채점 정보';

-- submissions 인덱스
CREATE INDEX IF NOT EXISTS idx_submissions_assignment_id ON public.submissions(assignment_id);
CREATE INDEX IF NOT EXISTS idx_submissions_learner_id ON public.submissions(learner_id);
CREATE INDEX IF NOT EXISTS idx_submissions_status ON public.submissions(status);
CREATE INDEX IF NOT EXISTS idx_submissions_is_late ON public.submissions(is_late);

-- ================================================================
-- 7. 운영
-- ================================================================

-- reports 테이블: 신고 접수 및 처리
CREATE TABLE IF NOT EXISTS public.reports (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  reporter_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  target_type text NOT NULL CHECK (target_type IN ('course', 'assignment', 'submission', 'user')),
  target_id uuid NOT NULL,
  reason text NOT NULL,
  content text NOT NULL,
  status text NOT NULL DEFAULT 'received' CHECK (status IN ('received', 'investigating', 'resolved')),
  action_taken text,
  resolved_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.reports IS '사용자 신고 접수 및 처리 이력';

-- reports 인덱스
CREATE INDEX IF NOT EXISTS idx_reports_reporter_id ON public.reports(reporter_id);
CREATE INDEX IF NOT EXISTS idx_reports_target_type ON public.reports(target_type);
CREATE INDEX IF NOT EXISTS idx_reports_status ON public.reports(status);

-- ================================================================
-- 8. 트리거 및 자동화
-- ================================================================

-- updated_at 자동 갱신 함수
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- profiles updated_at 트리거
CREATE TRIGGER update_profiles_updated_at
  BEFORE UPDATE ON public.profiles
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- categories updated_at 트리거
CREATE TRIGGER update_categories_updated_at
  BEFORE UPDATE ON public.categories
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- difficulty_levels updated_at 트리거
CREATE TRIGGER update_difficulty_levels_updated_at
  BEFORE UPDATE ON public.difficulty_levels
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- courses updated_at 트리거
CREATE TRIGGER update_courses_updated_at
  BEFORE UPDATE ON public.courses
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- enrollments updated_at 트리거
CREATE TRIGGER update_enrollments_updated_at
  BEFORE UPDATE ON public.enrollments
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- assignments updated_at 트리거
CREATE TRIGGER update_assignments_updated_at
  BEFORE UPDATE ON public.assignments
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- submissions updated_at 트리거
CREATE TRIGGER update_submissions_updated_at
  BEFORE UPDATE ON public.submissions
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- reports updated_at 트리거
CREATE TRIGGER update_reports_updated_at
  BEFORE UPDATE ON public.reports
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- ================================================================
-- 9. Row Level Security (RLS) 비활성화
-- ================================================================

ALTER TABLE IF EXISTS public.profiles DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.categories DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.difficulty_levels DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.courses DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.enrollments DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.assignments DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.submissions DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.reports DISABLE ROW LEVEL SECURITY;
