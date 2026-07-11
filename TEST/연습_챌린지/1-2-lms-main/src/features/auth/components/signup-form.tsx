'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useRouter } from 'next/navigation';
import { SignupRequestSchema, type SignupRequest } from '../lib/dto';
import { useSignup } from '../hooks/useSignup';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { RoleSelect } from './role-select';
import { TermsCheckbox } from './terms-checkbox';
import { useToast } from '@/hooks/use-toast';

const defaultValues: SignupRequest = {
  email: '',
  password: '',
  role: 'learner',
  name: '',
  phone: '',
  termsAgreed: {
    service: false,
    privacy: false,
  },
};

export function SignupForm() {
  const router = useRouter();
  const { toast } = useToast();
  const { mutate: signup, isPending } = useSignup();

  const form = useForm<SignupRequest>({
    resolver: zodResolver(SignupRequestSchema),
    defaultValues,
  });

  const onSubmit = (data: SignupRequest) => {
    signup(data, {
      onSuccess: (response) => {
        toast({
          title: '회원가입 성공',
          description: '환영합니다! 잠시 후 이동합니다.',
        });

        setTimeout(() => {
          router.push(response.redirectTo);
        }, 1000);
      },
      onError: (error) => {
        toast({
          variant: 'destructive',
          title: '회원가입 실패',
          description: error.message,
        });
      },
    });
  };

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="flex flex-col gap-4"
      >
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>이메일</FormLabel>
              <FormControl>
                <Input
                  type="email"
                  autoComplete="email"
                  placeholder="example@email.com"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>비밀번호</FormLabel>
              <FormControl>
                <Input
                  type="password"
                  autoComplete="new-password"
                  placeholder="8자 이상 입력해주세요"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>이름</FormLabel>
              <FormControl>
                <Input
                  type="text"
                  autoComplete="name"
                  placeholder="홍길동"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="phone"
          render={({ field }) => (
            <FormItem>
              <FormLabel>휴대폰번호</FormLabel>
              <FormControl>
                <Input
                  type="tel"
                  autoComplete="tel"
                  placeholder="010-1234-5678"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <RoleSelect control={form.control} name="role" />

        <TermsCheckbox
          control={form.control}
          serviceName="termsAgreed.service"
          privacyName="termsAgreed.privacy"
          setValue={form.setValue}
          serviceValue={form.watch('termsAgreed.service')}
          privacyValue={form.watch('termsAgreed.privacy')}
        />

        <Button type="submit" disabled={isPending} className="mt-2">
          {isPending ? '가입 중...' : '회원가입'}
        </Button>
      </form>
    </Form>
  );
}
