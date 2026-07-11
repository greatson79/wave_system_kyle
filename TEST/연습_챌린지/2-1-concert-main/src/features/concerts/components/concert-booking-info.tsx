'use client';

import { Users, AlertCircle } from 'lucide-react';
import { formatBookingDeadline } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface ConcertBookingInfoProps {
  availableSeats: number;
  totalSeats: number;
  isSoldOut: boolean;
  isBookable: boolean;
  bookingDeadline: string;
}

export const ConcertBookingInfo = ({
  availableSeats,
  totalSeats,
  isSoldOut,
  isBookable,
  bookingDeadline,
}: ConcertBookingInfoProps) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">예약 정보</h3>
        {isSoldOut && (
          <Badge variant="destructive">매진</Badge>
        )}
        {!isSoldOut && !isBookable && (
          <Badge variant="secondary">예약 마감</Badge>
        )}
      </div>

      <div className="flex items-center gap-2 text-muted-foreground">
        <Users className="h-4 w-4" />
        <span>
          남은 좌석: <strong className="text-foreground">{availableSeats}</strong> / {totalSeats}석
        </span>
      </div>

      {!isBookable && !isSoldOut && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            예약이 마감되었습니다. (마감일: {formatBookingDeadline(bookingDeadline)})
          </AlertDescription>
        </Alert>
      )}

      {isSoldOut && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            모든 좌석이 매진되었습니다.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
};
