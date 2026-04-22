import type { SupabaseClient } from '@supabase/supabase-js';
import type { HandlerResult } from '@/backend/http/response';
import { success, failure } from '@/backend/http/response';
import { reportsErrorCodes, type ReportsServiceError } from './error';
import type {
  SubmitReportRequest,
  SubmitReportResponse,
  ReportsListQuery,
  ReportsListResponse,
  ReportDetailResponse,
  UpdateReportRequest,
  UpdateReportResponse,
  TargetType,
  ActionType,
} from './schema';
import { canTransitionStatus } from '../lib/report-status-utils';
import { createNotification } from '@/features/notifications/backend/service';

/**
 * 신고 접수
 */
export const submitReport = async (
  supabase: SupabaseClient,
  userId: string,
  data: SubmitReportRequest,
): Promise<HandlerResult<SubmitReportResponse, ReportsServiceError>> => {
  try {
    // 대상 존재 확인
    const targetExists = await validateTargetExists(
      supabase,
      data.targetType,
      data.targetId,
    );

    if (!targetExists) {
      return failure(
        404,
        reportsErrorCodes.targetNotFound,
        '신고 대상을 찾을 수 없습니다.',
      );
    }

    // 신고 생성
    const { data: report, error } = await supabase
      .from('reports')
      .insert({
        reporter_id: userId,
        target_type: data.targetType,
        target_id: data.targetId,
        reason: data.reason,
        content: data.content,
        status: 'received',
      })
      .select('id, status, created_at')
      .single();

    if (error || !report) {
      return failure(
        500,
        reportsErrorCodes.invalidRequest,
        error?.message || '신고 접수에 실패했습니다.',
      );
    }

    return success(
      {
        reportId: report.id,
        status: report.status as 'received',
        createdAt: report.created_at,
        message: '신고가 정상적으로 접수되었습니다.',
      },
      201,
    );
  } catch (err) {
    return failure(
      500,
      reportsErrorCodes.invalidRequest,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

/**
 * 신고 목록 조회 (운영자 전용)
 */
export const getReportsList = async (
  supabase: SupabaseClient,
  query: ReportsListQuery,
): Promise<HandlerResult<ReportsListResponse, ReportsServiceError>> => {
  try {
    let queryBuilder = supabase
      .from('reports')
      .select(
        `
        id,
        target_type,
        target_id,
        reason,
        status,
        created_at,
        resolved_at,
        reporter:profiles!reports_reporter_id_fkey(id, name)
      `,
        { count: 'exact' },
      )
      .order('created_at', { ascending: false })
      .range(query.offset, query.offset + query.limit - 1);

    if (query.status) {
      queryBuilder = queryBuilder.eq('status', query.status);
    }

    if (query.targetType) {
      queryBuilder = queryBuilder.eq('target_type', query.targetType);
    }

    const { data: reports, error, count } = await queryBuilder;

    if (error || !reports) {
      return failure(
        500,
        reportsErrorCodes.invalidRequest,
        error?.message || '신고 목록 조회에 실패했습니다.',
      );
    }

    const formattedReports = reports.map((report: any) => ({
      id: report.id,
      reporter: {
        id: report.reporter.id,
        name: report.reporter.name,
      },
      targetType: report.target_type,
      targetId: report.target_id,
      reason: report.reason,
      status: report.status,
      createdAt: report.created_at,
      resolvedAt: report.resolved_at,
    }));

    return success({
      reports: formattedReports,
      total: count || 0,
      limit: query.limit,
      offset: query.offset,
    });
  } catch (err) {
    return failure(
      500,
      reportsErrorCodes.invalidRequest,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

/**
 * 신고 상세 조회 (운영자 전용)
 */
export const getReportDetail = async (
  supabase: SupabaseClient,
  reportId: string,
): Promise<HandlerResult<ReportDetailResponse, ReportsServiceError>> => {
  try {
    const { data: report, error } = await supabase
      .from('reports')
      .select(
        `
        id,
        target_type,
        target_id,
        reason,
        content,
        status,
        action_taken,
        created_at,
        updated_at,
        resolved_at,
        reporter:profiles!reports_reporter_id_fkey(id, name)
      `,
      )
      .eq('id', reportId)
      .single();

    if (error || !report) {
      return failure(
        404,
        reportsErrorCodes.reportNotFound,
        '신고 내역을 찾을 수 없습니다.',
      );
    }

    // 대상 정보 조회
    const targetInfo = await getTargetInfo(
      supabase,
      report.target_type as TargetType,
      report.target_id,
    );

    return success({
      id: report.id,
      reporter: {
        id: (report.reporter as any).id,
        name: (report.reporter as any).name,
      },
      targetType: report.target_type as TargetType,
      targetId: report.target_id,
      targetInfo,
      reason: report.reason,
      content: report.content,
      status: report.status as any,
      actionTaken: report.action_taken,
      createdAt: report.created_at,
      updatedAt: report.updated_at,
      resolvedAt: report.resolved_at,
    });
  } catch (err) {
    return failure(
      500,
      reportsErrorCodes.invalidRequest,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

/**
 * 신고 처리 (운영자 전용)
 */
export const updateReport = async (
  supabase: SupabaseClient,
  reportId: string,
  data: UpdateReportRequest,
): Promise<HandlerResult<UpdateReportResponse, ReportsServiceError>> => {
  try {
    // 현재 신고 상태 조회
    const { data: currentReport, error: fetchError } = await supabase
      .from('reports')
      .select('id, status, target_type, target_id, reporter_id')
      .eq('id', reportId)
      .single();

    if (fetchError || !currentReport) {
      return failure(
        404,
        reportsErrorCodes.reportNotFound,
        '신고 내역을 찾을 수 없습니다.',
      );
    }

    // 상태 전환 가능 여부 확인
    if (!canTransitionStatus(currentReport.status as any, data.status)) {
      return failure(
        400,
        reportsErrorCodes.statusTransitionNotAllowed,
        '해당 상태로 전환할 수 없습니다.',
      );
    }

    // resolved 상태로 변경 시 조치 실행
    let actionTakenText: string | null = null;
    if (data.status === 'resolved') {
      if (!data.actionType) {
        return failure(
          400,
          reportsErrorCodes.actionRequired,
          '처리 완료 시 조치 유형을 선택해야 합니다.',
        );
      }

      const actionResult = await executeAction(
        supabase,
        currentReport.target_type as TargetType,
        currentReport.target_id,
        data.actionType,
        data.suspensionDays,
      );

      if (!actionResult.ok) {
        return failure(
          500,
          reportsErrorCodes.actionFailed,
          '조치 실행에 실패했습니다.',
        );
      }

      actionTakenText = data.actionNote || actionResult.data.actionDescription;

      // 알림 발송 (신고자, 대상자)
      await createNotification(supabase, {
        userId: currentReport.reporter_id,
        type: 'report_resolved',
        title: '신고가 처리되었습니다',
        content: '접수하신 신고가 처리 완료되었습니다.',
      });

      // 대상이 user인 경우에만 대상자에게 알림 발송
      if (currentReport.target_type === 'user') {
        await createNotification(supabase, {
          userId: currentReport.target_id,
          type: 'report_action',
          title: '신고에 대한 조치가 있습니다',
          content: actionTakenText || '귀하에 대한 신고가 접수되어 조치되었습니다.',
        });
      }
    }

    // 신고 업데이트
    const updateData: any = {
      status: data.status,
    };

    if (data.status === 'resolved') {
      updateData.resolved_at = new Date().toISOString();
      updateData.action_taken = actionTakenText;
    }

    const { data: updatedReport, error: updateError } = await supabase
      .from('reports')
      .update(updateData)
      .eq('id', reportId)
      .select('id, status, resolved_at')
      .single();

    if (updateError || !updatedReport) {
      return failure(
        500,
        reportsErrorCodes.invalidRequest,
        updateError?.message || '신고 처리에 실패했습니다.',
      );
    }

    return success({
      reportId: updatedReport.id,
      status: updatedReport.status as any,
      resolvedAt: updatedReport.resolved_at,
      message: '신고가 정상적으로 처리되었습니다.',
    });
  } catch (err) {
    return failure(
      500,
      reportsErrorCodes.invalidRequest,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

/**
 * 헬퍼: 대상 존재 확인
 */
const validateTargetExists = async (
  supabase: SupabaseClient,
  targetType: TargetType,
  targetId: string,
): Promise<boolean> => {
  const tableMap: Record<TargetType, string> = {
    course: 'courses',
    assignment: 'assignments',
    submission: 'submissions',
    user: 'profiles',
  };

  const tableName = tableMap[targetType];
  const { data, error } = await supabase
    .from(tableName)
    .select('id')
    .eq('id', targetId)
    .maybeSingle();

  return !error && !!data;
};

/**
 * 헬퍼: 대상 정보 조회
 */
const getTargetInfo = async (
  supabase: SupabaseClient,
  targetType: TargetType,
  targetId: string,
): Promise<{ title?: string; name?: string } | null> => {
  try {
    if (targetType === 'course') {
      const { data } = await supabase
        .from('courses')
        .select('title')
        .eq('id', targetId)
        .maybeSingle();
      return data ? { title: data.title } : null;
    }

    if (targetType === 'assignment') {
      const { data } = await supabase
        .from('assignments')
        .select('title')
        .eq('id', targetId)
        .maybeSingle();
      return data ? { title: data.title } : null;
    }

    if (targetType === 'submission') {
      const { data } = await supabase
        .from('submissions')
        .select('id')
        .eq('id', targetId)
        .maybeSingle();
      return data ? { title: `제출물 ${data.id}` } : null;
    }

    if (targetType === 'user') {
      const { data } = await supabase
        .from('profiles')
        .select('name')
        .eq('id', targetId)
        .maybeSingle();
      return data ? { name: data.name } : null;
    }

    return null;
  } catch {
    return null;
  }
};

/**
 * 헬퍼: 조치 실행
 */
const executeAction = async (
  supabase: SupabaseClient,
  targetType: TargetType,
  targetId: string,
  actionType: ActionType,
  suspensionDays?: number,
): Promise<HandlerResult<{ actionDescription: string }, ReportsServiceError>> => {
  try {
    if (actionType === 'invalidate_submission') {
      if (targetType !== 'submission') {
        return failure(
          400,
          reportsErrorCodes.actionFailed,
          '제출물 무효화는 제출물에만 적용할 수 있습니다.',
        );
      }

      const { error } = await supabase
        .from('submissions')
        .update({
          status: 'invalidated' as any,
          score: 0,
        })
        .eq('id', targetId);

      if (error) {
        return failure(
          500,
          reportsErrorCodes.actionFailed,
          '제출물 무효화에 실패했습니다.',
        );
      }

      return success({
        actionDescription: '제출물이 무효화되었습니다. (점수: 0점)',
      });
    }

    if (actionType === 'warning') {
      return success({
        actionDescription: '경고가 발송되었습니다.',
      });
    }

    if (actionType === 'suspend_account') {
      return success({
        actionDescription: `계정이 ${suspensionDays || 7}일간 일시정지되었습니다.`,
      });
    }

    if (actionType === 'ban_account') {
      return success({
        actionDescription: '계정이 영구정지되었습니다.',
      });
    }

    if (actionType === 'dismiss') {
      return success({
        actionDescription: '신고가 기각되었습니다.',
      });
    }

    return failure(
      400,
      reportsErrorCodes.actionFailed,
      '알 수 없는 조치 유형입니다.',
    );
  } catch (err) {
    return failure(
      500,
      reportsErrorCodes.actionFailed,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};
