import { z } from 'zod';

// 카테고리 항목
export const CategoryItemSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  isActive: z.boolean(),
  createdAt: z.string(),
  updatedAt: z.string(),
});

// 난이도 항목
export const DifficultyItemSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  level: z.number().int(),
  isActive: z.boolean(),
  createdAt: z.string(),
  updatedAt: z.string(),
});

// 카테고리 목록 응답
export const CategoriesListResponseSchema = z.object({
  categories: z.array(CategoryItemSchema),
  total: z.number(),
});

// 난이도 목록 응답
export const DifficultiesListResponseSchema = z.object({
  difficulties: z.array(DifficultyItemSchema),
  total: z.number(),
});

// 카테고리 생성 요청
export const CreateCategoryRequestSchema = z.object({
  name: z.string().min(1, '카테고리 이름은 필수 항목입니다.'),
});

// 카테고리 수정 요청
export const UpdateCategoryRequestSchema = z.object({
  name: z.string().min(1).optional(),
  isActive: z.boolean().optional(),
});

// 카테고리 생성/수정 응답
export const CategoryResponseSchema = z.object({
  categoryId: z.string().uuid(),
  name: z.string(),
  isActive: z.boolean(),
  message: z.string(),
  usageCount: z.number().optional(),
});

// 난이도 생성 요청
export const CreateDifficultyRequestSchema = z.object({
  name: z.string().min(1, '난이도 이름은 필수 항목입니다.'),
  level: z.number().int().min(1, '레벨은 1 이상이어야 합니다.'),
});

// 난이도 수정 요청
export const UpdateDifficultyRequestSchema = z.object({
  name: z.string().min(1).optional(),
  level: z.number().int().min(1).optional(),
  isActive: z.boolean().optional(),
});

// 난이도 생성/수정 응답
export const DifficultyResponseSchema = z.object({
  difficultyId: z.string().uuid(),
  name: z.string(),
  level: z.number().int(),
  isActive: z.boolean(),
  message: z.string(),
  usageCount: z.number().optional(),
});

// TypeScript 타입 추출
export type CategoryItem = z.infer<typeof CategoryItemSchema>;
export type DifficultyItem = z.infer<typeof DifficultyItemSchema>;
export type CategoriesListResponse = z.infer<typeof CategoriesListResponseSchema>;
export type DifficultiesListResponse = z.infer<typeof DifficultiesListResponseSchema>;
export type CreateCategoryRequest = z.infer<typeof CreateCategoryRequestSchema>;
export type UpdateCategoryRequest = z.infer<typeof UpdateCategoryRequestSchema>;
export type CategoryResponse = z.infer<typeof CategoryResponseSchema>;
export type CreateDifficultyRequest = z.infer<typeof CreateDifficultyRequestSchema>;
export type UpdateDifficultyRequest = z.infer<typeof UpdateDifficultyRequestSchema>;
export type DifficultyResponse = z.infer<typeof DifficultyResponseSchema>;
