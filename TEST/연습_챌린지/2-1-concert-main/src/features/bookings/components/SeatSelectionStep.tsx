'use client';

import { useConcertSeats } from '../hooks/useConcertSeats';
import { useSeatSelectionStore } from '../stores/useSeatSelectionStore';
import { SeatMap } from './SeatMap';
import { SeatSelectionSidebar } from './SeatSelectionSidebar';
import { SeatGradeLegend } from './SeatGradeLegend';
import { Button } from '@/components/ui/button';

interface SeatSelectionStepProps {
  concertId: string;
  onProceed: () => void;
}

export const SeatSelectionStep = ({ concertId, onProceed }: SeatSelectionStepProps) => {
  const { data, isLoading, isError, error } = useConcertSeats(concertId);
  const { selectedSeats } = useSeatSelectionStore();

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">로딩 중...</div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <h2 className="text-xl font-bold text-red-600">좌석 정보를 불러올 수 없습니다</h2>
          <p className="mt-2 text-gray-600">{error.message}</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <div className="max-w-7xl mx-auto px-6 md:px-8 lg:px-12 py-8">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-primary mb-2">{data.concertTitle}</h1>
          <p className="text-lg text-gray-600">
            남은 좌석: <span className="font-semibold text-primary">{data.availableSeats}</span>/{data.totalSeats}석
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-[1fr_350px] gap-8">
          <div className="space-y-6">
            <SeatGradeLegend
              grades={data.grades}
              gradeAvailability={data.gradeAvailability}
            />

            <SeatMap sections={data.sections as Array<{ name: 'A' | 'B' | 'C' | 'D'; seats: typeof data.sections[number]['seats'] }>} />
          </div>

          <div>
            <SeatSelectionSidebar
              selectedSeats={selectedSeats}
              availableSeats={data.availableSeats}
              totalSeats={data.totalSeats}
            />

            <Button
              className="w-full mt-6"
              disabled={selectedSeats.length === 0}
              onClick={onProceed}
              size="lg"
            >
              예약하기 ({selectedSeats.length}석 선택)
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
