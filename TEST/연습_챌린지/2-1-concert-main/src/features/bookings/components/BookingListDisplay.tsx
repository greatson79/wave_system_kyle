'use client';

import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { BookingCard } from './BookingCard';
import type { BookingSummary } from '../lib/dto';

interface BookingListDisplayProps {
  bookings: BookingSummary[];
  phone: string;
  password: string;
  onBack: () => void;
}

export const BookingListDisplay = ({ bookings, phone, password, onBack }: BookingListDisplayProps) => {
  if (bookings.length === 0) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">예약 내역이 없습니다</h2>
        <p className="text-gray-600 mb-6">입력하신 정보로 예약된 내역을 찾을 수 없습니다.</p>
        <Button onClick={onBack} variant="outline">
          다시 조회하기
        </Button>
      </div>
    );
  }

  return (
    <div>
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6"
      >
        <ArrowLeft className="w-5 h-5" />
        <span>다시 조회하기</span>
      </button>

      <div className="mb-6">
        <h2 className="text-2xl font-bold">예약 내역</h2>
        <p className="text-gray-600 mt-1">총 {bookings.length}건의 예약</p>
      </div>

      <div className="space-y-4">
        {bookings.map((booking) => (
          <BookingCard key={booking.bookingId} booking={booking} phone={phone} password={password} />
        ))}
      </div>
    </div>
  );
};
