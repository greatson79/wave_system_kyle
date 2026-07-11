import { BookingLookupContainer } from '@/features/bookings/components/BookingLookupContainer';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: '예약 조회',
  description: '휴대폰번호와 비밀번호로 예약을 조회하고 관리하세요',
};

export default function BookingLookupPage() {
  return (
    <div className="container mx-auto px-6 md:px-8 lg:px-12 py-12 max-w-7xl">
      <header className="mb-8 text-center">
        <h1 className="text-3xl font-bold">예약 조회</h1>
        <p className="text-gray-600 mt-2">휴대폰번호와 비밀번호를 입력하여 예약을 조회하세요.</p>
      </header>
      <BookingLookupContainer />
    </div>
  );
}
