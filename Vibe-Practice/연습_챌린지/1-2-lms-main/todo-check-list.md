# TODO 항목 구현 가능 여부 종합 리포트

> 생성일: 2025-10-09
> 최종 수정일: 2025-10-09
> 분석 대상: LMS 프로젝트 코드베이스
> 상태: ✅ 구현 방안 확정

---

## 📌 실행 요약 (Executive Summary)

코드베이스에서 **총 3개의 TODO 항목**을 발견했으며, 모두 구현 가능한 상태입니다.

### 발견된 TODO
1. ✅ **과제 생성 페이지** - 코스 목록 API 연동 (즉시 구현 가능)
2. ⚠️ **코스 생성 페이지** - 카테고리/난이도 API 연동 (추가 작업 필요)
3. ⚠️ **코스 편집 페이지** - 카테고리/난이도 API 연동 (추가 작업 필요)

### 채택된 솔루션
- **옵션 A**: 공개 메타데이터 엔드포인트 추가 (권장 방식 채택)
- **이유**: 장기 유지보수성, 확장성, 보안성 우수

### 예상 소요 시간
- **Phase 1** (기초 작업): 30분
- **Phase 2** (API 구현): 1-1.5시간
- **총 소요 시간**: 약 2시간

---

## 📋 발견된 TODO 목록

### 1. 코스 생성 페이지 - 카테고리/난이도 데이터
**위치:** `src/app/instructor/courses/new/page.tsx:6`
```typescript
// TODO: 실제로는 카테고리/난이도 데이터를 fetch해야 함
```

**현재 코드:**
```typescript
const mockCategories = [
  { id: '1', name: '프로그래밍' },
  { id: '2', name: '디자인' },
];

const mockDifficulties = [
  { id: '1', name: '초급', level: 1 },
  { id: '2', name: '중급', level: 2 },
  { id: '3', name: '고급', level: 3 },
];
```

---

### 2. 코스 편집 페이지 - 카테고리/난이도 데이터
**위치:** `src/app/instructor/courses/[courseId]/edit/page.tsx:18`
```typescript
// TODO: 실제로는 카테고리/난이도 데이터를 fetch해야 함
```

**현재 코드:** (1번과 동일한 mock 데이터 사용)

---

### 3. 과제 생성 페이지 - 코스 목록 데이터
**위치:** `src/app/instructor/assignments/new/page.tsx:9`
```typescript
// TODO: Replace with actual courses data from API
```

**현재 코드:**
```typescript
const mockCourses = [
  { id: '1', title: 'Introduction to Programming' },
  { id: '2', title: 'Web Development Basics' },
  { id: '3', title: 'Database Design' },
];
```

---

## ✅ 즉시 구현 가능한 TODO

### TODO #3: 과제 생성 페이지 - 코스 목록 가져오기

**상태:** ✅ **완전히 구현 가능** (모든 필수 리소스 존재)

#### 필요한 리소스 체크리스트
- ✅ 데이터베이스 테이블: `courses` (존재)
- ✅ 백엔드 라우트: `GET /api/instructor/courses` (존재)
- ✅ 백엔드 서비스: `getMyCourses()` (존재)
  - 파일: `src/features/courses/backend/service.ts:774`
- ✅ 프론트엔드 훅: `useMyCourses()` (존재)
  - 파일: `src/features/courses/hooks/useMyCourses.ts:20`
- ✅ 스키마 정의: `MyCoursesResponse` (존재)
  - 파일: `src/features/courses/lib/dto.ts`

#### 구현 방법

**변경 전:**
```typescript
// src/app/instructor/assignments/new/page.tsx
const mockCourses = [
  { id: '1', title: 'Introduction to Programming' },
  { id: '2', title: 'Web Development Basics' },
  { id: '3', title: 'Database Design' },
];

export default function CreateAssignmentPage() {
  // ...
  return (
    <AssignmentForm
      courses={mockCourses}
      onSubmit={handleSubmit}
      isSubmitting={createMutation.isPending}
    />
  );
}
```

