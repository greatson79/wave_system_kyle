'use client';

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useCreateCategory } from '../hooks/useCreateCategory';
import { useUpdateCategory } from '../hooks/useUpdateCategory';
import {
  CreateCategoryRequestSchema,
  UpdateCategoryRequestSchema,
  type CreateCategoryRequest,
  type UpdateCategoryRequest,
  type CategoryItem,
} from '../lib/dto';

interface CategoryFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  category?: CategoryItem;
}

export function CategoryFormDialog({
  open,
  onOpenChange,
  category,
}: CategoryFormDialogProps) {
  const [error, setError] = useState<string | null>(null);
  const { mutate: createCategory, isPending: isCreating } = useCreateCategory();
  const { mutate: updateCategory, isPending: isUpdating } = useUpdateCategory();

  const isEdit = !!category;
  const isPending = isCreating || isUpdating;

  const form = useForm<CreateCategoryRequest | UpdateCategoryRequest>({
    resolver: zodResolver(
      isEdit ? UpdateCategoryRequestSchema : CreateCategoryRequestSchema
    ),
    defaultValues: {
      name: category?.name || '',
    },
  });

  useEffect(() => {
    if (category) {
      form.reset({ name: category.name });
    } else {
      form.reset({ name: '' });
    }
  }, [category, form]);

  const onSubmit = (data: CreateCategoryRequest | UpdateCategoryRequest) => {
    setError(null);

    if (isEdit && category) {
      updateCategory(
        {
          categoryId: category.id,
          data: data as UpdateCategoryRequest,
        },
        {
          onSuccess: () => {
            form.reset();
            onOpenChange(false);
          },
          onError: (err) => {
            setError(err.message);
          },
        }
      );
    } else {
      createCategory(data as CreateCategoryRequest, {
        onSuccess: () => {
          form.reset();
          onOpenChange(false);
        },
        onError: (err) => {
          setError(err.message);
        },
      });
    }
  };

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen && !isPending) {
      form.reset();
      setError(null);
    }
    onOpenChange(newOpen);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>
            {isEdit ? '카테고리 수정' : '새 카테고리 추가'}
          </DialogTitle>
          <DialogDescription>
            {isEdit
              ? '카테고리 정보를 수정하세요.'
              : '새로운 카테고리를 추가하세요.'}
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>카테고리 이름</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="예: 프로그래밍, 디자인, 마케팅"
                      disabled={isPending}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => handleOpenChange(false)}
                disabled={isPending}
              >
                취소
              </Button>
              <Button type="submit" disabled={isPending}>
                {isPending
                  ? isEdit
                    ? '수정 중...'
                    : '추가 중...'
                  : isEdit
                    ? '수정'
                    : '추가'}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
