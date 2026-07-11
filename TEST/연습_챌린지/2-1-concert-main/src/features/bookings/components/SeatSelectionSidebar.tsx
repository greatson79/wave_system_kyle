'use client';

import { X } from 'lucide-react';
import { useSeatSelectionStore } from '../stores/useSeatSelectionStore';
import type { Seat } from '../backend/schema';

interface SeatSelectionSidebarProps {
  selectedSeats: Seat[];
  availableSeats: number;
  totalSeats: number;
}

export const SeatSelectionSidebar = ({
  selectedSeats,
  availableSeats,
  totalSeats,
}: SeatSelectionSidebarProps) => {
  const { removeSeat } = useSeatSelectionStore();

  const totalAmount = selectedSeats.reduce((sum, seat) => sum + seat.price, 0);

  return (
    <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200 sticky top-20">
      <h3 className="font-bold text-xl mb-3 text-gray-800">선택된 좌석</h3>
      <p className="text-sm text-gray-600 mb-6">
        남은 좌석: <span className="font-semibold text-primary">{availableSeats}</span>/{totalSeats}석
      </p>

      {selectedSeats.length === 0 && (
        <div className="text-center py-12 text-gray-400 bg-gray-50 rounded-lg">
          <p className="font-medium">좌석을 선택해주세요</p>
          <p className="text-xs mt-2">최대 4석까지 선택 가능</p>
        </div>
      )}

      {selectedSeats.length > 0 && (
        <>
          <ul className="space-y-3 mb-6">
            {selectedSeats.map((seat) => (
              <li
                key={seat.id}
                className="flex items-center justify-between bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg px-4 py-3 border border-purple-100 transition-all hover:shadow-md"
              >
                <div className="flex flex-col">
                  <span className="text-sm font-semibold text-gray-800">
                    {seat.section}구역 {seat.row}행 {seat.seatColumn}열
                  </span>
                  <span className="text-xs text-gray-600 mt-1">
                    {seat.gradeName} - {seat.price.toLocaleString()}원
                  </span>
                </div>
                <button
                  onClick={() => removeSeat(seat.id)}
                  className="text-gray-400 hover:text-red-500 transition-colors duration-200 hover:scale-110"
                  aria-label={`${seat.section}구역 ${seat.row}행 ${seat.seatColumn}열 선택 해제`}
                >
                  <X className="w-5 h-5" />
                </button>
              </li>
            ))}
          </ul>

          <div className="border-t-2 border-gray-200 pt-5">
            <div className="flex items-center justify-between">
              <span className="font-bold text-lg text-gray-800">총 금액</span>
              <span className="font-bold text-2xl bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                {totalAmount.toLocaleString()}원
              </span>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
