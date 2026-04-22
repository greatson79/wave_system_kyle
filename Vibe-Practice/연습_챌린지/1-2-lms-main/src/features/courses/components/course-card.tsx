'use client';

import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Users } from 'lucide-react';
import type { CourseListResponse } from '../lib/dto';

type CourseCardProps = {
  course: CourseListResponse['courses'][number];
};

export const CourseCard = ({ course }: CourseCardProps) => {
  const truncateDescription = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text;
    return `${text.slice(0, maxLength)}...`;
  };

  return (
    <Link href={`/courses/${course.id}`}>
      <Card className="h-full transition-shadow hover:shadow-lg cursor-pointer">
        <CardHeader>
          <div className="flex items-start justify-between gap-2 mb-2">
            <CardTitle className="text-lg line-clamp-2">
              {course.title}
            </CardTitle>
          </div>
          <div className="flex gap-2">
            <Badge variant="secondary">{course.category.name}</Badge>
            <Badge variant="outline">{course.difficulty.name}</Badge>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">
            {truncateDescription(course.description, 100)}
          </p>
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span>강사: {course.instructor.name}</span>
            <div className="flex items-center gap-1">
              <Users className="w-4 h-4" />
              <span>{course.enrollmentsCount}</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
};
