'use client';

import { format } from 'date-fns';
import { ko } from 'date-fns/locale';
import { Calendar, MapPin, User, Phone, Hash, Clock } from 'lucide-react';
import type { BookingDetailResponse } from '../lib/dto';
import Image from 'next/image';

interface BookingInfoCardProps {
  booking: BookingDetailResponse;
}

export const BookingInfoCard = ({ booking }: BookingInfoCardProps) => {
  const eventDate = new Date(booking.eventDate);
  const createdAt = new Date(booking.createdAt);

  return (
    <div className="bg-white rounded-lg shadow-sm overflow-hidden">
      {/* 콘서트 썸네일 */}
      {booking.thumbnailUrl && (
        <div className="relative w-full h-48">
          <Image
            src={booking.thumbnailUrl}
            alt={booking.concertTitle}
            fill
            className="object-cover"
          />
        </div>
      )}

      <div className="p-6 space-y-4">
        {/* 콘서트 정보 */}
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-1">{booking.concertTitle}</h2>
          {booking.concertDescription && (
            <p className="text-sm text-gray-600">{booking.concertDescription}</p>
          )}
        </div>

        {/* 예약 정보 그리드 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t">
          <div className="flex items-start gap-3">
            <Calendar className="w-5 h-5 text-gray-400 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-gray-500">공연 일시</p>
              <p className="text-base text-gray-900">
                {format(eventDate, 'yyyy년 MM월 dd일 (EEE) HH:mm', { locale: ko })}
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <MapPin className="w-5 h-5 text-gray-400 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-gray-500">장소</p>
              <p className="text-base text-gray-900">{booking.location}</p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <User className="w-5 h-5 text-gray-400 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-gray-500">예약자명</p>
              <p className="text-base text-gray-900">{booking.bookingName}</p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <Phone className="w-5 h-5 text-gray-400 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-gray-500">휴대폰번호</p>
              <p className="text-base text-gray-900">{booking.bookingPhone}</p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <Hash className="w-5 h-5 text-gray-400 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-gray-500">예약 번호</p>
              <p className="text-base text-gray-900 font-mono break-all">
                {booking.bookingId}
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <Clock className="w-5 h-5 text-gray-400 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-gray-500">예약 일시</p>
              <p className="text-base text-gray-900">
                {format(createdAt, 'yyyy년 MM월 dd일 HH:mm', { locale: ko })}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
