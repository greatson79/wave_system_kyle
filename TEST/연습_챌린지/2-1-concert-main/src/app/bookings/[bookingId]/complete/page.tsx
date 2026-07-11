import { BookingCompleteContainer } from '@/features/bookings/components/BookingCompleteContainer';

interface PageProps {
  params: Promise<{
    bookingId: string;
  }>;
}

export default async function BookingCompletePage({ params }: PageProps) {
  const { bookingId } = await params;

  return <BookingCompleteContainer bookingId={bookingId} />;
}

// 메타데이터 (SEO)
export async function generateMetadata({ params }: PageProps) {
  return {
    title: '예약 완료',
    description: '콘서트 예약이 완료되었습니다',
  };
}
