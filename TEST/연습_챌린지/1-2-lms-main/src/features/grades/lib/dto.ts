export {
  GradeItemSchema,
  GradesSummarySchema,
  CourseGradesResponseSchema,
  type GradeItem,
  type GradesSummary,
  type CourseGradesResponse,
} from '@/features/grades/backend/schema';

export {
  calculateTotalScore,
  calculateAverageScore,
  calculateCompletionRate,
} from './grade-calculator';
