'use client';

import { useLearnerDashboardQuery } from '../hooks/useLearnerDashboardQuery';
import { dashboardEmptyState } from '../lib/empty-state';
import { formatDistanceToNow } from 'date-fns';
import { ko } from 'date-fns/locale';
import Link from 'next/link';

const LoadingState = () => (
  <div className="space-y-6">
    <div className="h-8 w-48 bg-gray-200 animate-pulse rounded" />
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-32 bg-gray-200 animate-pulse rounded-lg" />
      ))}
    </div>
  </div>
);

const EmptyCoursesState = () => {
  const config = dashboardEmptyState.noCourses();
  return (
    <div className="text-center py-12">
      <h3 className="text-xl font-semibold text-gray-900">{config.title}</h3>
      <p className="mt-2 text-gray-600">{config.message}</p>
      {config.actionText && config.actionLink && (
        <Link
          href={config.actionLink}
          className="mt-4 inline-block px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          {config.actionText}
        </Link>
      )}
    </div>
  );
};

const ErrorState = ({ error, refetch }: { error: Error; refetch: () => void }) => {
  const config = dashboardEmptyState.error();
  return (
    <div className="text-center py-12">
      <h3 className="text-xl font-semibold text-red-600">{config.title}</h3>
      <p className="mt-2 text-gray-600">{config.message}</p>
      <p className="mt-1 text-sm text-gray-500">{error.message}</p>
      {config.actionText && (
        <button
          onClick={() => refetch()}
          className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          {config.actionText}
        </button>
      )}
    </div>
  );
};

const ProgressBar = ({ progress }: { progress: number }) => (
  <div className="w-full bg-gray-200 rounded-full h-2.5">
    <div
      className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
      style={{ width: `${progress}%` }}
    />
  </div>
);

export const LearnerDashboardSummary = () => {
  const { data, isLoading, isError, error, refetch } = useLearnerDashboardQuery();

  if (isLoading) {
    return <LoadingState />;
  }

  if (isError || !data) {
    return <ErrorState error={error as Error} refetch={refetch} />;
  }

  if (data.courses.length === 0) {
    return <EmptyCoursesState />;
  }

  return (
    <div className="space-y-8">
      <section>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">내 코스 진행률</h2>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {data.courses.map((course) => (
            <div key={course.courseId} className="bg-white p-6 rounded-lg shadow border">
              <h3 className="font-semibold text-lg text-gray-900 mb-2">
                {course.courseTitle}
              </h3>
              <div className="space-y-2">
                <div className="flex justify-between text-sm text-gray-600">
                  <span>진행률</span>
                  <span className="font-medium">{course.progress}%</span>
                </div>
                <ProgressBar progress={course.progress} />
                <p className="text-sm text-gray-500">
                  {course.completedAssignments} / {course.totalAssignments} 과제 완료
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {data.dueAssignments.length > 0 && (
        <section>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">마감 임박 과제</h2>
          <div className="grid gap-4 md:grid-cols-2">
            {data.dueAssignments.map((assignment) => (
              <div
                key={assignment.assignmentId}
                className="bg-yellow-50 p-4 rounded-lg border border-yellow-200"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900">
                      {assignment.assignmentTitle}
                    </h3>
                    <p className="text-sm text-gray-600">{assignment.courseTitle}</p>
                  </div>
                  <span className="text-xs font-medium text-yellow-700 bg-yellow-100 px-2 py-1 rounded">
                    {assignment.hoursRemaining.toFixed(1)}시간 남음
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  마감: {formatDistanceToNow(new Date(assignment.dueDate), { addSuffix: true, locale: ko })}
                </p>
              </div>
            ))}
          </div>
        </section>
      )}

      {data.recentFeedback.length > 0 && (
        <section>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">최근 피드백</h2>
          <div className="space-y-4">
            {data.recentFeedback.map((feedback) => (
              <div
                key={feedback.submissionId}
                className="bg-white p-4 rounded-lg shadow border"
              >
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h3 className="font-semibold text-gray-900">
                      {feedback.assignmentTitle}
                    </h3>
                    <p className="text-sm text-gray-600">{feedback.courseTitle}</p>
                  </div>
                  {feedback.score !== null && (
                    <span className="text-lg font-bold text-blue-600">
                      {feedback.score}점
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-700 mt-2">{feedback.feedback}</p>
                <p className="text-xs text-gray-500 mt-2">
                  {formatDistanceToNow(new Date(feedback.gradedAt), { addSuffix: true, locale: ko })}
                </p>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
};
