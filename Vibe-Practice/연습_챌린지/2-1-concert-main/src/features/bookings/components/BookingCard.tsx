'use client';

import { useState } from 'react';
import { format, isPast } from 'date-fns';
import { ko } from 'date-fns/locale';
import { MapPin, Calendar, User } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { CancelBookingDialog } from './CancelBookingDialog';
import type { BookingSummary } from '../lib/dto';
import { cn } from '@/lib/utils';

interface BookingCardProps {
  booking: BookingSummary;
  phone: string;
  password: string;
}

export const BookingCard = ({ booking, phone, password }: BookingCardProps) => {
  const [isCancelDialogOpen, setIsCancelDialogOpen] = useState(false);
  const [localStatus, setLocalStatus] = useState(booking.status);

  const isPastConcert = isPast(new Date(booking.eventDate));
  const isCancelled = localStatus === 'cancelled';
  const canCancel = !isCancelled && !isPastConcert;

  const handleCancelSuccess = () => {
    setLocalStatus('cancelled');
    setIsCancelDialogOpen(false);
  };

  return (
    <div
      className={cn(
        'bg-white rounded-xl p-6 shadow-sm border-2 transition-all duration-300',
        isCancelled && 'bg-gray-50 border-[hsl(270,12%,88%)] opacity-75',
        !isCancelled && 'border-[hsl(270,12%,88%)] hover:shadow-lg hover:-translate-y-1',
      )}
    >
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-xl font-bold text-gray-900">{booking.concertTitle}</h3>
          <div className="flex items-center gap-4 text-sm text-gray-600 mt-2">
            <span
              className={cn(
                'px-2 py-1 rounded text-xs font-medium',
                isCancelled && 'bg-gray-200 text-gray-700',
                !isCancelled && 'bg-green-100 text-green-700',
              )}
            >
              {isCancelled ? '취소됨' : '확정'}
            </span>
            {isPastConcert && !isCancelled && (
              <span className="px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-700">
                완료됨
              </span>
            )}
          </div>
        </div>

        {canCancel && (
          <Button onClick={() => setIsCancelDialogOpen(true)} variant="destructive" size="sm">
            예약취소
          </Button>
        )}
      </div>

      <div className="space-y-2 text-sm text-gray-700">
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 text-[hsl(270,60%,50%)]" />
          <span>{format(new Date(booking.eventDate), 'yyyy년 M월 d일 (E) HH:mm', { locale: ko })}</span>
        </div>

        <div className="flex items-center gap-2">
          <MapPin className="w-4 h-4 text-[hsl(270,60%,50%)]" />
          <span>{booking.location}</span>
        </div>

        <div className="flex items-center gap-2">
          <User className="w-4 h-4 text-[hsl(270,60%,50%)]" />
          <span>{booking.bookingName}</span>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-[hsl(270,12%,88%)]">
        <h4 className="text-sm font-semibold text-gray-700 mb-2">
          예약된 좌석 ({booking.seats.length}석)
        </h4>
        <div className="space-y-2">
          {booking.seats.map((seat, index) => (
            <div
              key={index}
              className="flex items-center justify-between bg-[hsl(270,20%,98%)] rounded-lg px-3 py-2"
            >
              <span className="text-sm">
                {seat.section}구역 {seat.row}행 {seat.seatColumn}열
                <span className="text-xs text-gray-600 ml-2">({seat.gradeName})</span>
              </span>
              <span className="text-sm font-medium">
                {seat.price.toLocaleString()}원
              </span>
            </div>
          ))}
        </div>

        <div className="mt-3 pt-3 border-t border-[hsl(270,12%,88%)] flex items-center justify-between">
          <span className="font-semibold">총 금액</span>
          <span className="text-lg font-bold text-[hsl(270,60%,50%)]">
            {booking.totalAmount.toLocaleString()}원
          </span>
        </div>
      </div>

      <div className="mt-4 text-xs text-gray-500">
        예약일시: {format(new Date(booking.createdAt), 'yyyy-MM-dd HH:mm')}
      </div>

      {canCancel && (
        <CancelBookingDialog
          isOpen={isCancelDialogOpen}
          onClose={() => setIsCancelDialogOpen(false)}
          bookingId={booking.bookingId}
          concertTitle={booking.concertTitle}
          seats={booking.seats as Array<{ section: 'A' | 'B' | 'C' | 'D'; row: number; seatColumn: number }>}
          phone={phone}
          password={password}
          onSuccess={handleCancelSuccess}
        />
      )}
    </div>
  );
};
