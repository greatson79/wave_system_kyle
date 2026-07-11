-- Migration: 약관 동의 이력 테이블 생성
-- 사용자의 약관 동의 이력을 영구 보관하기 위한 테이블

-- terms_agreements 테이블: 약관 동의 이력
CREATE TABLE IF NOT EXISTS public.terms_agreements (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  terms_type text NOT NULL CHECK (terms_type IN ('service', 'privacy')),
  agreed_at timestamptz NOT NULL DEFAULT now(),
  ip_address text,
  user_agent text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.terms_agreements IS '사용자 약관 동의 이력 (감사용 영구 보관)';
COMMENT ON COLUMN public.terms_agreements.terms_type IS '약관 유형: service(서비스 이용약관), privacy(개인정보 처리방침)';

-- terms_agreements 인덱스
CREATE INDEX IF NOT EXISTS idx_terms_agreements_user_id ON public.terms_agreements(user_id);
CREATE INDEX IF NOT EXISTS idx_terms_agreements_terms_type ON public.terms_agreements(terms_type);
CREATE INDEX IF NOT EXISTS idx_terms_agreements_agreed_at ON public.terms_agreements(agreed_at);

-- terms_agreements updated_at 트리거
CREATE TRIGGER update_terms_agreements_updated_at
  BEFORE UPDATE ON public.terms_agreements
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- RLS 비활성화
ALTER TABLE IF EXISTS public.terms_agreements DISABLE ROW LEVEL SECURITY;
