'use client';

import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';

interface ConcertBookingButtonProps {
  concertId: string;
  isBookable: boolean;
  isSoldOut: boolean;
}

export const ConcertBookingButton = ({
  concertId,
  isBookable,
  isSoldOut,
}: ConcertBookingButtonProps) => {
  const router = useRouter();

  const handleBooking = () => {
    router.push(`/concerts/${concertId}/booking`);
  };

  const isDisabled = !isBookable || isSoldOut;

  return (
    <Button
      onClick={handleBooking}
      disabled={isDisabled}
      className="w-full py-4 px-8 text-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-200"
      size="lg"
    >
      {isSoldOut ? '매진' : !isBookable ? '예약 마감' : '예약하기'}
    </Button>
  );
};
