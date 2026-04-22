'use client';

import Container from '@/components/layout/Container';
import { ConcertList } from '@/features/concerts/components/ConcertList';

export default function HomePage() {
  return (
    <Container className="py-12">
      <header className="mb-12 text-center">
        <h1 className="text-4xl font-bold mb-4">예약 가능한 콘서트</h1>
        <p className="text-lg text-muted-foreground">
          원하시는 콘서트를 선택하여 예약을 진행하세요
        </p>
      </header>
      <ConcertList />
    </Container>
  );
}
