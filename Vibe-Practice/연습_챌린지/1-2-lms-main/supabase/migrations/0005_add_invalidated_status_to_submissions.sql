-- Migration: submissions 테이블 상태에 'invalidated' 추가
-- Description: 운영자가 제출물을 무효화할 수 있도록 status 컬럼에 'invalidated' 값 허용

-- 기존 CHECK 제약조건 삭제
ALTER TABLE public.submissions
  DROP CONSTRAINT IF EXISTS submissions_status_check;

-- 새로운 CHECK 제약조건 추가 (invalidated 포함)
ALTER TABLE public.submissions
  ADD CONSTRAINT submissions_status_check
  CHECK (status IN ('submitted', 'graded', 'resubmission_required', 'invalidated'));

-- 제약조건 설명 추가
COMMENT ON CONSTRAINT submissions_status_check ON public.submissions IS '제출물 상태: submitted(제출됨), graded(채점됨), resubmission_required(재제출 요청), invalidated(무효화됨)';
