import type { Hono } from 'hono';
import { failure, respond } from '@/backend/http/response';
import {
  getLogger,
  getSupabase,
  type AppEnv,
} from '@/backend/hono/context';
import {
  CourseListQuerySchema,
  CreateCourseRequestSchema,
  UpdateCourseRequestSchema,
  UpdateCourseStatusRequestSchema,
} from './schema';
import {
  getCourses,
  getCourseDetail,
  enrollCourse,
  unenrollCourse,
  getEnrollmentStatus,
  createCourse,
  updateCourse,
  updateCourseStatus,
  getMyCourses,
  getInstructorCourseDetail,
  getMyEnrolledCourses,
} from './service';
import { coursesErrorCodes } from './error';

export const registerCoursesRoutes = (app: Hono<AppEnv>) => {
  app.get('/api/courses', async (c) => {
    const logger = getLogger(c);
    logger.info('Get courses request received at /api/courses');

    const query = c.req.query();
    const parsedQuery = CourseListQuerySchema.safeParse(query);

    if (!parsedQuery.success) {
      return respond(
        c,
        failure(
          400,
          coursesErrorCodes.invalidRequest,
          '쿼리 파라미터가 올바르지 않습니다.',
          parsedQuery.error.format(),
        ),
      );
    }

    const supabase = getSupabase(c);
    const result = await getCourses(supabase, parsedQuery.data);

    return respond(c, result);
  });

  app.get('/api/courses/:id', async (c) => {
    const logger = getLogger(c);
    const courseId = c.req.param('id');
    logger.info(`Get course detail request received for course ${courseId}`);

    const supabase = getSupabase(c);
    const result = await getCourseDetail(supabase, courseId);

    return respond(c, result);
  });

  app.post('/api/courses/:id/enroll', async (c) => {
    const logger = getLogger(c);
    const courseId = c.req.param('id');
    logger.info(`Enroll request received for course ${courseId}`);

    const userId = c.req.header('x-user-id');
    if (!userId) {
      return respond(
        c,
        failure(401, coursesErrorCodes.unauthorized, '인증이 필요합니다.'),
      );
    }

    const supabase = getSupabase(c);
    const result = await enrollCourse(supabase, userId, courseId);

    return respond(c, result);
  });

  app.delete('/api/courses/:id/enroll', async (c) => {
    const logger = getLogger(c);
    const courseId = c.req.param('id');
    logger.info(`Unenroll request received for course ${courseId}`);

    const userId = c.req.header('x-user-id');
    if (!userId) {
      return respond(
        c,
        failure(401, coursesErrorCodes.unauthorized, '인증이 필요합니다.'),
      );
    }

    const supabase = getSupabase(c);
    const result = await unenrollCourse(supabase, userId, courseId);

    return respond(c, result);
  });

  app.get('/api/courses/:id/enrollment', async (c) => {
    const logger = getLogger(c);
    const courseId = c.req.param('id');
    logger.info(`Get enrollment status request for course ${courseId}`);

    const userId = c.req.header('x-user-id');
    if (!userId) {
      return respond(
        c,
        failure(401, coursesErrorCodes.unauthorized, '인증이 필요합니다.'),
      );
    }

    const supabase = getSupabase(c);
    const result = await getEnrollmentStatus(supabase, userId, courseId);

    return respond(c, result);
  });

  // Instructor: 코스 생성
  app.post('/api/instructor/courses', async (c) => {
    const logger = getLogger(c);
    logger.info('Create course request received');

    const userId = c.req.header('x-user-id');
    if (!userId) {
      return respond(
        c,
        failure(401, coursesErrorCodes.unauthorized, '인증이 필요합니다.'),
      );
    }

    const body = await c.req.json();
    const parsed = CreateCourseRequestSchema.safeParse(body);

    if (!parsed.success) {
      return respond(
        c,
        failure(
          400,
          coursesErrorCodes.invalidRequest,
          '요청 데이터가 올바르지 않습니다.',
          parsed.error.format(),
        ),
      );
    }

    const supabase = getSupabase(c);
    const result = await createCourse(supabase, userId, parsed.data);

    return respond(c, result);
  });

  // Instructor: 내 코스 목록 조회
  app.get('/api/instructor/courses', async (c) => {
    const logger = getLogger(c);
    logger.info('Get my courses request received');

    const userId = c.req.header('x-user-id');
    if (!userId) {
      return respond(
        c,
        failure(401, coursesErrorCodes.unauthorized, '인증이 필요합니다.'),
      );
    }

    const supabase = getSupabase(c);
    const result = await getMyCourses(supabase, userId);

    return respond(c, result);
  });

  // Instructor: 내 코스 상세 조회
  app.get('/api/instructor/courses/:id', async (c) => {
    const logger = getLogger(c);
    const courseId = c.req.param('id');
    logger.info(`Get instructor course detail request received for ${courseId}`);

    const userId = c.req.header('x-user-id');
    if (!userId) {
      return respond(
        c,
        failure(401, coursesErrorCodes.unauthorized, '인증이 필요합니다.'),
      );
    }

    const supabase = getSupabase(c);
    const result = await getInstructorCourseDetail(supabase, userId, courseId);

    return respond(c, result);
  });

  // Instructor: 코스 수정
  app.patch('/api/instructor/courses/:id', async (c) => {
    const logger = getLogger(c);
    const courseId = c.req.param('id');
    logger.info(`Update course request received for ${courseId}`);

    const userId = c.req.header('x-user-id');
    if (!userId) {
      return respond(
        c,
        failure(401, coursesErrorCodes.unauthorized, '인증이 필요합니다.'),
      );
    }

    const body = await c.req.json();
    const parsed = UpdateCourseRequestSchema.safeParse(body);

    if (!parsed.success) {
      return respond(
        c,
        failure(
          400,
          coursesErrorCodes.invalidRequest,
          '요청 데이터가 올바르지 않습니다.',
          parsed.error.format(),
        ),
      );
    }

    const supabase = getSupabase(c);
    const result = await updateCourse(supabase, userId, courseId, parsed.data);

    return respond(c, result);
  });

  // Instructor: 코스 상태 전환
  app.patch('/api/instructor/courses/:id/status', async (c) => {
    const logger = getLogger(c);
    const courseId = c.req.param('id');
    logger.info(`Update course status request received for ${courseId}`);

    const userId = c.req.header('x-user-id');
    if (!userId) {
      return respond(
        c,
        failure(401, coursesErrorCodes.unauthorized, '인증이 필요합니다.'),
      );
    }

    const body = await c.req.json();
    const parsed = UpdateCourseStatusRequestSchema.safeParse(body);

    if (!parsed.success) {
      return respond(
        c,
        failure(
          400,
          coursesErrorCodes.invalidRequest,
          '요청 데이터가 올바르지 않습니다.',
          parsed.error.format(),
        ),
      );
    }

    const supabase = getSupabase(c);
    const result = await updateCourseStatus(
      supabase,
      userId,
      courseId,
      parsed.data.status,
    );

    return respond(c, result);
  });

  // Learner: 수강 중인 코스 목록 조회
  app.get('/api/learner/courses/enrolled', async (c) => {
    const logger = getLogger(c);
    logger.info('Get my enrolled courses request received');

    const userId = c.req.header('x-user-id');
    if (!userId) {
      return respond(
        c,
        failure(401, coursesErrorCodes.unauthorized, '인증이 필요합니다.'),
      );
    }

    const supabase = getSupabase(c);
    const result = await getMyEnrolledCourses(supabase, userId);

    return respond(c, result);
  });
};
