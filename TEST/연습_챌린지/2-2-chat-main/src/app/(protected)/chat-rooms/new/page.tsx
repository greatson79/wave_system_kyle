'use client';

import React from 'react';
import { CreateChatRoomForm } from '@/features/chat-rooms/components/create-chat-room-form';

export default function CreateChatRoomPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <CreateChatRoomForm />
    </div>
  );
}
