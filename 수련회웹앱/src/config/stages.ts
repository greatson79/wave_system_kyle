import type { RouteId } from '../types/game'

export const ROUTE_ORDER: RouteId[] = [
  'landing',
  'setup',
  'team-prep',
  'personality',
  'stage2',
  'stage3',
  'stage4',
  'reflection',
  'export',
]

export const STAGES = [
  { id: 'personality', number: 1, title: '팀을 구성하라' },
  { id: 'stage2', number: 2, title: '힌트를 획득하라' },
  { id: 'stage3', number: 3, title: '말씀으로 협력하라' },
  { id: 'stage4', number: 4, title: '공동체 약속을 완성하라' },
] as const
