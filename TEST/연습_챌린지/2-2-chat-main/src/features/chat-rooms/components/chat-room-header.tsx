'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { ChevronLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';

type ChatRoomHeaderProps = {
  roomName: string;
};

export const ChatRoomHeader: React.FC<ChatRoomHeaderProps> = ({
  roomName,
}) => {
  const router = useRouter();

  return (
    <header className="flex items-center gap-3 px-4 py-3 border-b bg-white">
      <Button
        variant="ghost"
        size="icon"
        onClick={() => router.back()}
        className="h-8 w-8"
      >
        <ChevronLeft className="h-5 w-5" />
      </Button>
      <h1 className="text-lg font-semibold">{roomName}</h1>
    </header>
  );
};
