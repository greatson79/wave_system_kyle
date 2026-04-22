import { format, formatDistanceToNow, isPast, isFuture, differenceInHours } from 'date-fns';
import { ko } from 'date-fns/locale';

/**
 * 날짜 포맷팅
 * @param date 포맷팅할 날짜
 * @param formatStr 포맷 문자열 (기본: 'yyyy-MM-dd HH:mm')
 */
export const formatDate = (date: string | Date, formatStr: string = 'yyyy-MM-dd HH:mm'): string => {
  return format(new Date(date), formatStr, { locale: ko });
};

/**
 * 상대 시간 표시 (예: "3일 전", "2시간 후")
 * @param date 대상 날짜
 */
export const formatRelativeTime = (date: string | Date): string => {
  return formatDistanceToNow(new Date(date), { addSuffix: true, locale: ko });
};

/**
 * 마감일 임박 여부 (기본: 72시간 이내)
 * @param dueDate 마감일
 * @param hoursThreshold 임박 기준 시간 (기본: 72시간)
 */
export const isDueSoon = (dueDate: string | Date, hoursThreshold: number = 72): boolean => {
  const now = new Date();
  const due = new Date(dueDate);
  return isFuture(due) && differenceInHours(due, now) <= hoursThreshold;
};

/**
 * 마감일 지남 여부
 * @param dueDate 마감일
 */
export const isPastDue = (dueDate: string | Date): boolean => {
  return isPast(new Date(dueDate));
};

/**
 * 마감일까지 남은 시간 표시 (예: "2일 3시간 남음", "3시간 지남")
 * @param dueDate 마감일
 */
export const formatDueStatus = (dueDate: string | Date): string => {
  const due = new Date(dueDate);
  const now = new Date();

  if (isPast(due)) {
    return `${formatRelativeTime(due).replace('전', '지남')}`;
  }

  return `${formatRelativeTime(due).replace('후', '남음')}`;
};
