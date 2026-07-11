type AssignmentStatus = 'published' | 'closed' | 'draft';
type SubmissionStatus = 'submitted' | 'graded' | 'resubmission_required' | null;

export type CanSubmitResult = {
  canSubmit: boolean;
  reason?: string;
};

/**
 * 제출 가능 여부 판단
 */
export const canSubmitAssignment = (
  assignmentStatus: AssignmentStatus,
  dueDate: string,
  allowLate: boolean,
  allowResubmit: boolean,
  submissionStatus: SubmissionStatus,
): CanSubmitResult => {
  // 1. 과제가 closed 상태
  if (assignmentStatus === 'closed') {
    return { canSubmit: false, reason: '마감된 과제입니다.' };
  }

  // 2. 과제가 published 상태가 아님
  if (assignmentStatus !== 'published') {
    return { canSubmit: false, reason: '과제를 찾을 수 없습니다.' };
  }

  // 3. 마감일 지남 & 지각 불허
  const isPastDue = new Date(dueDate) < new Date();
  if (isPastDue && !allowLate) {
    return { canSubmit: false, reason: '제출 기한이 지났습니다.' };
  }

  // 4. 제출 이력이 없으면 제출 가능
  if (!submissionStatus) {
    return { canSubmit: true };
  }

  // 5. 재제출 요청된 경우
  if (submissionStatus === 'resubmission_required') {
    if (!allowResubmit) {
      return { canSubmit: false, reason: '재제출이 허용되지 않습니다.' };
    }
    // 재제출도 마감일 제약 적용
    if (isPastDue && !allowLate) {
      return { canSubmit: false, reason: '재제출 기한이 지났습니다.' };
    }
    return { canSubmit: true };
  }

  // 6. 이미 제출됨 또는 채점됨
  if (submissionStatus === 'submitted' || submissionStatus === 'graded') {
    return { canSubmit: false, reason: '이미 제출된 과제입니다.' };
  }

  return { canSubmit: false, reason: '제출할 수 없습니다.' };
};

/**
 * 제출 상태 표시용 텍스트
 */
export const getSubmissionStatusText = (
  status: SubmissionStatus,
  score: number | null,
): string => {
  if (!status) return '미제출';
  if (status === 'submitted') return '제출 완료';
  if (status === 'graded' && score !== null) return `채점 완료 (${score}점)`;
  if (status === 'graded') return '채점 완료';
  if (status === 'resubmission_required') return '재제출 요청';
  return '알 수 없음';
};

/**
 * 제출 상태별 색상 (Tailwind classes)
 */
export const getSubmissionStatusColor = (status: SubmissionStatus): string => {
  if (!status) return 'text-gray-500';
  if (status === 'submitted') return 'text-blue-600';
  if (status === 'graded') return 'text-green-600';
  if (status === 'resubmission_required') return 'text-orange-600';
  return 'text-gray-500';
};
