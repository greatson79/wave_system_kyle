# 공통 모듈 작업 계획

## 1. 문서 목적

이 문서는 수련회 팀빌딩 성경 미션 게임 웹앱의 페이지 단위 구현을 시작하기 전에 먼저 확정해야 할 공통 모듈 계획을 정의한다.

기준 문서:

- `docs/requirement.md`
- `docs/prd.md`
- `docs/userflow.md`
- `docs/database.md`
- `docs/usecases/*/spec.md`

전제:

- 아직 코드베이스는 없다.
- MVP 기술 스택은 `Vite + React + TypeScript`로 가정한다.
- 서버, 로그인, 외부 데이터베이스, 실시간 동기화는 구현하지 않는다.
- 상태는 브라우저 메모리와 `localStorage` 단일 키 `retreat-game:v1:state`로 관리한다.
- 공통 모듈은 특정 페이지 UI에 의존하지 않는 순수 로직과 설정 중심으로 작성한다.

## 2. 현재 코드베이스 상태

현재 작업 폴더에는 구현 코드가 없고 문서와 agent/prompt 파일만 존재한다.

확인된 주요 파일:

- `docs/requirement.md`
- `docs/prd.md`
- `docs/userflow.md`
- `docs/database.md`
- `docs/usecases/001-game-setup/spec.md`
- `docs/usecases/002-team-names-participants/spec.md`
- `docs/usecases/003-personality-team-building/spec.md`
- `docs/usecases/004-stage2-item-assignment/spec.md`
- `docs/usecases/005-stage3-bible-mission/spec.md`
- `docs/usecases/006-stage4-final-mission/spec.md`
- `docs/usecases/007-reflection/spec.md`
- `docs/usecases/008-result-export/spec.md`
- `docs/usecases/009-session-recovery/spec.md`

아직 없는 항목:

- `package.json`
- Vite 앱 구조
- `src/` 디렉터리
- TypeScript 타입
- 공통 상태 관리 코드
- 테스트 설정

따라서 이 문서는 신규 프로젝트 생성 직후 만들 공통 파일의 책임과 최소 인터페이스를 정리한다.

## 3. 공통 모듈 설계 원칙

1. 페이지 UI와 도메인 로직을 분리한다.
2. 팀 배정, 아이템 배정, 미션 완료 판정, 소감 검증은 React 컴포넌트 없이 테스트 가능해야 한다.
3. MVP에서는 단일 브라우저, 단일 기기 진행을 우선한다.
4. `localStorage`에는 하나의 전체 상태 객체만 저장한다.
5. 기본 콘텐츠는 코드 또는 설정 파일에 두고, 저장 상태에는 콘텐츠 ID와 사용자 입력값만 둔다.
6. PDF, 관리자 화면, 서버 저장, 다중 기기 동기화는 확장 가능성만 남기고 구현하지 않는다.
7. 페이지 작업자가 동시에 개발할 때 충돌이 날 수 있는 타입, 상수, 검증 규칙, 상태 변경 로직은 모두 공통 모듈로 먼저 만든다.

## 4. 권장 디렉터리 구조

```txt
src/
├── app/
│   └── initialState.ts
├── config/
│   ├── content.ts
│   └── stages.ts
├── lib/
│   ├── exporter.ts
│   ├── itemMatcher.ts
│   ├── missionEngine.ts
│   ├── reflectionManager.ts
│   ├── stageManager.ts
│   ├── storage.ts
│   ├── teamBuilder.ts
│   └── validation.ts
├── types/
│   ├── content.ts
│   └── game.ts
└── test/
    └── fixtures.ts
```

테스트 파일은 구현 시 모듈 옆 또는 `src/lib/__tests__/`에 둘 수 있다. 중요한 것은 공통 로직 테스트가 페이지 컴포넌트에 의존하지 않는 것이다.

## 5. 공통 타입 모듈

### 5.1 `src/types/game.ts`

역할:

- `localStorage`에 저장되는 전체 상태 타입을 정의한다.
- 모든 페이지와 공통 로직이 동일한 데이터 구조를 사용하게 한다.

포함 타입:

