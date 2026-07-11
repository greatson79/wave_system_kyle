import type { SupabaseClient } from '@supabase/supabase-js';
import type { HandlerResult } from '@/backend/http/response';
import { success, failure } from '@/backend/http/response';

export interface NotificationData {
  userId: string;
  type: string;
  title: string;
  content: string;
}

export type NotificationServiceError = string;

/**
 * 알림 생성 및 발송
 * 향후 확장: 이메일, 푸시 알림 등
 */
export const createNotification = async (
  supabase: SupabaseClient,
  data: NotificationData,
): Promise<HandlerResult<{ notificationId: string }, NotificationServiceError>> => {
  try {
    const { data: notification, error } = await supabase
      .from('notifications')
      .insert({
        user_id: data.userId,
        type: data.type,
        title: data.title,
        content: data.content,
        is_read: false,
      })
      .select('id')
      .single();

    if (error || !notification) {
      return failure(500, 'NOTIFICATION_FAILED', error?.message || '알림 생성에 실패했습니다.');
    }

    return success({ notificationId: notification.id });
  } catch (err) {
    return failure(
      500,
      'NOTIFICATION_FAILED',
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};