**변경 후:**
```typescript
// src/app/instructor/assignments/new/page.tsx
'use client';

import { useMyCourses } from '@/features/courses/hooks/useMyCourses';
import { Skeleton } from '@/components/ui/skeleton';

export default function CreateAssignmentPage() {
  const router = useRouter();
  const createMutation = useCreateAssignment();
  const { data: myCoursesData, isLoading, error } = useMyCourses();

  // 로딩 상태 처리
  if (isLoading) {
    return (
      <div className="container mx-auto py-8 max-w-3xl">
        <Skeleton className="h-10 w-64 mb-4" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  // 에러 상태 처리
  if (error || !myCoursesData) {
    return (
      <div className="container mx-auto py-8 max-w-3xl">
        <div className="text-center text-destructive">
          코스 목록을 불러올 수 없습니다.
        </div>
      </div>
    );
  }

  // API 데이터를 AssignmentForm이 요구하는 형식으로 변환
  const courses = myCoursesData.courses.map(course => ({
    id: course.id,
    title: course.title,
  }));

  const handleSubmit = (data: CreateAssignmentRequest) => {
    // ... 기존 로직
  };

  return (
    <div className="container mx-auto py-8 max-w-3xl">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">새 과제 만들기</CardTitle>
        </CardHeader>
        <CardContent>
          <AssignmentForm
            courses={courses}
            onSubmit={handleSubmit}
            isSubmitting={createMutation.isPending}
          />
        </CardContent>
      </Card>
    </div>
  );
}
```

#### 예상 소요 시간
- **10-15분** (import 추가, 로딩/에러 상태 처리, 데이터 변환)

---

## ⚠️ 추가 작업 필요한 TODO

### TODO #1-2: 코스 생성/편집 페이지 - 카테고리/난이도 데이터

**상태:** ⚠️ **추가 작업 필요** (백엔드 엔드포인트 접근 권한 문제)

#### 현재 상황 분석

**✅ 존재하는 리소스:**
1. **데이터베이스 테이블**
   - `categories` 테이블 (파일: `supabase/migrations/0002_create_lms_schema.sql:32`)
   - `difficulty_levels` 테이블 (파일: `supabase/migrations/0002_create_lms_schema.sql:43`)

2. **백엔드 서비스**
   - `getCategories()` (파일: `src/features/metadata/backend/service.ts:19`)
   - `getDifficulties()` (파일: `src/features/metadata/backend/service.ts:207`)

3. **프론트엔드 훅**
   - `useCategories()` (파일: `src/features/metadata/hooks/useCategories.ts:20`)
   - `useDifficulties()` (파일: `src/features/metadata/hooks/useDifficulties.ts:20`)

4. **스키마 정의**
   - `CategoriesListResponse`, `DifficultiesListResponse` (파일: `src/features/metadata/backend/schema.ts`)

**❌ 문제점:**
- 엔드포인트가 `requireRole(['operator'])`로 보호되어 있어 Instructor가 접근 불가
- 현재 엔드포인트:
  - `GET /api/operator/metadata/categories` (Operator 전용)
  - `GET /api/operator/metadata/difficulties` (Operator 전용)

---

## ✅ 채택된 해결 방법

### 솔루션: Instructor용 공개 엔드포인트 추가 (옵션 A 채택)

**장점:**
- 권한 분리가 명확함
- 활성화된 항목만 노출 가능
- 보안성 우수

**구현 방법:**

**1단계: 백엔드 서비스 함수 추가**
```typescript
// src/features/metadata/backend/service.ts에 추가

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
      .eq('is_active', true)  // 활성화된 항목만
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
      .eq('is_active', true)  // 활성화된 항목만
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
```

**2단계: 공개 라우트 추가**
```typescript
// src/features/metadata/backend/route.ts에 추가

export const registerMetadataRoutes = (app: Hono<AppEnv>) => {
  // 기존 operator 전용 라우트들...

  /**
   * GET /api/metadata/categories
   * 활성화된 카테고리 목록 조회 (인증 불필요, 공개)
   */
  app.get('/api/metadata/categories', async (c) => {
    const logger = getLogger(c);
    logger.info('Fetching active categories (public)');

    const supabase = getSupabase(c);
    const result = await getActiveCategories(supabase);

    return respond(c, result);
  });

  /**
   * GET /api/metadata/difficulties
   * 활성화된 난이도 목록 조회 (인증 불필요, 공개)
   */
  app.get('/api/metadata/difficulties', async (c) => {
    const logger = getLogger(c);
    logger.info('Fetching active difficulties (public)');

    const supabase = getSupabase(c);
    const result = await getActiveDifficulties(supabase);

    return respond(c, result);
  });
};
```

**3단계: 프론트엔드 훅 추가**
```typescript
// src/features/metadata/hooks/useActiveCategories.ts (신규 파일)
'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  CategoriesListResponseSchema,
  type CategoriesListResponse,
} from '../lib/dto';

const getActiveCategories = async (): Promise<CategoriesListResponse> => {
  try {
    const { data } = await apiClient.get('/api/metadata/categories');
    return CategoriesListResponseSchema.parse(data);
  } catch (error) {
    const message = extractApiErrorMessage(error, '카테고리 목록 조회에 실패했습니다.');
    throw new Error(message);
  }
};

export const useActiveCategories = () => {
  return useQuery({
    queryKey: ['metadata', 'categories', 'active'],
    queryFn: getActiveCategories,
    staleTime: 5 * 60 * 1000, // 5분 캐시
  });
};
```

