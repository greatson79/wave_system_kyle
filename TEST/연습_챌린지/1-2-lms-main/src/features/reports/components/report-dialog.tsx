'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useSubmitReport } from '../hooks/useSubmitReport';
import {
  SubmitReportRequestSchema,
  type TargetType,
  type SubmitReportRequest,
} from '../lib/dto';

interface ReportDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  targetType: TargetType;
  targetId: string;
  onSuccess?: () => void;
}

const reportReasons = [
  { value: '부적절한 콘텐츠', label: '부적절한 콘텐츠' },
  { value: '스팸 또는 광고', label: '스팸 또는 광고' },
  { value: '저작권 침해', label: '저작권 침해' },
  { value: '괴롭힘 또는 협박', label: '괴롭힘 또는 협박' },
  { value: '허위 정보', label: '허위 정보' },
  { value: '기타', label: '기타' },
];

export function ReportDialog({
  open,
  onOpenChange,
  targetType,
  targetId,
  onSuccess,
}: ReportDialogProps) {
  const [error, setError] = useState<string | null>(null);
  const { mutate: submitReport, isPending } = useSubmitReport();

  const form = useForm<SubmitReportRequest>({
    resolver: zodResolver(SubmitReportRequestSchema),
    defaultValues: {
      targetType,
      targetId,
      reason: '',
      content: '',
    },
  });

  const onSubmit = (data: SubmitReportRequest) => {
    setError(null);
    submitReport(data, {
      onSuccess: () => {
        form.reset();
        onSuccess?.();
        onOpenChange(false);
      },
      onError: (err) => {
        setError(err.message);
      },
    });
  };

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen && !isPending) {
      form.reset();
      setError(null);
    }
    onOpenChange(newOpen);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>신고하기</DialogTitle>
          <DialogDescription>
            신고 사유와 내용을 입력해주세요. 검토 후 적절한 조치가 취해집니다.
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <FormField
              control={form.control}
              name="reason"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>신고 사유</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    defaultValue={field.value}
                    disabled={isPending}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="신고 사유를 선택하세요" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {reportReasons.map((reason) => (
                        <SelectItem key={reason.value} value={reason.value}>
                          {reason.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="content"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>신고 내용</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="신고 내용을 상세히 입력해주세요 (최소 10자)"
                      className="min-h-[120px]"
                      disabled={isPending}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => handleOpenChange(false)}
                disabled={isPending}
              >
                취소
              </Button>
              <Button type="submit" disabled={isPending}>
                {isPending ? '제출 중...' : '신고 접수'}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
