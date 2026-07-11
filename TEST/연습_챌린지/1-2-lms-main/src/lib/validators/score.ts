export const MIN_SCORE = 0;
export const MAX_SCORE = 100;

export const isValidScore = (score: number): boolean => {
  return score >= MIN_SCORE && score <= MAX_SCORE;
};

export const getScoreErrorMessage = (score: number): string | null => {
  if (score < MIN_SCORE) {
    return `점수는 ${MIN_SCORE} 이상이어야 합니다.`;
  }
  if (score > MAX_SCORE) {
    return `점수는 ${MAX_SCORE} 이하여야 합니다.`;
  }
  return null;
};
