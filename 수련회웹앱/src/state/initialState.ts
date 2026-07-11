import { DEFAULT_CONTENT_SET } from '../config/content'
import type { GameStorageState } from '../types/game'

export function createInitialState(): GameStorageState {
  return {
    schemaVersion: 1,
    savedAt: new Date().toISOString(),
    currentRoute: 'landing',
    game: {
      config: {
        title: '수련회 팀빌딩 성경 미션',
        participantCount: 12,
        teamCount: 3,
        themeKeyword: DEFAULT_CONTENT_SET.themeKeyword,
        ageGroup: 'middleHigh',
      },
      progress: {
        stage1: 'ready',
        stage2: 'locked',
        stage3: 'locked',
        stage4: 'locked',
      },
    },
    teams: [],
    participants: [],
    personalityResponses: [],
    personalityResults: [],
    teamAssignments: [],
    hintPool: DEFAULT_CONTENT_SET.items.map((item) => ({
      ...item,
      selected: true,
    })),
    itemAssignments: [],
    missionResponses: {
      stage3: [],
      stage4: [],
    },
    reflections: [],
    exportState: {},
  }
}
