export const dashboardErrorCodes = {
  fetchError: 'DASHBOARD_FETCH_ERROR',
  notFound: 'DASHBOARD_NOT_FOUND',
  validationError: 'DASHBOARD_VALIDATION_ERROR',
  permissionDenied: 'DASHBOARD_PERMISSION_DENIED',
} as const;

type DashboardErrorValue =
  (typeof dashboardErrorCodes)[keyof typeof dashboardErrorCodes];

export type DashboardServiceError = DashboardErrorValue;
