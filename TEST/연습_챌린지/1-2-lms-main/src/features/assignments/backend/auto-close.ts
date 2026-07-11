import type { SupabaseClient } from '@supabase/supabase-js';
import type { HandlerResult } from '@/backend/http/response';
import { success, failure } from '@/backend/http/response';
import { assignmentsErrorCodes, type AssignmentsServiceError } from './error';

export interface AutoCloseResult {
  closedCount: number;
  closedAssignmentIds: string[];
  message: string;
}

/**
 * 마감일이 경과한 published 상태 과제를 자동으로 closed 상태로 변경
 */
export const autoCloseAssignments = async (
  supabase: SupabaseClient,
): Promise<HandlerResult<AutoCloseResult, AssignmentsServiceError>> => {
  try {
    const now = new Date().toISOString();

    // 1. 마감일 경과한 published 과제 조회
    const { data: assignments, error: fetchError } = await supabase
      .from('assignments')
      .select('id, title, due_date')
      .eq('status', 'published')
      .lt('due_date', now);

    if (fetchError) {
      return failure(
        500,
        assignmentsErrorCodes.invalidRequest,
        fetchError.message,
      );
    }

    if (!assignments || assignments.length === 0) {
      return success({
        closedCount: 0,
        closedAssignmentIds: [],
        message: '자동 마감할 과제가 없습니다.',
      });
    }

    const assignmentIds = assignments.map((a) => a.id);

    // 2. 일괄 업데이트
    const { data: updated, error: updateError } = await supabase
      .from('assignments')
      .update({ status: 'closed' })
      .in('id', assignmentIds)
      .select('id');

    if (updateError) {
      return failure(
        500,
        assignmentsErrorCodes.closeFailed,
        updateError.message,
      );
    }

    const closedIds = (updated || []).map((a: { id: string }) => a.id);

    return success({
      closedCount: closedIds.length,
      closedAssignmentIds: closedIds,
      message: `${closedIds.length}개의 과제가 자동으로 마감되었습니다.`,
    });
  } catch (err) {
    return failure(
      500,
      assignmentsErrorCodes.closeFailed,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};
