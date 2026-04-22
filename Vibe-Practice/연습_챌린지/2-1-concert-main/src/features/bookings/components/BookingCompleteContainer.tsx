'use client';

import { useBookingDetail } from '../hooks/useBookingDetail';
import { BookingSuccessMessage } from './BookingSuccessMessage';
import { BookingInfoCard } from './BookingInfoCard';
import { BookingSeatsList } from './BookingSeatsList';
import { BookingActionsSection } from './BookingActionsSection';
import { Loader2, AlertCircle } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

interface BookingCompleteContainerProps {
  bookingId: string;
}

export const BookingCompleteContainer = ({ bookingId }: BookingCompleteContainerProps) => {
  const { data, isLoading, isError, error } = useBookingDetail(bookingId);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600">예약 정보를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>예약 정보를 불러올 수 없습니다</AlertTitle>
            <AlertDescription>{error.message}</AlertDescription>
          </Alert>
          <div className="mt-6 flex gap-3">
            <Button asChild variant="outline" className="flex-1">
              <Link href="/">홈으로 가기</Link>
            </Button>
            <Button asChild className="flex-1">
              <Link href="/bookings/lookup">예약 조회</Link>
            </Button>
          </div>
        </div>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  // 취소된 예약인 경우
  if (data.status === 'cancelled') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full">
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>예약 취소됨</AlertTitle>
            <AlertDescription>
              이 예약은 이미 취소되었습니다.
              <br />
              새로운 예약을 진행하시려면 홈으로 이동해주세요.
            </AlertDescription>
          </Alert>
          <div className="mt-6 flex gap-3">
            <Button asChild variant="outline" className="flex-1">
              <Link href="/">홈으로 가기</Link>
            </Button>
            <Button asChild className="flex-1">
              <Link href="/bookings/lookup">예약 조회</Link>
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // 확정된 예약인 경우
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8 max-w-3xl">
        <BookingSuccessMessage />

        <div className="mt-8 space-y-6">
          <BookingInfoCard booking={data} />

          <BookingSeatsList seats={data.seats} totalAmount={data.totalAmount} />

          <Alert className="bg-blue-50 border-blue-200">
            <AlertCircle className="h-4 w-4 text-blue-600" />
            <AlertTitle className="text-blue-900">예약 조회 안내</AlertTitle>
            <AlertDescription className="text-blue-800">
              예약 내역은 휴대폰번호와 비밀번호 4자리로 조회하실 수 있습니다.
              <br />
              예약 번호를 별도로 기록하실 필요는 없습니다.
            </AlertDescription>
          </Alert>

          <BookingActionsSection bookingId={bookingId} />
        </div>
      </div>
    </div>
  );
};
