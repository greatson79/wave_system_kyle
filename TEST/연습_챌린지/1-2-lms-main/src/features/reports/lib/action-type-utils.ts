import type { ActionType } from '../backend/schema';

export const getActionTypeText = (actionType: ActionType): string => {
  const actionMap: Record<ActionType, string> = {
    warning: '경고 발송',
    invalidate_submission: '제출물 무효화',
    suspend_account: '계정 일시정지',
    ban_account: '계정 영구정지',
    dismiss: '신고 기각',
  };
  return actionMap[actionType];
};

export const getActionTypeDescription = (actionType: ActionType): string => {
  const descriptionMap: Record<ActionType, string> = {
    warning: '대상자에게 경고 메시지를 전송합니다.',
    invalidate_submission: '제출물의 점수를 0점으로 변경하고 무효화합니다.',
    suspend_account: '지정된 기간 동안 계정을 일시정지합니다.',
    ban_account: '계정을 영구적으로 비활성화합니다.',
    dismiss: '신고 내용이 부적절하거나 증거 불충분 시 사용합니다.',
  };
  return descriptionMap[actionType];
};
