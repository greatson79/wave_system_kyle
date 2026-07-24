# Wave AI Networks — Paperclip 등록 가이드

> 이 가이드를 순서대로 따라하면 Wave AI 회사가 Paperclip에 완전히 등록됩니다.

---

## 사전 준비: API 키 확인

등록 전 아래 3개 API 키를 준비합니다.

| 제공사 | 환경변수 | 사용 에이전트 |
|--------|----------|---------------|
| Anthropic | `ANTHROPIC_API_KEY` | Flow Ops Orchestrator, Learning, Network |
| OpenAI | `OPENAI_API_KEY` | AI Systems Orchestrator, Content, AI Systems Lead |
| Google | `GOOGLE_API_KEY` | Knowledge Wave Lead, Flow Operations Lead |

---

## Step 1. Paperclip 회사 기본 설정

1. Paperclip 대시보드 → **Company Settings**
2. 아래 내용 입력:

```
Company Name:  Wave AI Networks
Description:   AI가 기획하고, AI가 만들고, AI가 실행하는 조직
Owner:         Kyle Choi
Owner Title:   Chief Wave Architect
Timezone:      Asia/Seoul
Language:      Korean
```

---

## Step 2. API 키 등록

1. **Settings → Integrations → API Keys**
2. 각 제공사별 키 입력:
   - Anthropic API Key
   - OpenAI API Key
   - Google API Key

---

## Step 3. 에이전트 등록 (8개 순서대로)

> 각 에이전트: **Agents → Add Agent** 에서 등록

---

### 에이전트 1: Flow Operations Orchestrator

```
Name:       Flow Operations Orchestrator
Title:      운영총괄
Department: Executive
Model:      Anthropic / claude-sonnet-4-6
Activation: On-Demand
Reports To: Chief Wave Architect (Kyle Choi)
Manages:    Learning / Content / Network / Knowledge / Flow Operations Lead
```

**System Prompt:** `system-prompts/01_flow-operations-orchestrator.md` 파일 내 코드블록 내용 붙여넣기

**Budget:**
```
Max tokens/task: 8,000
Daily limit:     $5.00
```

---

### 에이전트 2: AI Systems Orchestrator

```
Name:       AI Systems Orchestrator
Title:      CTO
Department: Executive
Model:      OpenAI / gpt-4o
Activation: On-Demand
Reports To: Chief Wave Architect (Kyle Choi)
Manages:    AI Systems Lead
```

**System Prompt:** `system-prompts/02_ai-systems-orchestrator.md` 파일 내 코드블록 내용 붙여넣기

**Budget:**
```
Max tokens/task: 8,000
Daily limit:     $5.00
```

---

### 에이전트 3: Learning Wave Lead

```
Name:       Learning Wave Lead
Title:      교육본부 팀장
Department: Learning Wave Team
Model:      Anthropic / claude-sonnet-4-6
Activation: On-Demand
Reports To: Flow Operations Orchestrator
```

**System Prompt:** `system-prompts/03_learning-wave-lead.md` 파일 내 코드블록 내용 붙여넣기

**Budget:**
```
Max tokens/task: 12,000
Daily limit:     $8.00
```

---

### 에이전트 4: Content Wave Lead

```
Name:       Content Wave Lead
Title:      콘텐츠본부 팀장
Department: Content Wave Team
Model:      OpenAI / gpt-4o
Activation: On-Demand
Reports To: Flow Operations Orchestrator
```

**System Prompt:** `system-prompts/04_content-wave-lead.md` 파일 내 코드블록 내용 붙여넣기

**Budget:**
```
Max tokens/task: 6,000
Daily limit:     $5.00
```

---

### 에이전트 5: Network Wave Lead

```
Name:       Network Wave Lead
Title:      네트워크본부 팀장
Department: Network Wave Team
Model:      Anthropic / claude-sonnet-4-6
Activation: On-Demand
Reports To: Flow Operations Orchestrator
```

**System Prompt:** `system-prompts/05_network-wave-lead.md` 파일 내 코드블록 내용 붙여넣기

**Budget:**
```
Max tokens/task: 6,000
Daily limit:     $3.00
```

---

### 에이전트 6: Knowledge Wave Lead

```
Name:       Knowledge Wave Lead
Title:      출판본부 팀장
Department: Knowledge Wave Team
Model:      Google / gemini-2.5-pro
Activation: On-Demand
Reports To: Flow Operations Orchestrator
```

**System Prompt:** `system-prompts/06_knowledge-wave-lead.md` 파일 내 코드블록 내용 붙여넣기

**Budget:**
```
Max tokens/task: 32,000
Daily limit:     $8.00
```

---

### 에이전트 7: Flow Operations Lead

```
Name:       Flow Operations Lead
Title:      운영본부 팀장
Department: Flow Operations Team
Model:      Google / gemini-2.0-flash
Activation: On-Demand
Reports To: Flow Operations Orchestrator
```

**System Prompt:** `system-prompts/07_flow-operations-lead.md` 파일 내 코드블록 내용 붙여넣기

**Budget:**
```
Max tokens/task: 4,000
Daily limit:     $1.00
```

---

### 에이전트 8: AI Systems Lead

```
Name:       AI Systems Lead
Title:      AI개발본부 팀장
Department: AI Systems Team
Model:      OpenAI / gpt-4o
Activation: On-Demand
Reports To: AI Systems Orchestrator
```

**System Prompt:** `system-prompts/08_ai-systems-lead.md` 파일 내 코드블록 내용 붙여넣기

**Budget:**
```
Max tokens/task: 8,000
Daily limit:     $5.00
```

---

## Step 4. 에스컬레이션 규칙 설정

**Settings → Escalation Rules**

```
신학적 판단 필요      → Chief Wave Architect
재정 집행 결정        → Chief Wave Architect
브랜드 방향 결정      → Chief Wave Architect
에이전트 3회 실패     → Chief Wave Architect
```

---

## Step 5. 등록 완료 확인 체크리스트

```
□ 회사 정보 설정 완료
□ API 키 3개 등록 완료
□ Flow Operations Orchestrator 등록 + 테스트
□ AI Systems Orchestrator 등록 + 테스트
□ Learning Wave Lead 등록
□ Content Wave Lead 등록
□ Network Wave Lead 등록
□ Knowledge Wave Lead 등록
□ Flow Operations Lead 등록
□ AI Systems Lead 등록
□ 조직도 (Org Chart) 확인
□ 에스컬레이션 규칙 설정
```

---

## 등록 후 첫 번째 테스트

등록 완료 후 아래 요청으로 전체 흐름을 테스트합니다:

```
"다음 주 목회자 AI 활용 세미나 준비를 위한 실행 계획을 세워줘"
```

→ Flow Operations Orchestrator가 받아서 Learning + Content + Flow Operations Lead를 호출하는 흐름이 정상 작동하면 등록 성공입니다.
