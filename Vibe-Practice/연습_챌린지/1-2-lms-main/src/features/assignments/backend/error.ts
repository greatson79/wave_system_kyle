export const assignmentsErrorCodes = {
  invalidRequest: 'ASSIGNMENTS_INVALID_REQUEST',
  assignmentNotFound: 'ASSIGNMENTS_NOT_FOUND',
  assignmentNotPublished: 'ASSIGNMENTS_NOT_PUBLISHED',
  notEnrolled: 'ASSIGNMENTS_NOT_ENROLLED',
  unauthorized: 'ASSIGNMENTS_UNAUTHORIZED',

  // 제출 관련 에러 코드
  submissionNotAllowed: 'ASSIGNMENTS_SUBMISSION_NOT_ALLOWED',
  assignmentClosed: 'ASSIGNMENTS_CLOSED',
  pastDueNotAllowed: 'ASSIGNMENTS_PAST_DUE_NOT_ALLOWED',
  alreadySubmitted: 'ASSIGNMENTS_ALREADY_SUBMITTED',
  resubmitNotAllowed: 'ASSIGNMENTS_RESUBMIT_NOT_ALLOWED',
  invalidUrl: 'ASSIGNMENTS_INVALID_URL',
  submissionTextRequired: 'ASSIGNMENTS_SUBMISSION_TEXT_REQUIRED',
  submissionNotFound: 'ASSIGNMENTS_SUBMISSION_NOT_FOUND',

  // Instructor 관리 관련 에러 코드
  notInstructor: 'ASSIGNMENTS_NOT_INSTRUCTOR',
  notOwner: 'ASSIGNMENTS_NOT_OWNER',
  courseNotFound: 'ASSIGNMENTS_COURSE_NOT_FOUND',
  courseArchived: 'ASSIGNMENTS_COURSE_ARCHIVED',
  invalidDueDate: 'ASSIGNMENTS_INVALID_DUE_DATE',
  invalidWeight: 'ASSIGNMENTS_INVALID_WEIGHT',
  cannotModifyPublished: 'ASSIGNMENTS_CANNOT_MODIFY_PUBLISHED',
  createFailed: 'ASSIGNMENTS_CREATE_FAILED',
  updateFailed: 'ASSIGNMENTS_UPDATE_FAILED',
  publishFailed: 'ASSIGNMENTS_PUBLISH_FAILED',
  closeFailed: 'ASSIGNMENTS_CLOSE_FAILED',
  missingRequiredFields: 'ASSIGNMENTS_MISSING_REQUIRED_FIELDS',
  weightWarning: 'ASSIGNMENTS_WEIGHT_WARNING',

  // 채점 관련 에러 코드
  invalidScore: 'ASSIGNMENTS_INVALID_SCORE',
  feedbackRequired: 'ASSIGNMENTS_FEEDBACK_REQUIRED',
  gradeFailed: 'ASSIGNMENTS_GRADE_FAILED',
  requestResubmissionFailed: 'ASSIGNMENTS_REQUEST_RESUBMISSION_FAILED',
  resubmitNotAllowedForAssignment: 'ASSIGNMENTS_RESUBMIT_NOT_ALLOWED_FOR_ASSIGNMENT',
  cannotGradeOwnSubmission: 'ASSIGNMENTS_CANNOT_GRADE_OWN_SUBMISSION',
} as const;

export type AssignmentsServiceError = (typeof assignmentsErrorCodes)[keyof typeof assignmentsErrorCodes];
