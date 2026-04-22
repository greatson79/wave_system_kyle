'use client';

import { Armchair } from 'lucide-react';
import type { BookingDetailResponse } from '../lib/dto';

interface BookingSeatsListProps {
  seats: BookingDetailResponse['seats'];
  totalAmount: number;
}

export const BookingSeatsList = ({ seats, totalAmount }: BookingSeatsListProps) => {
  return (
    <div className="bg-white rounded-lg p-6 shadow-sm">
      <div className="flex items-center gap-2 mb-4">
        <Armchair className="w-5 h-5 text-blue-600" />
        <h3 className="text-lg font-bold">예약된 좌석 ({seats.length}석)</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
        {seats.map((seat, index) => (
          <div
            key={index}
            className="flex items-center justify-between bg-blue-50 border border-blue-200 rounded-lg px-4 py-3"
          >
            <div className="flex flex-col">
              <span className="text-sm font-semibold text-gray-900">
                {seat.section}구역 {seat.row}행 {seat.seatColumn}열
              </span>
              <span className="text-xs text-gray-600">{seat.gradeName}</span>
            </div>
            <span className="text-sm font-medium text-blue-700">
              {seat.price.toLocaleString()}원
            </span>
          </div>
        ))}
      </div>

      <div className="border-t pt-4">
        <div className="flex items-center justify-between">
          <span className="text-lg font-bold">총 결제 금액</span>
          <span className="text-2xl font-bold text-blue-600">
            {totalAmount.toLocaleString()}원
          </span>
        </div>
      </div>
    </div>
  );
};
