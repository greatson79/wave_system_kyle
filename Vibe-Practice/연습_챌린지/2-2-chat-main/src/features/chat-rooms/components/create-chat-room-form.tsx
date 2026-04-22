'use client';

import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useRouter } from 'next/navigation';
import { Loader2 } from 'lucide-react';
import { useCreateChatRoom } from '../hooks/useCreateChatRoom';
import { CreateChatRoomRequestSchema } from '../lib/dto';
import type { CreateChatRoomRequest } from '../lib/dto';
import { extractApiErrorMessage } from '@/lib/remote/api-client';

export const CreateChatRoomForm: React.FC = () => {
  const router = useRouter();
  const createChatRoom = useCreateChatRoom();

  const form = useForm<CreateChatRoomRequest>({
    resolver: zodResolver(CreateChatRoomRequestSchema),
    defaultValues: {
      name: '',
    },
    mode: 'onChange',
  });

  const handleSubmit = form.handleSubmit(async (data) => {
    try {
      await createChatRoom.mutateAsync(data);
      // 성공 시 자동 리다이렉트 (useCreateChatRoom onSuccess에서 처리)
    } catch (error) {
      console.error('채팅방 생성 실패:', error);
      // 에러 처리는 mutation hook에서 수행
    }
  });

  const handleCancel = () => {
    router.push('/');
  };

  const nameLength = form.watch('name')?.length || 0;
  const isValid = form.formState.isValid;
  const isPending = createChatRoom.isPending;

  return (
    <div className="max-w-lg mx-auto bg-white shadow-md rounded-lg mt-8">
      {/* Header */}
      <div className="px-6 py-4 border-b">
        <h1 className="text-2xl font-bold">채팅방 만들기</h1>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="p-6">
        {/* Input Field */}
        <div className="mb-6">
          <label htmlFor="name" className="block text-sm font-medium mb-2">
            채팅방 이름
          </label>
          <div className="relative">
            <input
              id="name"
              {...form.register('name')}
              type="text"
              placeholder="채팅방 이름을 입력하세요"
              maxLength={50}
              disabled={isPending}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary disabled:bg-gray-100"
            />
            <span className="absolute right-3 top-3 text-sm text-gray-500">
              {nameLength}/50자
            </span>
          </div>

          {/* Error Message */}
          {form.formState.errors.name && (
            <p className="text-sm text-destructive mt-2">
              {form.formState.errors.name.message}
            </p>
          )}
        </div>

        {/* API Error */}
        {createChatRoom.error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-600">
              {extractApiErrorMessage(
                createChatRoom.error,
                '채팅방 생성에 실패했습니다. 다시 시도해주세요.'
              )}
            </p>
          </div>
        )}

        {/* Footer Buttons */}
        <div className="flex gap-3">
          <button
            type="button"
            onClick={handleCancel}
            disabled={isPending}
            className="flex-1 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
          >
            취소
          </button>
          <button
            type="submit"
            disabled={!isValid || isPending}
            className="flex-1 py-3 bg-primary text-white rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {isPending ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                생성 중...
              </>
            ) : (
              '생성'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
