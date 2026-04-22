'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useCreateProfile } from '@/features/profile/hooks/useCreateProfile'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { GraduationCap, Users } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

const onboardingSchema = z.object({
  name: z.string().min(1, '이름을 입력해주세요'),
  phone: z.string().regex(/^[0-9]{10,11}$/, '올바른 휴대폰번호를 입력해주세요 (10-11자리 숫자)'),
  role: z.enum(['learner', 'instructor'], {
    required_error: '역할을 선택해주세요',
  }),
  termsAgreed: z.boolean().refine(val => val === true, '약관에 동의해주세요'),
})

type OnboardingFormData = z.infer<typeof onboardingSchema>

export default function OnboardingForm() {
  const router = useRouter()
  const { toast } = useToast()
  const [selectedRole, setSelectedRole] = useState<'learner' | 'instructor' | null>(null)

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<OnboardingFormData>({
    resolver: zodResolver(onboardingSchema),
  })

  const createProfile = useCreateProfile()

  const onSubmit = async (data: OnboardingFormData) => {
    try {
      await createProfile.mutateAsync(data)

      toast({
        title: '프로필 생성 완료',
        description: '환영합니다!',
      })

      // 역할에 따라 리다이렉트
      if (data.role === 'learner') {
        router.push('/courses')
      } else {
        router.push('/instructor/dashboard')
      }
    } catch (error) {
      toast({
        title: '오류',
        description: '프로필 생성에 실패했습니다. 다시 시도해주세요.',
        variant: 'destructive',
      })
    }
  }

  const handleRoleSelect = (role: 'learner' | 'instructor') => {
    setSelectedRole(role)
    setValue('role', role, { shouldValidate: true })
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* 기본 정보 */}
      <Card>
        <CardHeader>
          <CardTitle>기본 정보</CardTitle>
          <CardDescription>이름과 연락처를 입력해주세요</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="name">이름 *</Label>
            <Input
              id="name"
              placeholder="홍길동"
              {...register('name')}
              className={errors.name ? 'border-red-500' : ''}
            />
            {errors.name && (
              <p className="text-sm text-red-500 mt-1">{errors.name.message}</p>
            )}
          </div>

          <div>
            <Label htmlFor="phone">휴대폰번호 *</Label>
            <Input
              id="phone"
              placeholder="01012345678"
              {...register('phone')}
              className={errors.phone ? 'border-red-500' : ''}
            />
            {errors.phone && (
              <p className="text-sm text-red-500 mt-1">{errors.phone.message}</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 역할 선택 */}
      <Card>
        <CardHeader>
          <CardTitle>역할 선택 *</CardTitle>
          <CardDescription>학습자 또는 강사 중 하나를 선택해주세요</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-4">
            <button
              type="button"
              onClick={() => handleRoleSelect('learner')}
              className={`
                p-6 border-2 rounded-lg transition-all
                ${selectedRole === 'learner'
                  ? 'border-blue-600 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
                }
              `}
            >
              <GraduationCap className={`
                w-12 h-12 mx-auto mb-3
                ${selectedRole === 'learner' ? 'text-blue-600' : 'text-gray-400'}
              `} />
              <h3 className="font-semibold text-lg mb-2">학습자</h3>
              <p className="text-sm text-gray-600">
                코스를 수강하고 과제를 제출합니다
              </p>
            </button>

            <button
              type="button"
              onClick={() => handleRoleSelect('instructor')}
              className={`
                p-6 border-2 rounded-lg transition-all
                ${selectedRole === 'instructor'
                  ? 'border-purple-600 bg-purple-50'
                  : 'border-gray-200 hover:border-gray-300'
                }
              `}
            >
              <Users className={`
                w-12 h-12 mx-auto mb-3
                ${selectedRole === 'instructor' ? 'text-purple-600' : 'text-gray-400'}
              `} />
              <h3 className="font-semibold text-lg mb-2">강사</h3>
              <p className="text-sm text-gray-600">
                코스를 개설하고 과제를 채점합니다
              </p>
            </button>
          </div>
          {errors.role && (
            <p className="text-sm text-red-500 mt-2">{errors.role.message}</p>
          )}
        </CardContent>
      </Card>

      {/* 약관 동의 */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-start space-x-3">
            <Checkbox
              id="terms"
              onCheckedChange={(checked) => {
                setValue('termsAgreed', checked === true, { shouldValidate: true })
              }}
            />
            <div className="space-y-1">
              <Label
                htmlFor="terms"
                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >
                서비스 이용약관 및 개인정보처리방침에 동의합니다 *
              </Label>
              {errors.termsAgreed && (
                <p className="text-sm text-red-500">{errors.termsAgreed.message}</p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 제출 버튼 */}
      <Button
        type="submit"
        className="w-full"
        size="lg"
        disabled={createProfile.isPending}
      >
        {createProfile.isPending ? '처리중...' : '시작하기'}
      </Button>
    </form>
  )
}
