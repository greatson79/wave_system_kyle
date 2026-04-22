import { z } from 'zod';

// DB 매핑용 스키마
export const AssignmentRowSchema = z.object({
  id: z.string().uuid(),
  course_id: z.string().uuid(),
  title: z.string(),
  description: z.string(),
  due_date: z.string(),
  weight: z.number(),
  allow_late: z.boolean(),
  allow_resubmit: z.boolean(),
  status: z.enum(['draft', 'published', 'closed']),
  created_at: z.string(),
  updated_at: z.string(),
});

export const SubmissionRowSchema = z.object({
  id: z.string().uuid(),
  assignment_id: z.string().uuid(),
  learner_id: z.string().uuid(),
  submission_text: z.string(),
  submission_link: z.string().nullable(),
  submission_file_url: z.string().nullable(),
  is_late: z.boolean(),
  score: z.number().nullable(),
  feedback: z.string().nullable(),
  status: z.enum(['submitted', 'graded', 'resubmission_required']),
  submitted_at: z.string(),
  graded_at: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
});

// API 응답용 스키마
export const AssignmentItemSchema = z.object({
  id: z.string().uuid(),
  title: z.string(),
  dueDate: z.string(),
  weight: z.number(),
  status: z.enum(['published', 'closed']),
  submissionStatus: z.enum(['not_submitted', 'submitted', 'graded', 'resubmission_required']),
  submittedAt: z.string().nullable(),
  isLate: z.boolean().nullable(),
  score: z.number().nullable(),
});

export const AssignmentListResponseSchema = z.object({
  assignments: z.array(AssignmentItemSchema),
  courseId: z.string().uuid(),
  courseTitle: z.string(),
});

export const AssignmentDetailResponseSchema = z.object({
  id: z.string().uuid(),
  courseId: z.string().uuid(),
  courseTitle: z.string(),
  title: z.string(),
  description: z.string(),
  dueDate: z.string(),
  weight: z.number(),
  allowLate: z.boolean(),
  allowResubmit: z.boolean(),
  status: z.enum(['published', 'closed']),
  createdAt: z.string(),
  submission: z.object({
    id: z.string().uuid(),
    submissionText: z.string(),
    submissionLink: z.string().nullable(),
    submittedAt: z.string(),
    isLate: z.boolean(),
    score: z.number().nullable(),
    feedback: z.string().nullable(),
    status: z.enum(['submitted', 'graded', 'resubmission_required']),
    gradedAt: z.string().nullable(),
  }).nullable(),
  canSubmit: z.boolean(),
});

// 제출 요청 스키마
export const SubmitAssignmentRequestSchema = z.object({
  submissionText: z.string().min(1, '제출 텍스트는 필수 항목입니다.'),
  submissionLink: z.string().url('올바른 URL 형식을 입력해주세요.').optional().nullable(),
});

// 재제출 요청 스키마 (동일한 구조)
export const ResubmitAssignmentRequestSchema = SubmitAssignmentRequestSchema;

// 제출 응답 스키마
export const SubmitAssignmentResponseSchema = z.object({
  submissionId: z.string().uuid(),
  assignmentId: z.string().uuid(),
  status: z.enum(['submitted', 'graded', 'resubmission_required']),
  isLate: z.boolean(),
  submittedAt: z.string(),
  message: z.string(),
});

// Instructor용 스키마
export const CreateAssignmentRequestSchema = z.object({
  courseId: z.string().uuid('올바른 코스 ID를 선택해주세요.'),
  title: z.string().min(1, '제목은 필수 항목입니다.'),
  description: z.string().min(1, '설명은 필수 항목입니다.'),
  dueDate: z.string(),
  weight: z.number().min(0, '점수 비중은 0 이상이어야 합니다.').max(100, '점수 비중은 100 이하여야 합니다.'),
  allowLate: z.boolean(),
  allowResubmit: z.boolean(),
});

export const UpdateAssignmentRequestSchema = z.object({
  title: z.string().min(1, '제목은 필수 항목입니다.').optional(),
  description: z.string().min(1, '설명은 필수 항목입니다.').optional(),
});

export const PublishAssignmentResponseSchema = z.object({
  assignmentId: z.string().uuid(),
  status: z.literal('published'),
  message: z.string(),
});

export const CloseAssignmentResponseSchema = z.object({
  assignmentId: z.string().uuid(),
  status: z.literal('closed'),
  message: z.string(),
});

export const CreateAssignmentResponseSchema = z.object({
  assignmentId: z.string().uuid(),
  title: z.string(),
  status: z.enum(['draft', 'published', 'closed']),
  courseId: z.string().uuid(),
  createdAt: z.string(),
  message: z.string(),
  weightWarning: z.string().optional(),
});

export const UpdateAssignmentResponseSchema = z.object({
  assignmentId: z.string().uuid(),
  title: z.string(),
  updatedAt: z.string(),
  message: z.string(),
});

export const MyAssignmentItemSchema = z.object({
  id: z.string().uuid(),
  courseId: z.string().uuid(),
  courseTitle: z.string(),
  title: z.string(),
  dueDate: z.string(),
  weight: z.number(),
  status: z.enum(['draft', 'published', 'closed']),
  submissionsCount: z.number().int(),
  gradedCount: z.number().int(),
  createdAt: z.string(),
});

