import type { SupabaseClient } from '@supabase/supabase-js';
import type { HandlerResult } from '@/backend/http/response';
import { success, failure } from '@/backend/http/response';
import { assignmentsErrorCodes, type AssignmentsServiceError } from './error';
import type {
  AssignmentListResponse,
  AssignmentDetailResponse,
  AssignmentItem,
  SubmitAssignmentRequest,
  SubmitAssignmentResponse,
  ResubmitAssignmentRequest,
  CreateAssignmentRequest,
  CreateAssignmentResponse,
  UpdateAssignmentRequest,
  UpdateAssignmentResponse,
  PublishAssignmentResponse,
  CloseAssignmentResponse,
  MyAssignmentsResponse,
  AssignmentSubmissionsResponse,
  SubmissionItem,
  GradeSubmissionRequest,
  GradeSubmissionResponse,
  RequestResubmissionRequest,
  RequestResubmissionResponse,
  SubmissionDetailResponse,
} from './schema';

/**
 * 헬퍼: 학습자가 특정 코스에 수강 등록되어 있는지 확인
 */
const checkEnrollment = async (
  supabase: SupabaseClient,
  learnerId: string,
  courseId: string,
): Promise<boolean> => {
  const { data, error } = await supabase
    .from('enrollments')
    .select('id')
    .eq('learner_id', learnerId)
    .eq('course_id', courseId)
    .is('cancelled_at', null)
    .maybeSingle();

  if (error || !data) {
    return false;
  }

  return true;
};

/**
 * 헬퍼: 제출 가능 여부 계산
 */
export const calculateCanSubmit = (
  assignment: {
    status: string;
    due_date: string;
    allow_late: boolean;
    allow_resubmit: boolean;
  },
  submission: { status: string } | null,
  now: Date,
): boolean => {
  // 1. 과제가 closed 상태
  if (assignment.status === 'closed') {
    return false;
  }

  // 2. 과제가 published 상태가 아님
  if (assignment.status !== 'published') {
    return false;
  }

  // 3. 마감일 지남 & 지각 불허
  const isPastDue = new Date(assignment.due_date) < now;
  if (isPastDue && !assignment.allow_late) {
    return false;
  }

  // 4. 제출 이력이 없으면 제출 가능
  if (!submission) {
    return true;
  }

  // 5. 재제출 요청된 경우
  if (submission.status === 'resubmission_required') {
    if (!assignment.allow_resubmit) {
      return false;
    }
    // 재제출도 마감일 제약 적용
    if (isPastDue && !assignment.allow_late) {
      return false;
    }
    return true;
  }

  // 6. 이미 제출됨 또는 채점됨
  if (submission.status === 'submitted' || submission.status === 'graded') {
    return false;
  }

  return false;
};

/**
 * 특정 코스의 과제 목록 조회 (학습자용)
 */
