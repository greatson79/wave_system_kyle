'use client';

import { useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';

export const ConcertHeader = () => {
  const router = useRouter();

  return (
    <div className="flex items-center gap-4">
      <Button
        variant="ghost"
        size="icon"
        onClick={() => router.back()}
        aria-label="뒤로가기"
        className="text-primary hover:text-primary-dark hover:bg-primary/10 transition-colors duration-200"
      >
        <ArrowLeft className="h-5 w-5" />
      </Button>
      <h1 className="text-2xl font-bold text-neutral-900">콘서트 상세</h1>
    </div>
  );
};
