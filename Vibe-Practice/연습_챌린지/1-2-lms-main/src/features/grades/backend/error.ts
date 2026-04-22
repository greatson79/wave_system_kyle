export const gradesErrorCodes = {
  invalidRequest: 'GRADES_INVALID_REQUEST',
  courseNotFound: 'GRADES_COURSE_NOT_FOUND',
  notEnrolled: 'GRADES_NOT_ENROLLED',
  unauthorized: 'GRADES_UNAUTHORIZED',
  enrollmentCancelled: 'GRADES_ENROLLMENT_CANCELLED',
} as const;

export type GradesServiceError = (typeof gradesErrorCodes)[keyof typeof gradesErrorCodes];
