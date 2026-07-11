'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';

export const MyPageHeader: React.FC = () => {
  const router = useRouter();

  return (
    <header className="h-14 bg-background border-b flex items-center px-4">
      <Button
        variant="ghost"
        size="icon"
        onClick={() => router.back()}
        aria-label="뒤로 가기"
      >
        <ArrowLeft className="w-5 h-5" />
      </Button>
      <h1 className="ml-2 text-lg font-semibold">마이페이지</h1>
    </header>
  );
};