```ts
export type StageId = 1 | 2 | 3 | 4 | "reflection" | "export";

export type RouteId =
  | "setup"
  | "team-names"
  | "personality"
  | "team-result"
  | "stage2"
  | "stage3"
  | "stage4"
  | "reflection"
  | "export";

export type PersonalityType = "idea" | "analysis" | "action" | "encouragement";

export type GameStorageState = {
  schemaVersion: 1;
  appVersion?: string;
  savedAt: string;
  game: GameMeta;
  teams: Team[];
  participants: Participant[];
  personalityResponses: PersonalityResponse[];
  personalityResults: PersonalityResult[];
  teamAssignments: TeamAssignment[];
  itemAssignments: ItemAssignment[];
  itemRevealState: ItemRevealState;
  missionResponses: MissionResponses;
  usedItems: UsedItem[];
  reflections: Reflection[];
  exportState: ExportState;
};
```

`docs/database.md`의 스키마를 기준으로 아래 타입도 함께 둔다.

- `GameMeta`
- `GameConfig`
- `StageState`
- `StageProgress`
- `StageProgressItem`
- `ContentSelection`
- `Team`
- `Participant`
- `PersonalityResponse`
- `PersonalityAnswer`
- `PersonalityResult`
- `TeamAssignment`
- `ItemAssignment`
- `ItemRevealState`
- `MissionResponses`
- `Stage3MissionResponse`
- `Stage4MissionResponse`
- `UsedItem`
- `Reflection`
- `ExportState`

### 5.2 `src/types/content.ts`

역할:

- 기본 콘텐츠 설정 타입을 정의한다.
- 성향 질문, 아이템, 미션 데이터가 페이지와 분리되도록 한다.

포함 타입:

- `ContentSet`
- `PersonalityQuestion`
- `PersonalityScoreMap`
- `GameItem`
- `Stage3Mission`
- `Stage4Mission`
- `MissionType`
- `AgeGroup`
- `Difficulty`

MVP 기본값:

- 기본 주제: `공동체`
- 기본 대상: `middleHigh`
- 기본 난이도: `normal`
- 성향 질문: 5개
- 아이템: 6개
- 3단계 미션: 5개
- 4단계 최종 미션: 1개

## 6. 공통 설정 모듈

### 6.1 `src/config/stages.ts`

역할:

- 4단계 스테이지와 후속 흐름을 중앙에서 정의한다.
- 진행 표시 UI가 같은 단계명과 순서를 사용하게 한다.

포함 내용:

- `STAGES`
- `ROUTE_ORDER`
- `STAGE_ROUTE_MAP`
- 단계별 완료 조건에서 참조할 기본 메타데이터

주의:

- 이 파일은 표시용 제목, 단계 번호, 기본 설명까지만 관리한다.
- 페이지 컴포넌트나 라우터 구현을 직접 import하지 않는다.

### 6.2 `src/config/content.ts`

역할:

- 기본 콘텐츠 세트를 관리한다.
- 화면 로직과 콘텐츠 데이터를 분리한다.

포함 내용:

- `DEFAULT_CONTENT_SET`
- 성향 질문 5개와 점수 매핑
- 기본 아이템 6개
- 3단계 성경 협업 미션 5개
- 4단계 최종 미션 1개

MVP 방침:

- 관리자용 콘텐츠 편집 화면은 만들지 않는다.
- 주제 키워드는 게임 설정에서 바꿀 수 있지만, 기본 콘텐츠는 코드 설정으로 둔다.
- 콘텐츠가 누락되면 기본 콘텐츠 세트를 사용한다.

## 7. 초기 상태 모듈

### 7.1 `src/app/initialState.ts`

역할:

- 새 게임 시작 시 사용할 초기 상태를 생성한다.
- 저장 데이터 손상 또는 새 게임 시작 시 같은 초기화 로직을 재사용한다.

공개 함수:

```ts
export function createInitialState(now?: Date): GameStorageState;

export function createConfiguredState(
  input: {
    title?: string;
    participantCount: number;
    teamCount: number;
    topicKeyword?: string;
    ageGroup?: "elementary" | "middleHigh" | "youngAdult";
    difficulty?: "easy" | "normal" | "hard";
  },
  now?: Date
): GameStorageState;
```

기본값:

- `title`: `수련회 팀빌딩 성경 미션 게임`
- `topicKeyword`: `공동체`
- `ageGroup`: `middleHigh`
- `difficulty`: `normal`
- `schemaVersion`: `1`
- `currentRoute`: `setup`

## 8. `storage` 모듈

### 8.1 `src/lib/storage.ts`

역할:

- `localStorage` 저장, 조회, 삭제, 파싱, 버전 검증을 담당한다.
- 저장 실패 시 앱 진행 자체가 중단되지 않도록 결과 객체를 반환한다.

