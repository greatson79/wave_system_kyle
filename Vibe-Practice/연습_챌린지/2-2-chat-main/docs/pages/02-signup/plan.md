# 회원가입 페이지 구현 계획

## 문서 정보

- **페이지**: 회원가입 페이지 (`/signup`)
- **작성일**: 2025-10-20
- **참고 문서**:
  - `/docs/prd.md` - PRD 3.1, 6.1 (F-001)
  - `/docs/userflow.md` - 1.1 회원가입
  - `/docs/usecases/1-signup/spec.md` - UC-001 회원가입
  - `/docs/common-modules.md` - 공통 모듈 계획

---

## 1. 페이지 개요

### 1.1 목적

신규 사용자가 닉네임, 이메일, 비밀번호를 입력하여 계정을 생성하고 채팅 서비스를 이용할 수 있도록 한다.

### 1.2 주요 기능

- 닉네임, 이메일, 비밀번호, 비밀번호 확인 입력 폼
- 클라이언트 측 유효성 검증 (React Hook Form + Zod)
- Supabase Auth 기반 회원가입 API 호출
- 사용자 프로필 테이블에 닉네임 저장
- 회원가입 완료 시 로그인 페이지로 리다이렉트

### 1.3 접근 제어

- **비로그인 사용자**: 접근 가능
- **로그인 사용자**: 자동으로 홈(`/`)으로 리다이렉트

---

## 2. 파일 구조

### 2.1 프론트엔드

```
src/
├── app/
│   └── signup/
│       └── page.tsx                          # 회원가입 페이지 (기존)
└── features/
    └── auth/
        ├── components/
        │   └── signup-form.tsx               # 회원가입 폼 컴포넌트 (신규)
        ├── hooks/
        │   ├── useCurrentUser.ts             # 현재 사용자 훅 (기존)
        │   └── useSignupMutation.ts          # 회원가입 Mutation 훅 (신규)
        ├── context/
        │   └── current-user-context.tsx      # 사용자 컨텍스트 (기존)
        ├── backend/
        │   ├── schema.ts                     # 스키마 정의 (기존)
        │   └── error.ts                      # 에러 코드 (기존)
        └── types.ts                          # 타입 정의 (기존)
```

### 2.2 백엔드

```
src/
├── backend/
│   └── hono/
│       └── app.ts                            # Hono 앱 등록 (기존)
└── features/
    └── auth/
        └── backend/
            ├── route.ts                      # 회원가입 라우터 (신규)
            ├── service.ts                    # 회원가입 서비스 로직 (신규)
            ├── schema.ts                     # 요청/응답 스키마 (기존)
            └── error.ts                      # 에러 코드 (기존)
```

### 2.3 기존 파일 수정

- `src/app/signup/page.tsx`: 기존 간단한 구현을 SignupForm 컴포넌트로 교체
- `src/backend/hono/app.ts`: 회원가입 라우터 등록

---

## 3. 컴포넌트 계층 구조

```
SignupPage (app/signup/page.tsx)
└── SignupForm (features/auth/components/signup-form.tsx)
    ├── 닉네임 입력 필드
    │   └── ErrorMessage (인라인)
    ├── 이메일 입력 필드
    │   └── ErrorMessage (인라인)
    ├── 비밀번호 입력 필드
    │   └── ErrorMessage (인라인)
    ├── 비밀번호 확인 입력 필드
    │   └── ErrorMessage (인라인)
    ├── 제출 버튼 (로딩 상태)
    └── 로그인 링크
```

### 컴포넌트 책임 분리

- **SignupPage**: 페이지 레이아웃, 인증 상태 확인 및 리다이렉트
- **SignupForm**: 폼 상태 관리, 유효성 검증, API 호출, 에러 처리

---

## 4. 상태 관리

### 4.1 React Hook Form 상태

```typescript
type SignupFormData = {
  nickname: string;
  email: string;
  password: string;
  passwordConfirm: string;
};
```

### 4.2 전역 상태 (Context)

- **CurrentUserContext** (기존):
  - `isAuthenticated`: 로그인 여부
  - `user`: 현재 사용자 정보
  - `refresh()`: 사용자 정보 새로고침

### 4.3 로컬 상태 (SignupForm 컴포넌트)

- `isSubmitting`: 제출 중 여부 (React Hook Form 제공)
- `serverError`: 서버 에러 메시지 (useState)

### 4.4 상태 흐름

1. **초기 로드**:
   - `isAuthenticated` 확인 → 로그인 상태면 홈으로 리다이렉트

2. **입력 중**:
   - React Hook Form의 실시간 검증
   - 필드별 에러 메시지 표시

3. **제출 시**:
   - `isSubmitting = true`
   - API 호출 (`useSignupMutation`)
   - 성공: 로그인 페이지로 리다이렉트
   - 실패: `serverError` 설정 → 에러 메시지 표시

