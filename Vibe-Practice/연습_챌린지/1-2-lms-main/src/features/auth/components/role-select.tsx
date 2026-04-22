'use client';

import type { Control, FieldPath, FieldValues } from 'react-hook-form';
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';

type RoleOption = 'learner' | 'instructor';

const roleOptions: Array<{
  value: RoleOption;
  label: string;
  description: string;
}> = [
  {
    value: 'learner',
    label: '학습자',
    description: '코스를 탐색하고 학습합니다',
  },
  {
    value: 'instructor',
    label: '강사',
    description: '코스를 개설하고 관리합니다',
  },
];

type RoleSelectProps<
  TFieldValues extends FieldValues = FieldValues,
  TName extends FieldPath<TFieldValues> = FieldPath<TFieldValues>,
> = {
  control: Control<TFieldValues>;
  name: TName;
};

export function RoleSelect<
  TFieldValues extends FieldValues = FieldValues,
  TName extends FieldPath<TFieldValues> = FieldPath<TFieldValues>,
>({ control, name }: RoleSelectProps<TFieldValues, TName>) {
  return (
    <FormField
      control={control}
      name={name}
      render={({ field }) => (
        <FormItem>
          <FormLabel>역할 선택</FormLabel>
          <FormControl>
            <div className="flex flex-col gap-3">
              {roleOptions.map((option) => (
                <label
                  key={option.value}
                  className={`flex cursor-pointer items-start gap-3 rounded-lg border p-4 transition ${
                    field.value === option.value
                      ? 'border-slate-900 bg-slate-50'
                      : 'border-slate-200 hover:border-slate-300'
                  }`}
                >
                  <input
                    type="radio"
                    value={option.value}
                    checked={field.value === option.value}
                    onChange={(e) => field.onChange(e.target.value)}
                    className="mt-1"
                  />
                  <div className="flex flex-col gap-1">
                    <span className="font-medium text-slate-900">
                      {option.label}
                    </span>
                    <span className="text-sm text-slate-600">
                      {option.description}
                    </span>
                  </div>
                </label>
              ))}
            </div>
          </FormControl>
          <FormMessage />
        </FormItem>
      )}
    />
  );
}
