'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { CreateAssignmentRequest } from '../lib/dto';

const formSchema = z.object({
  courseId: z.string().min(1, '코스를 선택해주세요.'),
  title: z.string().min(1, '제목은 필수 항목입니다.'),
  description: z.string().min(1, '설명은 필수 항목입니다.'),
  dueDate: z.string().min(1, '마감일은 필수 항목입니다.'),
  weight: z.coerce.number().min(0).max(100),
  allowLate: z.boolean(),
  allowResubmit: z.boolean(),
});

interface AssignmentFormProps {
  courses: Array<{ id: string; title: string }>;
  defaultValues?: Partial<CreateAssignmentRequest>;
  onSubmit: (data: CreateAssignmentRequest) => void;
  isSubmitting?: boolean;
}

export function AssignmentForm({
  courses,
  defaultValues,
  onSubmit,
  isSubmitting,
}: AssignmentFormProps) {
  const form = useForm<CreateAssignmentRequest>({
    resolver: zodResolver(formSchema),
    defaultValues: defaultValues || {
      courseId: '',
      title: '',
      description: '',
      dueDate: '',
      weight: 0,
      allowLate: false,
      allowResubmit: false,
    },
  });

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="courseId"
          render={({ field }) => (
            <FormItem>
              <FormLabel>코스</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="코스를 선택하세요" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {courses.map((course) => (
                    <SelectItem key={course.id} value={course.id}>
                      {course.title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="title"
          render={({ field }) => (
            <FormItem>
              <FormLabel>과제 제목</FormLabel>
              <FormControl>
                <Input placeholder="과제 제목을 입력하세요" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="description"
          render={({ field }) => (
            <FormItem>
              <FormLabel>과제 설명</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="과제 설명을 입력하세요"
                  className="min-h-[200px]"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="dueDate"
          render={({ field }) => (
            <FormItem>
              <FormLabel>마감일</FormLabel>
              <FormControl>
                <Input type="datetime-local" {...field} />
              </FormControl>
              <FormDescription>학습자들이 과제를 제출해야 하는 마감일을 설정하세요.</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="weight"
          render={({ field }) => (
            <FormItem>
              <FormLabel>점수 비중 (%)</FormLabel>
              <FormControl>
                <Input type="number" min="0" max="100" {...field} />
              </FormControl>
              <FormDescription>
                전체 코스에서 이 과제가 차지하는 점수 비중을 입력하세요 (0-100).
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="allowLate"
          render={({ field }) => (
            <FormItem className="flex flex-row items-start space-x-3 space-y-0">
              <FormControl>
                <Checkbox checked={field.value} onCheckedChange={field.onChange} />
              </FormControl>
              <div className="space-y-1 leading-none">
                <FormLabel>지각 제출 허용</FormLabel>
                <FormDescription>
                  마감일 이후에도 과제 제출을 허용합니다.
                </FormDescription>
              </div>
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="allowResubmit"
          render={({ field }) => (
            <FormItem className="flex flex-row items-start space-x-3 space-y-0">
              <FormControl>
                <Checkbox checked={field.value} onCheckedChange={field.onChange} />
              </FormControl>
              <div className="space-y-1 leading-none">
                <FormLabel>재제출 허용</FormLabel>
                <FormDescription>
                  채점 후 재제출을 요청할 수 있습니다.
                </FormDescription>
              </div>
            </FormItem>
          )}
        />

        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? '저장 중...' : '과제 생성'}
        </Button>
      </form>
    </Form>
  );
}
