type EmptyStateConfig = {
  title: string;
  message: string;
  actionText?: string;
  actionLink?: string;
};

export const dashboardEmptyState = {
  noCourses: (): EmptyStateConfig => ({
    title: '수강 중인 코스가 없습니다',
    message: '새로운 코스를 찾아 학습을 시작해보세요.',
    actionText: '코스 둘러보기',
    actionLink: '/courses',
  }),
  noDueAssignments: (): EmptyStateConfig => ({
    title: '마감 임박 과제가 없습니다',
    message: '현재 72시간 이내 마감되는 과제가 없습니다.',
  }),
  noFeedback: (): EmptyStateConfig => ({
    title: '최근 피드백이 없습니다',
    message: '과제를 제출하고 강사의 피드백을 받아보세요.',
  }),
  error: (): EmptyStateConfig => ({
    title: '데이터를 불러올 수 없습니다',
    message: '일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요.',
    actionText: '다시 시도',
  }),
};
