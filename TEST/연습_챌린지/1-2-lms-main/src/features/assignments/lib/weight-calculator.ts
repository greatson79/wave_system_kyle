export interface WeightInfo {
  sum: number;
  exceeds100: boolean;
  warning: string | null;
}

export const calculateWeightInfo = (
  existingWeights: number[],
  newWeight: number,
): WeightInfo => {
  const sum = existingWeights.reduce((acc, w) => acc + w, 0) + newWeight;
  const exceeds100 = sum > 100;
  const warning = exceeds100
    ? `현재 코스의 과제 점수 비중 합계가 ${sum.toFixed(1)}%로 100%를 초과합니다.`
    : null;

  return { sum, exceeds100, warning };
};
