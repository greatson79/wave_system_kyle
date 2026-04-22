'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Button } from '@/components/ui/button';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { useCreateCourse } from '../hooks/useCreateCourse';
import { useUpdateCourse } from '../hooks/useUpdateCourse';
import {
  CreateCourseRequestSchema,
  UpdateCourseRequestSchema,
  type CreateCourseRequest,
  type UpdateCourseRequest,
} from '../lib/dto';

type CourseFormMode = 'create' | 'edit';

interface CourseFormProps {
  mode: CourseFormMode;
  courseId?: string;
  defaultValues?: Partial<CreateCourseRequest>;
  categories?: Array<{ id: string; name: string }>;
  difficulties?: Array<{ id: string; name: string; level: number }>;
}

export const CourseForm = ({
  mode,
  courseId,
  defaultValues,
  categories = [],
  difficulties = [],
}: CourseFormProps) => {
  const { toast } = useToast();
  const { mutate: createCourse, isPending: isCreating } = useCreateCourse();
  const { mutate: updateCourse, isPending: isUpdating } = useUpdateCourse(courseId || '');

  const schema = mode === 'create' ? CreateCourseRequestSchema : UpdateCourseRequestSchema;
  const form = useForm<CreateCourseRequest | UpdateCourseRequest>({
    resolver: zodResolver(schema),
    defaultValues: defaultValues || {
      title: '',
      description: '',
      categoryId: '',
      difficultyId: '',
      curriculum: '',
    },
  });

  const onSubmit = (data: CreateCourseRequest | UpdateCourseRequest) => {
    if (mode === 'create') {
      createCourse(data as CreateCourseRequest, {
        onSuccess: (response) => {
          toast({
            title: '성공',
            description: response.message,
          });
        },
        onError: (error) => {
          toast({
            title: '오류',
            description: error.message,
            variant: 'destructive',
          });
        },
      });
    } else {
      updateCourse(data as UpdateCourseRequest, {
        onSuccess: (response) => {
          toast({
            title: '성공',
            description: response.message,
          });
        },
        onError: (error) => {
          toast({
            title: '오류',
            description: error.message,
            variant: 'destructive',
          });
        },
      });
    }
  };

  const isPending = isCreating || isUpdating;

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="title"
          render={({ field }) => (
            <FormItem>
              <FormLabel>제목</FormLabel>
              <FormControl>
                <Input placeholder="코스 제목을 입력하세요" {...field} />
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
              <FormLabel>소개</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="코스에 대한 간단한 소개를 입력하세요"
                  className="min-h-[100px]"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="categoryId"
          render={({ field }) => (
            <FormItem>
              <FormLabel>카테고리</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="카테고리를 선택하세요" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {categories.map((category) => (
                    <SelectItem key={category.id} value={category.id}>
                      {category.name}
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
          name="difficultyId"
          render={({ field }) => (
            <FormItem>
              <FormLabel>난이도</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="난이도를 선택하세요" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {difficulties.map((difficulty) => (
                    <SelectItem key={difficulty.id} value={difficulty.id}>
                      {difficulty.name}
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
          name="curriculum"
          render={({ field }) => (
            <FormItem>
              <FormLabel>커리큘럼 (선택)</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="커리큘럼을 입력하세요"
                  className="min-h-[200px]"
                  {...field}
                  value={field.value || ''}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button type="submit" disabled={isPending}>
          {isPending ? '처리 중...' : mode === 'create' ? '생성' : '저장'}
        </Button>
      </form>
    </Form>
  );
};