---

## 5. API 연동

### 5.1 엔드포인트

**POST /api/auth/signup**

### 5.2 요청/응답 스키마 (기존)

**요청**:
```typescript
// src/features/auth/backend/schema.ts (기존)
{
  nickname: string,  // 2~20자, 특수문자 제외
  email: string,     // 유효한 이메일 형식
  password: string   // 8자 이상, 영문+숫자 조합
}
```

**응답 (성공)**:
```typescript
{
  success: true,
  redirectTo: "/login"
}
```

**응답 (실패)**:
```typescript
{
  error: {
    code: string,
    message: string
  }
}
```

### 5.3 React Query 훅

**useSignupMutation** (신규):
```typescript
// src/features/auth/hooks/useSignupMutation.ts

import { useMutation } from '@tanstack/react-query';
import { apiClient } from '@/lib/remote/api-client';
import { SignupRequest, SignupResponse } from '../backend/schema';

export const useSignupMutation = () => {
  return useMutation({
    mutationFn: async (data: SignupRequest) => {
      const response = await apiClient.post<SignupResponse>(
        '/api/auth/signup',
        data
      );
      return response;
    },
  });
};
```

### 5.4 백엔드 라우터 (신규)

```typescript
// src/features/auth/backend/route.ts

import { Hono } from 'hono';
import { zValidator } from '@hono/zod-validator';
import { SignupRequestSchema } from './schema';
import { signupUser } from './service';
import { respond } from '@/backend/http/response';
import type { AppEnv } from '@/backend/hono/context';

export const authRouter = new Hono<AppEnv>();

authRouter.post(
  '/api/auth/signup',
  zValidator('json', SignupRequestSchema),
  async (c) => {
    const logger = c.get('logger');
    const supabase = c.get('supabase');
    const data = c.req.valid('json');

    logger.info('회원가입 요청', { email: data.email });

    const result = await signupUser(supabase, data);

    return respond(c, result);
  }
);
```

### 5.5 백엔드 서비스 (신규)

```typescript
// src/features/auth/backend/service.ts

import type { SupabaseClient } from '@supabase/supabase-js';
import { success, failure } from '@/backend/http/response';
import { AuthErrorCode } from './error';
import type { SignupRequest, SignupResponse } from './schema';

export async function signupUser(
  supabase: SupabaseClient,
  data: SignupRequest
) {
  // 1. Supabase Auth 사용자 생성
  const { data: authData, error: authError } = await supabase.auth.admin.createUser({
    email: data.email,
    password: data.password,
    email_confirm: true, // 이메일 인증 스킵 (개발 환경)
  });

  if (authError) {
    // 이메일 중복 에러 처리
    if (authError.message.includes('already registered')) {
      return failure(AuthErrorCode.EMAIL_DUPLICATE, 409);
    }
    return failure('SIGNUP_FAILED', 500, authError.message);
  }

  // 2. user_profiles 테이블에 닉네임 저장
  const { error: profileError } = await supabase
    .from('user_profiles')
    .insert({
      id: authData.user.id,
      nickname: data.nickname,
    });

  if (profileError) {
    // 프로필 생성 실패 (Auth 사용자는 이미 생성됨)
    // 추후 재시도 로직 또는 관리자 알림 추가 고려
    return failure('PROFILE_CREATION_FAILED', 500, profileError.message);
  }

  // 3. 성공 응답
  return success<SignupResponse>({
    success: true,
    redirectTo: '/login',
  });
}
```

---

## 6. UI/UX 상세

### 6.1 레이아웃

**데스크톱 (화면 너비 ≥ 768px)**:
- 좌우 2단 레이아웃
  - 왼쪽: 회원가입 폼
  - 오른쪽: 이미지 (picsum.photos)
- 최대 너비: 1024px (중앙 정렬)

**모바일 (화면 너비 < 768px)**:
- 세로 1단 레이아웃
- 폼만 표시 (이미지 숨김 또는 상단 배치)

### 6.2 폼 필드 구성

**1. 닉네임 입력**:
- Label: "닉네임"
- Input Type: text
- Placeholder: "2~20자, 특수문자 제외"
- 검증:
  - 필수 입력
  - 2~20자
  - 한글/영문/숫자만 허용 (특수문자 제외)

**2. 이메일 입력**:
- Label: "이메일"
- Input Type: email
- Placeholder: "example@example.com"
- AutoComplete: email
- 검증:
  - 필수 입력
  - 유효한 이메일 형식

**3. 비밀번호 입력**:
- Label: "비밀번호"
- Input Type: password
- Placeholder: "8자 이상, 영문+숫자 조합"
- AutoComplete: new-password
- 검증:
  - 필수 입력
  - 8자 이상
  - 영문+숫자 조합 (정규식: `/^(?=.*[A-Za-z])(?=.*\d)/`)

