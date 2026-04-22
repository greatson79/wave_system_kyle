'use client';

import { Badge } from '@/components/ui/badge';

type CourseStatus = 'draft' | 'published' | 'archived';

interface CourseStatusBadgeProps {
  status: CourseStatus;
}

export const CourseStatusBadge = ({ status }: CourseStatusBadgeProps) => {
  const config = {
    draft: {
      label: '초안',
      variant: 'secondary' as const,
    },
    published: {
      label: '게시됨',
      variant: 'default' as const,
    },
    archived: {
      label: '보관됨',
      variant: 'outline' as const,
    },
  };

  const { label, variant } = config[status];

  return <Badge variant={variant}>{label}</Badge>;
};
