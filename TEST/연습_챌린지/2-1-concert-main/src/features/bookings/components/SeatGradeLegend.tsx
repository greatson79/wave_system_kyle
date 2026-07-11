'use client';

import type { SeatGrade, GradeAvailability } from '../backend/schema';

interface SeatGradeLegendProps {
  grades: SeatGrade[];
  gradeAvailability: GradeAvailability[];
}

export const SeatGradeLegend = ({ grades, gradeAvailability }: SeatGradeLegendProps) => {
  return (
    <div className="bg-white rounded-lg p-4 shadow-sm mb-4">
      <h3 className="font-bold text-sm mb-3">등급별 가격 안내</h3>
      <div className="space-y-2">
        {gradeAvailability.map((availability) => {
          const grade = grades.find((g) => g.gradeCode === availability.gradeCode);
          if (!grade) return null;

          return (
            <div
              key={availability.gradeCode}
              className="flex items-center justify-between text-sm"
            >
              <div className="flex items-center gap-2">
                <div
                  className="w-4 h-4 rounded border-2"
                  style={{ borderColor: availability.colorCode }}
                />
                <span className="font-medium">{availability.gradeName}</span>
                <span className="text-gray-500 text-xs">
                  ({grade.startRow}~{grade.endRow || 20}행)
                </span>
              </div>
              <div className="flex items-center gap-3">
                <span className="font-semibold">
                  {availability.price.toLocaleString()}원
                </span>
                <span className="text-gray-600 text-xs">
                  {availability.availableSeats}/{availability.totalSeats}석
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
