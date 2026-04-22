'use client';

import React from 'react';
import { Loader2 } from 'lucide-react';

export type LoadingSpinnerProps = {
  size?: 'sm' | 'md' | 'lg';
};

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
}) => {
  const sizeClass = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  }[size];

  return (
    <div className="flex items-center justify-center py-8">
      <Loader2 className={`${sizeClass} animate-spin text-primary`} />
    </div>
  );
};
