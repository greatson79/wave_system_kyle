import { ConcertDetailView } from '@/features/concerts/components/concert-detail-view';

interface PageProps {
  params: Promise<{
    concertId: string;
  }>;
}

export default async function ConcertDetailPage({ params }: PageProps) {
  const { concertId } = await params;

  return (
    <div className="min-h-screen bg-neutral-50">
      <ConcertDetailView concertId={concertId} />
    </div>
  );
}

export async function generateMetadata({ params }: PageProps) {
  const { concertId } = await params;

  return {
    title: '콘서트 상세',
    description: '콘서트 상세 정보 및 예약',
  };
}
