import { createContext } from 'react'
import type { Dispatch } from 'react'
import type { GameStorageState } from '../types/game'
import type { GameAction } from './gameReducer'

export const GameContext = createContext<{
  state: GameStorageState
  dispatch: Dispatch<GameAction>
} | null>(null)
