'use client';

import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { Home, Search } from 'lucide-react';

interface BookingActionsSectionProps {
  bookingId: string;
}

export const BookingActionsSection = ({ bookingId }: BookingActionsSectionProps) => {
  return (
    <div className="bg-white rounded-lg p-6 shadow-sm">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Button asChild variant="outline" size="lg" className="w-full">
          <Link href="/">
            <Home className="w-4 h-4 mr-2" />
            홈으로 돌아가기
          </Link>
        </Button>

        <Button asChild size="lg" className="w-full">
          <Link href="/bookings/lookup">
            <Search className="w-4 h-4 mr-2" />
            예약 조회하기
          </Link>
        </Button>
      </div>
    </div>
  );
};
