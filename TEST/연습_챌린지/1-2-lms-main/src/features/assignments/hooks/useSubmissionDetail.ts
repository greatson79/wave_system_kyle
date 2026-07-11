'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  SubmissionDetailResponseSchema,
  type SubmissionDetailResponse,
} from '../lib/dto';

const fetchSubmissionDetail = async (
  submissionId: string,
): Promise<SubmissionDetailResponse> => {
  try {
    const { data } = await apiClient.get(`/api/instructor/submissions/${submissionId}`);
    return SubmissionDetailResponseSchema.parse(data);
  } catch (error) {
    const message = extractApiErrorMessage(
      error,
      '제출물을 불러오지 못했습니다.',
    );
    throw new Error(message);
  }
};

export const useSubmissionDetail = (submissionId: string) =>
  useQuery({
    queryKey: ['submission', submissionId],
    queryFn: () => fetchSubmissionDetail(submissionId),
    staleTime: 30 * 1000,
  });
