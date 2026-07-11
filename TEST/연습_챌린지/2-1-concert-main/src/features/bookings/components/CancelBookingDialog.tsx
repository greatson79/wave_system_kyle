'use client';

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { Loader2 } from 'lucide-react';
import { useCancelBooking } from '../hooks/useCancelBooking';

interface Seat {
  section: 'A' | 'B' | 'C' | 'D';
  row: number;
  seatColumn: number;
}

interface CancelBookingDialogProps {
  isOpen: boolean;
  onClose: () => void;
  bookingId: string;
  concertTitle: string;
  seats: Seat[];
  phone: string;
  password: string;
  onSuccess: () => void;
}

export const CancelBookingDialog = ({
  isOpen,
  onClose,
  bookingId,
  concertTitle,
  seats,
  phone,
  password,
  onSuccess,
}: CancelBookingDialogProps) => {
  const { mutate, isPending } = useCancelBooking();

  const handleConfirm = () => {
    mutate(
      { bookingId, phone, password },
      {
        onSuccess: () => {
          onSuccess();
          alert('예약이 취소되었습니다.');
        },
        onError: (error: any) => {
          if (error.code === 'AUTHENTICATION_FAILED') {
            alert('인증 오류가 발생했습니다. 다시 로그인해주세요.');
          } else if (error.code === 'ALREADY_CANCELLED') {
            alert('이미 취소된 예약입니다.');
            onSuccess();
          } else if (error.code === 'CANCELLATION_NOT_ALLOWED') {
            alert('공연 시작 후에는 취소할 수 없습니다.');
          } else {
            alert('예약 취소 중 오류가 발생했습니다. 다시 시도해주세요.');
          }
        },
      },
    );
  };

  return (
    <AlertDialog open={isOpen} onOpenChange={onClose}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>예약을 취소하시겠습니까?</AlertDialogTitle>
          <AlertDialogDescription>
            <div className="space-y-2">
              <p className="text-red-600 font-medium">이 작업은 되돌릴 수 없습니다.</p>

              <div className="mt-4 bg-gray-50 rounded p-3 text-sm text-gray-800">
                <p className="font-semibold mb-1">{concertTitle}</p>
                <p className="text-gray-600">
                  좌석: {seats.map((s) => `${s.section}${s.row}-${s.seatColumn}`).join(', ')}
                </p>
              </div>
            </div>
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={isPending}>취소</AlertDialogCancel>
          <AlertDialogAction
            onClick={(e) => {
              e.preventDefault();
              handleConfirm();
            }}
            disabled={isPending}
            className="bg-red-600 hover:bg-red-700"
          >
            {isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
            {isPending ? '처리 중...' : '예약 취소'}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
};
