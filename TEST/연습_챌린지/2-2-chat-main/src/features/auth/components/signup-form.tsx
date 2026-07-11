'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import Link from 'next/link';
import { useSignupMutation } from '../hooks/useSignupMutation';
import { extractApiErrorMessage } from '@/lib/remote/api-client';

const signupFormSchema = z
  .object({
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
    passwordConfirm: z.string().min(1, '비밀번호 확인을 입력하세요'),
  })
  .refine((data) => data.password === data.passwordConfirm, {
    message: '비밀번호가 일치하지 않습니다',
    path: ['passwordConfirm'],
  });

type SignupFormData = z.infer<typeof signupFormSchema>;

export function SignupForm() {
  const router = useRouter();
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<SignupFormData>({
    resolver: zodResolver(signupFormSchema),
    mode: 'onBlur',
  });

  const signupMutation = useSignupMutation();

  const onSubmit = async (data: SignupFormData) => {
    setServerError(null);

    try {
      const result = await signupMutation.mutateAsync({
        nickname: data.nickname,
        email: data.email,
        password: data.password,
      });

      router.push(result.redirectTo);
    } catch (error) {
      const errorMessage = extractApiErrorMessage(
        error,
        '회원가입에 실패했습니다. 다시 시도해주세요.',
      );
      setServerError(errorMessage);
    }
  };

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="flex flex-col gap-4 rounded-xl border border-slate-200 p-6 shadow-sm"
    >
      <label className="flex flex-col gap-2 text-sm text-slate-700">
        닉네임
        <input
          type="text"
          placeholder="2~20자, 특수문자 제외"
          {...register('nickname')}
          className="rounded-md border border-slate-300 px-3 py-2 focus:border-slate-500 focus:outline-none"
        />
        {errors.nickname && (
          <span className="text-xs text-rose-500">{errors.nickname.message}</span>
        )}
      </label>

      <label className="flex flex-col gap-2 text-sm text-slate-700">
        이메일
        <input
          type="email"
          placeholder="example@example.com"
          autoComplete="email"
          {...register('email')}
          className="rounded-md border border-slate-300 px-3 py-2 focus:border-slate-500 focus:outline-none"
        />
        {errors.email && (
          <span className="text-xs text-rose-500">{errors.email.message}</span>
        )}
      </label>

      <label className="flex flex-col gap-2 text-sm text-slate-700">
        비밀번호
        <input
          type="password"
          placeholder="8자 이상, 영문+숫자 조합"
          autoComplete="new-password"
          {...register('password')}
          className="rounded-md border border-slate-300 px-3 py-2 focus:border-slate-500 focus:outline-none"
        />
        {errors.password && (
          <span className="text-xs text-rose-500">{errors.password.message}</span>
        )}
      </label>

      <label className="flex flex-col gap-2 text-sm text-slate-700">
        비밀번호 확인
        <input
          type="password"
          autoComplete="new-password"
          {...register('passwordConfirm')}
          className="rounded-md border border-slate-300 px-3 py-2 focus:border-slate-500 focus:outline-none"
        />
        {errors.passwordConfirm && (
          <span className="text-xs text-rose-500">
            {errors.passwordConfirm.message}
          </span>
        )}
      </label>

      {serverError && <p className="text-sm text-rose-500">{serverError}</p>}

      <button
        type="submit"
        disabled={isSubmitting}
        className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-400"
      >
        {isSubmitting ? '회원가입 중...' : '회원가입'}
      </button>

      <p className="text-xs text-slate-500">
        이미 계정이 있으신가요?{' '}
        <Link
          href="/login"
          className="font-medium text-slate-700 underline hover:text-slate-900"
        >
          로그인으로 이동
        </Link>
      </p>
    </form>
  );
}
