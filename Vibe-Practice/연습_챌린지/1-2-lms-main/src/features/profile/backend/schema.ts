import { z } from 'zod'

export const createProfileSchema = z.object({
  name: z.string().min(1, '이름을 입력해주세요'),
  phone: z.string().regex(/^[0-9]{10,11}$/, '올바른 휴대폰번호를 입력해주세요'),
  role: z.enum(['learner', 'instructor', 'operator'], {
    required_error: '역할을 선택해주세요',
  }),
})

export const profileResponseSchema = z.object({
  id: z.string().uuid(),
  role: z.enum(['learner', 'instructor', 'operator']),
  name: z.string(),
  phone: z.string(),
  terms_agreed_at: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
})

export type CreateProfileInput = z.infer<typeof createProfileSchema>
export type ProfileResponse = z.infer<typeof profileResponseSchema>
