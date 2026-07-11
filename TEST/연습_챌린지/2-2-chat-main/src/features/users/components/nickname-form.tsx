'use client';

import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Loader2 } from 'lucide-react';
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
import { UpdateNicknameRequestSchema, type UpdateNicknameRequest } from '../lib/dto';
import { useUpdateNickname } from '../hooks/use-update-nickname';
import type { UserProfile } from '../types';

export type NicknameFormProps = {
  userProfile: UserProfile;
};

export const NicknameForm: React.FC<NicknameFormProps> = ({ userProfile }) => {
  const { mutate, isPending } = useUpdateNickname();

  const form = useForm<UpdateNicknameRequest>({
    resolver: zodResolver(UpdateNicknameRequestSchema),
    defaultValues: {
      nickname: userProfile.nickname,
    },
  });

  const onSubmit = (data: UpdateNicknameRequest) => {
    mutate(data);
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="px-6 space-y-4">
        <FormField
          control={form.control}
          name="nickname"
          render={({ field }) => (
            <FormItem>
              <FormLabel>새 닉네임</FormLabel>
              <FormControl>
                <Input placeholder="닉네임을 입력하세요" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button
          type="submit"
          className="w-full"
          disabled={isPending || !form.formState.isDirty}
        >
          {isPending ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              저장 중...
            </>
          ) : (
            '저장'
          )}
        </Button>
      </form>
    </Form>
  );
};
