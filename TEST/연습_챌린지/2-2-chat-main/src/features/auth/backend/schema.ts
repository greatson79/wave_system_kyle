import { z } from 'zod';

// 회원가입
export const SignupRequestSchema = z.object({
  nickname: z
    .string()
    .min(2, '닉네임은 2~20자여야 합니다')
    .max(20, '닉네임은 2~20자여야 합니다')
    .regex(/^[가-힣a-zA-Z0-9]+$/, '특수문자는 사용할 수 없습니다'),
  email: z.string().email('유효한 이메일 주소를 입력하세요'),
  password: z
    .string()
    .min(8, '비밀번호는 8자 이상이어야 합니다')
    .regex(/^(?=.*[A-Za-z])(?=.*\d)/, '영문+숫자 조합이어야 합니다'),
});

export const SignupResponseSchema = z.object({
  success: z.literal(true),
  redirectTo: z.string(),
});

// 로그인
export const LoginRequestSchema = z.object({
  email: z.string().email(),
  password: z.string().min(1),
});

export const LoginResponseSchema = z.object({
  success: z.literal(true),
  user: z.object({
    id: z.string(),
    email: z.string(),
    nickname: z.string(),
  }),
  redirectTo: z.string(),
});

export type SignupRequest = z.infer<typeof SignupRequestSchema>;
export type SignupResponse = z.infer<typeof SignupResponseSchema>;
export type LoginRequest = z.infer<typeof LoginRequestSchema>;
export type LoginResponse = z.infer<typeof LoginResponseSchema>;
