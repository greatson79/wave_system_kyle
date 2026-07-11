export type SubmissionStatus = 'submitted' | 'graded' | 'resubmission_required';

export const getSubmissionStatusText = (status: SubmissionStatus): string => {
  const statusMap: Record<SubmissionStatus, string> = {
    submitted: '제출됨',
    graded: '채점 완료',
    resubmission_required: '재제출 요청',
  };
  return statusMap[status];
};

export const getSubmissionStatusColor = (
  status: SubmissionStatus,
): 'default' | 'success' | 'warning' => {
  const colorMap: Record<SubmissionStatus, 'default' | 'success' | 'warning'> = {
    submitted: 'default',
    graded: 'success',
    resubmission_required: 'warning',
  };
  return colorMap[status];
};
