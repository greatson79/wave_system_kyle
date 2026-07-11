import type { Reflection, ValidationResult } from '../types/game'

export function validateReflection(reflection: Reflection): ValidationResult {
  const required = [
    reflection.memorableWord,
    reflection.solvedTogether,
    reflection.gratitude,
    reflection.practice,
  ]

  if (required.some((value) => value.trim().length === 0)) {
    return { valid: false, errors: ['REFLECTION_REQUIRED_FIELD_MISSING'] }
  }

  if (required.some((value) => value.length > 280)) {
    return { valid: false, errors: ['REFLECTION_TEXT_TOO_LONG'] }
  }

  return { valid: true, errors: [] }
}
