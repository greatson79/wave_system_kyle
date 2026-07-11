import type { SupabaseClient } from '@supabase/supabase-js';
import type { HandlerResult } from '@/backend/http/response';
import { success, failure } from '@/backend/http/response';
import { coursesErrorCodes, type CoursesServiceError } from './error';
import type {
  CourseListQuery,
  CourseListResponse,
  CourseDetailResponse,
  EnrollResponse,
  EnrollmentStatusResponse,
  CreateCourseRequest,
  CreateCourseResponse,
  UpdateCourseRequest,
  UpdateCourseResponse,
  UpdateCourseStatusResponse,
  MyCourseItem,
  MyCoursesResponse,
  InstructorCourseDetailResponse,
  MyEnrolledCoursesResponse,
} from './schema';

type CourseRowJoined = {
  id: string;
  title: string;
  description: string;
  curriculum: string | null;
  enrollments_count: number;
  status: string;
  created_at: string;
  updated_at: string;
  instructor_id: string;
  instructor_name: string;
  category_id: string;
  category_name: string;
  difficulty_id: string;
  difficulty_name: string;
  difficulty_level: number;
};

export const getCourses = async (
  supabase: SupabaseClient,
  query: CourseListQuery,
): Promise<HandlerResult<CourseListResponse, CoursesServiceError>> => {
  try {
    let queryBuilder = supabase
      .from('courses')
      .select(
        `
        id,
        title,
        description,
        enrollments_count,
        status,
        created_at,
        instructor_id,
        profiles!courses_instructor_id_fkey(name),
        category_id,
        categories(name),
        difficulty_id,
        difficulty_levels(name, level)
      `,
        { count: 'exact' },
      )
      .eq('status', 'published');

    if (query.search) {
      queryBuilder = queryBuilder.or(
        `title.ilike.%${query.search}%,description.ilike.%${query.search}%`,
      );
    }

    if (query.categoryId) {
      queryBuilder = queryBuilder.eq('category_id', query.categoryId);
    }

    if (query.difficultyId) {
      queryBuilder = queryBuilder.eq('difficulty_id', query.difficultyId);
    }

    if (query.sort === 'popular') {
      queryBuilder = queryBuilder.order('enrollments_count', {
        ascending: false,
      });
    } else {
      queryBuilder = queryBuilder.order('created_at', { ascending: false });
    }

    queryBuilder = queryBuilder.range(
      query.offset,
      query.offset + query.limit - 1,
    );

    const { data, error, count } = await queryBuilder;

    if (error) {
      return failure(500, coursesErrorCodes.invalidRequest, error.message);
    }

    const courses = (data || []).map((row: any) => ({
      id: row.id,
      title: row.title,
      description: row.description,
      instructor: {
        id: row.instructor_id,
        name: row.profiles?.name || '',
      },
      category: {
        id: row.category_id,
        name: row.categories?.name || '',
      },
      difficulty: {
        id: row.difficulty_id,
        name: row.difficulty_levels?.name || '',
        level: row.difficulty_levels?.level || 0,
      },
      enrollmentsCount: row.enrollments_count,
      status: 'published' as const,
      createdAt: row.created_at,
    }));

    return success({
      courses,
      total: count || 0,
      limit: query.limit,
      offset: query.offset,
    });
  } catch (err) {
    return failure(
      500,
      coursesErrorCodes.invalidRequest,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

export const getCourseDetail = async (
  supabase: SupabaseClient,
  courseId: string,
): Promise<HandlerResult<CourseDetailResponse, CoursesServiceError>> => {
  try {
    const { data, error } = await supabase
      .from('courses')
      .select(
        `
        id,
        title,
        description,
        curriculum,
        enrollments_count,
        status,
        created_at,
        updated_at,
        instructor_id,
        profiles!courses_instructor_id_fkey(name),
        category_id,
        categories(name),
        difficulty_id,
        difficulty_levels(name, level)
      `,
      )
      .eq('id', courseId)
      .eq('status', 'published')
      .single();

    if (error || !data) {
      return failure(404, coursesErrorCodes.courseNotFound, '코스를 찾을 수 없습니다.');
    }

    if (data.status !== 'published') {
      return failure(
        400,
        coursesErrorCodes.courseNotPublished,
        '이 코스는 공개되지 않았습니다.',
      );
    }

    const course: CourseDetailResponse = {
      id: data.id,
      title: data.title,
      description: data.description,
      curriculum: data.curriculum,
      instructor: {
        id: data.instructor_id,
        name: (data.profiles as any)?.name || '',
      },
      category: {
        id: data.category_id,
        name: (data.categories as any)?.name || '',
      },
      difficulty: {
        id: data.difficulty_id,
        name: (data.difficulty_levels as any)?.name || '',
        level: (data.difficulty_levels as any)?.level || 0,
      },
      enrollmentsCount: data.enrollments_count,
      status: 'published' as const,
      createdAt: data.created_at,
      updatedAt: data.updated_at,
    };

    return success(course);
  } catch (err) {
    return failure(
      500,
      coursesErrorCodes.invalidRequest,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

export const enrollCourse = async (
  supabase: SupabaseClient,
  learnerId: string,
  courseId: string,
): Promise<HandlerResult<EnrollResponse, CoursesServiceError>> => {
  try {
    const { data: course, error: courseError } = await supabase
      .from('courses')
      .select('id, status')
      .eq('id', courseId)
      .single();

    if (courseError || !course) {
      return failure(404, coursesErrorCodes.courseNotFound, '코스를 찾을 수 없습니다.');
    }

    if (course.status !== 'published') {
      return failure(
        400,
        coursesErrorCodes.courseNotPublished,
        '이 코스는 더 이상 신청할 수 없습니다.',
      );
    }

    const { data: existingEnrollment, error: checkError } = await supabase
      .from('enrollments')
      .select('id, cancelled_at')
      .eq('learner_id', learnerId)
      .eq('course_id', courseId)
      .maybeSingle();

    if (checkError) {
      return failure(
        500,
        coursesErrorCodes.enrollmentFailed,
        checkError.message,
      );
    }

    if (existingEnrollment && !existingEnrollment.cancelled_at) {
      return failure(
        409,
        coursesErrorCodes.alreadyEnrolled,
        '이미 수강 중인 코스입니다.',
      );
    }

    const enrolledAt = new Date().toISOString();

    const { data: enrollment, error: enrollError } = await supabase
      .from('enrollments')
      .insert({
        learner_id: learnerId,
        course_id: courseId,
        enrolled_at: enrolledAt,
      })
      .select('enrolled_at')
      .single();

    if (enrollError) {
      return failure(
        500,
        coursesErrorCodes.enrollmentFailed,
        enrollError.message,
      );
    }

    // enrollments_count 업데이트: 조회 → 계산 → 업데이트 패턴 적용
    type CountRow = { enrollments_count: number | null };
    const {
      data: beforeCountRow,
      error: beforeCountError,
    } = await supabase
      .from('courses')
      .select('enrollments_count')
      .eq('id', courseId)
      .single();

    if (beforeCountError || !beforeCountRow) {
      return failure(
        500,
        coursesErrorCodes.enrollmentFailed,
        beforeCountError?.message ?? '카운터 조회에 실패했습니다.',
      );
    }

    const current = (
      (beforeCountRow as unknown as CountRow).enrollments_count ?? 0
    ) as number;
    const next = current + 1;

    const { error: updateError } = await supabase
      .from('courses')
      .update({ enrollments_count: next })
      .eq('id', courseId);

    if (updateError) {
      return failure(
        500,
        coursesErrorCodes.enrollmentFailed,
        updateError.message,
      );
    }

    return success(
      {
        enrolled: true,
        courseId,
        enrolledAt: enrollment.enrolled_at,
      },
      201,
    );
  } catch (err) {
    return failure(
      500,
      coursesErrorCodes.enrollmentFailed,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

export const unenrollCourse = async (
  supabase: SupabaseClient,
  learnerId: string,
  courseId: string,
): Promise<HandlerResult<void, CoursesServiceError>> => {
  try {
    const { data: enrollment, error: checkError } = await supabase
      .from('enrollments')
      .select('id, cancelled_at')
      .eq('learner_id', learnerId)
      .eq('course_id', courseId)
      .is('cancelled_at', null)
      .maybeSingle();

    if (checkError) {
      return failure(
        500,
        coursesErrorCodes.unenrollmentFailed,
        checkError.message,
      );
    }

    if (!enrollment) {
      return failure(
        400,
        coursesErrorCodes.notEnrolled,
        '수강 중인 코스가 아닙니다.',
      );
    }

    const { error: updateError } = await supabase
      .from('enrollments')
      .update({
        cancelled_at: new Date().toISOString(),
      })
      .eq('id', enrollment.id);

    if (updateError) {
      return failure(
        500,
        coursesErrorCodes.unenrollmentFailed,
        updateError.message,
      );
    }

    // enrollments_count 감소: 조회 → 계산 → 업데이트 패턴 적용
    type CountRow = { enrollments_count: number | null };
    const {
      data: beforeCountRow,
      error: beforeCountError,
    } = await supabase
      .from('courses')
      .select('enrollments_count')
      .eq('id', courseId)
      .single();

    if (beforeCountError || !beforeCountRow) {
      return failure(
        500,
        coursesErrorCodes.unenrollmentFailed,
        beforeCountError?.message ?? '카운터 조회에 실패했습니다.',
      );
    }

    const current = (
      (beforeCountRow as unknown as CountRow).enrollments_count ?? 0
    ) as number;
    const next = Math.max(0, current - 1);

    const { error: decrementError } = await supabase
      .from('courses')
      .update({ enrollments_count: next })
      .eq('id', courseId);

    if (decrementError) {
      return failure(
        500,
        coursesErrorCodes.unenrollmentFailed,
        decrementError.message,
      );
    }

    return success(undefined);
  } catch (err) {
    return failure(
      500,
      coursesErrorCodes.unenrollmentFailed,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

export const getEnrollmentStatus = async (
  supabase: SupabaseClient,
  learnerId: string,
  courseId: string,
): Promise<HandlerResult<EnrollmentStatusResponse, CoursesServiceError>> => {
  try {
    const { data, error } = await supabase
      .from('enrollments')
      .select('enrolled_at, cancelled_at')
      .eq('learner_id', learnerId)
      .eq('course_id', courseId)
      .maybeSingle();

    if (error) {
      return failure(500, coursesErrorCodes.invalidRequest, error.message);
    }

    if (!data) {
      return success({
        enrolled: false,
        enrolledAt: null,
        cancelledAt: null,
      });
    }

    return success({
      enrolled: !data.cancelled_at,
      enrolledAt: data.enrolled_at,
      cancelledAt: data.cancelled_at,
    });
  } catch (err) {
    return failure(
      500,
      coursesErrorCodes.invalidRequest,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

// Instructor 코스 관리 Service

export const createCourse = async (
  supabase: SupabaseClient,
  instructorId: string,
  data: CreateCourseRequest,
): Promise<HandlerResult<CreateCourseResponse, CoursesServiceError>> => {
  try {
    // 1. 카테고리 활성 상태 확인
    const { data: category, error: categoryError } = await supabase
      .from('categories')
      .select('id, is_active')
      .eq('id', data.categoryId)
      .single();

    if (categoryError || !category) {
      return failure(
        404,
        coursesErrorCodes.categoryNotFound,
        '선택한 카테고리를 찾을 수 없습니다.',
      );
    }

    if (!category.is_active) {
      return failure(
        400,
        coursesErrorCodes.categoryInactive,
        '선택한 카테고리는 더 이상 사용할 수 없습니다.',
      );
    }

    // 2. 난이도 활성 상태 확인
    const { data: difficulty, error: difficultyError } = await supabase
      .from('difficulty_levels')
      .select('id, is_active')
      .eq('id', data.difficultyId)
      .single();

    if (difficultyError || !difficulty) {
      return failure(
        404,
        coursesErrorCodes.difficultyNotFound,
        '선택한 난이도를 찾을 수 없습니다.',
      );
    }

    if (!difficulty.is_active) {
      return failure(
        400,
        coursesErrorCodes.difficultyInactive,
        '선택한 난이도는 더 이상 사용할 수 없습니다.',
      );
    }

    // 3. 코스 생성
    const { data: course, error: createError } = await supabase
      .from('courses')
      .insert({
        instructor_id: instructorId,
        category_id: data.categoryId,
        difficulty_id: data.difficultyId,
        title: data.title,
        description: data.description,
        curriculum: data.curriculum || null,
        status: 'draft',
        enrollments_count: 0,
      })
      .select('id, title, status, created_at')
      .single();

    if (createError || !course) {
      return failure(
        500,
        coursesErrorCodes.createFailed,
        createError?.message || '코스 생성 중 오류가 발생했습니다.',
      );
    }

    return success(
      {
        courseId: course.id,
        title: course.title,
        status: course.status as 'draft' | 'published' | 'archived',
        createdAt: course.created_at,
        message: '코스가 성공적으로 생성되었습니다.',
      },
      201,
    );
  } catch (err) {
    return failure(
      500,
      coursesErrorCodes.createFailed,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

export const updateCourse = async (
  supabase: SupabaseClient,
  instructorId: string,
  courseId: string,
  data: UpdateCourseRequest,
): Promise<HandlerResult<UpdateCourseResponse, CoursesServiceError>> => {
  try {
    // 1. 코스 소유자 확인
    const { data: course, error: checkError } = await supabase
      .from('courses')
      .select('id, instructor_id, title')
      .eq('id', courseId)
      .single();

    if (checkError || !course) {
      return failure(404, coursesErrorCodes.courseNotFound, '코스를 찾을 수 없습니다.');
    }

    if (course.instructor_id !== instructorId) {
      return failure(403, coursesErrorCodes.notOwner, '권한이 없습니다.');
    }

    // 2. 카테고리 변경 시 활성 상태 확인
    if (data.categoryId) {
      const { data: category, error: categoryError } = await supabase
        .from('categories')
        .select('id, is_active')
        .eq('id', data.categoryId)
        .single();

      if (categoryError || !category) {
        return failure(
          404,
          coursesErrorCodes.categoryNotFound,
          '선택한 카테고리를 찾을 수 없습니다.',
        );
      }

      if (!category.is_active) {
        return failure(
          400,
          coursesErrorCodes.categoryInactive,
          '선택한 카테고리는 더 이상 사용할 수 없습니다.',
        );
      }
    }

    // 3. 난이도 변경 시 활성 상태 확인
    if (data.difficultyId) {
      const { data: difficulty, error: difficultyError } = await supabase
        .from('difficulty_levels')
        .select('id, is_active')
        .eq('id', data.difficultyId)
        .single();

      if (difficultyError || !difficulty) {
        return failure(
          404,
          coursesErrorCodes.difficultyNotFound,
          '선택한 난이도를 찾을 수 없습니다.',
        );
      }

      if (!difficulty.is_active) {
        return failure(
          400,
          coursesErrorCodes.difficultyInactive,
          '선택한 난이도는 더 이상 사용할 수 없습니다.',
        );
      }
    }

    // 4. 코스 업데이트
    const updateData: Record<string, unknown> = {};
    if (data.title !== undefined) updateData.title = data.title;
    if (data.description !== undefined) updateData.description = data.description;
    if (data.categoryId !== undefined) updateData.category_id = data.categoryId;
    if (data.difficultyId !== undefined) updateData.difficulty_id = data.difficultyId;
    if (data.curriculum !== undefined) updateData.curriculum = data.curriculum;

    const { data: updated, error: updateError } = await supabase
      .from('courses')
      .update(updateData)
      .eq('id', courseId)
      .select('id, title, updated_at')
      .single();

    if (updateError || !updated) {
      return failure(
        500,
        coursesErrorCodes.updateFailed,
        updateError?.message || '코스 수정 중 오류가 발생했습니다.',
      );
    }

    return success({
      courseId: updated.id,
      title: updated.title,
      updatedAt: updated.updated_at,
      message: '코스가 성공적으로 수정되었습니다.',
    });
  } catch (err) {
    return failure(
      500,
      coursesErrorCodes.updateFailed,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

export const updateCourseStatus = async (
  supabase: SupabaseClient,
  instructorId: string,
  courseId: string,
  newStatus: 'draft' | 'published' | 'archived',
): Promise<HandlerResult<UpdateCourseStatusResponse, CoursesServiceError>> => {
  try {
    // 1. 코스 소유자 및 현재 상태 확인
    const { data: course, error: checkError } = await supabase
      .from('courses')
      .select('id, instructor_id, status')
      .eq('id', courseId)
      .single();

    if (checkError || !course) {
      return failure(404, coursesErrorCodes.courseNotFound, '코스를 찾을 수 없습니다.');
    }

    if (course.instructor_id !== instructorId) {
      return failure(403, coursesErrorCodes.notOwner, '권한이 없습니다.');
    }

    // 2. 상태 전환 가능 여부 확인
    if (course.status === 'archived') {
      return failure(
        400,
        coursesErrorCodes.cannotReactivate,
        '보관된 코스는 다시 활성화할 수 없습니다. 새 코스를 생성해주세요.',
      );
    }

    // 3. published → archived 전환 시 과제 일괄 마감
    let archivedAssignmentsCount = 0;
    if (course.status === 'published' && newStatus === 'archived') {
      // 3-1. 코스의 published 상태 과제 조회
      const { data: publishedAssignments, error: assignmentsError } = await supabase
        .from('assignments')
        .select('id')
        .eq('course_id', courseId)
        .eq('status', 'published');

      if (assignmentsError) {
        return failure(
          500,
          coursesErrorCodes.assignmentsUpdateFailed,
          assignmentsError.message,
        );
      }

      archivedAssignmentsCount = publishedAssignments?.length || 0;

      // 3-2. 과제들 상태 일괄 변경 (published → closed)
      if (archivedAssignmentsCount > 0) {
        const { error: closeError } = await supabase
          .from('assignments')
          .update({ status: 'closed' })
          .eq('course_id', courseId)
          .eq('status', 'published');

        if (closeError) {
          return failure(
            500,
            coursesErrorCodes.assignmentsUpdateFailed,
            closeError.message,
          );
        }
      }
    }

    // 4. 코스 상태 업데이트
    const { data: updated, error: updateError } = await supabase
      .from('courses')
      .update({ status: newStatus })
      .eq('id', courseId)
      .select('id, status')
      .single();

    if (updateError || !updated) {
      return failure(
        500,
        coursesErrorCodes.statusUpdateFailed,
        updateError?.message || '코스 상태 변경 중 오류가 발생했습니다.',
      );
    }

    const messages = {
      draft: '코스가 초안 상태로 변경되었습니다.',
      published: '코스가 게시되었습니다.',
      archived: `코스가 보관되었습니다.${archivedAssignmentsCount > 0 ? ` ${archivedAssignmentsCount}개의 과제가 마감되었습니다.` : ''}`,
    };

    return success({
      courseId: updated.id,
      status: updated.status as 'draft' | 'published' | 'archived',
      archivedAssignmentsCount: newStatus === 'archived' ? archivedAssignmentsCount : undefined,
      message: messages[newStatus],
    });
  } catch (err) {
    return failure(
      500,
      coursesErrorCodes.statusUpdateFailed,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

export const getMyCourses = async (
  supabase: SupabaseClient,
  instructorId: string,
): Promise<HandlerResult<MyCoursesResponse, CoursesServiceError>> => {
  try {
    const { data, error, count } = await supabase
      .from('courses')
      .select(
        `
        id,
        title,
        description,
        status,
        enrollments_count,
        created_at,
        updated_at,
        category_id,
        categories(name),
        difficulty_id,
        difficulty_levels(name, level)
      `,
        { count: 'exact' },
      )
      .eq('instructor_id', instructorId)
      .order('created_at', { ascending: false });

    if (error) {
      return failure(500, coursesErrorCodes.invalidRequest, error.message);
    }

    const courses: MyCourseItem[] = (data || []).map((row: any) => ({
      id: row.id,
      title: row.title,
      description: row.description,
      status: row.status,
      enrollmentsCount: row.enrollments_count,
      createdAt: row.created_at,
      updatedAt: row.updated_at,
      category: {
        id: row.category_id,
        name: row.categories?.name || '',
      },
      difficulty: {
        id: row.difficulty_id,
        name: row.difficulty_levels?.name || '',
        level: row.difficulty_levels?.level || 0,
      },
    }));

    return success({
      courses,
      total: count || 0,
    });
  } catch (err) {
    return failure(
      500,
      coursesErrorCodes.invalidRequest,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

export const getInstructorCourseDetail = async (
  supabase: SupabaseClient,
  instructorId: string,
  courseId: string,
): Promise<HandlerResult<InstructorCourseDetailResponse, CoursesServiceError>> => {
  try {
    const { data, error } = await supabase
      .from('courses')
      .select(
        `
        id,
        title,
        description,
        curriculum,
        status,
        enrollments_count,
        created_at,
        updated_at,
        category_id,
        categories(name),
        difficulty_id,
        difficulty_levels(name, level)
      `,
      )
      .eq('id', courseId)
      .eq('instructor_id', instructorId)
      .single();

    if (error || !data) {
      return failure(404, coursesErrorCodes.courseNotFound, '코스를 찾을 수 없습니다.');
    }

    const course: InstructorCourseDetailResponse = {
      id: data.id,
      title: data.title,
      description: data.description,
      curriculum: data.curriculum,
      status: data.status as 'draft' | 'published' | 'archived',
      enrollmentsCount: data.enrollments_count,
      createdAt: data.created_at,
      updatedAt: data.updated_at,
      category: {
        id: data.category_id,
        name: (data.categories as any)?.name || '',
      },
      difficulty: {
        id: data.difficulty_id,
        name: (data.difficulty_levels as any)?.name || '',
        level: (data.difficulty_levels as any)?.level || 0,
      },
    };

    return success(course);
  } catch (err) {
    return failure(
      500,
      coursesErrorCodes.invalidRequest,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

// Learner: 수강 중인 코스 목록 조회
export const getMyEnrolledCourses = async (
  supabase: SupabaseClient,
  userId: string,
): Promise<HandlerResult<MyEnrolledCoursesResponse, CoursesServiceError>> => {
  try {
    // 1. 수강 중인 코스 조회 (enrollments + courses 조인)
    const { data: enrollments, error: enrollError } = await supabase
      .from('enrollments')
      .select(`
        id,
        enrolled_at,
        course_id,
        courses (
          id,
          title,
          description,
          categories (name),
          difficulty_levels (name),
          profiles (name)
        )
      `)
      .eq('learner_id', userId)
      .is('cancelled_at', null)
      .order('enrolled_at', { ascending: false });

    if (enrollError) {
      return failure(500, coursesErrorCodes.databaseError, '수강 중인 코스 조회에 실패했습니다.');
    }

    if (!enrollments || enrollments.length === 0) {
      return success({ courses: [] });
    }

    // 2. 각 코스의 과제 진행률 계산
    const coursesWithProgress = await Promise.all(
      enrollments.map(async (enrollment) => {
        const courseId = enrollment.course_id;

        // 전체 과제 수 조회
        const { data: assignments } = await supabase
          .from('assignments')
          .select('id')
          .eq('course_id', courseId)
          .eq('status', 'published');

        const totalAssignments = assignments?.length || 0;

        // 완료한 과제 수 조회 (제출 + 채점완료)
        const { data: submissions } = await supabase
          .from('submissions')
          .select('assignment_id')
          .eq('learner_id', userId)
          .in('status', ['graded', 'resubmission_required']);

        const completedAssignmentIds = new Set(submissions?.map(s => s.assignment_id) || []);
        const completedAssignments = completedAssignmentIds.size;

        const progress = totalAssignments > 0
          ? Math.round((completedAssignments / totalAssignments) * 100)
          : 0;

        const course = enrollment.courses as any;
        const category = course.categories as any;
        const difficulty = course.difficulty_levels as any;
        const instructor = course.profiles as any;

        return {
          enrollmentId: enrollment.id,
          courseId: course.id,
          courseTitle: course.title,
          courseDescription: course.description,
          categoryName: category?.name || '',
          difficultyName: difficulty?.name || '',
          instructorName: instructor?.name || '',
          enrolledAt: enrollment.enrolled_at,
          progress,
          totalAssignments,
          completedAssignments,
        };
      })
    );

    return success({ courses: coursesWithProgress });
  } catch (error) {
    return failure(500, coursesErrorCodes.unknown, '알 수 없는 오류가 발생했습니다.');
  }
};