export const getCourseAssignments = async (
  supabase: SupabaseClient,
  learnerId: string,
  courseId: string,
): Promise<HandlerResult<AssignmentListResponse, AssignmentsServiceError>> => {
  try {
    // 1. 수강 등록 확인
    const isEnrolled = await checkEnrollment(supabase, learnerId, courseId);
    if (!isEnrolled) {
      return failure(
        403,
        assignmentsErrorCodes.notEnrolled,
        '수강 중인 코스가 아닙니다.',
      );
    }

    // 2. 코스 정보 조회
    const { data: course, error: courseError } = await supabase
      .from('courses')
      .select('id, title')
      .eq('id', courseId)
      .single();

    if (courseError || !course) {
      return failure(
        404,
        assignmentsErrorCodes.invalidRequest,
        '코스를 찾을 수 없습니다.',
      );
    }

    // 3. 과제 목록 조회 (LEFT JOIN submissions)
    const { data: assignmentsData, error: assignmentsError } = await supabase
      .from('assignments')
      .select(
        `
        id,
        title,
        due_date,
        weight,
        status,
        submissions!left(
          id,
          status,
          submitted_at,
          is_late,
          score
        )
      `,
      )
      .eq('course_id', courseId)
      .in('status', ['published', 'closed'])
      .order('due_date', { ascending: true });

    if (assignmentsError) {
      return failure(
        500,
        assignmentsErrorCodes.invalidRequest,
        assignmentsError.message,
      );
    }

    // 4. 응답 데이터 매핑
    const assignments: AssignmentItem[] = (assignmentsData || []).map(
      (row: any) => {
        const submissions = row.submissions || [];
        const userSubmission = submissions.find(
          (s: any) => s !== null,
        );

        let submissionStatus: 'not_submitted' | 'submitted' | 'graded' | 'resubmission_required' = 'not_submitted';
        if (userSubmission) {
          submissionStatus = userSubmission.status;
        }

        return {
          id: row.id,
          title: row.title,
          dueDate: row.due_date,
          weight: row.weight,
          status: row.status,
          submissionStatus,
          submittedAt: userSubmission?.submitted_at || null,
          isLate: userSubmission?.is_late || null,
          score: userSubmission?.score || null,
        };
      },
    );

    return success({
      assignments,
      courseId: course.id,
      courseTitle: course.title,
    });
  } catch (err) {
    return failure(
      500,
      assignmentsErrorCodes.invalidRequest,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

/**
 * 헬퍼: 지각 여부 계산
 */
export const calculateIsLate = (dueDate: string, submittedAt: Date): boolean => {
  return new Date(dueDate) < submittedAt;
};

/**
 * 특정 과제의 상세 정보 조회 (학습자용)
 */
export const getAssignmentDetail = async (
  supabase: SupabaseClient,
  learnerId: string,
  assignmentId: string,
): Promise<HandlerResult<AssignmentDetailResponse, AssignmentsServiceError>> => {
  try {
    // 1. 과제 정보 조회 (JOIN courses, LEFT JOIN submissions)
    const { data: assignmentData, error: assignmentError } = await supabase
      .from('assignments')
      .select(
        `
        id,
        course_id,
        title,
        description,
        due_date,
        weight,
        allow_late,
        allow_resubmit,
        status,
        created_at,
        courses!inner(
          id,
          title
        ),
        submissions!left(
          id,
          submission_text,
          submission_link,
          submitted_at,
          is_late,
          score,
          feedback,
          status,
          graded_at,
          learner_id
        )
      `,
      )
      .eq('id', assignmentId)
      .single();

    if (assignmentError || !assignmentData) {
      return failure(
        404,
        assignmentsErrorCodes.assignmentNotFound,
        '과제를 찾을 수 없습니다.',
      );
    }

    // 2. 과제 상태 확인 (draft는 거부)
    if (assignmentData.status === 'draft') {
      return failure(
        404,
        assignmentsErrorCodes.assignmentNotPublished,
        '과제를 찾을 수 없습니다.',
      );
    }

    // 3. 수강 등록 확인
    const isEnrolled = await checkEnrollment(
      supabase,
      learnerId,
      assignmentData.course_id,
    );
    if (!isEnrolled) {
      return failure(
        403,
        assignmentsErrorCodes.notEnrolled,
        '수강 중인 코스가 아닙니다.',
      );
    }

    // 4. 제출 이력 필터링 (현재 학습자의 제출만)
    const submissions = (assignmentData.submissions || []).filter(
      (s: any) => s && s.learner_id === learnerId,
    );
    const userSubmission = submissions.length > 0 ? submissions[0] : null;

    // 5. 제출 가능 여부 계산
    const canSubmit = calculateCanSubmit(
      {
        status: assignmentData.status,
        due_date: assignmentData.due_date,
        allow_late: assignmentData.allow_late,
        allow_resubmit: assignmentData.allow_resubmit,
      },
      userSubmission,
      new Date(),
    );

    // 6. 응답 데이터 구성
    const response: AssignmentDetailResponse = {
      id: assignmentData.id,
      courseId: assignmentData.course_id,
      courseTitle: (assignmentData.courses as any)?.title || '',
      title: assignmentData.title,
      description: assignmentData.description,
      dueDate: assignmentData.due_date,
      weight: assignmentData.weight,
      allowLate: assignmentData.allow_late,
      allowResubmit: assignmentData.allow_resubmit,
      status: assignmentData.status as 'published' | 'closed',
      createdAt: assignmentData.created_at,
      submission: userSubmission
        ? {
            id: userSubmission.id,
            submissionText: userSubmission.submission_text,
            submissionLink: userSubmission.submission_link,
            submittedAt: userSubmission.submitted_at,
            isLate: userSubmission.is_late,
            score: userSubmission.score,
            feedback: userSubmission.feedback,
            status: userSubmission.status,
            gradedAt: userSubmission.graded_at,
          }
        : null,
      canSubmit,
    };

    return success(response);
  } catch (err) {
    return failure(
      500,
      assignmentsErrorCodes.invalidRequest,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

/**
 * 과제 최초 제출
 */
export const submitAssignment = async (
  supabase: SupabaseClient,
  learnerId: string,
  assignmentId: string,
  data: SubmitAssignmentRequest,
): Promise<HandlerResult<SubmitAssignmentResponse, AssignmentsServiceError>> => {
  try {
    // 1. 과제 정보 조회
    const { data: assignment, error: assignmentError } = await supabase
      .from('assignments')
      .select('id, course_id, status, due_date, allow_late')
      .eq('id', assignmentId)
      .single();

    if (assignmentError || !assignment) {
      return failure(
        404,
        assignmentsErrorCodes.assignmentNotFound,
        '과제를 찾을 수 없습니다.',
      );
    }

    // 2. 과제 상태 확인
    if (assignment.status !== 'published') {
      if (assignment.status === 'closed') {
        return failure(
          403,
          assignmentsErrorCodes.assignmentClosed,
          '마감된 과제입니다.',
        );
      }
      return failure(
        403,
        assignmentsErrorCodes.assignmentNotPublished,
        '제출할 수 없는 과제입니다.',
      );
    }

    // 3. 수강 등록 확인
    const isEnrolled = await checkEnrollment(supabase, learnerId, assignment.course_id);
    if (!isEnrolled) {
      return failure(
        403,
        assignmentsErrorCodes.notEnrolled,
        '수강 중인 코스가 아닙니다.',
      );
    }

    // 4. 이미 제출된 이력 확인
    const { data: existingSubmission } = await supabase
      .from('submissions')
      .select('id, status')
      .eq('assignment_id', assignmentId)
      .eq('learner_id', learnerId)
      .maybeSingle();

    if (existingSubmission) {
      return failure(
        409,
        assignmentsErrorCodes.alreadySubmitted,
        '이미 제출된 과제입니다.',
      );
    }

    // 5. 마감일 확인
    const now = new Date();
    const isPastDue = new Date(assignment.due_date) < now;

    if (isPastDue && !assignment.allow_late) {
      return failure(
        403,
        assignmentsErrorCodes.pastDueNotAllowed,
        '제출 기한이 지났습니다.',
      );
    }

    // 6. 제출 데이터 삽입
    const isLate = calculateIsLate(assignment.due_date, now);
    const submittedAt = now.toISOString();

    const { data: newSubmission, error: insertError } = await supabase
      .from('submissions')
      .insert({
        assignment_id: assignmentId,
        learner_id: learnerId,
        submission_text: data.submissionText,
        submission_link: data.submissionLink || null,
        is_late: isLate,
        status: 'submitted',
        submitted_at: submittedAt,
      })
      .select('id, status, is_late, submitted_at')
      .single();

    if (insertError || !newSubmission) {
      return failure(
        500,
        assignmentsErrorCodes.invalidRequest,
        '제출에 실패했습니다.',
      );
    }

    return success({
      submissionId: newSubmission.id,
      assignmentId,
      status: newSubmission.status as 'submitted' | 'graded' | 'resubmission_required',
      isLate: newSubmission.is_late,
      submittedAt: newSubmission.submitted_at,
      message: isLate ? '과제가 지각 제출되었습니다.' : '과제가 제출되었습니다.',
    });
  } catch (err) {
    return failure(
      500,
      assignmentsErrorCodes.invalidRequest,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

/**
 * 과제 재제출
 */
export const resubmitAssignment = async (
  supabase: SupabaseClient,
  learnerId: string,
  assignmentId: string,
  data: ResubmitAssignmentRequest,
): Promise<HandlerResult<SubmitAssignmentResponse, AssignmentsServiceError>> => {
  try {
    // 1. 과제 정보 조회
    const { data: assignment, error: assignmentError } = await supabase
      .from('assignments')
      .select('id, course_id, status, due_date, allow_late, allow_resubmit')
      .eq('id', assignmentId)
      .single();

    if (assignmentError || !assignment) {
      return failure(
        404,
        assignmentsErrorCodes.assignmentNotFound,
        '과제를 찾을 수 없습니다.',
      );
    }

    // 2. 과제 상태 확인
    if (assignment.status !== 'published') {
      if (assignment.status === 'closed') {
        return failure(
          403,
          assignmentsErrorCodes.assignmentClosed,
          '마감된 과제입니다.',
        );
      }
      return failure(
        403,
        assignmentsErrorCodes.assignmentNotPublished,
        '재제출할 수 없는 과제입니다.',
      );
    }

    // 3. 재제출 허용 확인
    if (!assignment.allow_resubmit) {
      return failure(
        403,
        assignmentsErrorCodes.resubmitNotAllowed,
        '이 과제는 재제출이 허용되지 않습니다.',
      );
    }

    // 4. 수강 등록 확인
    const isEnrolled = await checkEnrollment(supabase, learnerId, assignment.course_id);
    if (!isEnrolled) {
      return failure(
        403,
        assignmentsErrorCodes.notEnrolled,
        '수강 중인 코스가 아닙니다.',
      );
    }

    // 5. 기존 제출 이력 확인
    const { data: existingSubmission, error: submissionError } = await supabase
      .from('submissions')
      .select('id, status, is_late, submitted_at')
      .eq('assignment_id', assignmentId)
      .eq('learner_id', learnerId)
      .maybeSingle();

    if (submissionError) {
      return failure(
        500,
        assignmentsErrorCodes.invalidRequest,
        '제출 이력을 조회할 수 없습니다.',
      );
    }

    if (!existingSubmission) {
      return failure(
        404,
        assignmentsErrorCodes.submissionNotFound,
        '제출 이력이 없습니다.',
      );
    }

    if (existingSubmission.status !== 'resubmission_required') {
      return failure(
        403,
        assignmentsErrorCodes.submissionNotAllowed,
        '재제출이 요청되지 않은 과제입니다.',
      );
    }

    // 6. 마감일 확인 (재제출도 마감일 제약 적용)
    const now = new Date();
    const isPastDue = new Date(assignment.due_date) < now;

    if (isPastDue && !assignment.allow_late) {
      return failure(
        403,
        assignmentsErrorCodes.pastDueNotAllowed,
        '제출 기한이 지났습니다.',
      );
    }

    // 7. is_late 재계산: 최초 과제 due_date 기준
    // 최초 제출이 지각이었으면 재제출도 지각으로 유지
    const isLate = existingSubmission.is_late || calculateIsLate(assignment.due_date, now);
    const submittedAt = now.toISOString();

    // 8. 제출 데이터 업데이트
    const { data: updatedSubmission, error: updateError } = await supabase
      .from('submissions')
      .update({
        submission_text: data.submissionText,
        submission_link: data.submissionLink || null,
        is_late: isLate,
        status: 'submitted',
        submitted_at: submittedAt,
      })
      .eq('id', existingSubmission.id)
      .select('id, status, is_late, submitted_at')
      .single();

    if (updateError || !updatedSubmission) {
      return failure(
        500,
        assignmentsErrorCodes.invalidRequest,
        '재제출에 실패했습니다.',
      );
    }

    return success({
      submissionId: updatedSubmission.id,
      assignmentId,
      status: updatedSubmission.status as 'submitted' | 'graded' | 'resubmission_required',
      isLate: updatedSubmission.is_late,
      submittedAt: updatedSubmission.submitted_at,
      message: '과제가 재제출되었습니다.',
    });
  } catch (err) {
    return failure(
      500,
      assignmentsErrorCodes.invalidRequest,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

/**
 * Instructor 헬퍼: 코스 소유권 확인
 */
export const checkCourseOwnership = async (
  supabase: SupabaseClient,
  courseId: string,
  instructorId: string,
): Promise<boolean> => {
  const { data, error } = await supabase
    .from('courses')
    .select('id, instructor_id')
    .eq('id', courseId)
    .eq('instructor_id', instructorId)
    .maybeSingle();

  return !error && !!data;
};

/**
 * Instructor 헬퍼: 점수 비중 합계 계산
 */
export const calculateWeightSum = async (
  supabase: SupabaseClient,
  courseId: string,
  excludeAssignmentId?: string,
): Promise<number> => {
  let query = supabase
    .from('assignments')
    .select('weight')
    .eq('course_id', courseId)
    .in('status', ['draft', 'published', 'closed']);

  if (excludeAssignmentId) {
    query = query.neq('id', excludeAssignmentId);
  }

  const { data, error } = await query;

  if (error || !data) {
    return 0;
  }

  return data.reduce((sum, row) => sum + (row.weight || 0), 0);
};

/**
 * 강사용: 과제 생성
 */
export const createAssignment = async (
  supabase: SupabaseClient,
  instructorId: string,
  data: CreateAssignmentRequest,
): Promise<HandlerResult<CreateAssignmentResponse, AssignmentsServiceError>> => {
  try {
    const { data: course, error: courseError } = await supabase
      .from('courses')
      .select('id, instructor_id, title, status')
      .eq('id', data.courseId)
      .single();

    if (courseError || !course) {
      return failure(
        404,
        assignmentsErrorCodes.courseNotFound,
        '코스를 찾을 수 없습니다.',
      );
    }

    if (course.instructor_id !== instructorId) {
      return failure(403, assignmentsErrorCodes.notOwner, '권한이 없습니다.');
    }

    if (course.status === 'archived') {
      return failure(
        400,
        assignmentsErrorCodes.courseArchived,
        '보관된 코스에는 과제를 생성할 수 없습니다.',
      );
    }

    if (new Date(data.dueDate) <= new Date()) {
      return failure(
        400,
        assignmentsErrorCodes.invalidDueDate,
        '마감일은 현재 시점 이후로 설정해야 합니다.',
      );
    }

    const currentWeightSum = await calculateWeightSum(supabase, data.courseId);
    const newWeightSum = currentWeightSum + data.weight;

    let weightWarning: string | undefined;
    if (newWeightSum > 100) {
      weightWarning = `현재 코스의 과제 점수 비중 합계가 ${newWeightSum.toFixed(1)}%로 100%를 초과합니다.`;
    }

    const { data: assignment, error: createError } = await supabase
      .from('assignments')
      .insert({
        course_id: data.courseId,
        title: data.title,
        description: data.description,
        due_date: data.dueDate,
        weight: data.weight,
        allow_late: data.allowLate,
        allow_resubmit: data.allowResubmit,
        status: 'draft',
      })
      .select('id, title, status, course_id, created_at')
      .single();

    if (createError || !assignment) {
      return failure(
        500,
        assignmentsErrorCodes.createFailed,
        createError?.message || '과제 생성 중 오류가 발생했습니다.',
      );
    }

    return success(
      {
        assignmentId: assignment.id,
        title: assignment.title,
        status: assignment.status as 'draft' | 'published' | 'closed',
        courseId: assignment.course_id,
        createdAt: assignment.created_at,
        message: '과제가 성공적으로 임시 저장되었습니다.',
        weightWarning,
      },
      201,
    );
  } catch (err) {
    return failure(
      500,
      assignmentsErrorCodes.createFailed,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

/**
 * 강사용: 과제 수정
 */
export const updateAssignment = async (
  supabase: SupabaseClient,
  instructorId: string,
  assignmentId: string,
  data: UpdateAssignmentRequest,
): Promise<HandlerResult<UpdateAssignmentResponse, AssignmentsServiceError>> => {
  try {
    const { data: assignment, error: checkError } = await supabase
      .from('assignments')
      .select('id, course_id, status, title')
      .eq('id', assignmentId)
      .single();

    if (checkError || !assignment) {
      return failure(
        404,
        assignmentsErrorCodes.assignmentNotFound,
        '과제를 찾을 수 없습니다.',
      );
    }

    const isOwner = await checkCourseOwnership(
      supabase,
      assignment.course_id,
      instructorId,
    );

    if (!isOwner) {
      return failure(403, assignmentsErrorCodes.notOwner, '권한이 없습니다.');
    }

    const updateData: Record<string, unknown> = {};
    if (data.title !== undefined) updateData.title = data.title;
    if (data.description !== undefined) updateData.description = data.description;

    const { data: updated, error: updateError } = await supabase
      .from('assignments')
      .update(updateData)
      .eq('id', assignmentId)
      .select('id, title, updated_at')
      .single();

    if (updateError || !updated) {
      return failure(
        500,
        assignmentsErrorCodes.updateFailed,
        updateError?.message || '과제 수정 중 오류가 발생했습니다.',
      );
    }

    return success({
      assignmentId: updated.id,
      title: updated.title,
      updatedAt: updated.updated_at,
      message: '과제가 성공적으로 수정되었습니다.',
    });
  } catch (err) {
    return failure(
      500,
      assignmentsErrorCodes.updateFailed,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

/**
 * 강사용: 과제 게시
 */
export const publishAssignment = async (
  supabase: SupabaseClient,
  instructorId: string,
  assignmentId: string,
): Promise<HandlerResult<PublishAssignmentResponse, AssignmentsServiceError>> => {
  try {
    const { data: assignment, error: checkError } = await supabase
      .from('assignments')
      .select('id, course_id, status, title, description, due_date, weight')
      .eq('id', assignmentId)
      .single();

    if (checkError || !assignment) {
      return failure(
        404,
        assignmentsErrorCodes.assignmentNotFound,
        '과제를 찾을 수 없습니다.',
      );
    }

    const isOwner = await checkCourseOwnership(
      supabase,
      assignment.course_id,
      instructorId,
    );

    if (!isOwner) {
      return failure(403, assignmentsErrorCodes.notOwner, '권한이 없습니다.');
    }

    if (assignment.status !== 'draft') {
      return failure(
        400,
        assignmentsErrorCodes.publishFailed,
        '이미 게시된 과제입니다.',
      );
    }

    if (!assignment.title || !assignment.description || !assignment.due_date) {
      return failure(
        400,
        assignmentsErrorCodes.missingRequiredFields,
        '필수 정보를 모두 입력해주세요.',
      );
    }

    const { data: course, error: courseError } = await supabase
      .from('courses')
      .select('status')
      .eq('id', assignment.course_id)
      .single();

    if (courseError || !course) {
      return failure(
        404,
        assignmentsErrorCodes.courseNotFound,
        '코스를 찾을 수 없습니다.',
      );
    }

    if (course.status === 'archived') {
      return failure(
        400,
        assignmentsErrorCodes.courseArchived,
        '보관된 코스의 과제는 게시할 수 없습니다.',
      );
    }

    const { data: updated, error: updateError } = await supabase
      .from('assignments')
      .update({ status: 'published' })
      .eq('id', assignmentId)
      .select('id, status')
      .single();

    if (updateError || !updated) {
      return failure(
        500,
        assignmentsErrorCodes.publishFailed,
        updateError?.message || '과제 게시 중 오류가 발생했습니다.',
      );
    }

    return success({
      assignmentId: updated.id,
      status: 'published' as const,
      message: '과제가 게시되었습니다.',
    });
  } catch (err) {
    return failure(
      500,
      assignmentsErrorCodes.publishFailed,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

/**
 * 강사용: 과제 마감
 */
export const closeAssignment = async (
  supabase: SupabaseClient,
  instructorId: string,
  assignmentId: string,
): Promise<HandlerResult<CloseAssignmentResponse, AssignmentsServiceError>> => {
  try {
    const { data: assignment, error: checkError } = await supabase
      .from('assignments')
      .select('id, course_id, status')
      .eq('id', assignmentId)
      .single();

    if (checkError || !assignment) {
      return failure(
        404,
        assignmentsErrorCodes.assignmentNotFound,
        '과제를 찾을 수 없습니다.',
      );
    }

    const isOwner = await checkCourseOwnership(
      supabase,
      assignment.course_id,
      instructorId,
    );

    if (!isOwner) {
      return failure(403, assignmentsErrorCodes.notOwner, '권한이 없습니다.');
    }

    if (assignment.status !== 'published') {
      return failure(
        400,
        assignmentsErrorCodes.closeFailed,
        '게시된 과제만 마감할 수 있습니다.',
      );
    }

    const { data: updated, error: updateError } = await supabase
      .from('assignments')
      .update({ status: 'closed' })
      .eq('id', assignmentId)
      .select('id, status')
      .single();

    if (updateError || !updated) {
      return failure(
        500,
        assignmentsErrorCodes.closeFailed,
        updateError?.message || '과제 마감 중 오류가 발생했습니다.',
      );
    }

    return success({
      assignmentId: updated.id,
      status: 'closed' as const,
      message: '과제가 마감되었습니다.',
    });
  } catch (err) {
    return failure(
      500,
      assignmentsErrorCodes.closeFailed,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

/**
 * 강사용: 내 과제 목록 조회
 */
export const getMyAssignments = async (
  supabase: SupabaseClient,
  instructorId: string,
): Promise<HandlerResult<MyAssignmentsResponse, AssignmentsServiceError>> => {
  try {
    const { data: courses, error: coursesError } = await supabase
      .from('courses')
      .select('id')
      .eq('instructor_id', instructorId);

    if (coursesError) {
      return failure(500, assignmentsErrorCodes.invalidRequest, coursesError.message);
    }

    const courseIds = (courses || []).map((c) => c.id);

    if (courseIds.length === 0) {
      return success({
        assignments: [],
        total: 0,
      });
    }

    const { data: assignmentsData, error: assignmentsError, count } = await supabase
      .from('assignments')
      .select(
        `
        id,
        course_id,
        title,
        due_date,
        weight,
        status,
        created_at,
        courses!inner(title)
      `,
        { count: 'exact' },
      )
      .in('course_id', courseIds)
      .order('created_at', { ascending: false });

    if (assignmentsError) {
      return failure(
        500,
        assignmentsErrorCodes.invalidRequest,
        assignmentsError.message,
      );
    }

    const assignments = await Promise.all(
      (assignmentsData || []).map(async (row: any) => {
        const { data: submissionsData } = await supabase
          .from('submissions')
          .select('id, status')
          .eq('assignment_id', row.id);

        const submissionsCount = submissionsData?.length || 0;
        const gradedCount = submissionsData?.filter((s) => s.status === 'graded').length || 0;

        return {
          id: row.id,
          courseId: row.course_id,
          courseTitle: row.courses?.title || '',
          title: row.title,
          dueDate: row.due_date,
          weight: row.weight,
          status: row.status,
          submissionsCount,
          gradedCount,
          createdAt: row.created_at,
        };
      }),
    );

    return success({
      assignments,
      total: count || 0,
    });
  } catch (err) {
    return failure(
      500,
      assignmentsErrorCodes.invalidRequest,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

/**
 * 강사용: 제출물 목록 조회
 */
export const getAssignmentSubmissions = async (
  supabase: SupabaseClient,
  instructorId: string,
  assignmentId: string,
  filter: 'all' | 'ungraded' | 'late' | 'resubmission_required',
): Promise<HandlerResult<AssignmentSubmissionsResponse, AssignmentsServiceError>> => {
  try {
    const { data: assignment, error: assignmentError } = await supabase
      .from('assignments')
      .select('id, course_id, title')
      .eq('id', assignmentId)
      .single();

    if (assignmentError || !assignment) {
      return failure(
        404,
        assignmentsErrorCodes.assignmentNotFound,
        '과제를 찾을 수 없습니다.',
      );
    }

    const isOwner = await checkCourseOwnership(
      supabase,
      assignment.course_id,
      instructorId,
    );

    if (!isOwner) {
      return failure(403, assignmentsErrorCodes.notOwner, '권한이 없습니다.');
    }

    let query = supabase
      .from('submissions')
      .select(
        `
        id,
        learner_id,
        submission_text,
        submission_link,
        submitted_at,
        is_late,
        score,
        feedback,
        status,
        graded_at,
        profiles!submissions_learner_id_fkey(name)
      `,
        { count: 'exact' },
      )
      .eq('assignment_id', assignmentId);

    if (filter === 'ungraded') {
      query = query.eq('status', 'submitted');
    } else if (filter === 'late') {
      query = query.eq('is_late', true);
    } else if (filter === 'resubmission_required') {
      query = query.eq('status', 'resubmission_required');
    }

    query = query.order('submitted_at', { ascending: false });

    const { data, error, count } = await query;

    if (error) {
      return failure(500, assignmentsErrorCodes.invalidRequest, error.message);
    }

    const submissions: SubmissionItem[] = (data || []).map((row: any) => ({
      id: row.id,
      learnerId: row.learner_id,
      learnerName: row.profiles?.name || '',
      submissionText: row.submission_text,
      submissionLink: row.submission_link,
      submittedAt: row.submitted_at,
      isLate: row.is_late,
      score: row.score,
      feedback: row.feedback,
      status: row.status,
      gradedAt: row.graded_at,
    }));

    return success({
      assignmentId: assignment.id,
      assignmentTitle: assignment.title,
      submissions,
      total: count || 0,
    });
  } catch (err) {
    return failure(
      500,
      assignmentsErrorCodes.invalidRequest,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

/**
 * 강사용: 제출물 상세 조회
 */
export const getSubmissionDetail = async (
  supabase: SupabaseClient,
  instructorId: string,
  submissionId: string,
): Promise<HandlerResult<SubmissionDetailResponse, AssignmentsServiceError>> => {
  try {
    const { data: submission, error: submissionError } = await supabase
      .from('submissions')
      .select(
        `
        id,
        assignment_id,
        learner_id,
        submission_text,
        submission_link,
        submitted_at,
        is_late,
        score,
        feedback,
        status,
        graded_at,
        assignments!inner(
          id,
          title,
          due_date,
          allow_resubmit,
          course_id
        ),
        profiles!submissions_learner_id_fkey(name)
      `,
      )
      .eq('id', submissionId)
      .single();

    if (submissionError || !submission) {
      return failure(
        404,
        assignmentsErrorCodes.submissionNotFound,
        '제출물을 찾을 수 없습니다.',
      );
    }

    const assignment = submission.assignments as any;
    const isOwner = await checkCourseOwnership(
      supabase,
      assignment.course_id,
      instructorId,
    );

    if (!isOwner) {
      return failure(403, assignmentsErrorCodes.notOwner, '권한이 없습니다.');
    }

    const profile = submission.profiles as any;

    return success({
      id: submission.id,
      assignmentId: submission.assignment_id,
      assignmentTitle: assignment.title,
      assignmentDueDate: assignment.due_date,
      assignmentAllowResubmit: assignment.allow_resubmit,
      learnerId: submission.learner_id,
      learnerName: profile?.name || '',
      submissionText: submission.submission_text,
      submissionLink: submission.submission_link,
      submittedAt: submission.submitted_at,
      isLate: submission.is_late,
      score: submission.score,
      feedback: submission.feedback,
      status: submission.status as 'submitted' | 'graded' | 'resubmission_required',
      gradedAt: submission.graded_at,
    });
  } catch (err) {
    return failure(
      500,
      assignmentsErrorCodes.invalidRequest,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

/**
 * 강사용: 채점 완료
 */
export const gradeSubmission = async (
  supabase: SupabaseClient,
  instructorId: string,
  submissionId: string,
  data: GradeSubmissionRequest,
): Promise<HandlerResult<GradeSubmissionResponse, AssignmentsServiceError>> => {
  try {
    const { data: submission, error: submissionError } = await supabase
      .from('submissions')
      .select(
        `
        id,
        assignment_id,
        learner_id,
        status,
        assignments!inner(
          id,
          course_id
        )
      `,
      )
      .eq('id', submissionId)
      .single();

    if (submissionError || !submission) {
      return failure(
        404,
        assignmentsErrorCodes.submissionNotFound,
        '제출물을 찾을 수 없습니다.',
      );
    }

    const assignment = submission.assignments as any;
    const isOwner = await checkCourseOwnership(
      supabase,
      assignment.course_id,
      instructorId,
    );

    if (!isOwner) {
      return failure(403, assignmentsErrorCodes.notOwner, '권한이 없습니다.');
    }

    if (submission.learner_id === instructorId) {
      return failure(
        403,
        assignmentsErrorCodes.cannotGradeOwnSubmission,
        '본인의 제출물은 채점할 수 없습니다.',
      );
    }

    if (data.score < 0 || data.score > 100) {
      return failure(
        400,
        assignmentsErrorCodes.invalidScore,
        '점수는 0에서 100 사이의 값이어야 합니다.',
      );
    }

    if (!data.feedback || data.feedback.trim().length === 0) {
      return failure(
        400,
        assignmentsErrorCodes.feedbackRequired,
        '피드백은 필수 입력 항목입니다.',
      );
    }

    const now = new Date().toISOString();
    const { data: updated, error: updateError } = await supabase
      .from('submissions')
      .update({
        score: data.score,
        feedback: data.feedback,
        status: 'graded',
        graded_at: now,
      })
      .eq('id', submissionId)
      .select('id, assignment_id, status, score, graded_at')
      .single();

    if (updateError || !updated) {
      return failure(
        500,
        assignmentsErrorCodes.gradeFailed,
        updateError?.message || '채점 중 오류가 발생했습니다.',
      );
    }

    return success({
      submissionId: updated.id,
      assignmentId: updated.assignment_id,
      status: 'graded' as const,
      score: updated.score as number,
      gradedAt: updated.graded_at as string,
      message: '채점이 완료되었습니다.',
    });
  } catch (err) {
    return failure(
      500,
      assignmentsErrorCodes.gradeFailed,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

/**
 * 강사용: 재제출 요청
 */
export const requestResubmission = async (
  supabase: SupabaseClient,
  instructorId: string,
  submissionId: string,
  data: RequestResubmissionRequest,
): Promise<HandlerResult<RequestResubmissionResponse, AssignmentsServiceError>> => {
  try {
    const { data: submission, error: submissionError } = await supabase
      .from('submissions')
      .select(
        `
        id,
        assignment_id,
        learner_id,
        status,
        assignments!inner(
          id,
          course_id,
          allow_resubmit
        )
      `,
      )
      .eq('id', submissionId)
      .single();

    if (submissionError || !submission) {
      return failure(
        404,
        assignmentsErrorCodes.submissionNotFound,
        '제출물을 찾을 수 없습니다.',
      );
    }

    const assignment = submission.assignments as any;
    const isOwner = await checkCourseOwnership(
      supabase,
      assignment.course_id,
      instructorId,
    );

    if (!isOwner) {
      return failure(403, assignmentsErrorCodes.notOwner, '권한이 없습니다.');
    }

    if (submission.learner_id === instructorId) {
      return failure(
        403,
        assignmentsErrorCodes.cannotGradeOwnSubmission,
        '본인의 제출물에는 재제출을 요청할 수 없습니다.',
      );
    }

    if (!assignment.allow_resubmit) {
      return failure(
        403,
        assignmentsErrorCodes.resubmitNotAllowedForAssignment,
        '이 과제는 재제출이 허용되지 않습니다.',
      );
    }

    if (!data.feedback || data.feedback.trim().length === 0) {
      return failure(
        400,
        assignmentsErrorCodes.feedbackRequired,
        '피드백은 필수 입력 항목입니다.',
      );
    }

    if (data.score !== undefined && data.score !== null) {
      if (data.score < 0 || data.score > 100) {
        return failure(
          400,
          assignmentsErrorCodes.invalidScore,
          '점수는 0에서 100 사이의 값이어야 합니다.',
        );
      }
    }

    const now = new Date().toISOString();
    const updateData: any = {
      feedback: data.feedback,
      status: 'resubmission_required',
      graded_at: now,
    };

    if (data.score !== undefined && data.score !== null) {
      updateData.score = data.score;
    }

    const { data: updated, error: updateError } = await supabase
      .from('submissions')
      .update(updateData)
      .eq('id', submissionId)
      .select('id, assignment_id, status, score, graded_at')
      .single();

    if (updateError || !updated) {
      return failure(
        500,
        assignmentsErrorCodes.requestResubmissionFailed,
        updateError?.message || '재제출 요청 중 오류가 발생했습니다.',
      );
    }

    return success({
      submissionId: updated.id,
      assignmentId: updated.assignment_id,
      status: 'resubmission_required' as const,
      score: updated.score,
      gradedAt: updated.graded_at as string,
      message: '재제출 요청이 완료되었습니다.',
    });
  } catch (err) {
    return failure(
      500,
      assignmentsErrorCodes.requestResubmissionFailed,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};
