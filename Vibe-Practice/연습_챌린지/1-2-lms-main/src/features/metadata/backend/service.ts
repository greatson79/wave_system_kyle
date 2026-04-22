import type { SupabaseClient } from '@supabase/supabase-js';
import type { HandlerResult } from '@/backend/http/response';
import { success, failure } from '@/backend/http/response';
import { metadataErrorCodes, type MetadataServiceError } from './error';
import type {
  CategoriesListResponse,
  DifficultiesListResponse,
  CreateCategoryRequest,
  UpdateCategoryRequest,
  CategoryResponse,
  CreateDifficultyRequest,
  UpdateDifficultyRequest,
  DifficultyResponse,
} from './schema';

/**
 * 카테고리 목록 조회
 */
export const getCategories = async (
  supabase: SupabaseClient,
): Promise<HandlerResult<CategoriesListResponse, MetadataServiceError>> => {
  try {
    const { data: categories, error, count } = await supabase
      .from('categories')
      .select('*', { count: 'exact' })
      .order('name', { ascending: true });

    if (error || !categories) {
      return failure(
        500,
        metadataErrorCodes.invalidRequest,
        error?.message || '카테고리 목록 조회에 실패했습니다.',
      );
    }

    const formattedCategories = categories.map((cat: any) => ({
      id: cat.id,
      name: cat.name,
      isActive: cat.is_active,
      createdAt: cat.created_at,
      updatedAt: cat.updated_at,
    }));

    return success({
      categories: formattedCategories,
      total: count || 0,
    });
  } catch (err) {
    return failure(
      500,
      metadataErrorCodes.invalidRequest,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

/**
 * 카테고리 생성
 */
export const createCategory = async (
  supabase: SupabaseClient,
  data: CreateCategoryRequest,
): Promise<HandlerResult<CategoryResponse, MetadataServiceError>> => {
  try {
    // 이름 중복 확인
    const { data: existing } = await supabase
      .from('categories')
      .select('id')
      .eq('name', data.name)
      .maybeSingle();

    if (existing) {
      return failure(
        409,
        metadataErrorCodes.duplicateName,
        '이미 존재하는 카테고리 이름입니다.',
      );
    }

    // 카테고리 생성
    const { data: category, error } = await supabase
      .from('categories')
      .insert({
        name: data.name,
        is_active: true,
      })
      .select('id, name, is_active')
      .single();

    if (error || !category) {
      return failure(
        500,
        metadataErrorCodes.createFailed,
        error?.message || '카테고리 생성에 실패했습니다.',
      );
    }

    return success(
      {
        categoryId: category.id,
        name: category.name,
        isActive: category.is_active,
        message: '카테고리가 생성되었습니다.',
      },
      201,
    );
  } catch (err) {
    return failure(
      500,
      metadataErrorCodes.createFailed,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

/**
 * 카테고리 수정
 */
export const updateCategory = async (
  supabase: SupabaseClient,
  categoryId: string,
  data: UpdateCategoryRequest,
): Promise<HandlerResult<CategoryResponse, MetadataServiceError>> => {
  try {
    // 카테고리 존재 확인
    const { data: existing, error: fetchError } = await supabase
      .from('categories')
      .select('id, name')
      .eq('id', categoryId)
      .maybeSingle();

    if (fetchError || !existing) {
      return failure(
        404,
        metadataErrorCodes.categoryNotFound,
        '카테고리를 찾을 수 없습니다.',
      );
    }

    // 이름 변경 시 중복 확인
    if (data.name && data.name !== existing.name) {
      const { data: duplicate } = await supabase
        .from('categories')
        .select('id')
        .eq('name', data.name)
        .neq('id', categoryId)
        .maybeSingle();

      if (duplicate) {
        return failure(
          409,
          metadataErrorCodes.duplicateName,
          '이미 존재하는 카테고리 이름입니다.',
        );
      }
    }

    // 카테고리 업데이트
    const updateData: any = {};
    if (data.name !== undefined) updateData.name = data.name;
    if (data.isActive !== undefined) updateData.is_active = data.isActive;

    const { data: updated, error: updateError } = await supabase
      .from('categories')
      .update(updateData)
      .eq('id', categoryId)
      .select('id, name, is_active')
      .single();

    if (updateError || !updated) {
      return failure(
        500,
        metadataErrorCodes.updateFailed,
        updateError?.message || '카테고리 수정에 실패했습니다.',
      );
    }

    // 비활성화 시 사용 중인 코스 수 조회
    let usageCount: number | undefined;
    if (data.isActive === false) {
      const { count } = await supabase
        .from('courses')
        .select('id', { count: 'exact', head: true })
        .eq('category_id', categoryId);
      usageCount = count || 0;
    }

    return success({
      categoryId: updated.id,
      name: updated.name,
      isActive: updated.is_active,
      message: '카테고리가 수정되었습니다.',
      usageCount,
    });
  } catch (err) {
    return failure(
      500,
      metadataErrorCodes.updateFailed,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

/**
 * 난이도 목록 조회
 */
export const getDifficulties = async (
  supabase: SupabaseClient,
): Promise<HandlerResult<DifficultiesListResponse, MetadataServiceError>> => {
  try {
    const { data: difficulties, error, count } = await supabase
      .from('difficulty_levels')
      .select('*', { count: 'exact' })
      .order('level', { ascending: true });

    if (error || !difficulties) {
      return failure(
        500,
        metadataErrorCodes.invalidRequest,
        error?.message || '난이도 목록 조회에 실패했습니다.',
      );
    }

    const formattedDifficulties = difficulties.map((diff: any) => ({
      id: diff.id,
      name: diff.name,
      level: diff.level,
      isActive: diff.is_active,
      createdAt: diff.created_at,
      updatedAt: diff.updated_at,
    }));

    return success({
      difficulties: formattedDifficulties,
      total: count || 0,
    });
  } catch (err) {
    return failure(
      500,
      metadataErrorCodes.invalidRequest,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

/**
 * 난이도 생성
 */
export const createDifficulty = async (
  supabase: SupabaseClient,
  data: CreateDifficultyRequest,
): Promise<HandlerResult<DifficultyResponse, MetadataServiceError>> => {
  try {
    // 이름 중복 확인
    const { data: existingName } = await supabase
      .from('difficulty_levels')
      .select('id')
      .eq('name', data.name)
      .maybeSingle();

    if (existingName) {
      return failure(
        409,
        metadataErrorCodes.duplicateName,
        '이미 존재하는 난이도 이름입니다.',
      );
    }

    // 레벨 중복 확인
    const { data: existingLevel } = await supabase
      .from('difficulty_levels')
      .select('id')
      .eq('level', data.level)
      .maybeSingle();

    if (existingLevel) {
      return failure(
        409,
        metadataErrorCodes.duplicateLevel,
        '이미 존재하는 레벨입니다.',
      );
    }

    // 난이도 생성
    const { data: difficulty, error } = await supabase
      .from('difficulty_levels')
      .insert({
        name: data.name,
        level: data.level,
        is_active: true,
      })
      .select('id, name, level, is_active')
      .single();

    if (error || !difficulty) {
      return failure(
        500,
        metadataErrorCodes.createFailed,
        error?.message || '난이도 생성에 실패했습니다.',
      );
    }

    return success(
      {
        difficultyId: difficulty.id,
        name: difficulty.name,
        level: difficulty.level,
        isActive: difficulty.is_active,
        message: '난이도가 생성되었습니다.',
      },
      201,
    );
  } catch (err) {
    return failure(
      500,
      metadataErrorCodes.createFailed,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

/**
 * 난이도 수정
 */
export const updateDifficulty = async (
  supabase: SupabaseClient,
  difficultyId: string,
  data: UpdateDifficultyRequest,
): Promise<HandlerResult<DifficultyResponse, MetadataServiceError>> => {
  try {
    // 난이도 존재 확인
    const { data: existing, error: fetchError } = await supabase
      .from('difficulty_levels')
      .select('id, name, level')
      .eq('id', difficultyId)
      .maybeSingle();

    if (fetchError || !existing) {
      return failure(
        404,
        metadataErrorCodes.difficultyNotFound,
        '난이도를 찾을 수 없습니다.',
      );
    }

    // 이름 변경 시 중복 확인
    if (data.name && data.name !== existing.name) {
      const { data: duplicate } = await supabase
        .from('difficulty_levels')
        .select('id')
        .eq('name', data.name)
        .neq('id', difficultyId)
        .maybeSingle();

      if (duplicate) {
        return failure(
          409,
          metadataErrorCodes.duplicateName,
          '이미 존재하는 난이도 이름입니다.',
        );
      }
    }

    // 레벨 변경 시 중복 확인
    if (data.level !== undefined && data.level !== existing.level) {
      const { data: duplicate } = await supabase
        .from('difficulty_levels')
        .select('id')
        .eq('level', data.level)
        .neq('id', difficultyId)
        .maybeSingle();

      if (duplicate) {
        return failure(
          409,
          metadataErrorCodes.duplicateLevel,
          '이미 존재하는 레벨입니다.',
        );
      }
    }

    // 난이도 업데이트
    const updateData: any = {};
    if (data.name !== undefined) updateData.name = data.name;
    if (data.level !== undefined) updateData.level = data.level;
    if (data.isActive !== undefined) updateData.is_active = data.isActive;

    const { data: updated, error: updateError } = await supabase
      .from('difficulty_levels')
      .update(updateData)
      .eq('id', difficultyId)
      .select('id, name, level, is_active')
      .single();

    if (updateError || !updated) {
      return failure(
        500,
        metadataErrorCodes.updateFailed,
        updateError?.message || '난이도 수정에 실패했습니다.',
      );
    }

    // 비활성화 시 사용 중인 코스 수 조회
    let usageCount: number | undefined;
    if (data.isActive === false) {
      const { count } = await supabase
        .from('courses')
        .select('id', { count: 'exact', head: true })
        .eq('difficulty_id', difficultyId);
      usageCount = count || 0;
    }

    return success({
      difficultyId: updated.id,
      name: updated.name,
      level: updated.level,
      isActive: updated.is_active,
      message: '난이도가 수정되었습니다.',
      usageCount,
    });
  } catch (err) {
    return failure(
      500,
      metadataErrorCodes.updateFailed,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

/**
 * 활성화된 카테고리 목록 조회 (공개용)
 */
export const getActiveCategories = async (
  supabase: SupabaseClient,
): Promise<HandlerResult<CategoriesListResponse, MetadataServiceError>> => {
  try {
    const { data: categories, error, count } = await supabase
      .from('categories')
      .select('*', { count: 'exact' })
      .eq('is_active', true)
      .order('name', { ascending: true });

    if (error || !categories) {
      return failure(
        500,
        metadataErrorCodes.invalidRequest,
        error?.message || '카테고리 목록 조회에 실패했습니다.',
      );
    }

    const formattedCategories = categories.map((cat: any) => ({
      id: cat.id,
      name: cat.name,
      isActive: cat.is_active,
      createdAt: cat.created_at,
      updatedAt: cat.updated_at,
    }));

    return success({
      categories: formattedCategories,
      total: count || 0,
    });
  } catch (err) {
    return failure(
      500,
      metadataErrorCodes.invalidRequest,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};

/**
 * 활성화된 난이도 목록 조회 (공개용)
 */
export const getActiveDifficulties = async (
  supabase: SupabaseClient,
): Promise<HandlerResult<DifficultiesListResponse, MetadataServiceError>> => {
  try {
    const { data: difficulties, error, count } = await supabase
      .from('difficulty_levels')
      .select('*', { count: 'exact' })
      .eq('is_active', true)
      .order('level', { ascending: true });

    if (error || !difficulties) {
      return failure(
        500,
        metadataErrorCodes.invalidRequest,
        error?.message || '난이도 목록 조회에 실패했습니다.',
      );
    }

    const formattedDifficulties = difficulties.map((diff: any) => ({
      id: diff.id,
      name: diff.name,
      level: diff.level,
      isActive: diff.is_active,
      createdAt: diff.created_at,
      updatedAt: diff.updated_at,
    }));

    return success({
      difficulties: formattedDifficulties,
      total: count || 0,
    });
  } catch (err) {
    return failure(
      500,
      metadataErrorCodes.invalidRequest,
      err instanceof Error ? err.message : 'Unknown error',
    );
  }
};
