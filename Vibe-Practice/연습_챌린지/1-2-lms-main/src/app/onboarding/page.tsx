import { redirect } from 'next/navigation'
import { createSupabaseServerClient } from '@/lib/supabase/server-client'
import OnboardingForm from '@/features/onboarding/components/OnboardingForm'

export default async function OnboardingPage() {
  const supabase = await createSupabaseServerClient()

  // 1. 인증 확인
  const { data: { session } } = await supabase.auth.getSession()

  if (!session) {
    redirect('/login')
  }

  // 2. 프로필 확인 (이미 있으면 역할별 페이지로)
  const { data: profile, error } = await supabase
    .from('profiles')
    .select('role')
    .eq('id', session.user.id)
    .maybeSingle()

  if (!error && profile) {
    const profileData = profile as unknown as { role: 'learner' | 'instructor' | 'operator' }
    // 프로필이 이미 있으면 역할에 따라 리다이렉트
    if (profileData.role === 'learner') {
      redirect('/courses')
    }
    if (profileData.role === 'instructor') {
      redirect('/instructor/dashboard')
    }
  }

  return (
    <div className="container mx-auto px-4 py-16 max-w-2xl">
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold mb-2">프로필 설정</h1>
        <p className="text-muted-foreground">
          서비스 이용을 위해 기본 정보를 입력해주세요
        </p>
      </div>
      <OnboardingForm />
    </div>
  )
}
