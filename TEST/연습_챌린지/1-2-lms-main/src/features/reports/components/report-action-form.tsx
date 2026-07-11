'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Form,
  FormControl,
  FormDescription,
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
import { Input } from '@/components/ui/input';
import { useUpdateReport } from '../hooks/useUpdateReport';
import {
  UpdateReportRequestSchema,
  getActionTypeText,
  getActionTypeDescription,
  canTransitionStatus,
  type UpdateReportRequest,
  type ReportStatus,
  type ActionType,
} from '../lib/dto';

interface ReportActionFormProps {
  reportId: string;
  currentStatus: ReportStatus;
  onSuccess?: () => void;
}

const statusOptions: { value: ReportStatus; label: string }[] = [
  { value: 'received', label: '접수됨' },
  { value: 'investigating', label: '조사 중' },
  { value: 'resolved', label: '처리 완료' },
];

const actionTypeOptions: { value: ActionType; label: string }[] = [
  { value: 'warning', label: '경고 발송' },
  { value: 'invalidate_submission', label: '제출물 무효화' },
  { value: 'suspend_account', label: '계정 일시정지' },
  { value: 'ban_account', label: '계정 영구정지' },
  { value: 'dismiss', label: '신고 기각' },
];

export function ReportActionForm({
  reportId,
  currentStatus,
  onSuccess,
}: ReportActionFormProps) {
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const { mutate: updateReport, isPending } = useUpdateReport(reportId);

  const form = useForm<UpdateReportRequest>({
    resolver: zodResolver(UpdateReportRequestSchema),
    defaultValues: {
      status: currentStatus,
      actionType: undefined,
      actionNote: '',
      suspensionDays: undefined,
    },
  });

  const watchedStatus = form.watch('status');
  const watchedActionType = form.watch('actionType');
  const isResolved = watchedStatus === 'resolved';
  const isSuspension = watchedActionType === 'suspend_account';

  const onSubmit = (data: UpdateReportRequest) => {
    setError(null);
    setSuccessMessage(null);

    if (!canTransitionStatus(currentStatus, data.status)) {
      setError(
        `현재 상태(${currentStatus})에서 ${data.status}(으)로 변경할 수 없습니다.`
      );
      return;
    }

    if (data.status === 'resolved' && !data.actionType) {
      setError('처리 완료 시 조치 유형을 선택해야 합니다.');
      return;
    }

    updateReport(data, {
      onSuccess: (response) => {
        setSuccessMessage(response.message);
        form.reset({
          status: response.status,
          actionType: undefined,
          actionNote: '',
          suspensionDays: undefined,
        });
        onSuccess?.();
      },
      onError: (err) => {
        setError(err.message);
      },
    });
  };

  const availableStatuses = statusOptions.filter((option) =>
    canTransitionStatus(currentStatus, option.value)
  );

  if (currentStatus === 'resolved') {
    return (
      <Card>
        <CardHeader>
          <CardTitle>신고 처리</CardTitle>
        </CardHeader>
        <CardContent>
          <Alert>
            <AlertDescription>
              이미 처리 완료된 신고입니다. 추가 조치를 할 수 없습니다.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>신고 처리</CardTitle>
      </CardHeader>

      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {successMessage && (
              <Alert>
                <AlertDescription>{successMessage}</AlertDescription>
              </Alert>
            )}

            <FormField
              control={form.control}
              name="status"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>신고 상태</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    value={field.value}
                    disabled={isPending}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="신고 상태를 선택하세요" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {availableStatuses.map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormDescription>
                    현재 상태에서 전환 가능한 상태만 표시됩니다.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            {isResolved && (
              <>
                <FormField
                  control={form.control}
                  name="actionType"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>조치 유형</FormLabel>
                      <Select
                        onValueChange={field.onChange}
                        value={field.value}
                        disabled={isPending}
                      >
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="조치 유형을 선택하세요" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {actionTypeOptions.map((option) => (
                            <SelectItem key={option.value} value={option.value}>
                              {option.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      {watchedActionType && (
                        <FormDescription>
                          {getActionTypeDescription(watchedActionType)}
                        </FormDescription>
                      )}
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {isSuspension && (
                  <FormField
                    control={form.control}
                    name="suspensionDays"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>정지 기간 (일)</FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            min={1}
                            max={365}
                            placeholder="1-365 사이의 숫자를 입력하세요"
                            disabled={isPending}
                            {...field}
                            onChange={(e) =>
                              field.onChange(
                                e.target.value
                                  ? parseInt(e.target.value, 10)
                                  : undefined
                              )
                            }
                            value={field.value ?? ''}
                          />
                        </FormControl>
                        <FormDescription>
                          계정 일시정지 기간을 일 단위로 입력하세요.
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                )}

                <FormField
                  control={form.control}
                  name="actionNote"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>조치 사유</FormLabel>
                      <FormControl>
                        <Textarea
                          placeholder="조치 사유를 상세히 입력해주세요"
                          className="min-h-[120px]"
                          disabled={isPending}
                          {...field}
                        />
                      </FormControl>
                      <FormDescription>
                        대상자에게 전달될 조치 사유를 입력하세요.
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </>
            )}

            <Button type="submit" disabled={isPending} className="w-full">
              {isPending ? '처리 중...' : '신고 처리 완료'}
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}