export const MyAssignmentsResponseSchema = z.object({
  assignments: z.array(MyAssignmentItemSchema),
  total: z.number().int(),
});

export const SubmissionItemSchema = z.object({
  id: z.string().uuid(),
  learnerId: z.string().uuid(),
  learnerName: z.string(),
  submissionText: z.string(),
  submissionLink: z.string().nullable(),
  submittedAt: z.string(),
  isLate: z.boolean(),
  score: z.number().nullable(),
  feedback: z.string().nullable(),
  status: z.enum(['submitted', 'graded', 'resubmission_required']),
  gradedAt: z.string().nullable(),
});

export const SubmissionsQuerySchema = z.object({
  filter: z.enum(['all', 'ungraded', 'late', 'resubmission_required']).optional().default('all'),
});

export const AssignmentSubmissionsResponseSchema = z.object({
  assignmentId: z.string().uuid(),
  assignmentTitle: z.string(),
  submissions: z.array(SubmissionItemSchema),
  total: z.number().int(),
});

// TypeScript 타입 추출
export type AssignmentRow = z.infer<typeof AssignmentRowSchema>;
export type SubmissionRow = z.infer<typeof SubmissionRowSchema>;
export type AssignmentItem = z.infer<typeof AssignmentItemSchema>;
export type AssignmentListResponse = z.infer<typeof AssignmentListResponseSchema>;
export type AssignmentDetailResponse = z.infer<typeof AssignmentDetailResponseSchema>;
export type SubmitAssignmentRequest = z.infer<typeof SubmitAssignmentRequestSchema>;
export type ResubmitAssignmentRequest = z.infer<typeof ResubmitAssignmentRequestSchema>;
export type SubmitAssignmentResponse = z.infer<typeof SubmitAssignmentResponseSchema>;

export type CreateAssignmentRequest = z.infer<typeof CreateAssignmentRequestSchema>;
export type UpdateAssignmentRequest = z.infer<typeof UpdateAssignmentRequestSchema>;
export type PublishAssignmentResponse = z.infer<typeof PublishAssignmentResponseSchema>;
export type CloseAssignmentResponse = z.infer<typeof CloseAssignmentResponseSchema>;
export type CreateAssignmentResponse = z.infer<typeof CreateAssignmentResponseSchema>;
export type UpdateAssignmentResponse = z.infer<typeof UpdateAssignmentResponseSchema>;
export type MyAssignmentItem = z.infer<typeof MyAssignmentItemSchema>;
export type MyAssignmentsResponse = z.infer<typeof MyAssignmentsResponseSchema>;
export type SubmissionItem = z.infer<typeof SubmissionItemSchema>;
export type SubmissionsQuery = z.infer<typeof SubmissionsQuerySchema>;
export type AssignmentSubmissionsResponse = z.infer<typeof AssignmentSubmissionsResponseSchema>;

// 채점 요청 스키마
export const GradeSubmissionRequestSchema = z.object({
  score: z.number()
    .min(0, '점수는 0 이상이어야 합니다.')
    .max(100, '점수는 100 이하여야 합니다.'),
  feedback: z.string().min(1, '피드백은 필수 항목입니다.'),
});

// 재제출 요청 스키마
export const RequestResubmissionRequestSchema = z.object({
  score: z.number()
    .min(0, '점수는 0 이상이어야 합니다.')
    .max(100, '점수는 100 이하여야 합니다.')
    .optional()
    .nullable(),
  feedback: z.string().min(1, '피드백은 필수 항목입니다.'),
});

// 채점 응답 스키마
export const GradeSubmissionResponseSchema = z.object({
  submissionId: z.string().uuid(),
  assignmentId: z.string().uuid(),
  status: z.literal('graded'),
  score: z.number(),
  gradedAt: z.string(),
  message: z.string(),
});

// 재제출 요청 응답 스키마
export const RequestResubmissionResponseSchema = z.object({
  submissionId: z.string().uuid(),
  assignmentId: z.string().uuid(),
  status: z.literal('resubmission_required'),
  score: z.number().nullable(),
  gradedAt: z.string(),
  message: z.string(),
});

// 제출물 상세 조회 응답 스키마 (강사용)
export const SubmissionDetailResponseSchema = z.object({
  id: z.string().uuid(),
  assignmentId: z.string().uuid(),
  assignmentTitle: z.string(),
  assignmentDueDate: z.string(),
  assignmentAllowResubmit: z.boolean(),
  learnerId: z.string().uuid(),
  learnerName: z.string(),
  submissionText: z.string(),
  submissionLink: z.string().nullable(),
  submittedAt: z.string(),
  isLate: z.boolean(),
  score: z.number().nullable(),
  feedback: z.string().nullable(),
  status: z.enum(['submitted', 'graded', 'resubmission_required']),
  gradedAt: z.string().nullable(),
});

// TypeScript 타입 추출
export type GradeSubmissionRequest = z.infer<typeof GradeSubmissionRequestSchema>;
export type RequestResubmissionRequest = z.infer<typeof RequestResubmissionRequestSchema>;
export type GradeSubmissionResponse = z.infer<typeof GradeSubmissionResponseSchema>;
export type RequestResubmissionResponse = z.infer<typeof RequestResubmissionResponseSchema>;
export type SubmissionDetailResponse = z.infer<typeof SubmissionDetailResponseSchema>;
