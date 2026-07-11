import { describe, expect, it } from 'vitest'
import { DEFAULT_CONTENT_SET } from '../config/content'
import { createInitialState } from '../state/initialState'
import { assignItems } from './itemMatcher'
import { isStage3Complete, isStage4Complete } from './missionEngine'
import { validateReflection } from './reflectionManager'
import { loadGameState, STORAGE_KEY } from './storage'
import { buildBalancedTeams, scorePersonalityResponses } from './teamBuilder'
import {
  validateGameSetup,
  validateTeamNames,
} from './validation'
import type { PersonalityType } from '../types/game'

const localStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: (key: string) => store[key] ?? null,
    setItem: (key: string, value: string) => {
      store[key] = value
    },
    removeItem: (key: string) => {
      delete store[key]
    },
    clear: () => {
      store = {}
    },
  }
})()

Object.defineProperty(globalThis, 'localStorage', {
  value: localStorageMock,
})

describe('game setup validation', () => {
  it('accepts a participant and team count that can start the MVP flow', () => {
    expect(validateGameSetup({ participantCount: 12, teamCount: 3 })).toEqual({
      valid: true,
      errors: [],
    })
  })

  it('rejects a team count larger than the participant count', () => {
    expect(validateGameSetup({ participantCount: 3, teamCount: 4 })).toEqual({
      valid: false,
      errors: ['TEAM_COUNT_EXCEEDS_PARTICIPANTS'],
    })
  })
})

describe('team preparation validation', () => {
  it('rejects empty and duplicate team names', () => {
    expect(validateTeamNames(['믿음팀', ' ', '믿음팀'])).toEqual({
      valid: false,
      errors: ['TEAM_NAME_REQUIRED', 'DUPLICATE_TEAM_NAME'],
    })
  })
})

describe('personality team building', () => {
  it('scores participant answers and chooses the strongest personality type', () => {
    const result = scorePersonalityResponses(
      'participant-1',
      DEFAULT_CONTENT_SET.personalityQuestions.map((question) => ({
        questionId: question.id,
        optionId: 'idea',
      })),
      DEFAULT_CONTENT_SET.personalityQuestions,
    )

    expect(result.primaryType).toBe('idea')
    expect(result.scores.idea).toBeGreaterThan(result.scores.analysis)
  })

  it('balances participants across teams while preserving all participants', () => {
    const teams = [
      { id: 'team-1', name: '믿음팀' },
      { id: 'team-2', name: '사랑팀' },
    ]
    const types: PersonalityType[] = ['idea', 'analysis', 'action', 'encouragement']
    const results = types.map(
      (type, index) => ({
        participantId: `participant-${index + 1}`,
        primaryType: type,
        scores: {
          idea: type === 'idea' ? 3 : 0,
          analysis: type === 'analysis' ? 3 : 0,
          action: type === 'action' ? 3 : 0,
          encouragement: type === 'encouragement' ? 3 : 0,
        },
      }),
    )

    const assignments = buildBalancedTeams(teams, results)

    expect(assignments).toHaveLength(4)
    expect(new Set(assignments.map((assignment) => assignment.participantId)).size).toBe(4)
    expect(assignments.filter((assignment) => assignment.teamId === 'team-1')).toHaveLength(2)
    expect(assignments.filter((assignment) => assignment.teamId === 'team-2')).toHaveLength(2)
  })
})

describe('item matching and missions', () => {
  it('assigns one item to every team', () => {
    const assignments = assignItems(
      [
        { id: 'team-1', name: '믿음팀' },
        { id: 'team-2', name: '사랑팀' },
      ],
      DEFAULT_CONTENT_SET.items,
      1,
    )

    expect(assignments).toHaveLength(2)
    expect(assignments[0].teamId).toBe('team-1')
    expect(assignments[0].itemId).toBeTruthy()
  })

  it('can assign custom hints through the ladder matching flow', () => {
    const assignments = assignItems(
      [
        { id: 'team-1', name: '믿음팀' },
        { id: 'team-2', name: '사랑팀' },
      ],
      [
        { id: 'hint-a', name: '요한복음 힌트', description: '서로 사랑하라' },
        { id: 'hint-b', name: '전도서 힌트', description: '함께 일으킨다' },
      ],
      2,
    )

    expect(assignments.map((assignment) => assignment.itemId).sort()).toEqual([
      'hint-a',
      'hint-b',
    ])
  })

  it('marks stage 3 complete only when every team has an answer', () => {
    expect(
      isStage3Complete(
        [
          { teamId: 'team-1', answers: { 'mission-1': '서로 섬김', 'mission-2': '함께 은사 사용' }, completed: true },
          { teamId: 'team-2', answers: {}, completed: false },
        ],
        ['team-1', 'team-2'],
        ['mission-1', 'mission-2'],
      ),
    ).toBe(false)
  })

  it('marks stage 3 complete only when every team answered all required missions', () => {
    expect(
      isStage3Complete(
        [
          { teamId: 'team-1', answers: { 'mission-1': 'A', 'mission-2': 'B' }, completed: true },
          { teamId: 'team-2', answers: { 'mission-1': 'C', 'mission-2': '' }, completed: false },
        ],
        ['team-1', 'team-2'],
        ['mission-1', 'mission-2'],
      ),
    ).toBe(false)
  })

  it('marks stage 4 complete when every team is confirmed', () => {
    expect(
      isStage4Complete(
        [
          { teamId: 'team-1', finalAnswer: '함께 사랑하겠습니다', confirmed: true },
          { teamId: 'team-2', finalAnswer: '서로 돕겠습니다', confirmed: true },
        ],
        ['team-1', 'team-2'],
      ),
    ).toBe(true)
  })
})

describe('reflection and initial state', () => {
  it('requires every reflection field for a team result card', () => {
    expect(
      validateReflection({
        teamId: 'team-1',
        memorableWord: '공동체',
        solvedTogether: '',
        gratitude: '함께해 준 팀원들',
        practice: '먼저 돕기',
      }),
    ).toEqual({
      valid: false,
      errors: ['REFLECTION_REQUIRED_FIELD_MISSING'],
    })
  })

  it('creates a schema-versioned empty game state', () => {
    const state = createInitialState()

    expect(state.schemaVersion).toBe(1)
    expect(state.currentRoute).toBe('landing')
    expect(state.game.config.themeKeyword).toBe('공동체')
    expect(state.teams).toEqual([])
  })

  it('loads saved progress through the landing page first', () => {
    const saved = {
      ...createInitialState(),
      currentRoute: 'stage3',
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(saved))

    const loaded = loadGameState()

    expect(loaded?.currentRoute).toBe('landing')
    expect(loaded?.resumeRoute).toBe('stage3')
  })
})
