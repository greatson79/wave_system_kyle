'use client';

import { Button } from '@/components/ui/button';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { useEnroll } from '../hooks/useEnroll';
import { useUnenroll } from '../hooks/useUnenroll';
import { useEnrollmentStatus } from '../hooks/useEnrollmentStatus';
import { useState } from 'react';
import { useToast } from '@/hooks/use-toast';
import { Loader2 } from 'lucide-react';
import { useRouter } from 'next/navigation';

type EnrollButtonProps = {
  courseId: string;
};

export const EnrollButton = ({ courseId }: EnrollButtonProps) => {
  const router = useRouter();
  const { toast } = useToast();
  const [showUnenrollDialog, setShowUnenrollDialog] = useState(false);

  const { data: enrollmentStatus, isLoading: isLoadingStatus } =
    useEnrollmentStatus(courseId);

  const enrollMutation = useEnroll();
  const unenrollMutation = useUnenroll();

  const handleEnroll = async () => {
    try {
      await enrollMutation.mutateAsync(courseId);
      toast({
        title: '수강신청 완료',
        description: '과제를 시작해보세요!',
      });
      // 수강신청 후 내 코스 상세 페이지로 이동
      router.push(`/courses/my/${courseId}`);
    } catch (error) {
      toast({
        title: '수강신청 실패',
        description:
          error instanceof Error ? error.message : '수강신청에 실패했습니다.',
        variant: 'destructive',
      });
    }
  };

  const handleUnenroll = async () => {
    try {
      await unenrollMutation.mutateAsync(courseId);
      setShowUnenrollDialog(false);
      toast({
        title: '수강취소 완료',
        description: '수강취소가 완료되었습니다.',
      });
    } catch (error) {
      toast({
        title: '수강취소 실패',
        description:
          error instanceof Error ? error.message : '수강취소에 실패했습니다.',
        variant: 'destructive',
      });
    }
  };

  const isLoading =
    isLoadingStatus ||
    enrollMutation.isPending ||
    unenrollMutation.isPending;
  const isEnrolled = enrollmentStatus?.enrolled || false;

  if (isLoadingStatus) {
    return (
      <Button disabled>
        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
        확인 중...
      </Button>
    );
  }

  if (isEnrolled) {
    return (
      <>
        <Button
          onClick={() => setShowUnenrollDialog(true)}
          disabled={isLoading}
          variant="outline"
        >
          {unenrollMutation.isPending && (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          )}
          수강취소
        </Button>

        <AlertDialog
          open={showUnenrollDialog}
          onOpenChange={setShowUnenrollDialog}
        >
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>수강취소 확인</AlertDialogTitle>
              <AlertDialogDescription>
                정말 이 코스의 수강을 취소하시겠습니까? 취소 후에도 다시
                신청할 수 있습니다.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>취소</AlertDialogCancel>
              <AlertDialogAction onClick={handleUnenroll}>
                확인
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </>
    );
  }

  return (
    <Button onClick={handleEnroll} disabled={isLoading}>
      {enrollMutation.isPending && (
        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
      )}
      수강신청
    </Button>
  );
};