```typescript
// src/features/metadata/hooks/useActiveDifficulties.ts (신규 파일)
'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  DifficultiesListResponseSchema,
  type DifficultiesListResponse,
} from '../lib/dto';

const getActiveDifficulties = async (): Promise<DifficultiesListResponse> => {
  try {
    const { data } = await apiClient.get('/api/metadata/difficulties');
    return DifficultiesListResponseSchema.parse(data);
  } catch (error) {
    const message = extractApiErrorMessage(error, '난이도 목록 조회에 실패했습니다.');
    throw new Error(message);
  }
};

export const useActiveDifficulties = () => {
  return useQuery({
    queryKey: ['metadata', 'difficulties', 'active'],
    queryFn: getActiveDifficulties,
    staleTime: 5 * 60 * 1000, // 5분 캐시
  });
};
```

**4단계: 페이지에 적용**
```typescript
// src/app/instructor/courses/new/page.tsx
'use client';

import { CourseForm } from '@/features/courses/components/course-form';
import { useActiveCategories } from '@/features/metadata/hooks/useActiveCategories';
import { useActiveDifficulties } from '@/features/metadata/hooks/useActiveDifficulties';
import { Skeleton } from '@/components/ui/skeleton';

export default function CreateCoursePage() {
  const { data: categoriesData, isLoading: isCategoriesLoading } = useActiveCategories();
  const { data: difficultiesData, isLoading: isDifficultiesLoading } = useActiveDifficulties();

  if (isCategoriesLoading || isDifficultiesLoading) {
    return (
      <div className="container mx-auto max-w-2xl py-8">
        <Skeleton className="h-10 w-64 mb-4" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  const categories = categoriesData?.categories.map(cat => ({
    id: cat.id,
    name: cat.name,
  })) || [];

  const difficulties = difficultiesData?.difficulties.map(diff => ({
    id: diff.id,
    name: diff.name,
    level: diff.level,
  })) || [];

  return (
    <div className="container mx-auto max-w-2xl py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">코스 생성</h1>
        <p className="text-muted-foreground mt-2">
          새로운 코스를 생성합니다. 생성 후 과제를 추가할 수 있습니다.
        </p>
      </div>
      <CourseForm
        mode="create"
        categories={categories}
        difficulties={difficulties}
      />
    </div>
  );
}
```

**예상 소요 시간:** 1-1.5시간

---

## 🗄️ 추가 필요 사항: Seed 데이터

현재 `categories`와 `difficulty_levels` 테이블에 기본 데이터가 없습니다.
다음 migration 파일을 생성하여 초기 데이터를 추가해야 합니다.

### Migration 파일 생성

**파일명:** `supabase/migrations/0006_seed_metadata.sql`

```sql
-- Migration: 메타데이터(카테고리, 난이도) 시드 데이터 추가
-- 설명: 코스 생성/편집 시 사용할 기본 카테고리 및 난이도 데이터 제공

BEGIN;

-- ================================================================
-- 1. 카테고리 시드 데이터
-- ================================================================

INSERT INTO public.categories (id, name, is_active, created_at, updated_at) VALUES
  (gen_random_uuid(), '프로그래밍', true, now(), now()),
  (gen_random_uuid(), '데이터 과학', true, now(), now()),
  (gen_random_uuid(), '웹 개발', true, now(), now()),
  (gen_random_uuid(), '모바일 개발', true, now(), now()),
  (gen_random_uuid(), 'DevOps', true, now(), now()),
  (gen_random_uuid(), '디자인', true, now(), now()),
  (gen_random_uuid(), '비즈니스', true, now(), now()),
  (gen_random_uuid(), '마케팅', true, now(), now())
ON CONFLICT (name) DO NOTHING;

COMMENT ON TABLE public.categories IS '카테고리 시드 데이터 추가됨';

-- ================================================================
-- 2. 난이도 레벨 시드 데이터
-- ================================================================

INSERT INTO public.difficulty_levels (id, name, level, is_active, created_at, updated_at) VALUES
  (gen_random_uuid(), '입문', 1, true, now(), now()),
  (gen_random_uuid(), '초급', 2, true, now(), now()),
  (gen_random_uuid(), '중급', 3, true, now(), now()),
  (gen_random_uuid(), '고급', 4, true, now(), now()),
  (gen_random_uuid(), '전문가', 5, true, now(), now())
ON CONFLICT (level) DO NOTHING;

COMMENT ON TABLE public.difficulty_levels IS '난이도 레벨 시드 데이터 추가됨';

COMMIT;
```

