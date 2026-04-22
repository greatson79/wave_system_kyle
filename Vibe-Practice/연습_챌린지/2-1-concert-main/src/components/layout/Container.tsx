'use client';

import { ReactNode, ElementType } from 'react';
import { cn } from '@/lib/utils';

interface ContainerProps {
  children: ReactNode;
  className?: string;
  as?: ElementType;
}

export default function Container({
  children,
  className,
  as: Component = 'div',
}: ContainerProps) {
  return (
    <Component
      className={cn('mx-auto max-w-7xl px-6 md:px-8 lg:px-12', className)}
    >
      {children}
    </Component>
  );
}
