export const metadataErrorCodes = {
  invalidRequest: 'METADATA_INVALID_REQUEST',
  unauthorized: 'METADATA_UNAUTHORIZED',
  categoryNotFound: 'METADATA_CATEGORY_NOT_FOUND',
  difficultyNotFound: 'METADATA_DIFFICULTY_NOT_FOUND',
  duplicateName: 'METADATA_DUPLICATE_NAME',
  duplicateLevel: 'METADATA_DUPLICATE_LEVEL',
  inUse: 'METADATA_IN_USE',
  createFailed: 'METADATA_CREATE_FAILED',
  updateFailed: 'METADATA_UPDATE_FAILED',
} as const;

type MetadataErrorValue = (typeof metadataErrorCodes)[keyof typeof metadataErrorCodes];

export type MetadataServiceError = MetadataErrorValue;
