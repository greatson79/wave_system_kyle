'use client';

import React from 'react';
import Link from 'next/link';
import { useCurrentUser } from '@/features/auth/hooks/useCurrentUser';

export const ChatRoomListHeader: React.FC = () => {
  const { user } = useCurrentUser();

  const displayName = (user?.userMetadata?.nickname as string) ?? user?.email ?? '사용자';

  return (
    <header className="sticky top-0 z-10 bg-background border-b">
      <div className="container max-w-4xl mx-auto flex items-center justify-between h-16 px-4">
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-bold">채팅</h1>
        </div>

        <div className="flex items-center gap-4">
          <span className="text-sm text-muted-foreground">
            {displayName}님
          </span>
          <Link
            href="/my-page"
            className="text-sm font-medium text-primary hover:underline"
          >
            마이페이지
          </Link>
        </div>
      </div>
    </header>
  );
};
