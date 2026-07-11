import type { PersonalityType } from './game'

export type PersonalityQuestion = {
  id: string
  text: string
  options: {
    id: PersonalityType
    label: string
    scoreType: PersonalityType
  }[]
}

export type GameItem = {
  id: string
  name: string
  description: string
}

export type Stage3Mission = {
  id: string
  type: 'choice' | 'short'
  question: string
  options?: string[]
  answer?: string
  collaborationPrompt: string
  personalityRoleHint: string
}

export type Stage4Mission = {
  id: string
  prompt: string
}

export type ContentSet = {
  themeKeyword: string
  bibleReferences: string[]
  personalityQuestions: PersonalityQuestion[]
  items: GameItem[]
  stage3Missions: Stage3Mission[]
  stage4Mission: Stage4Mission
}