### Migration 적용 방법

```bash
# Supabase 대시보드에서 SQL Editor를 열어 위 쿼리 실행
# 또는 Supabase CLI 사용 (로컬 환경이 있는 경우)
supabase db push
```

---

## 📊 채택된 구현 계획

### Phase 1: 즉시 구현 (30분 소요) ⚡

#### 1.1. TODO #3 - 과제 생성 페이지 API 연동
- ✅ **파일**: `src/app/instructor/assignments/new/page.tsx`
- ✅ **작업**: `useMyCourses()` 훅 적용
- ✅ **소요 시간**: 15분

#### 1.2. Seed 데이터 추가
- 🗄️ **파일**: `supabase/migrations/0006_seed_metadata.sql`
- 🗄️ **작업**: 카테고리/난이도 기본 데이터 생성
- 🗄️ **소요 시간**: 15분

---

### Phase 2: 메타데이터 공개 API 구현 (1-1.5시간 소요) 🚀

#### 2.1. 백엔드 서비스 함수 추가
- ⚠️ **파일**: `src/features/metadata/backend/service.ts`
- ⚠️ **작업**:
  - `getActiveCategories()` 함수 추가
  - `getActiveDifficulties()` 함수 추가
- ⚠️ **소요 시간**: 20분

#### 2.2. 백엔드 라우트 추가
- ⚠️ **파일**: `src/features/metadata/backend/route.ts`
- ⚠️ **작업**:
  - `GET /api/metadata/categories` 라우트 추가
  - `GET /api/metadata/difficulties` 라우트 추가
- ⚠️ **소요 시간**: 15분

#### 2.3. 프론트엔드 훅 생성
- ⚠️ **파일**:
  - `src/features/metadata/hooks/useActiveCategories.ts` (신규)
  - `src/features/metadata/hooks/useActiveDifficulties.ts` (신규)
- ⚠️ **소요 시간**: 20분

#### 2.4. 페이지 적용
- ⚠️ **파일**:
  - `src/app/instructor/courses/new/page.tsx`
  - `src/app/instructor/courses/[courseId]/edit/page.tsx`
- ⚠️ **작업**: API 훅 적용 및 mock 데이터 제거
- ⚠️ **소요 시간**: 20-30분

#### 2.5. 테스트 및 검증
- ⚠️ **작업**:
  - 빌드 테스트 (`npm run build`)
  - 타입 체크 (`npm run type-check`)
  - 브라우저 기능 테스트
- ⚠️ **소요 시간**: 15분

---

## 🔍 구현 체크리스트

### Phase 1: 즉시 구현

#### TODO #3 - 과제 생성 페이지
- [ ] `src/app/instructor/assignments/new/page.tsx` 파일 수정
- [ ] `useMyCourses()` 훅 import 및 적용
- [ ] 로딩/에러 상태 처리 추가
- [ ] `mockCourses` 제거 및 실제 API 데이터로 교체
- [ ] 빌드 테스트 (`npm run build`)
- [ ] 브라우저 기능 테스트

#### Seed 데이터 추가
- [ ] `supabase/migrations/0006_seed_metadata.sql` 파일 생성
- [ ] Supabase 대시보드에서 SQL Editor로 migration 실행
- [ ] 데이터 확인 쿼리 실행:
  - [ ] `SELECT * FROM public.categories;`
  - [ ] `SELECT * FROM public.difficulty_levels;`

---

### Phase 2: 메타데이터 공개 API 구현

#### 백엔드 서비스 레이어
- [ ] `src/features/metadata/backend/service.ts` 파일 수정
  - [ ] `getActiveCategories()` 함수 추가
  - [ ] `getActiveDifficulties()` 함수 추가

#### 백엔드 라우트 레이어
- [ ] `src/features/metadata/backend/route.ts` 파일 수정
  - [ ] `GET /api/metadata/categories` 라우트 추가
  - [ ] `GET /api/metadata/difficulties` 라우트 추가

#### 프론트엔드 훅 레이어
- [ ] `src/features/metadata/hooks/useActiveCategories.ts` 파일 생성
- [ ] `src/features/metadata/hooks/useActiveDifficulties.ts` 파일 생성

#### 페이지 적용
- [ ] `src/app/instructor/courses/new/page.tsx` 파일 수정
  - [ ] 새 훅 import
  - [ ] 로딩 상태 처리
  - [ ] mock 데이터 제거
