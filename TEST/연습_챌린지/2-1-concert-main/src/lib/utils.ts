import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * 콘서트 날짜 포맷팅
 * @example "2025년 12월 25일 (수) 19:00"
 */
export const formatConcertDate = (dateString: string): string => {
  const date = new Date(dateString);
  return format(date, 'yyyy년 MM월 dd일 (EEE) HH:mm', { locale: ko });
};

/**
 * 예약 마감 일시 포맷팅
 * @example "2025-12-24 23:59"
 */
export const formatBookingDeadline = (dateString: string): string => {
  const date = new Date(dateString);
  return format(date, 'yyyy-MM-dd HH:mm');
};