상수:

```ts
export const STORAGE_KEY = "retreat-game:v1:state";
export const SCHEMA_VERSION = 1;
```

공개 함수:

```ts
export function loadGameState(): LoadStateResult;
export function saveGameState(state: GameStorageState): SaveStateResult;
export function clearGameState(): ClearStateResult;
export function isStorageAvailable(): boolean;
export function validateStoredState(value: unknown): value is GameStorageState;
```

결과 타입:

- `LoadStateResult`: 정상 상태, 저장 없음, 파싱 실패, 버전 불일치, 접근 실패 구분
- `SaveStateResult`: 성공, 저장소 접근 실패, 용량 초과, 알 수 없는 오류 구분
- `ClearStateResult`: 성공, 실패 구분

MVP 처리:

- 저장 데이터가 손상되면 복구 가능한 항목만 살리는 복잡한 병합은 하지 않는다.
- 새 게임 시작 또는 저장 데이터 삭제 흐름을 제공할 수 있게 오류 종류만 반환한다.
- 파일이나 이미지 결과물 자체는 저장하지 않는다.

## 9. `validation` 모듈

### 9.1 `src/lib/validation.ts`

역할:

- 페이지별 입력 검증이 서로 다르게 구현되는 것을 막는다.
- 다음 단계 이동 가능 여부 판단에 필요한 검증을 공통화한다.

공개 함수:

```ts
export function validateGameConfig(input: GameConfigInput): ValidationResult;
export function validateTeamNames(teams: Team[]): ValidationResult;
export function validateParticipants(participants: Participant[], expectedCount: number): ValidationResult;
export function validatePersonalityResponses(
  responses: PersonalityResponse[],
  participants: Participant[],
  questionIds: string[]
): ValidationResult;
export function validateTeamAssignments(
  assignments: TeamAssignment[],
  teams: Team[],
  participants: Participant[]
): ValidationResult;
export function validateMissionResponses(state: GameStorageState, stage: 3 | 4): ValidationResult;
export function validateReflections(reflections: Reflection[], teams: Team[]): ValidationResult;
export function validateExportReady(state: GameStorageState): ValidationResult;
```

공통 결과 타입:

```ts
export type ValidationResult = {
  ok: boolean;
  errors: ValidationError[];
};

export type ValidationError = {
  code: string;
  message: string;
  field?: string;
  targetId?: string;
};
```

주요 규칙:

- 참가 인원 수는 1명 이상이다.
- 팀 수는 2~6팀이다.
- 팀 수는 참가 인원 수보다 클 수 없다.
- 팀 이름은 공백일 수 없고 중복될 수 없다.
- 모든 참가자는 필수 성향 질문에 답해야 한다.
- 모든 참가자는 정확히 하나의 팀에 배정되어야 한다.
- 빈 팀은 허용하지 않는다.
- 팀별 인원 차이는 가능한 한 1명 이하로 유지한다.
- 팀별 필수 미션 답변이 비어 있으면 해당 단계 완료로 처리하지 않는다.
- 모든 팀의 필수 소감 항목이 있어야 결과물 다운로드를 허용한다.

개인정보 방침:

- 실명, 연락처, 이메일을 완벽히 탐지하는 복잡한 로직은 MVP에서 만들지 않는다.
- 자유 입력 전후에 개인정보 입력 주의 안내를 보여줄 수 있도록 `containsPossiblePrivateInfo(text)` 정도의 보조 함수만 둔다.
- 이 보조 함수는 차단보다 안내 용도로만 사용한다.

## 10. `stageManager` 모듈

### 10.1 `src/lib/stageManager.ts`

역할:

- 현재 단계, 완료 단계, 잠긴 단계를 일관되게 관리한다.
- 페이지 구현자가 각자 단계 이동 규칙을 중복 작성하지 않게 한다.

공개 함수:

```ts
export function getStageStatus(state: GameStorageState): StageState;
export function canEnterRoute(state: GameStorageState, route: RouteId): boolean;
export function canCompleteCurrentStage(state: GameStorageState): ValidationResult;
export function completeStage(state: GameStorageState, stage: 1 | 2 | 3 | 4, now?: Date): GameStorageState;
export function moveToRoute(state: GameStorageState, route: RouteId): GameStorageState;
export function getNextRoute(state: GameStorageState): RouteId | null;
```

