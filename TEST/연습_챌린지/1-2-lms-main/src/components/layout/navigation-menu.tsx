"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Home, BookOpen, LayoutDashboard, FileText, Flag, Database } from 'lucide-react';

type MenuItem = {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
};

const ROLE_MENUS: Record<'learner' | 'instructor' | 'operator', MenuItem[]> = {
  learner: [
    { label: '코스 카탈로그', href: '/courses', icon: BookOpen },
    { label: '내 대시보드', href: '/dashboard', icon: LayoutDashboard },
    { label: '내 코스', href: '/courses/my', icon: Home },
  ],
  instructor: [
    { label: '대시보드', href: '/instructor/dashboard', icon: LayoutDashboard },
    { label: '코스 관리', href: '/instructor/courses', icon: BookOpen },
    { label: '과제 관리', href: '/instructor/assignments', icon: FileText },
  ],
  operator: [
    { label: '신고 관리', href: '/operator/reports', icon: Flag },
    { label: '메타데이터 관리', href: '/operator/metadata', icon: Database },
  ],
};

type NavigationMenuProps = {
  role: 'learner' | 'instructor' | 'operator';
};

export const NavigationMenu = ({ role }: NavigationMenuProps) => {
  const pathname = usePathname();
  const menuItems = ROLE_MENUS[role];

  return (
    <nav className="flex items-center gap-1">
      {menuItems.map((item) => {
        const Icon = item.icon;
        const isActive = pathname === item.href || pathname.startsWith(item.href + '/');

        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors',
              isActive
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
            )}
          >
            <Icon className="h-4 w-4" />
            <span className="hidden sm:inline">{item.label}</span>
          </Link>
        );
      })}
    </nav>
  );
};
