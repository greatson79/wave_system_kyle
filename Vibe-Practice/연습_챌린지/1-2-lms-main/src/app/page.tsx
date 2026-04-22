import { redirect } from 'next/navigation'
import { createSupabaseServerClient } from '@/lib/supabase/server-client'
import LandingPage from '@/features/landing/components/LandingPage'

export const dynamic = 'force-dynamic'
export const revalidate = 0

export default async function RootPage() {
  const supabase = await createSupabaseServerClient()

  // 1. 인증 확인
  const { data: { session } } = await supabase.auth.getSession()

  // 비로그인: 랜딩페이지 렌더링
  if (!session) {
    return <LandingPage />
  }

  // 2. 프로필 확인
  const { data: profile, error } = await supabase
    .from('profiles')
    .select('role')
    .eq('id', session.user.id)
    .maybeSingle()

  // 프로필 없음: 온보딩
  if (error || !profile) {
    redirect('/onboarding')
  }

  // 타입 캐스팅
  const profileData = profile as unknown as { role: 'learner' | 'instructor' | 'operator' }

  // 3. 역할 기반 리다이렉트
  if (profileData.role === 'learner') {
    redirect('/dashboard')
  }

  if (profileData.role === 'instructor') {
    redirect('/instructor/dashboard')
  }

  // 4. Operator는 별도 처리 (추후 구현)
  if (profileData.role === 'operator') {
    redirect('/operator/reports')
  }

  // Fallback
  redirect('/login')
}
