'use client';

import { useState } from 'react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { SubmissionRow } from './submission-row';
import type { SubmissionItem } from '../lib/dto';

interface SubmissionsTableProps {
  submissions: SubmissionItem[];
  onFilterChange?: (filter: 'all' | 'ungraded' | 'late' | 'resubmission_required') => void;
}

export function SubmissionsTable({ submissions, onFilterChange }: SubmissionsTableProps) {
  const [filter, setFilter] = useState<'all' | 'ungraded' | 'late' | 'resubmission_required'>('all');

  const handleFilterChange = (value: string) => {
    const newFilter = value as 'all' | 'ungraded' | 'late' | 'resubmission_required';
    setFilter(newFilter);
    onFilterChange?.(newFilter);
  };

  if (submissions.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">아직 제출된 과제가 없습니다.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">총 {submissions.length}개의 제출물</p>
        <Select value={filter} onValueChange={handleFilterChange}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="필터" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">전체</SelectItem>
            <SelectItem value="ungraded">미채점</SelectItem>
            <SelectItem value="late">지각</SelectItem>
            <SelectItem value="resubmission_required">재제출 요청</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>학습자</TableHead>
              <TableHead>제출 시간</TableHead>
              <TableHead>상태</TableHead>
              <TableHead>점수</TableHead>
              <TableHead>제출 내용</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {submissions.map((submission) => (
              <SubmissionRow key={submission.id} submission={submission} />
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
