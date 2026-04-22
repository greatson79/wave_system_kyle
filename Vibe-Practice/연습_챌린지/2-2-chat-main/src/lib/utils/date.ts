import { format, isToday, isYesterday } from 'date-fns';
import { ko } from 'date-fns/locale';

/**
 * 메시지 시간을 표시용으로 포맷
 * - 오늘: "오후 3:24"
 * - 어제: "어제"
 * - 그 외: "2025.10.20"
 */
export const formatMessageTime = (dateString: string): string => {
  const date = new Date(dateString);

  if (isToday(date)) {
    return format(date, 'a h:mm', { locale: ko });
  }

  if (isYesterday(date)) {
    return '어제';
  }

  return format(date, 'yyyy.MM.dd');
};

/**
 * 채팅방 목록의 최근 메시지 시간 포맷
 * - 오늘: "오후 3:24"
 * - 어제: "어제"
 * - 7일 이내: "월요일"
 * - 그 외: "2025.10.20"
 */
export const formatChatRoomTime = (dateString: string): string => {
  const date = new Date(dateString);

  if (isToday(date)) {
    return format(date, 'a h:mm', { locale: ko });
  }

  if (isYesterday(date)) {
    return '어제';
  }

  const daysDiff = Math.floor(
    (Date.now() - date.getTime()) / (1000 * 60 * 60 * 24)
  );
  if (daysDiff < 7) {
    return format(date, 'EEEE', { locale: ko });
  }

  return format(date, 'yyyy.MM.dd');
};
