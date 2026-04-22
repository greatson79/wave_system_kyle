import type { SupabaseClient } from '@supabase/supabase-js';
import type { HandlerResult } from '@/backend/http/response';
import { success, failure } from '@/backend/http/response';
import { gradesErrorCodes, type GradesServiceError } from './error';
import type { CourseGradesResponse, GradeItem } from './schema';
import { calculateTotalScore, calculateAverageScore } from '../lib/grade-calculator';

/**
 * 헬퍼: 학습자가 특정 코스에 수강 등록되어 있는지 확인
 */
const checkEnrollment = async (
  supabase: SupabaseClient,
  learnerId: string,
  courseId: string,
): Promise<{ enrolled: boolean; cancelled: boolean }> => {
  const { data, error } = await supabase
    .from('enrollments')
    .select('id, cancelled_at')
    .eq('learner_id', learnerId)
    .eq('course_id', courseId)
    .maybeSingle();

  if (error || !data) {
    return { enrolled: false, cancelled: false };
  }

  // cancelled_at이 NULL이 아니면 취소된 수강
  if (data.cancelled_at !== null) {
    return { enrolled: true, cancelled: true };
  }

  return { enrolled: true, cancelled: false };
};

/**
 * 특정 코스의 학습자 성적 조회
 */
export const getCourseGrades = async (
  supabase: SupabaseClient,
  learnerId: string,
  courseId: string,
): Promise<HandlerResult<CourseGradesResponse, GradesServiceError>> => {
  try {
    // 1. 수강 등록 확인
    const enrollmentStatus = await checkEnrollment(supabase, learnerId, courseId);

    if (!enrollmentStatus.enrolled) {
      return failure(
        403,
        gradesErrorCodes.notEnrolled,
        '수강 중인 코스가 아닙니다.',
      );
    }

    if (enrollmentStatus.cancelled) {
      return failure(
        403,
        gradesErrorCodes.enrollmentCancelled,
        '수강 취소된 코스입니다.',
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
        gradesErrorCodes.courseNotFound,
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
        submissions!left(
          id,
          submitted_at,
          is_late,
          status,
          score,
          feedback,
          graded_at,
          learner_id
        )
      `,
      )
      .eq('course_id', courseId)
      .in('status', ['published', 'closed'])
      .order('due_date', { ascending: true });

    if (assignmentsError) {
      return failure(
        500,
        gradesErrorCodes.invalidRequest,
        assignmentsError.message,
      );
    }

    // 4. 응답 데이터 매핑
    const grades: GradeItem[] = (assignmentsData || []).map((row: any) => {
      const submissions = row.submissions || [];
      const userSubmission = submissions.find(
        (s: any) => s !== null && s.learner_id === learnerId,
      );

      let submissionStatus: 'not_submitted' | 'submitted' | 'graded' | 'resubmission_required' = 'not_submitted';
      if (userSubmission) {
        submissionStatus = userSubmission.status;
      }

      return {
        assignmentId: row.id,
        assignmentTitle: row.title,
        dueDate: row.due_date,
        weight: row.weight,
        submittedAt: userSubmission?.submitted_at || null,
        isLate: userSubmission?.is_late || null,
        status: submissionStatus,
        score: userSubmission?.score || null,
        feedback: userSubmission?.feedback || null,
        gradedAt: userSubmission?.graded_at || null,
      };
    });

    // 5. 성적 요약 계산
    const totalAssignments = grades.length;
    const gradedAssignments = grades.filter((g) => g.status === 'graded').length;
    const totalScore = calculateTotalScore(grades);
    const averageScore = calculateAverageScore(grades);

    return success({
      courseId: course.id,
      courseTitle: course.title,
      grades,
      summary: {
        totalAssignments,
        gradedAssignments,
        totalScore,
        averageScore,
      },
    });
  } catch (err) {
    return failure(
      500,
      gradesErrorCodes.invalidRequest,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};
