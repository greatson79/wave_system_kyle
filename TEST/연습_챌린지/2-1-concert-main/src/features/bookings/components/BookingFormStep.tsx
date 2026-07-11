'use client';

import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useCreateBooking } from '../hooks/useCreateBooking';
import { useSeatSelectionStore } from '../stores/useSeatSelectionStore';
import type { CreateBookingRequest } from '../backend/schema';

interface BookingFormStepProps {
  concertId: string;
  onBack: () => void;
}

const formSchema = z.object({
  name: z.string().min(2, '예약자명은 2자 이상이어야 합니다').max(50),
  phone: z.string().regex(/^01[0-9]{8,9}$/, '올바른 휴대폰번호 형식이 아닙니다 (예: 01012345678)'),
  password: z.string().regex(/^[0-9]{4}$/, '비밀번호는 숫자 4자리여야 합니다'),
});

type FormData = z.infer<typeof formSchema>;

export const BookingFormStep = ({ concertId, onBack }: BookingFormStepProps) => {
  const router = useRouter();
  const { selectedSeats, clearSeats } = useSeatSelectionStore();
  const { mutate, isPending } = useCreateBooking();

  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: 'onChange',
  });

  const onSubmit = (data: FormData) => {
    const request: CreateBookingRequest = {
      concertId,
      seatIds: selectedSeats.map((s) => s.id),
      ...data,
    };

    mutate(request, {
      onSuccess: (response) => {
        clearSeats();
        router.push(`/bookings/${response.bookingId}/complete`);
      },
      onError: (error: Error & { code?: string }) => {
        if (error.code === 'SEAT_ALREADY_RESERVED') {
          alert('선택하신 좌석 중 일부가 이미 예약되었습니다. 다른 좌석을 선택해주세요.');
          onBack();
        } else if (error.code === 'BOOKING_CLOSED') {
          alert('예약 기간이 종료되었습니다.');
        } else {
          alert('예약 중 오류가 발생했습니다. 다시 시도해주세요.');
        }
      },
    });
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6"
        disabled={isPending}
      >
        <ArrowLeft className="w-5 h-5" />
        <span>좌석 선택으로 돌아가기</span>
      </button>

      <h1 className="text-2xl font-bold mb-6">예약자 정보 입력</h1>

      <div className="bg-gray-50 rounded-lg p-4 mb-6">
        <h3 className="font-semibold mb-2">선택된 좌석 ({selectedSeats.length}석)</h3>
        <div className="flex flex-wrap gap-2">
          {selectedSeats.map((seat) => (
            <span key={seat.id} className="bg-blue-100 text-blue-700 px-3 py-1 rounded text-sm">
              {seat.section}구역 {seat.row}행 {seat.seatColumn}열
            </span>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div>
          <Label htmlFor="name">예약자명</Label>
          <Input
            id="name"
            {...register('name')}
            placeholder="홍길동"
            className="mt-1"
            disabled={isPending}
          />
          {errors.name && <p className="text-sm text-red-600 mt-1">{errors.name.message}</p>}
        </div>

        <div>
          <Label htmlFor="phone">휴대폰번호 (숫자만)</Label>
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
          <Label htmlFor="password">비밀번호 4자리</Label>
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
          <p className="text-xs text-gray-500 mt-1">예약 조회 시 사용됩니다</p>
        </div>

        <Button type="submit" className="w-full" size="lg" disabled={!isValid || isPending}>
          {isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
          {isPending ? '예약 처리 중...' : '예약 완료하기'}
        </Button>
      </form>
    </div>
  );
};
