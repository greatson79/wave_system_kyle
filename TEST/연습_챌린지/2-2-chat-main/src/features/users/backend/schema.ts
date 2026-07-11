import { z } from 'zod';

export const UpdateNicknameRequestSchema = z.object({
  nickname: z
    .string()
    .min(2, '닉네임은 2~20자여야 합니다')
    .max(20, '닉네임은 2~20자여야 합니다')
    .regex(/^[가-힣a-zA-Z0-9]+$/, '특수문자는 사용할 수 없습니다'),
});

export const UpdateNicknameResponseSchema = z.object({
  success: z.literal(true),
  data: z.object({
    id: z.string(),
    nickname: z.string(),
    email: z.string(),
  }),
});

export type UpdateNicknameRequest = z.infer<typeof UpdateNicknameRequestSchema>;
export type UpdateNicknameResponse = z.infer<
  typeof UpdateNicknameResponseSchema
>;