**4. 비밀번호 확인 입력**:
- Label: "비밀번호 확인"
- Input Type: password
- AutoComplete: new-password
- 검증:
  - 필수 입력
  - 비밀번호와 일치 (React Hook Form의 `validate`)

### 6.3 제출 버튼

- 텍스트: "회원가입"
- 로딩 중: "회원가입 중..."
- 비활성화 조건:
  - 폼 검증 실패
  - `isSubmitting === true`

### 6.4 에러 메시지 표시

**클라이언트 측 검증 에러**:
- 각 필드 아래에 빨간색 텍스트로 표시
- 예: "닉네임은 2~20자여야 합니다."

**서버 측 에러**:
- 폼 상단 또는 제출 버튼 위에 표시
- 예: "이미 가입된 이메일입니다."

### 6.5 로그인 링크

- 텍스트: "이미 계정이 있으신가요? 로그인으로 이동"
- 위치: 폼 하단
- 링크: `/login`

---

## 7. 에러 처리

### 7.1 클라이언트 측 에러

**유효성 검증 실패**:
- React Hook Form이 실시간 검증
- 필드별 에러 메시지 표시
- 제출 버튼 비활성화

### 7.2 서버 측 에러

**이메일 중복 (HTTP 409)**:
- 에러 코드: `AUTH_EMAIL_DUPLICATE`
- 메시지: "이미 가입된 이메일입니다."
- 처리: 이메일 필드에 포커스 이동

**프로필 생성 실패 (HTTP 500)**:
- 에러 코드: `PROFILE_CREATION_FAILED`
- 메시지: "회원가입 중 오류가 발생했습니다. 고객센터로 문의해주세요."
- 처리: 전체 에러 메시지 표시, 재시도 안내

**네트워크 오류**:
- 메시지: "네트워크 연결을 확인해주세요."
- 처리: 전체 에러 메시지 표시, 재시도 버튼

**기타 서버 오류 (HTTP 500)**:
- 메시지: "일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
- 처리: 전체 에러 메시지 표시

### 7.3 에러 복구

- 에러 발생 시 `isSubmitting` 상태 해제
- 사용자가 입력값을 수정하면 에러 메시지 자동 제거 (React Hook Form)
- 서버 에러는 재제출 시 초기화

---

## 8. 구현 순서

### Phase 1: 백엔드 구현

**우선순위: 최고** (프론트엔드가 의존하므로 먼저 구현)

1. ✅ **스키마 정의** (기존 파일 확인)
   - `src/features/auth/backend/schema.ts`
   - `SignupRequestSchema`, `SignupResponseSchema` 확인

2. ✅ **에러 코드 정의** (기존 파일 확인)
   - `src/features/auth/backend/error.ts`
   - `AUTH_EMAIL_DUPLICATE` 등 확인

3. ⬜ **서비스 로직 구현** (신규)
   - `src/features/auth/backend/service.ts` 생성
   - `signupUser()` 함수 구현
     - Supabase Auth 사용자 생성
     - user_profiles 테이블에 닉네임 저장
     - 에러 처리

4. ⬜ **라우터 등록** (신규)
   - `src/features/auth/backend/route.ts` 생성
   - `POST /api/auth/signup` 엔드포인트 구현
   - `src/backend/hono/app.ts`에 라우터 등록

5. ⬜ **API 테스트** (curl 또는 Postman)
   - 정상 케이스 테스트
   - 이메일 중복 테스트
   - 유효성 검증 실패 테스트

### Phase 2: 프론트엔드 구현

**우선순위: 높음**

6. ⬜ **React Query 훅 구현** (신규)
   - `src/features/auth/hooks/useSignupMutation.ts` 생성
   - `useMutation` 훅 구현

7. ⬜ **SignupForm 컴포넌트 구현** (신규)
   - `src/features/auth/components/signup-form.tsx` 생성
   - React Hook Form 설정
   - Zod 스키마 연동
   - API 호출 및 에러 처리

8. ⬜ **SignupPage 리팩토링** (기존 파일 수정)
   - `src/app/signup/page.tsx` 수정
   - SignupForm 컴포넌트 사용
   - 인증 상태 확인 및 리다이렉트
   - 레이아웃 적용

### Phase 3: 통합 테스트 및 개선

**우선순위: 보통**

9. ⬜ **E2E 테스트** (수동)
   - 회원가입 성공 시나리오
   - 이메일 중복 시나리오
   - 유효성 검증 실패 시나리오
   - 네트워크 오류 시나리오

10. ⬜ **UI 개선**
    - 모바일 반응형 디자인 확인
    - 접근성 개선 (aria-label, focus 관리)
    - 로딩 상태 UX 개선