단계 완료 기준:

- 1단계: 성향 응답 완료, 팀 배정 생성, 빈 팀 없음
- 2단계: 모든 팀에 아이템 배정, 공개 상태 확정
- 3단계: 필수 미션의 팀별 답변 완료
- 4단계: 팀별 최종 답변 완료 또는 진행자 확인 완료
- 소감: 모든 팀의 필수 소감 항목 완료
- 결과물: 다운로드 준비 데이터 구성 가능

주의:

- React Router 같은 라우팅 라이브러리에 의존하지 않는다.
- 상태 객체를 입력받고 새 상태 객체를 반환하는 방식으로 작성한다.

## 11. `teamBuilder` 모듈

### 11.1 `src/lib/teamBuilder.ts`

역할:

- 성향 질문 응답을 점수화한다.
- 참가자를 팀별로 최대한 균등하고 성향이 섞이도록 자동 배정한다.

공개 함수:

```ts
export function scorePersonalityResponses(
  responses: PersonalityResponse[],
  questions: PersonalityQuestion[]
): PersonalityResult[];

export function buildTeamAssignments(input: {
  teams: Team[];
  participants: Participant[];
  results: PersonalityResult[];
}): TeamAssignment[];

export function summarizePersonalityDistribution(
  assignments: TeamAssignment[],
  results: PersonalityResult[]
): TeamAssignment[];
```

배정 규칙:

- 팀별 목표 인원 수를 먼저 계산한다.
- 대표 성향별 참가자를 나눈 뒤 팀에 순환 배치한다.
- 특정 성향이 부족하거나 모두 같은 성향이면 인원 균형을 우선한다.
- 참가자 수가 팀 수로 나누어떨어지지 않으면 일부 팀이 1명 많을 수 있다.
- 빈 팀은 허용하지 않는다.

MVP에서 하지 않는 것:

- 전문 성향검사 해석
- 복잡한 최적화 알고리즘
- 드래그 앤 드롭 수동 조정

## 12. `itemMatcher` 모듈

### 12.1 `src/lib/itemMatcher.ts`

역할:

- 2단계에서 팀별 힌트/도구 아이템을 배정한다.
- MVP에서는 사다리타기 애니메이션 대신 랜덤 매칭 결과 생성을 우선한다.

공개 함수:

```ts
export function assignItems(input: {
  teams: Team[];
  items: GameItem[];
  now?: Date;
  seed?: string;
}): ItemAssignment[];

export function createInitialRevealState(mode?: "all" | "sequence"): ItemRevealState;
export function revealItemForTeam(state: ItemRevealState, teamId: string): ItemRevealState;
export function finalizeItemReveal(state: ItemRevealState): ItemRevealState;
```

배정 규칙:

- 각 팀은 최소 1개 아이템을 받는다.
- 아이템 수가 팀 수보다 많으면 일부 아이템은 사용되지 않을 수 있다.
- 아이템 수가 팀 수보다 적으면 기본 아이템 세트를 우선 사용한다.
- 배정 결과는 재현이 필요하므로 확정 후 `itemAssignments`에 저장한다.

MVP에서 하지 않는 것:

- 실제 사다리타기 경로 렌더링
- 팀별 다중 아이템 전략
- 아이템 거래 또는 팀 간 교환 로직

## 13. `missionEngine` 모듈

### 13.1 `src/lib/missionEngine.ts`

역할:

- 3단계 성경 협업 미션과 4단계 최종 미션의 답변 저장, 완료 판정, 요약 생성을 담당한다.

공개 함수:

```ts
export function getStage3Missions(contentSet: ContentSet): Stage3Mission[];
export function getStage4Mission(contentSet: ContentSet): Stage4Mission;

export function upsertStage3Response(input: {
  responses: Stage3MissionResponse[];
  teamId: string;
  missionId: string;
  answer: string | string[];
  mission: Stage3Mission;
  now?: Date;
}): Stage3MissionResponse[];

export function upsertStage4Response(input: {
  responses: Stage4MissionResponse[];
  teamId: string;
  finalAnswer: string;
  facilitatorConfirmed: boolean;
  now?: Date;
}): Stage4MissionResponse[];

export function markItemUsed(input: {
  usedItems: UsedItem[];
  teamId: string;
  itemId: string;
  stage: 3 | 4;
  missionId?: string;
  now?: Date;
}): UsedItem[];

export function getMissionSummary(state: GameStorageState, contentSet: ContentSet): MissionSummary[];
```

