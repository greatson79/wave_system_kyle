"use client";

import { useCurrentUser } from '@/features/auth/hooks/useCurrentUser';
import { useProfile } from '@/features/profile/hooks/useProfile';
import { useLogout } from '@/features/auth/hooks/useLogout';
import { Button } from '@/components/ui/button';
import { NavigationMenu } from './navigation-menu';
import Link from 'next/link';

const ROLE_LABELS = {
  learner: '학습자',
  instructor: '강사',
  operator: '운영자',
} as const;

export const Header = () => {
  const { isAuthenticated, user } = useCurrentUser();
  const { data: profile } = useProfile();
  const { mutate: logout, isPending } = useLogout();

  // 로그인하지 않았으면 헤더를 표시하지 않습니다
  if (!isAuthenticated || !user) {
    return null;
  }

  const handleLogout = () => {
    logout();
  };

  return (
    <header className="border-b bg-white sticky top-0 z-50">
      <div className="container mx-auto flex items-center justify-between px-4 py-3">
        <div className="flex items-center gap-6">
          <Link href="/" className="flex items-center gap-2">
            <h1 className="text-xl font-bold">LMS</h1>
          </Link>

          {profile && (
            <NavigationMenu role={profile.role as 'learner' | 'instructor' | 'operator'} />
          )}
        </div>

        <div className="flex items-center gap-4">
          {profile && (
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">
                {ROLE_LABELS[profile.role as keyof typeof ROLE_LABELS]}
              </span>
              <span className="font-medium">{profile.name}</span>
              <span className="text-sm text-muted-foreground">({user.email})</span>
            </div>
          )}

          <Button
            variant="outline"
            size="sm"
            onClick={handleLogout}
            disabled={isPending}
          >
            {isPending ? '로그아웃 중...' : '로그아웃'}
          </Button>
        </div>
      </div>
    </header>
  );
};
