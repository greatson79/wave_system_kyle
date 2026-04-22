export const coursesErrorCodes = {
  invalidRequest: 'COURSES_INVALID_REQUEST',
  courseNotFound: 'COURSES_NOT_FOUND',
  courseNotPublished: 'COURSES_NOT_PUBLISHED',
  alreadyEnrolled: 'COURSES_ALREADY_ENROLLED',
  notEnrolled: 'COURSES_NOT_ENROLLED',
  enrollmentFailed: 'COURSES_ENROLLMENT_FAILED',
  unenrollmentFailed: 'COURSES_UNENROLLMENT_FAILED',
  unauthorized: 'COURSES_UNAUTHORIZED',
  databaseError: 'COURSES_DATABASE_ERROR',
  unknown: 'COURSES_UNKNOWN_ERROR',

  // Instructor 관리 관련 에러 코드
  notInstructor: 'COURSES_NOT_INSTRUCTOR',
  notOwner: 'COURSES_NOT_OWNER',
  categoryNotFound: 'COURSES_CATEGORY_NOT_FOUND',
  difficultyNotFound: 'COURSES_DIFFICULTY_NOT_FOUND',
  categoryInactive: 'COURSES_CATEGORY_INACTIVE',
  difficultyInactive: 'COURSES_DIFFICULTY_INACTIVE',
  invalidStatus: 'COURSES_INVALID_STATUS',
  cannotReactivate: 'COURSES_CANNOT_REACTIVATE_ARCHIVED',
  createFailed: 'COURSES_CREATE_FAILED',
  updateFailed: 'COURSES_UPDATE_FAILED',
  statusUpdateFailed: 'COURSES_STATUS_UPDATE_FAILED',
  assignmentsUpdateFailed: 'COURSES_ASSIGNMENTS_UPDATE_FAILED',
} as const;

type CoursesErrorValue =
  (typeof coursesErrorCodes)[keyof typeof coursesErrorCodes];

export type CoursesServiceError = CoursesErrorValue;