완료 판정:

- 선택형 문제는 정답이 있으면 `isCorrect`를 계산할 수 있다.
- 서술형 문제는 입력 여부와 진행자 확인 기준을 사용한다.
- 정답 데이터가 없는 미션은 완료 여부 중심으로 처리한다.
- 최종 미션은 팀별 최종 답변과 진행자 확인을 반영한다.

MVP에서 하지 않는 것:

- 서버 채점
- 점수판
- 랭킹
- AI 답변 평가

## 14. `reflectionManager` 모듈

### 14.1 `src/lib/reflectionManager.ts`

역할:

- 팀별 소감 입력 데이터를 생성, 갱신, 검증한다.
- 결과물 미리보기에서 사용할 수 있는 소감 데이터를 제공한다.

공개 함수:

```ts
export function createEmptyReflections(teams: Team[], now?: Date): Reflection[];

export function upsertReflection(input: {
  reflections: Reflection[];
  teamId: string;
  values: {
    memorableWord: string;
    solvedTogether: string;
    thankfulPoint: string;
    actionCommitment: string;
  };
  now?: Date;
}): Reflection[];

export function getReflectionCompletion(reflections: Reflection[], teams: Team[]): ReflectionCompletion[];
export function buildReflectionCards(state: GameStorageState): ReflectionCardData[];
```

검증 규칙:

- 팀별 4개 소감 필드는 필수다.
- 저장 가능 길이와 이미지 표시 길이는 분리한다.
- 긴 텍스트는 저장을 막기보다 결과물 표시에서 줄바꿈 또는 축약할 수 있게 데이터 상태를 반환한다.
- 다운로드 전 개인정보 검토 안내를 표시할 수 있도록 완료 상태와 주의 상태를 분리한다.

## 15. `exporter` 모듈

### 15.1 `src/lib/exporter.ts`

역할:

- 결과물 데이터 구성, 파일명 생성, 이미지 다운로드 실행을 담당한다.
- DOM 캡처 자체는 라이브러리 선택에 따라 달라질 수 있으므로 어댑터 형태로 둔다.

권장 라이브러리:

- 이미지: `html-to-image`
- PDF: MVP 이후

공개 함수:

```ts
export function buildExportData(state: GameStorageState, contentSet: ContentSet): ExportData;
export function createExportFilename(input: {
  title: string;
  teamName?: string;
  date?: Date;
  extension: "png";
}): string;

export async function exportElementToPng(input: {
  element: HTMLElement;
  filename: string;
}): Promise<ExportResult>;
```

주의:

- 다운로드 파일 자체는 `localStorage`에 저장하지 않는다.
- `exportState`에는 다운로드 시도 결과, 선택 팀, 마지막 오류만 저장한다.
- 모바일 브라우저에서 자동 다운로드가 제한될 수 있으므로 실패 결과를 반환하고 재시도 UI가 처리할 수 있게 한다.
- PDF 관련 타입이나 함수는 MVP에서 만들지 않는다. 필요하면 이후 `exportElementToPdf`를 추가한다.

## 16. 테스트 픽스처

### 16.1 `src/test/fixtures.ts`

역할:

- 공통 로직 테스트와 페이지 테스트가 같은 샘플 상태를 사용하게 한다.

포함 데이터:

- 2팀, 4명 기본 상태
- 4팀, 10명 기본 상태
- 성향 응답 완료 상태
- 팀 배정 완료 상태
- 아이템 배정 완료 상태
- 미션 완료 상태
- 소감 완료 상태
- 손상 저장 데이터 샘플

주의:

- 실제 UI 문구 테스트가 아니라 도메인 상태 테스트에 필요한 데이터만 둔다.
- 개인정보처럼 보이는 샘플 이름은 쓰지 않는다.

## 17. 공통 모듈 우선 구현 순서

1. Vite + React + TypeScript 프로젝트 생성
2. TypeScript strict 설정 확인
3. 테스트 도구 설정
   - 권장: `vitest`
   - DOM 이미지 다운로드 테스트는 최소화하고 순수 로직 테스트 우선
