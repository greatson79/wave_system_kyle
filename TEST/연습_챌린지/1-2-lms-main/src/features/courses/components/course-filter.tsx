'use client';

import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Search } from 'lucide-react';

type CourseFilterProps = {
  search: string;
  categoryId: string;
  difficultyId: string;
  sort: 'latest' | 'popular';
  onSearchChange: (value: string) => void;
  onCategoryChange: (value: string) => void;
  onDifficultyChange: (value: string) => void;
  onSortChange: (value: 'latest' | 'popular') => void;
  onReset: () => void;
};

export const CourseFilter = ({
  search,
  categoryId,
  difficultyId,
  sort,
  onSearchChange,
  onCategoryChange,
  onDifficultyChange,
  onSortChange,
  onReset,
}: CourseFilterProps) => {
  return (
    <div className="space-y-4 p-4 border rounded-lg bg-card">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
        <Input
          placeholder="코스 검색..."
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          className="pl-10"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Select value={categoryId} onValueChange={onCategoryChange}>
          <SelectTrigger>
            <SelectValue placeholder="카테고리" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">전체</SelectItem>
          </SelectContent>
        </Select>

        <Select value={difficultyId} onValueChange={onDifficultyChange}>
          <SelectTrigger>
            <SelectValue placeholder="난이도" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">전체</SelectItem>
          </SelectContent>
        </Select>

        <Select value={sort} onValueChange={onSortChange}>
          <SelectTrigger>
            <SelectValue placeholder="정렬" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="latest">최신순</SelectItem>
            <SelectItem value="popular">인기순</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Button onClick={onReset} variant="outline" className="w-full">
        필터 초기화
      </Button>
    </div>
  );
};
