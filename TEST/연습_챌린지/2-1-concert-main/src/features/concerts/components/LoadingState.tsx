'use client';

import { Card, CardContent, CardHeader } from '@/components/ui/card';

export const LoadingState = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {[1, 2, 3, 4, 5, 6].map((i) => (
        <Card key={i} className="animate-pulse">
          <div className="aspect-video w-full bg-muted rounded-t-lg" />
          <CardHeader>
            <div className="h-6 bg-muted rounded w-3/4" />
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="h-4 bg-muted rounded w-full" />
            <div className="h-4 bg-muted rounded w-2/3" />
            <div className="h-4 bg-muted rounded w-1/2" />
          </CardContent>
        </Card>
      ))}
    </div>
  );
};