- [ ] `src/app/instructor/courses/[courseId]/edit/page.tsx` 파일 수정
  - [ ] 새 훅 import
  - [ ] 로딩 상태 처리
  - [ ] mock 데이터 제거

#### 최종 검증
- [ ] 타입 체크 (`npm run type-check`)
- [ ] 빌드 테스트 (`npm run build`)
- [ ] 브라우저 기능 테스트
  - [ ] 코스 생성 페이지 정상 작동 확인
  - [ ] 코스 편집 페이지 정상 작동 확인
  - [ ] 과제 생성 페이지 정상 작동 확인

---

## 📁 관련 파일 참조

### 백엔드 파일
| 파일 경로 | 설명 | 주요 라인 |
|-----------|------|-----------|
| `supabase/migrations/0002_create_lms_schema.sql` | 메타데이터 테이블 정의 | 32 (categories), 43 (difficulty_levels) |
| `src/features/metadata/backend/service.ts` | 메타데이터 서비스 로직 | 19 (getCategories), 207 (getDifficulties) |
| `src/features/metadata/backend/route.ts` | 메타데이터 API 라우트 | 26 (categories), 104 (difficulties) |
| `src/features/metadata/backend/schema.ts` | 메타데이터 스키마 정의 | 전체 |
| `src/features/courses/backend/service.ts` | 코스 서비스 로직 | 774 (getMyCourses) |
| `src/features/courses/backend/route.ts` | 코스 API 라우트 | 156 (내 코스 목록) |

### 프론트엔드 파일
| 파일 경로 | 설명 | 주요 라인 |
|-----------|------|-----------|
| `src/features/metadata/hooks/useCategories.ts` | 카테고리 조회 훅 (Operator용) | 20 |
| `src/features/metadata/hooks/useDifficulties.ts` | 난이도 조회 훅 (Operator용) | 20 |
| `src/features/courses/hooks/useMyCourses.ts` | 내 코스 목록 훅 | 20 |
| `src/app/instructor/courses/new/page.tsx` | 코스 생성 페이지 | 6 (TODO) |
| `src/app/instructor/courses/[courseId]/edit/page.tsx` | 코스 편집 페이지 | 18 (TODO) |
| `src/app/instructor/assignments/new/page.tsx` | 과제 생성 페이지 | 9 (TODO) |

---

## 🎯 최종 구현 결정

### ✅ 채택된 접근 방식

본 프로젝트에서는 **장기적인 유지보수성과 확장성**을 고려하여 다음 방식을 채택했습니다:

#### Phase 1: 기초 데이터 및 즉시 해결 가능한 TODO (30분)
1. **Seed 데이터 추가**
   - 카테고리 8개 (프로그래밍, 데이터 과학, 웹 개발, 모바일 개발, DevOps, 디자인, 비즈니스, 마케팅)
   - 난이도 5개 (입문, 초급, 중급, 고급, 전문가)

2. **TODO #3 구현**
   - 과제 생성 페이지에 `useMyCourses()` 훅 적용
   - mock 데이터 제거 및 실제 API 연동

#### Phase 2: 공개 메타데이터 엔드포인트 추가 (1-1.5시간)
- **TODO #1-2 구현**
  - Instructor 및 일반 사용자가 접근 가능한 공개 API 추가
  - 활성화된 카테고리/난이도만 노출 (보안)
  - 기존 Operator 전용 API와 분리 (권한 명확성)

### 🎁 이점

1. **확장성**: 향후 learner가 코스 검색 시 동일 API 재사용 가능
2. **보안성**: 활성화된 메타데이터만 노출, 비활성 데이터 보호
3. **유지보수성**: 권한별 API 분리로 코드 의도 명확화
4. **성능**: 공개 API는 인증 없이 빠른 응답 가능

### 📈 예상 총 소요 시간
- **Phase 1**: 30분
- **Phase 2**: 1-1.5시간
- **총 소요 시간**: 약 2시간

---

## 📝 참고 사항

1. **데이터베이스 상태 확인**
   ```sql
   -- Supabase SQL Editor에서 실행
   SELECT COUNT(*) FROM public.categories;
   SELECT COUNT(*) FROM public.difficulty_levels;
   ```
   - 0건이면 seed 데이터 추가 필요

2. **빌드 검증**
   ```bash
   npm run build
   npm run type-check
   ```

3. **API 테스트**
   - Postman 또는 curl로 엔드포인트 테스트
   - 브라우저 개발자 도구에서 Network 탭 확인

---

**작성자:** Claude Code
**최종 수정일:** 2025-10-09
