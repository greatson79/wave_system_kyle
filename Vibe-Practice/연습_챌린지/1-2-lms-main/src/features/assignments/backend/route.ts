import type { Hono } from 'hono';
import { failure, respond } from '@/backend/http/response';
import {
  getLogger,
  getSupabase,
  type AppEnv,
} from '@/backend/hono/context';
import {
  getCourseAssignments,
  getAssignmentDetail,
  submitAssignment,
  resubmitAssignment,
  createAssignment,
  updateAssignment,
  publishAssignment,
  closeAssignment,
  getMyAssignments,
  getAssignmentSubmissions,
  getSubmissionDetail,
  gradeSubmission,
  requestResubmission,
} from './service';
import { assignmentsErrorCodes } from './error';
import {
  SubmitAssignmentRequestSchema,
  ResubmitAssignmentRequestSchema,
  CreateAssignmentRequestSchema,
  UpdateAssignmentRequestSchema,
  SubmissionsQuerySchema,
  GradeSubmissionRequestSchema,
  RequestResubmissionRequestSchema,
} from './schema';

export const registerAssignmentsRoutes = (app: Hono<AppEnv>) => {
  app.get('/api/courses/:courseId/assignments', async (c) => {
    const logger = getLogger(c);
    const courseId = c.req.param('courseId');
    logger.info(`Get course assignments request received for course ${courseId}`);

    const userId = c.req.header('x-user-id');
    if (!userId) {
      return respond(
        c,
        failure(401, assignmentsErrorCodes.unauthorized, '인증이 필요합니다.'),
      );
    }

    const supabase = getSupabase(c);
    const result = await getCourseAssignments(supabase, userId, courseId);

    return respond(c, result);
  });

  app.get('/api/assignments/:assignmentId', async (c) => {
    const logger = getLogger(c);
    const assignmentId = c.req.param('assignmentId');
    logger.info(`Get assignment detail request received for assignment ${assignmentId}`);

    const userId = c.req.header('x-user-id');
    if (!userId) {
      return respond(
        c,
        failure(401, assignmentsErrorCodes.unauthorized, '인증이 필요합니다.'),
      );
    }

    const supabase = getSupabase(c);
    const result = await getAssignmentDetail(supabase, userId, assignmentId);

    return respond(c, result);
  });

  app.post('/api/assignments/:assignmentId/submit', async (c) => {
    const logger = getLogger(c);
    const assignmentId = c.req.param('assignmentId');
    logger.info(`Submit assignment request received for assignment ${assignmentId}`);

    const userId = c.req.header('x-user-id');
    if (!userId) {
      return respond(
        c,
        failure(401, assignmentsErrorCodes.unauthorized, '인증이 필요합니다.'),
      );
    }

    let body;
    try {
      body = await c.req.json();
    } catch {
      return respond(
        c,
        failure(400, assignmentsErrorCodes.invalidRequest, '잘못된 요청입니다.'),
      );
    }

    const parsed = SubmitAssignmentRequestSchema.safeParse(body);
    if (!parsed.success) {
      const errorMessage = parsed.error.errors[0]?.message || '잘못된 요청입니다.';
      return respond(
        c,
        failure(400, assignmentsErrorCodes.invalidRequest, errorMessage),
      );
    }

    const supabase = getSupabase(c);
    const result = await submitAssignment(supabase, userId, assignmentId, parsed.data);

    return respond(c, result);
  });

  app.patch('/api/assignments/:assignmentId/submit', async (c) => {
    const logger = getLogger(c);
    const assignmentId = c.req.param('assignmentId');
    logger.info(`Resubmit assignment request received for assignment ${assignmentId}`);

    const userId = c.req.header('x-user-id');
    if (!userId) {
      return respond(
        c,
        failure(401, assignmentsErrorCodes.unauthorized, '인증이 필요합니다.'),
      );
    }

    let body;
    try {
      body = await c.req.json();
    } catch {
      return respond(
        c,
        failure(400, assignmentsErrorCodes.invalidRequest, '잘못된 요청입니다.'),
      );
    }

    const parsed = ResubmitAssignmentRequestSchema.safeParse(body);
    if (!parsed.success) {
      const errorMessage = parsed.error.errors[0]?.message || '잘못된 요청입니다.';
      return respond(
        c,
        failure(400, assignmentsErrorCodes.invalidRequest, errorMessage),
      );
    }

    const supabase = getSupabase(c);
    const result = await resubmitAssignment(supabase, userId, assignmentId, parsed.data);

    return respond(c, result);
  });

  // Instructor 라우트
  app.post('/api/instructor/assignments', async (c) => {
    const logger = getLogger(c);
    logger.info('Create assignment request received');

    const userId = c.req.header('x-user-id');
    if (!userId) {
      return respond(
        c,
        failure(401, assignmentsErrorCodes.unauthorized, '인증이 필요합니다.'),
      );
    }

    let body;
    try {
      body = await c.req.json();
    } catch {
      return respond(
        c,
        failure(400, assignmentsErrorCodes.invalidRequest, '잘못된 요청입니다.'),
      );
    }

    const parsed = CreateAssignmentRequestSchema.safeParse(body);
    if (!parsed.success) {
      const errorMessage = parsed.error.errors[0]?.message || '잘못된 요청입니다.';
      return respond(
        c,
        failure(400, assignmentsErrorCodes.invalidRequest, errorMessage),
      );
    }

    const supabase = getSupabase(c);
    const result = await createAssignment(supabase, userId, parsed.data);

    return respond(c, result);
  });

  app.get('/api/instructor/assignments', async (c) => {
    const logger = getLogger(c);
    logger.info('Get my assignments request received');

    const userId = c.req.header('x-user-id');
    if (!userId) {
      return respond(
        c,
        failure(401, assignmentsErrorCodes.unauthorized, '인증이 필요합니다.'),
      );
    }

    const supabase = getSupabase(c);
    const result = await getMyAssignments(supabase, userId);

    return respond(c, result);
  });

  app.patch('/api/instructor/assignments/:id', async (c) => {
    const logger = getLogger(c);
    const assignmentId = c.req.param('id');
    logger.info(`Update assignment request received for assignment ${assignmentId}`);

    const userId = c.req.header('x-user-id');
    if (!userId) {
      return respond(
        c,
        failure(401, assignmentsErrorCodes.unauthorized, '인증이 필요합니다.'),
      );
    }

    let body;
    try {
      body = await c.req.json();
    } catch {
      return respond(
        c,
        failure(400, assignmentsErrorCodes.invalidRequest, '잘못된 요청입니다.'),
      );
    }

    const parsed = UpdateAssignmentRequestSchema.safeParse(body);
    if (!parsed.success) {
      const errorMessage = parsed.error.errors[0]?.message || '잘못된 요청입니다.';
      return respond(
        c,
        failure(400, assignmentsErrorCodes.invalidRequest, errorMessage),
      );
    }

    const supabase = getSupabase(c);
    const result = await updateAssignment(supabase, userId, assignmentId, parsed.data);

    return respond(c, result);
  });

  app.patch('/api/instructor/assignments/:id/publish', async (c) => {
    const logger = getLogger(c);
    const assignmentId = c.req.param('id');
    logger.info(`Publish assignment request received for assignment ${assignmentId}`);

    const userId = c.req.header('x-user-id');
    if (!userId) {
      return respond(
        c,
        failure(401, assignmentsErrorCodes.unauthorized, '인증이 필요합니다.'),
      );
    }

    const supabase = getSupabase(c);
    const result = await publishAssignment(supabase, userId, assignmentId);

    return respond(c, result);
  });

  app.patch('/api/instructor/assignments/:id/close', async (c) => {
    const logger = getLogger(c);
    const assignmentId = c.req.param('id');
    logger.info(`Close assignment request received for assignment ${assignmentId}`);

    const userId = c.req.header('x-user-id');
    if (!userId) {
      return respond(
        c,
        failure(401, assignmentsErrorCodes.unauthorized, '인증이 필요합니다.'),
      );
    }

    const supabase = getSupabase(c);
    const result = await closeAssignment(supabase, userId, assignmentId);

    return respond(c, result);
  });

  app.get('/api/instructor/assignments/:id/submissions', async (c) => {
    const logger = getLogger(c);
    const assignmentId = c.req.param('id');
    logger.info(`Get assignment submissions request received for assignment ${assignmentId}`);

    const userId = c.req.header('x-user-id');
    if (!userId) {
      return respond(
        c,
        failure(401, assignmentsErrorCodes.unauthorized, '인증이 필요합니다.'),
      );
    }

    const query = c.req.query();
    const parsed = SubmissionsQuerySchema.safeParse(query);
    const filter = parsed.success ? parsed.data.filter : 'all';

    const supabase = getSupabase(c);
    const result = await getAssignmentSubmissions(supabase, userId, assignmentId, filter);

    return respond(c, result);
  });

  app.get('/api/instructor/submissions/:id', async (c) => {
    const logger = getLogger(c);
    const submissionId = c.req.param('id');
    logger.info(`Get submission detail request received for submission ${submissionId}`);

    const userId = c.req.header('x-user-id');
    if (!userId) {
      return respond(
        c,
        failure(401, assignmentsErrorCodes.unauthorized, '인증이 필요합니다.'),
      );
    }

    const supabase = getSupabase(c);
    const result = await getSubmissionDetail(supabase, userId, submissionId);

    return respond(c, result);
  });

  app.patch('/api/instructor/submissions/:id/grade', async (c) => {
    const logger = getLogger(c);
    const submissionId = c.req.param('id');
    logger.info(`Grade submission request received for submission ${submissionId}`);

    const userId = c.req.header('x-user-id');
    if (!userId) {
      return respond(
        c,
        failure(401, assignmentsErrorCodes.unauthorized, '인증이 필요합니다.'),
      );
    }

    let body;
    try {
      body = await c.req.json();
    } catch {
      return respond(
        c,
        failure(400, assignmentsErrorCodes.invalidRequest, '잘못된 요청입니다.'),
      );
    }

    const parsed = GradeSubmissionRequestSchema.safeParse(body);
    if (!parsed.success) {
      const errorMessage = parsed.error.errors[0]?.message || '잘못된 요청입니다.';
      return respond(
        c,
        failure(400, assignmentsErrorCodes.invalidRequest, errorMessage),
      );
    }

    const supabase = getSupabase(c);
    const result = await gradeSubmission(supabase, userId, submissionId, parsed.data);

    return respond(c, result);
  });

  app.patch('/api/instructor/submissions/:id/request-resubmission', async (c) => {
    const logger = getLogger(c);
    const submissionId = c.req.param('id');
    logger.info(`Request resubmission request received for submission ${submissionId}`);

    const userId = c.req.header('x-user-id');
    if (!userId) {
      return respond(
        c,
        failure(401, assignmentsErrorCodes.unauthorized, '인증이 필요합니다.'),
      );
    }

    let body;
    try {
      body = await c.req.json();
    } catch {
      return respond(
        c,
        failure(400, assignmentsErrorCodes.invalidRequest, '잘못된 요청입니다.'),
      );
    }

    const parsed = RequestResubmissionRequestSchema.safeParse(body);
    if (!parsed.success) {
      const errorMessage = parsed.error.errors[0]?.message || '잘못된 요청입니다.';
      return respond(
        c,
        failure(400, assignmentsErrorCodes.invalidRequest, errorMessage),
      );
    }

    const supabase = getSupabase(c);
    const result = await requestResubmission(supabase, userId, submissionId, parsed.data);

    return respond(c, result);
  });
};