11. ⬜ **에러 메시지 다국어 지원** (선택 사항)
    - 에러 메시지 상수 분리

---

## 9. 기존 코드와의 충돌 방지

### 9.1 기존 파일 재사용

- `src/features/auth/backend/schema.ts` (기존)
  - `SignupRequestSchema`, `SignupResponseSchema` 이미 정의됨
  - 수정 불필요

- `src/features/auth/backend/error.ts` (기존)
  - `AUTH_EMAIL_DUPLICATE` 등 이미 정의됨
  - 수정 불필요

- `src/features/auth/hooks/useCurrentUser.ts` (기존)
  - 인증 상태 확인용으로 재사용
  - 수정 불필요

### 9.2 신규 파일 생성

- `src/features/auth/backend/service.ts` (신규)
- `src/features/auth/backend/route.ts` (신규)
- `src/features/auth/hooks/useSignupMutation.ts` (신규)
- `src/features/auth/components/signup-form.tsx` (신규)

### 9.3 수정 필요 파일

- `src/app/signup/page.tsx` (기존):
  - 현재: 간단한 직접 구현
  - 변경: SignupForm 컴포넌트 사용으로 교체

- `src/backend/hono/app.ts` (기존):
  - 회원가입 라우터 등록 (`registerAuthRoutes(app)`)

---

## 10. 데이터베이스 마이그레이션 확인

### 10.1 필요 테이블

**user_profiles** (기존):
- `id` (uuid, PK, FK → auth.users)
- `nickname` (varchar(20), NOT NULL)
- `created_at` (timestamptz, DEFAULT NOW())

### 10.2 마이그레이션 파일 확인

- `supabase/migrations/0001_create_user_profiles.sql` 존재 여부 확인
- 없다면 생성 필요

---

## 11. 테스트 체크리스트

### 11.1 기능 테스트

- [ ] 정상 회원가입 시나리오
  - 닉네임, 이메일, 비밀번호 입력
  - 제출 버튼 클릭
  - `/login`으로 리다이렉트 확인
  - `user_profiles` 테이블에 데이터 삽입 확인

- [ ] 이메일 중복 시나리오
  - 이미 가입된 이메일 입력
  - 제출 버튼 클릭
  - "이미 가입된 이메일입니다." 에러 메시지 확인

- [ ] 유효성 검증 실패 시나리오
  - 닉네임 1자 입력 → 에러 메시지 확인
  - 이메일 형식 오류 → 에러 메시지 확인
  - 비밀번호 짧음 → 에러 메시지 확인
  - 비밀번호 불일치 → 에러 메시지 확인

- [ ] 로그인 사용자 접근 제어
  - 로그인 상태에서 `/signup` 접근
  - `/`로 자동 리다이렉트 확인

### 11.2 UI/UX 테스트

- [ ] 모바일 반응형 디자인
- [ ] 로딩 상태 표시
- [ ] 에러 메시지 표시 위치 및 스타일
- [ ] 포커스 이동 (Tab 키)
- [ ] 접근성 (스크린 리더)

### 11.3 성능 테스트

- [ ] API 응답 시간 < 500ms
- [ ] 페이지 로딩 시간 < 1.5초

---

## 12. 보안 고려사항

### 12.1 입력값 검증

- **클라이언트**: React Hook Form + Zod
- **서버**: Zod 스키마 검증 (`zValidator`)
- **XSS 방지**: 닉네임 sanitization (필요 시 `escapeHtml` 사용)

### 12.2 비밀번호 보안

- Supabase Auth가 bcrypt 해싱 처리
- HTTPS 통신으로 네트워크 암호화
- 평문 비밀번호 로그 출력 금지

### 12.3 에러 메시지 보안

- 구체적인 에러 정보 노출 방지
- 예: "이메일 또는 비밀번호가 올바르지 않습니다." (어느 쪽이 틀렸는지 명시 안 함)

---

## 13. 향후 확장 계획

### Phase 2

- [ ] 이메일 인증 기능 추가
- [ ] 소셜 로그인 (Google, GitHub 등)
- [ ] 비밀번호 강도 표시기

### Phase 3

- [ ] 회원가입 후 자동 로그인 옵션
- [ ] 프로필 이미지 업로드
- [ ] 약관 동의 체크박스

---

## 14. 참고 자료

- PRD: `/docs/prd.md` (F-001 회원가입)
- Userflow: `/docs/userflow.md` (1.1 회원가입)
- 유스케이스: `/docs/usecases/1-signup/spec.md`
- 공통 모듈: `/docs/common-modules.md`
- Database: `/docs/database.md` (user_profiles 테이블)

---

## 15. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
|------|------|--------|-----------|
| 1.0  | 2025-10-20 | Claude Code | 초기 작성 |

---

**문서 종료**
