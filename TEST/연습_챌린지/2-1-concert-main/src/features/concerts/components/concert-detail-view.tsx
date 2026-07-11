'use client';

import { useRouter } from 'next/navigation';
import { useConcertDetailQuery } from '../hooks/useConcertDetailQuery';
import { ConcertHeader } from './concert-header';
import { ConcertThumbnail } from './concert-thumbnail';
import { ConcertInfo } from './concert-info';
import { ConcertDescription } from './concert-description';
import { ConcertBookingInfo } from './concert-booking-info';
import { ConcertGradeAvailability } from './concert-grade-availability';
import { ConcertBookingButton } from './concert-booking-button';
import { ConcertDetailSkeleton } from './concert-detail-skeleton';
import { Button } from '@/components/ui/button';

interface ConcertDetailViewProps {
  concertId: string;
}

export const ConcertDetailView = ({ concertId }: ConcertDetailViewProps) => {
  const router = useRouter();
  const { data, isLoading, isError, error } = useConcertDetailQuery(concertId);

  if (isLoading) {
    return <ConcertDetailSkeleton />;
  }

  if (isError) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center space-y-4">
          <h1 className="text-2xl font-bold text-destructive">
            콘서트를 찾을 수 없습니다
          </h1>
          <p className="text-muted-foreground">
            {error?.message || '알 수 없는 오류가 발생했습니다.'}
          </p>
          <Button onClick={() => router.back()}>
            돌아가기
          </Button>
        </div>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <div className="min-h-screen">
      {/* Header */}
      <div className="bg-white border-b border-neutral-200 sticky top-0 z-10 backdrop-blur-md bg-white/80">
        <div className="max-w-7xl mx-auto px-6 md:px-8 lg:px-12 py-4">
          <ConcertHeader />
        </div>
      </div>

      {/* Hero Image */}
      <div className="w-full">
        <ConcertThumbnail src={data.thumbnailUrl} alt={data.title} />
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 md:px-8 lg:px-12 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Main Info */}
          <div className="lg:col-span-2 space-y-8">
            <ConcertInfo concert={data} />
            <ConcertDescription description={data.description} />
            <ConcertGradeAvailability gradeAvailability={data.gradeAvailability} />
          </div>

          {/* Right Column - Booking Card */}
          <div className="lg:col-span-1">
            <div className="sticky top-24 space-y-4">
              <div className="border-2 border-neutral-200 rounded-xl p-6 shadow-md bg-white">
                <ConcertBookingInfo
                  availableSeats={data.availableSeats}
                  totalSeats={data.totalSeats}
                  isSoldOut={data.isSoldOut}
                  isBookable={data.isBookable}
                  bookingDeadline={data.bookingDeadline}
                />
              </div>
              <ConcertBookingButton
                concertId={data.id}
                isBookable={data.isBookable}
                isSoldOut={data.isSoldOut}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
