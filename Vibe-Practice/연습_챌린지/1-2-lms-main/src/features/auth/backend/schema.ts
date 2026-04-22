import { z } from 'zod';
import { PHONE_REGEX } from '@/lib/validators/phone';
import { MIN_PASSWORD_LENGTH } from '@/lib/validators/password';

export const SignupRequestSchema = z.object({
  email: z.string().email({ message: '올바른 이메일 형식을 입력해주세요.' }),
  password: z
    .string()
    .min(MIN_PASSWORD_LENGTH, {
      message: `비밀번호는 최소 ${MIN_PASSWORD_LENGTH}자 이상이어야 합니다.`,
    }),
  role: z.enum(['learner', 'instructor'], {
    errorMap: () => ({ message: '역할을 선택해주세요.' }),
  }),
  name: z
    .string()
    .min(1, { message: '이름을 입력해주세요.' })
    .max(100, { message: '이름은 100자 이하로 입력해주세요.' }),
  phone: z
    .string()
    .regex(PHONE_REGEX, { message: '유효한 휴대폰번호를 입력해주세요.' }),
  termsAgreed: z.object({
    service: z.boolean().refine((val) => val === true, {
      message: '서비스 이용약관에 동의해주세요.',
    }),
    privacy: z.boolean().refine((val) => val === true, {
      message: '개인정보 처리방침에 동의해주세요.',
    }),
  }),
});

export type SignupRequest = z.infer<typeof SignupRequestSchema>;

export const SignupResponseSchema = z.object({
  userId: z.string().uuid(),
  role: z.enum(['learner', 'instructor']),
  redirectTo: z.string(),
});

export type SignupResponse = z.infer<typeof SignupResponseSchema>;

export const ProfileRowSchema = z.object({
  id: z.string().uuid(),
  role: z.string(),
  name: z.string(),
  phone: z.string(),
  terms_agreed_at: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
});

export type ProfileRow = z.infer<typeof ProfileRowSchema>;
