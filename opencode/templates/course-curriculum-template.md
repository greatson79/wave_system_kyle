# {{course_name}}

> {{course_tagline}}

## 강의 정보

| 항목 | 내용 |
|------|------|
| **대상** | {{target_audience}} |
| **수준** | {{difficulty_level}} |
| **기간** | {{duration}} ({{total_hours}}시간) |
| **형식** | {{format}} (온라인/{{offline_ratio}}) |
| **선수 지식** | {{prerequisites}} |

---

## 학습 목표

### 핵심 역량
{{#each competencies}}
- {{this}}
{{/each}}

### 학습 결과 (Learning Outcomes)
{{#each outcomes}}
{{increment @index}}. **{{title}}**: {{description}}
{{/each}}

---

## 커리큘럼 개요

```
{{curriculum_visual}}
```

---

## 모듈별 상세 설계

{{#each modules}}
### Module {{mod_num}}: {{title}}
**시간**: {{hours}}시간 ({{sessions}}세션)

#### 개요
{{description}}

#### 학습 목표
{{#each objectives}}
- {{this}}
{{/each}}

#### 커리큘럼 맵
| 세션 | 주제 | 시간 | 유형 | 활동 |
|------|------|------|------|------|
{{#each sessions}}
| {{mod_num}}.{{num}} | {{topic}} | {{duration}}분 | {{type}} | {{activity}} |
{{/each}}

#### 세부 수업 계획

{{#each sessions}}
##### 세션 {{mod_num}}.{{num}}: {{topic}}

**학습 목표**
{{#each objectives}}
- {{this}}
{{/each}}

**키 컨셉**
{{#each concepts}}
- {{this}}
{{/each}}

**사전 준비**
- 학습자: {{learner_prep}}
- 강사: {{instructor_prep}}

**수업 흐름**
| 시간 | 활동 | 방법 | 자료 |
|------|------|------|------|
{{#each flow}}
| {{time}} | {{activity}} | {{method}} | {{materials}} |
{{/each}}

**평가**
- 형성평가: {{formative}}
- 총괄평가: {{summative}}

**참고 자료**
{{#each resources}}
- [{{title}}]({{url}})
{{/each}}

---
{{/each}}

{{/each}}

---

## 평가 설계

### 성적 구성
| 평가 항목 | 비율 | 반영 내용 |
|-----------|------|-----------|
{{#each grading}}
| {{item}} | {{weight}}% | {{description}} |
{{/each}}

### 평가 기준 (Rubric)
{{#each rubrics}}
#### {{name}}
| 수준 | 기준 |
|------|------|
{{#each levels}}
| {{level}} | {{description}} |
{{/each}}
{{/each}}

---

## 학습 자료

### 필수 자료
{{#each required_materials}}
- **{{title}}**: {{description}}
{{/each}}

### 추천 자료
{{#each optional_materials}}
- **{{title}}**: {{description}}
{{/each}}

### 온라인 자료 ({{platform}})
| 주차 | 플랫폼 콘텐츠 | 과제 |
|------|---------------|------|
{{#each weekly_online}}
| {{week}} | {{content}} | {{assignment}} |
{{/each}}

---

## 주차별 계획

| 주차 | 주제 | 온라인 | 오프라인 | 과제 |
|------|------|--------|----------|------|
{{#each weekly_plan}}
| {{week}} | {{topic}} | {{online}} | {{offline}} | {{homework}} |
{{/each}}

---

## 정책 및 참고

### 출석 및 참여
{{attendance_policy}}

### 과제 정책
{{assignment_policy}}

### 연락처
- 강사: {{instructor_name}}
- 이메일: {{email}}
- 상담 시간: {{office_hours}}

---

*최종 수정일: {{last_updated}}*
