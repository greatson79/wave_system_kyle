import { z } from 'zod';

export const CourseListQuerySchema = z.object({
  search: z.string().optional(),
  categoryId: z.string().uuid().optional(),
  difficultyId: z.string().uuid().optional(),
  sort: z.enum(['latest', 'popular']).default('latest'),
  limit: z.coerce.number().int().min(1).max(100).default(20),
  offset: z.coerce.number().int().min(0).default(0),
});

export type CourseListQuery = z.infer<typeof CourseListQuerySchema>;

export const CourseInstructorSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
});

export const CourseCategorySchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
});

export const CourseDifficultySchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  level: z.number().int(),
});

export const CourseItemSchema = z.object({
  id: z.string().uuid(),
  title: z.string(),
  description: z.string(),
  instructor: CourseInstructorSchema,
  category: CourseCategorySchema,
  difficulty: CourseDifficultySchema,
  enrollmentsCount: z.number().int().min(0),
  status: z.literal('published'),
  createdAt: z.string(),
});

export const CourseListResponseSchema = z.object({
  courses: z.array(CourseItemSchema),
  total: z.number().int().min(0),
  limit: z.number().int().min(1),
  offset: z.number().int().min(0),
});

export type CourseListResponse = z.infer<typeof CourseListResponseSchema>;

export const CourseDetailResponseSchema = z.object({
  id: z.string().uuid(),
  title: z.string(),
  description: z.string(),
  curriculum: z.string().nullable(),
  instructor: CourseInstructorSchema,
  category: CourseCategorySchema,
  difficulty: CourseDifficultySchema,
  enrollmentsCount: z.number().int().min(0),
  status: z.literal('published'),
  createdAt: z.string(),
  updatedAt: z.string(),
});

export type CourseDetailResponse = z.infer<typeof CourseDetailResponseSchema>;

export const EnrollResponseSchema = z.object({
  enrolled: z.boolean(),
  courseId: z.string().uuid(),
  enrolledAt: z.string(),
});

export type EnrollResponse = z.infer<typeof EnrollResponseSchema>;

export const EnrollmentStatusResponseSchema = z.object({
  enrolled: z.boolean(),
  enrolledAt: z.string().nullable(),
  cancelledAt: z.string().nullable(),
});

export type EnrollmentStatusResponse = z.infer<
  typeof EnrollmentStatusResponseSchema
>;

export const CourseRowSchema = z.object({
  id: z.string().uuid(),
  instructor_id: z.string().uuid(),
  category_id: z.string().uuid(),
  difficulty_id: z.string().uuid(),
  title: z.string(),
  description: z.string(),
  curriculum: z.string().nullable(),
  enrollments_count: z.number().int().min(0),
  status: z.enum(['draft', 'published', 'archived']),
  created_at: z.string(),
  updated_at: z.string(),
});

export type CourseRow = z.infer<typeof CourseRowSchema>;

// Instructor 코스 관리 스키마

// 코스 생성 요청 스키마
export const CreateCourseRequestSchema = z.object({
  title: z.string().min(1, '제목은 필수 항목입니다.'),
  description: z.string().min(1, '소개는 필수 항목입니다.'),
  categoryId: z.string().uuid('올바른 카테고리를 선택해주세요.'),
  difficultyId: z.string().uuid('올바른 난이도를 선택해주세요.'),
  curriculum: z.string().optional().nullable(),
});

// 코스 수정 요청 스키마
export const UpdateCourseRequestSchema = z.object({
  title: z.string().min(1, '제목은 필수 항목입니다.').optional(),
  description: z.string().min(1, '소개는 필수 항목입니다.').optional(),
  categoryId: z.string().uuid('올바른 카테고리를 선택해주세요.').optional(),
  difficultyId: z.string().uuid('올바른 난이도를 선택해주세요.').optional(),
  curriculum: z.string().optional().nullable(),
});

// 코스 상태 전환 요청 스키마
export const UpdateCourseStatusRequestSchema = z.object({
  status: z.enum(['draft', 'published', 'archived']),
});

// 코스 생성 응답 스키마
export const CreateCourseResponseSchema = z.object({
  courseId: z.string().uuid(),
  title: z.string(),
  status: z.enum(['draft', 'published', 'archived']),
  createdAt: z.string(),
  message: z.string(),
});

// 코스 수정 응답 스키마
export const UpdateCourseResponseSchema = z.object({
  courseId: z.string().uuid(),
  title: z.string(),
  updatedAt: z.string(),
  message: z.string(),
});

// 코스 상태 전환 응답 스키마
export const UpdateCourseStatusResponseSchema = z.object({
  courseId: z.string().uuid(),
  status: z.enum(['draft', 'published', 'archived']),
  archivedAssignmentsCount: z.number().int().optional(),
  message: z.string(),
});

// 내 코스 아이템 스키마
export const MyCourseItemSchema = z.object({
  id: z.string().uuid(),
  title: z.string(),
  description: z.string(),
  status: z.enum(['draft', 'published', 'archived']),
  enrollmentsCount: z.number().int(),
  createdAt: z.string(),
  updatedAt: z.string(),
  category: z.object({
    id: z.string().uuid(),
    name: z.string(),
  }),
  difficulty: z.object({
    id: z.string().uuid(),
    name: z.string(),
    level: z.number().int(),
  }),
});

// 내 코스 목록 응답 스키마
export const MyCoursesResponseSchema = z.object({
  courses: z.array(MyCourseItemSchema),
  total: z.number().int(),
});

// Instructor 전용 코스 상세 응답 스키마
export const InstructorCourseDetailResponseSchema = z.object({
  id: z.string().uuid(),
  title: z.string(),
  description: z.string(),
  curriculum: z.string().nullable(),
  status: z.enum(['draft', 'published', 'archived']),
  enrollmentsCount: z.number().int(),
  createdAt: z.string(),
  updatedAt: z.string(),
  category: z.object({
    id: z.string().uuid(),
    name: z.string(),
  }),
  difficulty: z.object({
    id: z.string().uuid(),
    name: z.string(),
    level: z.number().int(),
  }),
});

// TypeScript 타입 추출
export type CreateCourseRequest = z.infer<typeof CreateCourseRequestSchema>;
export type UpdateCourseRequest = z.infer<typeof UpdateCourseRequestSchema>;
export type UpdateCourseStatusRequest = z.infer<
  typeof UpdateCourseStatusRequestSchema
>;
export type CreateCourseResponse = z.infer<typeof CreateCourseResponseSchema>;
export type UpdateCourseResponse = z.infer<typeof UpdateCourseResponseSchema>;
export type UpdateCourseStatusResponse = z.infer<
  typeof UpdateCourseStatusResponseSchema
>;
export type MyCourseItem = z.infer<typeof MyCourseItemSchema>;
export type MyCoursesResponse = z.infer<typeof MyCoursesResponseSchema>;
export type InstructorCourseDetailResponse = z.infer<
  typeof InstructorCourseDetailResponseSchema
>;

// Learner: 수강 중인 코스 목록 조회
export const MyEnrolledCoursesResponseSchema = z.object({
  courses: z.array(
    z.object({
      enrollmentId: z.string(),
      courseId: z.string(),
      courseTitle: z.string(),
      courseDescription: z.string(),
      categoryName: z.string(),
      difficultyName: z.string(),
      instructorName: z.string(),
      enrolledAt: z.string(),
      progress: z.number(),
      totalAssignments: z.number(),
      completedAssignments: z.number(),
    })
  ),
});

export type MyEnrolledCoursesResponse = z.infer<typeof MyEnrolledCoursesResponseSchema>;
