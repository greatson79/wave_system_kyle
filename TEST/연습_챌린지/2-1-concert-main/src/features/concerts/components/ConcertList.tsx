'use client';

import { useRouter } from 'next/navigation';
import { useConcertList } from '@/features/concerts/hooks/useConcertList';
import { ConcertCard } from './ConcertCard';
import { LoadingState } from './LoadingState';
import { EmptyState } from './EmptyState';

export const ConcertList = () => {
  const router = useRouter();
  const { data: concerts, isLoading, isError, error } = useConcertList();

  const handleConcertClick = (concertId: string) => {
    router.push(`/concerts/${concertId}`);
  };

  if (isLoading) {
    return <LoadingState />;
  }

  if (isError) {
    return (
      <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
        <h3 className="text-xl font-semibold mb-2">
          콘서트 목록을 불러오는 중 오류가 발생했습니다
        </h3>
        <p className="text-muted-foreground mb-4">
          {error instanceof Error ? error.message : '알 수 없는 오류'}
        </p>
        <button
          onClick={() => window.location.reload()}
          className="px-4 py-2 bg-primary text-primary-foreground rounded-md"
        >
          새로고침
        </button>
      </div>
    );
  }

  if (!concerts || concerts.length === 0) {
    return <EmptyState />;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
      {concerts.map((concert) => (
        <ConcertCard
          key={concert.id}
          concert={concert}
          onClick={handleConcertClick}
        />
      ))}
    </div>
  );
};
