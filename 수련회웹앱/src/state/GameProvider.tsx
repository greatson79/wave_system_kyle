import { useEffect, useMemo, useReducer } from 'react'
import type { ReactNode } from 'react'
import { loadGameState, saveGameState } from '../lib/storage'
import { GameContext } from './GameContext'
import { gameReducer } from './gameReducer'
import { createInitialState } from './initialState'

export function GameProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(
    gameReducer,
    undefined,
    () => loadGameState() ?? createInitialState(),
  )

  useEffect(() => {
    saveGameState(state)
  }, [state])

  const value = useMemo(() => ({ state, dispatch }), [state])
  return <GameContext.Provider value={value}>{children}</GameContext.Provider>
}
