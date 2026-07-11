import type { GradeItem } from '../backend/schema';

// 총점 계산: Σ(채점 완료된 과제의 점수 × 비중 / 100)
export const calculateTotalScore = (grades: GradeItem[]): number => {
  return grades.reduce((total, grade) => {
    if (grade.status === 'graded' && grade.score !== null) {
      return total + (grade.score * grade.weight) / 100;
    }
    return total;
  }, 0);
};

// 평균 점수 계산: 채점 완료된 과제의 평균
export const calculateAverageScore = (grades: GradeItem[]): number | null => {
  const gradedScores = grades
    .filter((g) => g.status === 'graded' && g.score !== null)
    .map((g) => g.score as number);

  if (gradedScores.length === 0) {
    return null;
  }

  const sum = gradedScores.reduce((acc, score) => acc + score, 0);
  return sum / gradedScores.length;
};

// 채점 완료율 계산
export const calculateCompletionRate = (
  totalAssignments: number,
  gradedAssignments: number,
): number => {
  if (totalAssignments === 0) return 0;
  return (gradedAssignments / totalAssignments) * 100;
};
