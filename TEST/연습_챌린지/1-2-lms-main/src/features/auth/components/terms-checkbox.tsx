'use client';

import type { Control, FieldPath, FieldValues, UseFormSetValue } from 'react-hook-form';
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Checkbox } from '@/components/ui/checkbox';

type TermsCheckboxProps<
  TFieldValues extends FieldValues = FieldValues,
  TServiceName extends FieldPath<TFieldValues> = FieldPath<TFieldValues>,
  TPrivacyName extends FieldPath<TFieldValues> = FieldPath<TFieldValues>,
> = {
  control: Control<TFieldValues>;
  serviceName: TServiceName;
  privacyName: TPrivacyName;
  setValue: UseFormSetValue<TFieldValues>;
  serviceValue: boolean;
  privacyValue: boolean;
};

export function TermsCheckbox<
  TFieldValues extends FieldValues = FieldValues,
  TServiceName extends FieldPath<TFieldValues> = FieldPath<TFieldValues>,
  TPrivacyName extends FieldPath<TFieldValues> = FieldPath<TFieldValues>,
>({
  control,
  serviceName,
  privacyName,
  setValue,
  serviceValue,
  privacyValue,
}: TermsCheckboxProps<TFieldValues, TServiceName, TPrivacyName>) {
  const allAgreed = serviceValue && privacyValue;

  const handleAllAgreedChange = (checked: boolean) => {
    setValue(serviceName, checked as never);
    setValue(privacyName, checked as never);
  };

  return (
    <div className="flex flex-col gap-3">
      <FormLabel>약관 동의</FormLabel>

      <label className="flex cursor-pointer items-center gap-2">
        <Checkbox
          checked={allAgreed}
          onCheckedChange={handleAllAgreedChange}
        />
        <span className="text-sm font-medium text-slate-900">전체 동의</span>
      </label>

      <div className="ml-6 flex flex-col gap-2">
        <FormField
          control={control}
          name={serviceName}
          render={({ field }) => (
            <FormItem className="flex items-center gap-2 space-y-0">
              <FormControl>
                <Checkbox
                  checked={field.value}
                  onCheckedChange={field.onChange}
                />
              </FormControl>
              <FormLabel className="cursor-pointer text-sm font-normal text-slate-700">
                서비스 이용약관 동의 (필수)
              </FormLabel>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={control}
          name={privacyName}
          render={({ field }) => (
            <FormItem className="flex items-center gap-2 space-y-0">
              <FormControl>
                <Checkbox
                  checked={field.value}
                  onCheckedChange={field.onChange}
                />
              </FormControl>
              <FormLabel className="cursor-pointer text-sm font-normal text-slate-700">
                개인정보 처리방침 동의 (필수)
              </FormLabel>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>
    </div>
  );
}
