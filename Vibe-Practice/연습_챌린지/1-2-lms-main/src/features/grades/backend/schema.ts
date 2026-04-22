import { z } from 'zod';

// 과제별 성적 아이템 스키마
export const GradeItemSchema = z.object({
  assignmentId: z.string().uuid(),
  assignmentTitle: z.string(),
  dueDate: z.string(), // ISO timestamp
  weight: z.number(), // 0-100 decimal
  submittedAt: z.string().nullable(), // ISO timestamp
  isLate: z.boolean().nullable(),
  status: z.enum(['not_submitted', 'submitted', 'graded', 'resubmission_required']),
  score: z.number().nullable(), // 0-100 decimal
  feedback: z.string().nullable(),
  gradedAt: z.string().nullable(), // ISO timestamp
});

// 성적 요약 스키마
export const GradesSummarySchema = z.object({
  totalAssignments: z.number().int(), // 전체 과제 수
  gradedAssignments: z.number().int(), // 채점 완료된 과제 수
  totalScore: z.number(), // 총점 (점수 × 비중 합계)
  averageScore: z.number().nullable(), // 평균 점수 (선택 사항)
});

// 코스별 성적 응답 스키마
export const CourseGradesResponseSchema = z.object({
  courseId: z.string().uuid(),
  courseTitle: z.string(),
  grades: z.array(GradeItemSchema),
  summary: GradesSummarySchema,
});

// TypeScript 타입 추출
export type GradeItem = z.infer<typeof GradeItemSchema>;
export type GradesSummary = z.infer<typeof GradesSummarySchema>;
export type CourseGradesResponse = z.infer<typeof CourseGradesResponseSchema>;
