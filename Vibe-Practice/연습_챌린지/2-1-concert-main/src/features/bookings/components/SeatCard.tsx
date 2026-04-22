'use client';

import { useSeatSelectionStore } from '../stores/useSeatSelectionStore';
import type { Seat } from '../backend/schema';
import { cn } from '@/lib/utils';

interface SeatCardProps {
  seat: Seat;
}

export const SeatCard = ({ seat }: SeatCardProps) => {
  const { addSeat, removeSeat, isSeatSelected, canSelectMore } = useSeatSelectionStore();

  const isSelected = isSeatSelected(seat.id);
  const isReserved = seat.isReserved;
  const isClickable = !isReserved;

  const handleClick = () => {
    if (isReserved) {
      return;
    }

    if (isSelected) {
      removeSeat(seat.id);
    } else {
      if (canSelectMore()) {
        addSeat(seat);
      } else {
        alert('최대 4석까지만 선택할 수 있습니다.');
      }
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={!isClickable}
      className={cn(
        'aspect-square rounded-lg text-xs font-semibold transition-all duration-200',
        'border-2',
        isReserved && 'bg-gray-300 text-gray-500 cursor-not-allowed border-gray-400',
        !isReserved &&
          !isSelected &&
          'bg-white cursor-pointer hover:scale-105 hover:shadow-lg',
        isSelected && 'text-white cursor-pointer shadow-lg hover:shadow-xl hover:scale-105',
      )}
      style={{
        // 예약된 좌석: 스타일 없음 (className으로 회색 처리)
        // 선택되지 않은 좌석: 등급 색상 테두리
        // 선택된 좌석: 등급 색상 배경 + 테두리
        ...(isReserved
          ? {}
          : isSelected
            ? {
                backgroundColor: seat.colorCode,
                borderColor: seat.colorCode,
                borderWidth: '3px',
              }
            : {
                borderColor: seat.colorCode,
                borderWidth: '3px',
              }),
      }}
      aria-label={`${seat.section}구역 ${seat.row}행 ${seat.seatColumn}열 ${seat.gradeName} ${
        isReserved ? '예약됨' : isSelected ? '선택됨' : '예약 가능'
      }`}
    >
      {seat.row}-{seat.seatColumn}
    </button>
  );
};
