'use client';

import type { GradeAvailability } from '../backend/schema';

interface ConcertGradeAvailabilityProps {
  gradeAvailability: GradeAvailability[];
}

export const ConcertGradeAvailability = ({
  gradeAvailability,
}: ConcertGradeAvailabilityProps) => {
  return (
    <div className="bg-white rounded-lg p-6 shadow-sm">
      <h3 className="text-lg font-bold mb-4">등급별 잔여 좌석</h3>
      <div className="space-y-3">
        {gradeAvailability.map((grade) => {
          const occupancyRate =
            (grade.totalSeats - grade.availableSeats) / grade.totalSeats;
          const isSoldOut = grade.availableSeats === 0;

          return (
            <div key={grade.gradeCode} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded"
                    style={{ backgroundColor: grade.colorCode }}
                  />
                  <span className="font-medium">{grade.gradeName}</span>
                  <span className="text-sm text-gray-600">
                    {grade.price.toLocaleString()}원
                  </span>
                </div>
                <div className="text-sm">
                  {isSoldOut ? (
                    <span className="text-red-600 font-semibold">매진</span>
                  ) : (
                    <span className="text-gray-700">
                      {grade.availableSeats}/{grade.totalSeats}석
                    </span>
                  )}
                </div>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="h-2 rounded-full transition-all"
                  style={{
                    width: `${occupancyRate * 100}%`,
                    backgroundColor: grade.colorCode,
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
