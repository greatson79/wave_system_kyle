import type { ContentSet } from '../types/content'

const personalityOptions = [
  { id: 'idea', label: '아이디어를 낸다', scoreType: 'idea' },
  { id: 'analysis', label: '차분히 정리한다', scoreType: 'analysis' },
  { id: 'action', label: '먼저 실행한다', scoreType: 'action' },
  { id: 'encouragement', label: '팀원을 격려한다', scoreType: 'encouragement' },
] as const

export const DEFAULT_CONTENT_SET: ContentSet = {
  themeKeyword: '공동체',
  bibleReferences: [
    '요한복음 13장 34-35절',
    '고린도전서 12장 12-27절',
    '전도서 4장 9-10절',
  ],
  personalityQuestions: [
    {
      id: 'pq-1',
      text: '새로운 활동을 시작할 때 나는 어떤 역할이 편한가요?',
      options: [...personalityOptions],
    },
    {
      id: 'pq-2',
      text: '문제가 생기면 나는 먼저 무엇을 하나요?',
      options: [...personalityOptions],
    },
    {
      id: 'pq-3',
      text: '팀 활동에서 가장 자주 맡는 역할은 무엇인가요?',
      options: [...personalityOptions],
    },
    {
      id: 'pq-4',
      text: '시간이 부족할 때 나는 어떤 방식으로 돕나요?',
      options: [...personalityOptions],
    },
    {
      id: 'pq-5',
      text: '모르는 내용이 나오면 나는 어떻게 반응하나요?',
      options: [...personalityOptions],
    },
  ],
  items: [
    { id: 'item-1', name: '말씀 힌트', description: '관련 성경 본문 하나를 확인합니다.' },
    { id: 'item-2', name: '키워드 카드', description: '미션 핵심 단어 하나를 얻습니다.' },
    { id: 'item-3', name: '다시 생각 카드', description: '답변을 한 번 고쳐 쓸 수 있습니다.' },
    { id: 'item-4', name: '선택지 제거권', description: '선택형 문제에서 후보 하나를 제외합니다.' },
    { id: 'item-5', name: '협력 요청권', description: '다른 팀과 1분 동안 상의할 수 있습니다.' },
    { id: 'item-6', name: '격려 카드', description: '팀원 한 명의 좋은 점을 말하고 힌트를 받습니다.' },
  ],
  stage3Missions: [
    {
      id: 'mission-1',
      type: 'choice',
      question: '예수님이 제자들에게 새 계명으로 주신 것은 무엇인가요?',
      options: ['서로 사랑하라', '혼자 해결하라', '가장 높아져라', '침묵하라'],
      answer: '서로 사랑하라',
      collaborationPrompt: '팀원 각자 보기 하나씩 근거를 말하고, 성경 근거가 가장 분명한 답으로 합의하세요.',
      personalityRoleHint: '아이디어형은 근거 제안, 분석형은 본문 확인, 실행형은 최종 선택 정리, 격려형은 발언 균형 조율',
    },
    {
      id: 'mission-2',
      type: 'short',
      question: '고린도전서 12장 관점에서 서로 다른 은사가 함께 필요하다는 이유를 2문장으로 정리하세요.',
      collaborationPrompt: '서로 다른 역할 경험을 1개씩 말한 뒤, 공통 키워드 2개를 뽑아 문장으로 합치세요.',
      personalityRoleHint: '아이디어형은 키워드 제안, 분석형은 문장 구조화, 실행형은 시간 관리, 격려형은 사례 이끌어내기',
    },
    {
      id: 'mission-3',
      type: 'choice',
      question: '전도서 4장 9-10절이 강조하는 공동체의 유익은 무엇인가요?',
      options: ['함께 일어나게 함', '혼자 빠르게 감', '경쟁에서 이김', '말하지 않음'],
      answer: '함께 일어나게 함',
      collaborationPrompt: '보기 중 틀린 선택지가 왜 틀렸는지 1개씩 설명하고 정답을 확정하세요.',
      personalityRoleHint: '아이디어형은 반례 제시, 분석형은 본문 대조, 실행형은 결론 도출, 격려형은 의견 충돌 조정',
    },
    {
      id: 'mission-4',
      type: 'short',
      question: '수련회 현장에서 갈등이 생겼을 때, 말씀에 근거한 해결 행동 3단계를 팀 합의안으로 작성하세요.',
      collaborationPrompt: '실제 갈등 상황 1개를 정하고, 누가/언제/어떻게를 포함한 3단계 실행안을 만드세요.',
      personalityRoleHint: '아이디어형은 대안 폭넓게 제시, 분석형은 우선순위 검토, 실행형은 행동 단계 명확화, 격려형은 관계 회복 표현 추가',
    },
    {
      id: 'mission-5',
      type: 'short',
      question: '우리 팀이 여름성경학교 기간에 실천할 공동체 약속을 “말씀+행동+점검방법” 형식으로 작성하세요.',
      collaborationPrompt: '말씀 1개를 선택하고, 실천 행동 1개와 점검 방법 1개를 연결해 한 문단으로 완성하세요.',
      personalityRoleHint: '아이디어형은 실천안 제시, 분석형은 측정 가능하게 다듬기, 실행형은 담당 정하기, 격려형은 모두 참여하도록 문장 톤 조정',
    },
  ],
  stage4Mission: {
    id: 'final-1',
    prompt: '오늘 받은 힌트와 말씀을 바탕으로 우리 팀의 공동체 실천 약속을 한 문장으로 완성하세요.',
  },
}
