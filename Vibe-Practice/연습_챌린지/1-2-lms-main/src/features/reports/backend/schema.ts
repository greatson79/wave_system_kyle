import { z } from 'zod';

// 신고 대상 유형
export const TargetTypeSchema = z.enum(['course', 'assignment', 'submission', 'user']);

// 신고 상태
export const ReportStatusSchema = z.enum(['received', 'investigating', 'resolved']);

// 조치 유형
export const ActionTypeSchema = z.enum([
  'warning',
  'invalidate_submission',
  'suspend_account',
  'ban_account',
  'dismiss',
]);

// 신고 접수 요청
export const SubmitReportRequestSchema = z.object({
  targetType: TargetTypeSchema,
  targetId: z.string().uuid(),
  reason: z.string().min(1, '신고 사유는 필수 항목입니다.'),
  content: z.string().min(10, '신고 내용은 최소 10자 이상 입력해주세요.'),
});

// 신고 접수 응답
export const SubmitReportResponseSchema = z.object({
  reportId: z.string().uuid(),
  status: ReportStatusSchema,
  createdAt: z.string(),
  message: z.string(),
});

// 신고 목록 조회 쿼리
export const ReportsListQuerySchema = z.object({
  status: ReportStatusSchema.optional(),
  targetType: TargetTypeSchema.optional(),
  limit: z.coerce.number().int().min(1).max(100).default(20),
  offset: z.coerce.number().int().min(0).default(0),
});

// 신고 항목
export const ReportItemSchema = z.object({
  id: z.string().uuid(),
  reporter: z.object({
    id: z.string().uuid(),
    name: z.string(),
  }),
  targetType: TargetTypeSchema,
  targetId: z.string().uuid(),
  reason: z.string(),
  status: ReportStatusSchema,
  createdAt: z.string(),
  resolvedAt: z.string().nullable(),
});

// 신고 목록 응답
export const ReportsListResponseSchema = z.object({
  reports: z.array(ReportItemSchema),
  total: z.number(),
  limit: z.number(),
  offset: z.number(),
});

// 신고 상세 응답
export const ReportDetailResponseSchema = z.object({
  id: z.string().uuid(),
  reporter: z.object({
    id: z.string().uuid(),
    name: z.string(),
  }),
  targetType: TargetTypeSchema,
  targetId: z.string().uuid(),
  targetInfo: z
    .object({
      title: z.string().optional(),
      name: z.string().optional(),
    })
    .nullable(),
  reason: z.string(),
  content: z.string(),
  status: ReportStatusSchema,
  actionTaken: z.string().nullable(),
  createdAt: z.string(),
  updatedAt: z.string(),
  resolvedAt: z.string().nullable(),
});

// 신고 처리 요청
export const UpdateReportRequestSchema = z.object({
  status: ReportStatusSchema,
  actionType: ActionTypeSchema.optional(),
  actionNote: z.string().optional(),
  suspensionDays: z.number().int().min(1).max(365).optional(),
});

// 신고 처리 응답
export const UpdateReportResponseSchema = z.object({
  reportId: z.string().uuid(),
  status: ReportStatusSchema,
  resolvedAt: z.string().nullable(),
  message: z.string(),
});

// TypeScript 타입 추출
export type TargetType = z.infer<typeof TargetTypeSchema>;
export type ReportStatus = z.infer<typeof ReportStatusSchema>;
export type ActionType = z.infer<typeof ActionTypeSchema>;
export type SubmitReportRequest = z.infer<typeof SubmitReportRequestSchema>;
export type SubmitReportResponse = z.infer<typeof SubmitReportResponseSchema>;
export type ReportsListQuery = z.infer<typeof ReportsListQuerySchema>;
export type ReportItem = z.infer<typeof ReportItemSchema>;
export type ReportsListResponse = z.infer<typeof ReportsListResponseSchema>;
export type ReportDetailResponse = z.infer<typeof ReportDetailResponseSchema>;
export type UpdateReportRequest = z.infer<typeof UpdateReportRequestSchema>;
export type UpdateReportResponse = z.infer<typeof UpdateReportResponseSchema>;
