'use client';

import React from 'react';
import Link from 'next/link';
import { Plus } from 'lucide-react';
import { ChatRoomListHeader } from '@/features/chat-rooms/components/chat-room-list-header';
import { ChatRoomList } from '@/features/chat-rooms/components/chat-room-list';
import { Button } from '@/components/ui/button';

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      <ChatRoomListHeader />

      <main className="flex-1 container max-w-4xl mx-auto py-6 px-4">
        <ChatRoomList />
      </main>

      <Link href="/chat-rooms/new" className="fixed bottom-6 right-6 z-50">
        <Button size="lg" className="rounded-full shadow-lg h-14 w-14 p-0">
          <Plus className="w-6 h-6" />
          <span className="sr-only">채팅방 추가</span>
        </Button>
      </Link>
    </div>
  );
}
