'use client';

import React from 'react';
import { Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useLogout } from '../hooks/use-logout';

export const LogoutButton: React.FC = () => {
  const { mutate, isPending } = useLogout();

  return (
    <div className="px-6 pb-6 mt-auto">
      <Button
        variant="outline"
        className="w-full"
        onClick={() => mutate()}
        disabled={isPending}
      >
        {isPending ? (
          <>
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            로그아웃 중...
          </>
        ) : (
          '로그아웃'
        )}
      </Button>
    </div>
  );
};
