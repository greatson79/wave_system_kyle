import { BookingFlowContainer } from '@/features/bookings/components/BookingFlowContainer';

interface PageProps {
  params: Promise<{
    concertId: string;
  }>;
}

export default async function BookingPage({ params }: PageProps) {
  const { concertId } = await params;

  return <BookingFlowContainer concertId={concertId} />;
}

export async function generateMetadata({ params }: PageProps) {
  return {
    title: '콘서트 예약',
    description: '좌석을 선택하고 예약을 완료하세요',
  };
}
