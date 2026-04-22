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
  FormDescription,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useCreateDifficulty } from '../hooks/useCreateDifficulty';
import { useUpdateDifficulty } from '../hooks/useUpdateDifficulty';
import {
  CreateDifficultyRequestSchema,
  UpdateDifficultyRequestSchema,
  type CreateDifficultyRequest,
  type UpdateDifficultyRequest,
  type DifficultyItem,
} from '../lib/dto';

interface DifficultyFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  difficulty?: DifficultyItem;
}

export function DifficultyFormDialog({
  open,
  onOpenChange,
  difficulty,
}: DifficultyFormDialogProps) {
  const [error, setError] = useState<string | null>(null);
  const { mutate: createDifficulty, isPending: isCreating } =
    useCreateDifficulty();
  const { mutate: updateDifficulty, isPending: isUpdating } =
    useUpdateDifficulty();

  const isEdit = !!difficulty;
  const isPending = isCreating || isUpdating;

  const form = useForm<CreateDifficultyRequest | UpdateDifficultyRequest>({
    resolver: zodResolver(
      isEdit ? UpdateDifficultyRequestSchema : CreateDifficultyRequestSchema
    ),
    defaultValues: {
      name: difficulty?.name || '',
      level: difficulty?.level || undefined,
    },
  });

  useEffect(() => {
    if (difficulty) {
      form.reset({ name: difficulty.name, level: difficulty.level });
    } else {
      form.reset({ name: '', level: undefined });
    }
  }, [difficulty, form]);

  const onSubmit = (
    data: CreateDifficultyRequest | UpdateDifficultyRequest
  ) => {
    setError(null);

    if (isEdit && difficulty) {
      updateDifficulty(
        {
          difficultyId: difficulty.id,
          data: data as UpdateDifficultyRequest,
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
      createDifficulty(data as CreateDifficultyRequest, {
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
            {isEdit ? '난이도 수정' : '새 난이도 추가'}
          </DialogTitle>
          <DialogDescription>
            {isEdit
              ? '난이도 정보를 수정하세요.'
              : '새로운 난이도를 추가하세요.'}
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
                  <FormLabel>난이도 이름</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="예: 초급, 중급, 고급"
                      disabled={isPending}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="level"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>레벨</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      min={1}
                      placeholder="1 이상의 숫자를 입력하세요"
                      disabled={isPending}
                      {...field}
                      onChange={(e) =>
                        field.onChange(
                          e.target.value ? parseInt(e.target.value, 10) : undefined
                        )
                      }
                      value={field.value ?? ''}
                    />
                  </FormControl>
                  <FormDescription>
                    레벨은 낮은 숫자부터 순서대로 정렬됩니다.
                  </FormDescription>
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
