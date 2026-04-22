'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useLookupBookings } from '../hooks/useLookupBookings';
import type { LookupBookingsResponse } from '../lib/dto';

const formSchema = z.object({
  phone: z.string().regex(/^01[0-9]{8,9}$/, '올바른 휴대폰번호 형식이 아닙니다 (예: 01012345678)'),
  password: z.string().regex(/^[0-9]{4}$/, '비밀번호는 숫자 4자리여야 합니다'),
});

type FormData = z.infer<typeof formSchema>;

interface BookingLookupFormProps {
  onSuccess: (result: LookupBookingsResponse, phone: string, password: string) => void;
}

export const BookingLookupForm = ({ onSuccess }: BookingLookupFormProps) => {
  const { mutate, isPending } = useLookupBookings();

  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: 'onChange',
  });

  const onSubmit = (data: FormData) => {
    mutate(data, {
      onSuccess: (result) => {
        onSuccess(result, data.phone, data.password);
      },
      onError: (error: any) => {
        if (error.code === 'AUTHENTICATION_FAILED') {
          alert('휴대폰번호 또는 비밀번호가 일치하지 않습니다.');
        } else {
          alert('예약 조회 중 오류가 발생했습니다. 다시 시도해주세요.');
        }
      },
    });
  };

  return (
    <div className="bg-white rounded-xl p-8 shadow-xl border border-[hsl(270,12%,88%)] max-w-md mx-auto">
      <h2 className="text-2xl font-bold mb-6 text-center">예약 정보 입력</h2>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div>
          <Label htmlFor="phone">휴대폰번호 * (숫자만)</Label>
          <Input
            id="phone"
            {...register('phone')}
            placeholder="01012345678"
            className="mt-1"
            disabled={isPending}
            maxLength={11}
          />
          {errors.phone && <p className="text-sm text-red-600 mt-1">{errors.phone.message}</p>}
          <p className="text-xs text-gray-500 mt-1">예: 01012345678 (하이픈 없이)</p>
        </div>

        <div>
          <Label htmlFor="password">비밀번호 4자리 *</Label>
          <Input
            id="password"
            type="password"
            {...register('password')}
            placeholder="1234"
            className="mt-1"
            disabled={isPending}
            maxLength={4}
          />
          {errors.password && <p className="text-sm text-red-600 mt-1">{errors.password.message}</p>}
        </div>

        <Button type="submit" variant="primary" className="w-full" size="lg" disabled={!isValid || isPending}>
          {isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
          {isPending ? '조회 중...' : '예약 조회'}
        </Button>
      </form>
    </div>
  );
};
