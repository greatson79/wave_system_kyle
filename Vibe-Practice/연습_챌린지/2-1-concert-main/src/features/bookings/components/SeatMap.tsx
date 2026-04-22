'use client';

import { SeatCard } from './SeatCard';
import type { Seat } from '../backend/schema';

interface Section {
  name: 'A' | 'B' | 'C' | 'D';
  seats: Seat[];
}

interface SeatMapProps {
  sections: Section[];
}

export const SeatMap = ({ sections }: SeatMapProps) => {
  return (
    <div className="bg-white rounded-xl p-8 shadow-lg border border-gray-200">
      <h2 className="text-2xl font-bold text-primary mb-6">좌석 배치도</h2>

      {/* 가로 스크롤 컨테이너 */}
      <div className="overflow-x-auto pb-4">
        <div className="flex gap-8 min-w-max">
          {sections.map((section) => (
            <div
              key={section.name}
              className="border-2 border-gray-200 rounded-xl p-6 transition-all hover:shadow-md flex-shrink-0"
              style={{ minWidth: '280px' }}
            >
              <h3 className="text-center font-bold text-xl mb-6 text-gray-800">{section.name}구역</h3>
              <div className="grid grid-cols-4 gap-3">
                {section.seats.map((seat) => (
                  <SeatCard key={seat.id} seat={seat} />
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-8 flex items-center justify-center gap-8 text-sm flex-wrap">
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 bg-white border-2 border-gray-300 rounded"></div>
          <span className="font-medium text-gray-700">예약 가능</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 border-2 rounded" style={{ backgroundColor: '#8B5CF6', borderColor: '#8B5CF6' }}></div>
          <span className="font-medium text-gray-700">선택됨 (등급별 색상)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 bg-gray-300 border-2 border-gray-400 rounded"></div>
          <span className="font-medium text-gray-700">예약됨</span>
        </div>
      </div>
    </div>
  );
};
