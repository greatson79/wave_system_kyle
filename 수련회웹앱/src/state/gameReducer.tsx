import { DEFAULT_CONTENT_SET } from '../config/content'
import { createInitialState } from './initialState'
import { isStage3Complete, isStage4Complete } from '../lib/missionEngine'
import { buildBalancedTeams, scorePersonalityResponses } from '../lib/teamBuilder'
import type {
  GameItem,
} from '../types/content'
import type {
  GameConfig,
  GameStorageState,
  Participant,
  PersonalityAnswer,
  Reflection,
  RouteId,
  Stage3Response,
  Stage4Response,
  Team,
} from '../types/game'

export type GameAction =
  | { type: 'RESET' }
  | { type: 'GO_TO'; route: RouteId }
  | { type: 'SET_CONFIG'; config: GameConfig }
  | { type: 'SET_TEAMS_AND_PARTICIPANTS'; teams: Team[]; participants: Participant[] }
  | { type: 'SET_PERSONALITY_RESPONSE'; participantId: string; answers: PersonalityAnswer[] }
  | { type: 'BUILD_TEAMS' }
  | { type: 'SET_HINT_POOL'; hints: GameStorageState['hintPool'] }
  | { type: 'SET_ITEM_ASSIGNMENTS'; assignments: GameStorageState['itemAssignments']; items: GameItem[] }
  | { type: 'SET_STAGE3_RESPONSE'; response: Stage3Response }
  | { type: 'SET_STAGE4_RESPONSE'; response: Stage4Response }
  | { type: 'SET_REFLECTION'; reflection: Reflection }
  | { type: 'MARK_EXPORTED' }

function upsertById<T>(items: T[], item: T, getId: (value: T) => string) {
  const exists = items.some((value) => getId(value) === getId(item))
  return exists ? items.map((value) => (getId(value) === getId(item) ? item : value)) : [...items, item]
}

export function gameReducer(state: GameStorageState, action: GameAction): GameStorageState {
  switch (action.type) {
    case 'RESET':
      return createInitialState()
    case 'GO_TO':
      return { ...state, currentRoute: action.route, resumeRoute: undefined }
    case 'SET_CONFIG':
      return {
        ...state,
        currentRoute: 'team-prep',
        game: { ...state.game, config: action.config },
      }
    case 'SET_TEAMS_AND_PARTICIPANTS':
      return {
        ...state,
        currentRoute: 'personality',
        teams: action.teams,
        participants: action.participants,
      }
    case 'SET_PERSONALITY_RESPONSE':
      return {
        ...state,
        personalityResponses: upsertById(
          state.personalityResponses,
          { participantId: action.participantId, answers: action.answers },
          (value) => value.participantId,
        ),
      }
    case 'BUILD_TEAMS': {
      const results = state.personalityResponses.map((response) =>
        scorePersonalityResponses(
          response.participantId,
          response.answers,
          DEFAULT_CONTENT_SET.personalityQuestions,
        ),
      )
      return {
        ...state,
        currentRoute: 'stage2',
        personalityResults: results,
        teamAssignments: buildBalancedTeams(state.teams, results),
        game: {
          ...state.game,
          progress: { ...state.game.progress, stage1: 'completed', stage2: 'ready' },
        },
      }
    }
    case 'SET_HINT_POOL':
      return {
        ...state,
        hintPool: action.hints,
      }
    case 'SET_ITEM_ASSIGNMENTS':
      return {
        ...state,
        currentRoute: 'stage2',
        itemAssignments: action.assignments,
        hintPool: action.items.map((item) => ({ ...item, selected: true })),
        game: {
          ...state.game,
          progress: { ...state.game.progress, stage2: 'completed', stage3: 'ready' },
        },
      }
    case 'SET_STAGE3_RESPONSE': {
      const stage3 = upsertById(
        state.missionResponses.stage3,
        action.response,
        (value) => value.teamId,
      )
      const complete = isStage3Complete(
        stage3,
        state.teams.map((team) => team.id),
        DEFAULT_CONTENT_SET.stage3Missions.map((mission) => mission.id),
      )
      return {
        ...state,
        missionResponses: { ...state.missionResponses, stage3 },
        game: {
          ...state.game,
          progress: { ...state.game.progress, stage3: complete ? 'completed' : 'active' },
        },
      }
    }
    case 'SET_STAGE4_RESPONSE': {
      const stage4 = upsertById(
        state.missionResponses.stage4,
        action.response,
        (value) => value.teamId,
      )
      const complete = isStage4Complete(stage4, state.teams.map((team) => team.id))
      return {
        ...state,
        missionResponses: { ...state.missionResponses, stage4 },
        game: {
          ...state.game,
          progress: { ...state.game.progress, stage4: complete ? 'completed' : 'active' },
        },
      }
    }
    case 'SET_REFLECTION':
      return {
        ...state,
        reflections: upsertById(state.reflections, action.reflection, (value) => value.teamId),
      }
    case 'MARK_EXPORTED':
      return {
        ...state,
        exportState: { lastDownloadedAt: new Date().toISOString() },
      }
  }
}
