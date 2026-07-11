export type PersonalityType = 'idea' | 'analysis' | 'action' | 'encouragement'

export type RouteId =
  | 'landing'
  | 'setup'
  | 'team-prep'
  | 'personality'
  | 'stage2'
  | 'stage3'
  | 'stage4'
  | 'reflection'
  | 'export'

export type StageStatus = 'locked' | 'ready' | 'active' | 'completed'

export type Team = {
  id: string
  name: string
}

export type Participant = {
  id: string
  displayName: string
}

export type PersonalityAnswer = {
  questionId: string
  optionId: PersonalityType
}

export type PersonalityResponse = {
  participantId: string
  answers: PersonalityAnswer[]
}

export type PersonalityScores = Record<PersonalityType, number>

export type PersonalityResult = {
  participantId: string
  primaryType: PersonalityType
  scores: PersonalityScores
}

export type TeamAssignment = {
  teamId: string
  participantId: string
  primaryType: PersonalityType
}

export type ItemAssignment = {
  teamId: string
  itemId: string
}

export type Stage3Response = {
  teamId: string
  answers: Record<string, string>
  completed: boolean
}

export type Stage4Response = {
  teamId: string
  finalAnswer: string
  confirmed: boolean
}

export type Reflection = {
  teamId: string
  memorableWord: string
  solvedTogether: string
  gratitude: string
  practice: string
}

export type GameConfig = {
  title: string
  participantCount: number
  teamCount: number
  themeKeyword: string
  ageGroup: 'middleHigh'
}

export type StageProgress = Record<'stage1' | 'stage2' | 'stage3' | 'stage4', StageStatus>

export type ExportState = {
  lastDownloadedAt?: string
}

export type GameStorageState = {
  schemaVersion: 1
  savedAt: string
  currentRoute: RouteId
  game: {
    config: GameConfig
    progress: StageProgress
  }
  teams: Team[]
  participants: Participant[]
  personalityResponses: PersonalityResponse[]
  personalityResults: PersonalityResult[]
  teamAssignments: TeamAssignment[]
  itemAssignments: ItemAssignment[]
  hintPool: {
    id: string
    name: string
    description: string
    selected: boolean
  }[]
  missionResponses: {
    stage3: Stage3Response[]
    stage4: Stage4Response[]
  }
  reflections: Reflection[]
  exportState: ExportState
  resumeRoute?: Exclude<RouteId, 'landing'>
}

export type ValidationResult = {
  valid: boolean
  errors: string[]
}
