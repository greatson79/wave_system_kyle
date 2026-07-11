export type AssignmentStatus = 'draft' | 'published' | 'closed';

export const getAssignmentStatusText = (status: AssignmentStatus): string => {
  const statusMap: Record<AssignmentStatus, string> = {
    draft: '임시 저장',
    published: '게시됨',
    closed: '마감됨',
  };
  return statusMap[status];
};

export const getAssignmentStatusColor = (
  status: AssignmentStatus,
): 'default' | 'success' | 'secondary' => {
  const colorMap: Record<AssignmentStatus, 'default' | 'success' | 'secondary'> = {
    draft: 'default',
    published: 'success',
    closed: 'secondary',
  };
  return colorMap[status];
};

/**
 * 과제가 게시 가능한 상태인지 확인
 */
export const canPublish = (assignment: {
  status: AssignmentStatus;
  title: string;
  description: string;
  dueDate: string;
  weight: number;
}): boolean => {
  return (
    assignment.status === 'draft' &&
    !!assignment.title &&
    !!assignment.description &&
    !!assignment.dueDate &&
    assignment.weight >= 0 &&
    assignment.weight <= 100
  );
};

/**
 * 과제가 마감 가능한 상태인지 확인
 */
export const canClose = (assignment: { status: AssignmentStatus }): boolean => {
  return assignment.status === 'published';
};
