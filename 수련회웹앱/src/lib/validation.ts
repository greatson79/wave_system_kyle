import type { ValidationResult } from '../types/game'

export function validateGameSetup(input: {
  participantCount: number
  teamCount: number
}): ValidationResult {
  const errors: string[] = []

  if (!Number.isInteger(input.participantCount) || input.participantCount < 2) {
    errors.push('INVALID_PARTICIPANT_COUNT')
  }

  if (!Number.isInteger(input.teamCount) || input.teamCount < 2) {
    errors.push('INVALID_TEAM_COUNT')
  }

  if (
    Number.isInteger(input.participantCount) &&
    Number.isInteger(input.teamCount) &&
    input.teamCount > input.participantCount
  ) {
    errors.push('TEAM_COUNT_EXCEEDS_PARTICIPANTS')
  }

  return { valid: errors.length === 0, errors }
}

export function validateTeamNames(names: string[]): ValidationResult {
  const errors: string[] = []
  const trimmed = names.map((name) => name.trim()).filter(Boolean)

  if (trimmed.length !== names.length) {
    errors.push('TEAM_NAME_REQUIRED')
  }

  if (new Set(trimmed).size !== trimmed.length) {
    errors.push('DUPLICATE_TEAM_NAME')
  }

  return { valid: errors.length === 0, errors }
}
