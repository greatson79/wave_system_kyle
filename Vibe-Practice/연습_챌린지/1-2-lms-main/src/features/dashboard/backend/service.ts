import type { SupabaseClient } from '@supabase/supabase-js';
import type { HandlerResult } from '@/backend/http/response';
import { success, failure } from '@/backend/http/response';
import { dashboardErrorCodes, type DashboardServiceError } from './error';
import type {
  LearnerDashboardResponse,
  CourseProgress,
  DueAssignment,
  RecentFeedback,
  InstructorDashboardResponse,
  MyCourseItem,
  RecentSubmissionItem,
} from './schema';

const HOURS_FOR_DUE_FILTER = 72;
const MAX_RECENT_FEEDBACK = 3;

export const getLearnerDashboard = async (
  supabase: SupabaseClient,
  learnerId: string,
): Promise<HandlerResult<LearnerDashboardResponse, DashboardServiceError>> => {
  try {
    const { data: enrollments, error: enrollmentsError } = await supabase
      .from('enrollments')
      .select(
        `
        id,
        course_id,
        courses!inner(id, title, status)
      `,
      )
      .eq('learner_id', learnerId)
      .is('cancelled_at', null);

    if (enrollmentsError) {
      return failure(
        500,
        dashboardErrorCodes.fetchError,
        `수강 목록을 가져오는 중 오류가 발생했습니다: ${enrollmentsError.message}`,
      );
    }

    if (!enrollments || enrollments.length === 0) {
      return success({
        courses: [],
        dueAssignments: [],
        recentFeedback: [],
      });
    }

    const publishedEnrollments = (enrollments as any[]).filter((e: any) => {
      const course = e.courses as { id: string; title: string; status: string } | null;
      return course?.status === 'published';
    });

    if (publishedEnrollments.length === 0) {
      return success({
        courses: [],
        dueAssignments: [],
        recentFeedback: [],
      });
    }

    const courseIds = publishedEnrollments.map((e: any) => e.course_id);

    const { data: assignments, error: assignmentsError } = await supabase
      .from('assignments')
      .select('*')
      .in('course_id', courseIds)
      .eq('status', 'published');

    if (assignmentsError) {
      return failure(
        500,
        dashboardErrorCodes.fetchError,
        `과제 목록을 가져오는 중 오류가 발생했습니다: ${assignmentsError.message}`,
      );
    }

    const { data: submissions, error: submissionsError } = await supabase
      .from('submissions')
      .select('*')
      .eq('learner_id', learnerId);

    if (submissionsError) {
      return failure(
        500,
        dashboardErrorCodes.fetchError,
        `제출 목록을 가져오는 중 오류가 발생했습니다: ${submissionsError.message}`,
      );
    }

    const courses: CourseProgress[] = publishedEnrollments.map((e: any) => {
      const course = e.courses as { id: string; title: string; status: string };
      const courseAssignments =
        assignments?.filter((a: any) => a.course_id === course.id) || [];
      const courseSubmissions =
        submissions?.filter((s: any) => {
          const assignmentIds = courseAssignments.map((a: any) => a.id);
          return assignmentIds.includes(s.assignment_id);
        }) || [];

      const totalAssignments = courseAssignments.length;
      const completedAssignments = courseSubmissions.filter(
        (s: any) => s.status === 'graded',
      ).length;

      const progress =
        totalAssignments > 0
          ? parseFloat(((completedAssignments / totalAssignments) * 100).toFixed(1))
          : 0.0;

      return {
        courseId: course.id,
        courseTitle: course.title,
        progress,
        totalAssignments,
        completedAssignments,
      };
    });

    const now = new Date();
    const dueThreshold = new Date(
      now.getTime() + HOURS_FOR_DUE_FILTER * 60 * 60 * 1000,
    );

    const submittedAssignmentIds = new Set(
      submissions?.map((s: any) => s.assignment_id) || [],
    );

    const dueAssignments: DueAssignment[] = (assignments || [])
      .filter((a: any) => {
        if (submittedAssignmentIds.has(a.id)) return false;
        const dueDate = new Date(a.due_date);
        return dueDate >= now && dueDate <= dueThreshold;
      })
      .map((a: any) => {
        const dueDate = new Date(a.due_date);
        const hoursRemaining = (dueDate.getTime() - now.getTime()) / (1000 * 60 * 60);
        const enrollment = publishedEnrollments.find(
          (e: any) => e.course_id === a.course_id,
        );
        const course = enrollment?.courses as { id: string; title: string; status: string } | undefined;
        const courseTitle = course?.title || '';

        return {
          assignmentId: a.id,
          courseId: a.course_id,
          courseTitle,
          assignmentTitle: a.title,
          dueDate: a.due_date,
          hoursRemaining: parseFloat(hoursRemaining.toFixed(1)),
        };
      })
      .sort((a, b) => a.hoursRemaining - b.hoursRemaining);

    const gradedSubmissions = (submissions || [])
      .filter((s: any) => s.status === 'graded' && s.graded_at && s.feedback)
      .sort(
        (a: any, b: any) =>
          new Date(b.graded_at).getTime() - new Date(a.graded_at).getTime(),
      )
      .slice(0, MAX_RECENT_FEEDBACK);

    const recentFeedback: RecentFeedback[] = gradedSubmissions.map((s: any) => {
      const assignment = assignments?.find((a: any) => a.id === s.assignment_id);
      const enrollment = publishedEnrollments.find(
        (e: any) => e.course_id === assignment?.course_id,
      );
      const course = enrollment?.courses as { id: string; title: string; status: string } | undefined;
      const courseTitle = course?.title || '';

      return {
        submissionId: s.id,
        assignmentId: s.assignment_id,
        assignmentTitle: assignment?.title || '',
        courseTitle,
        feedback: s.feedback || '',
        score: s.score,
        gradedAt: s.graded_at,
      };
    });

    return success({
      courses,
      dueAssignments,
      recentFeedback,
    });
  } catch (err) {
    return failure(
      500,
      dashboardErrorCodes.fetchError,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

const MAX_RECENT_SUBMISSIONS = 10;

export const getInstructorDashboard = async (
  supabase: SupabaseClient,
  instructorId: string,
): Promise<HandlerResult<InstructorDashboardResponse, DashboardServiceError>> => {
  try {
    const { data: courses, error: coursesError } = await supabase
      .from('courses')
      .select('id, title, status, enrollments_count, created_at')
      .eq('instructor_id', instructorId)
      .order('created_at', { ascending: false });

    if (coursesError) {
      return failure(
        500,
        dashboardErrorCodes.fetchError,
        `코스 목록을 가져오는 중 오류가 발생했습니다: ${coursesError.message}`,
      );
    }

    if (!courses || courses.length === 0) {
      return success({
        courses: [],
        pendingGradingCount: 0,
        recentSubmissions: [],
      });
    }

    const courseIds = courses.map((c: any) => c.id);

    const { data: assignmentsData, error: assignmentsError } = await supabase
      .from('assignments')
      .select('id')
      .in('course_id', courseIds);

    if (assignmentsError) {
      return failure(
        500,
        dashboardErrorCodes.fetchError,
        `과제 목록을 가져오는 중 오류가 발생했습니다: ${assignmentsError.message}`,
      );
    }

    const assignmentIds = (assignmentsData || []).map((a: any) => a.id);

    let pendingGradingCount = 0;
    if (assignmentIds.length > 0) {
      const { data: pendingSubmissions, error: pendingError } = await supabase
        .from('submissions')
        .select('id')
        .eq('status', 'submitted')
        .in('assignment_id', assignmentIds);

      if (pendingError) {
        return failure(
          500,
          dashboardErrorCodes.fetchError,
          `채점 대기 수를 계산하는 중 오류가 발생했습니다: ${pendingError.message}`,
        );
      }

      pendingGradingCount = pendingSubmissions?.length || 0;
    }

    let recentSubmissionsData: any[] = [];
    if (assignmentIds.length > 0) {
      const { data, error: submissionsError } = await supabase
        .from('submissions')
        .select(
          `
          id,
          assignment_id,
          learner_id,
          status,
          submitted_at,
          is_late,
          assignments!inner(id, title, course_id),
          profiles!inner(id, name)
        `,
        )
        .in('assignment_id', assignmentIds)
        .order('submitted_at', { ascending: false })
        .limit(MAX_RECENT_SUBMISSIONS);

      if (submissionsError) {
        return failure(
          500,
          dashboardErrorCodes.fetchError,
          `최근 제출물을 가져오는 중 오류가 발생했습니다: ${submissionsError.message}`,
        );
      }

      recentSubmissionsData = data || [];
    }

    const myCourses: MyCourseItem[] = courses.map((c: any) => ({
      courseId: c.id,
      courseTitle: c.title,
      status: c.status,
      enrollmentsCount: c.enrollments_count || 0,
      createdAt: c.created_at,
    }));

    const recentSubmissions: RecentSubmissionItem[] = recentSubmissionsData.map(
      (s: any) => {
        const assignment = s.assignments;
        const profile = s.profiles;
        const course = courses.find((c: any) => c.id === assignment.course_id);

        return {
          submissionId: s.id,
          assignmentId: assignment.id,
          assignmentTitle: assignment.title,
          courseId: assignment.course_id,
          courseTitle: course?.title || '',
          learnerName: profile?.name || 'Unknown',
          status: s.status,
          submittedAt: s.submitted_at,
          isLate: s.is_late,
        };
      },
    );

    return success({
      courses: myCourses,
      pendingGradingCount,
      recentSubmissions,
    });
  } catch (err) {
    return failure(
      500,
      dashboardErrorCodes.fetchError,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};