4. `src/types/game.ts`, `src/types/content.ts` 작성
5. `src/config/stages.ts`, `src/config/content.ts` 작성
6. `src/app/initialState.ts` 작성
7. `src/lib/validation.ts` 작성
8. `src/lib/storage.ts` 작성
9. `src/lib/stageManager.ts` 작성
10. `src/lib/teamBuilder.ts` 작성
11. `src/lib/itemMatcher.ts` 작성
12. `src/lib/missionEngine.ts` 작성
13. `src/lib/reflectionManager.ts` 작성
14. `src/lib/exporter.ts` 작성
15. `src/test/fixtures.ts` 작성
16. 각 공통 모듈의 단위 테스트 작성

## 18. 페이지 작업자가 의존할 공통 계약

페이지 작업자는 아래 공통 계약만 사용한다.

- 상태 구조: `GameStorageState`
- 기본 콘텐츠: `DEFAULT_CONTENT_SET`
- 단계 정의: `STAGES`
- 입력 검증: `validation.ts`
- 단계 이동: `stageManager.ts`
- 저장/복구: `storage.ts`
- 팀 배정: `teamBuilder.ts`
- 아이템 배정: `itemMatcher.ts`
- 미션 답변/요약: `missionEngine.ts`
- 소감 데이터: `reflectionManager.ts`
- 결과물 데이터/이미지 다운로드: `exporter.ts`

페이지 작업자가 직접 구현하지 않아야 할 것:

- 별도 단계 완료 판정
- 별도 `localStorage` 키
- 별도 팀 배정 알고리즘
- 별도 아이템 랜덤 배정 알고리즘
- 별도 미션 완료 판정
- 별도 소감 필수 항목 검증
- 별도 결과물 파일명 규칙

## 19. MVP 이후로 미룰 공통 작업

아래 항목은 현재 공통 모듈에 포함하지 않는다.

- 서버 API 클라이언트
- 사용자 계정 타입
- 관리자 콘텐츠 편집 타입
- QR 코드 생성
- 실시간 동기화
- 점수판과 랭킹
- PDF 다운로드 구현
- 다국어 처리
- 복잡한 개인정보 자동 탐지
- 사다리타기 애니메이션 엔진

## 20. 병렬 개발 충돌 방지 검증

### 20.1 1차 검증

페이지 단위 개발 중 여러 작업자가 동시에 수정할 가능성이 높은 항목을 공통 모듈로 분리했다.

- 타입
- 단계 정의
- 기본 콘텐츠
- 검증 규칙
- 저장 키
- 상태 초기화
- 팀 배정
- 아이템 배정
- 미션 완료 판정
- 소감 검증
- 결과물 데이터 구성

결론: 페이지 작업자는 화면 컴포넌트와 스타일을 중심으로 작업하고, 핵심 상태 변경은 공통 모듈을 호출하면 된다.

### 20.2 2차 검증

문서 요구사항에서 반복 등장하는 공통 관심사를 누락 없이 반영했다.

- `localStorage` 단일 키 저장
- 4단계 스테이지 관리
- 간이 성향 질문 기반 팀 구성
- 팀별 아이템 배정
- 성경 기반 3단계 미션
- 최종 4단계 미션
- 팀별 소감
- 결과 이미지 다운로드
- 개인정보 미수집 안내
- 저장 실패와 복구 실패 처리

결론: 공통 작성 모듈 범위가 문서 요구사항과 일치한다.

### 20.3 3차 검증

오버엔지니어링 가능성이 있는 항목은 MVP 범위에서 제외했다.

- 서버 저장 제외
- 로그인 제외
- 관리자 화면 제외
- PDF 구현 제외
- 다중 기기 동기화 제외
- 점수판 제외
- AI 평가 제외
- 복잡한 개인정보 탐지 제외

결론: 공통 모듈은 페이지 병렬 개발에 필요한 최소 범위로 제한되어 있다.

## 21. 완료 기준

공통 모듈 구현이 완료되었다고 판단하는 기준:

- 모든 공통 타입이 `docs/database.md` 스키마와 일치한다.
- 새 게임 초기 상태를 생성할 수 있다.
- 설정, 팀 이름, 성향 응답, 팀 배정, 아이템, 미션, 소감, 다운로드 준비 상태를 검증할 수 있다.
- `localStorage` 저장, 복구, 삭제 실패를 구분할 수 있다.
- 단계 완료와 다음 이동 가능 여부를 공통 로직으로 판단할 수 있다.
- 팀 배정, 아이템 배정, 미션 완료, 소감 검증이 페이지 없이 단위 테스트 가능하다.
- 결과물 이미지 다운로드에 필요한 데이터와 파일명을 공통 로직으로 만들 수 있다.
