'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { MyCoursesList } from '@/features/courses/components/my-courses-list';

export default function InstructorCoursesPage() {
  return (
    <div className="container mx-auto py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">내 코스</h1>
          <p className="text-muted-foreground mt-2">
            개설한 코스를 관리하고 상태를 변경할 수 있습니다.
          </p>
        </div>
        <Button asChild>
          <Link href="/instructor/courses/new">코스 생성</Link>
        </Button>
      </div>
      <MyCoursesList />
    </div>
  );
}
