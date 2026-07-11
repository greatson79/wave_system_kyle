'use client';

import React from 'react';

export type ErrorMessageProps = {
  message: string;
  onRetry?: () => void;
};

export const ErrorMessage: React.FC<ErrorMessageProps> = ({
  message,
  onRetry,
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-8 gap-4">
      <p className="text-destructive text-sm">{message}</p>
      {onRetry && (
        <button onClick={onRetry} className="text-primary underline text-sm">
          다시 시도
        </button>
      )}
    </div>
  );
};
