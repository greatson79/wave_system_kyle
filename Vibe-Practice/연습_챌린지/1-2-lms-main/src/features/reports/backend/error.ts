export const reportsErrorCodes = {
  invalidRequest: 'REPORTS_INVALID_REQUEST',
  unauthorized: 'REPORTS_UNAUTHORIZED',
  reportNotFound: 'REPORTS_NOT_FOUND',
  targetNotFound: 'REPORTS_TARGET_NOT_FOUND',
  invalidStatus: 'REPORTS_INVALID_STATUS',
  statusTransitionNotAllowed: 'REPORTS_STATUS_TRANSITION_NOT_ALLOWED',
  actionRequired: 'REPORTS_ACTION_REQUIRED',
  actionFailed: 'REPORTS_ACTION_FAILED',
  notificationFailed: 'REPORTS_NOTIFICATION_FAILED',
} as const;

type ReportsErrorValue = (typeof reportsErrorCodes)[keyof typeof reportsErrorCodes];

export type ReportsServiceError = ReportsErrorValue;
