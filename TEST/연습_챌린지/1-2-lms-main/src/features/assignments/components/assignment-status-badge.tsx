'use client';

import { Badge } from '@/components/ui/badge';

interface AssignmentStatusBadgeProps {
  status: 'draft' | 'published' | 'closed';
}

export function AssignmentStatusBadge({ status }: AssignmentStatusBadgeProps) {
  const variants = {
    draft: { variant: 'secondary' as const, label: '임시 저장' },
    published: { variant: 'default' as const, label: '게시됨' },
    closed: { variant: 'outline' as const, label: '마감됨' },
  };

  const { variant, label } = variants[status];

  return <Badge variant={variant}>{label}</Badge>;
}
