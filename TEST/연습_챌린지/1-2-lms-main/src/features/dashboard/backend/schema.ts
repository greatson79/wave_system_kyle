import { z } from 'zod';

// Supabase 레코드 스키마
export const EnrollmentRowSchema = z.object({
  id: z.string().uuid(),
  learner_id: z.string().uuid(),
  course_id: z.string().uuid(),
  enrolled_at: z.string(),
  cancelled_at: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
});

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

export type EnrollmentRow = z.infer<typeof EnrollmentRowSchema>;
export type AssignmentRow = z.infer<typeof AssignmentRowSchema>;
export type SubmissionRow = z.infer<typeof SubmissionRowSchema>;

// 응답 DTO 스키마
export const CourseProgressSchema = z.object({
  courseId: z.string().uuid(),
  courseTitle: z.string(),
  progress: z.number().min(0).max(100),
  totalAssignments: z.number().int().min(0),
  completedAssignments: z.number().int().min(0),
});

export const DueAssignmentSchema = z.object({
  assignmentId: z.string().uuid(),
  courseId: z.string().uuid(),
  courseTitle: z.string(),
  assignmentTitle: z.string(),
  dueDate: z.string(),
  hoursRemaining: z.number().min(0),
});

export const RecentFeedbackSchema = z.object({
  submissionId: z.string().uuid(),
  assignmentId: z.string().uuid(),
  assignmentTitle: z.string(),
  courseTitle: z.string(),
  feedback: z.string(),
  score: z.number().nullable(),
  gradedAt: z.string(),
});

export const LearnerDashboardResponseSchema = z.object({
  courses: z.array(CourseProgressSchema),
  dueAssignments: z.array(DueAssignmentSchema),
  recentFeedback: z.array(RecentFeedbackSchema),
});

export type CourseProgress = z.infer<typeof CourseProgressSchema>;
export type DueAssignment = z.infer<typeof DueAssignmentSchema>;
export type RecentFeedback = z.infer<typeof RecentFeedbackSchema>;
export type LearnerDashboardResponse = z.infer<
  typeof LearnerDashboardResponseSchema
>;

// Instructor: 내 코스 아이템
export const MyCourseItemSchema = z.object({
  courseId: z.string().uuid(),
  courseTitle: z.string(),
  status: z.enum(['draft', 'published', 'archived']),
  enrollmentsCount: z.number().int().min(0),
  createdAt: z.string(),
});

// Instructor: 최근 제출물 아이템
export const RecentSubmissionItemSchema = z.object({
  submissionId: z.string().uuid(),
  assignmentId: z.string().uuid(),
  assignmentTitle: z.string(),
  courseId: z.string().uuid(),
  courseTitle: z.string(),
  learnerName: z.string(),
  status: z.enum(['submitted', 'graded', 'resubmission_required']),
  submittedAt: z.string(),
  isLate: z.boolean(),
});

// Instructor 대시보드 응답 스키마
export const InstructorDashboardResponseSchema = z.object({
  courses: z.array(MyCourseItemSchema),
  pendingGradingCount: z.number().int().min(0),
  recentSubmissions: z.array(RecentSubmissionItemSchema),
});

export type MyCourseItem = z.infer<typeof MyCourseItemSchema>;
export type RecentSubmissionItem = z.infer<typeof RecentSubmissionItemSchema>;
export type InstructorDashboardResponse = z.infer<
  typeof InstructorDashboardResponseSchema
>;
