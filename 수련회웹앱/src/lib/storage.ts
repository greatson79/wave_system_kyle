import type { GameStorageState } from '../types/game'

export const STORAGE_KEY = 'retreat-game:v1:state'

export function saveGameState(state: GameStorageState) {
  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({ ...state, savedAt: new Date().toISOString() }),
  )
}

export function loadGameState(): GameStorageState | null {
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) return null

  try {
    const parsed = JSON.parse(raw) as GameStorageState
    if (parsed.schemaVersion !== 1) return null
    return {
      ...parsed,
      currentRoute: 'landing',
      resumeRoute: parsed.currentRoute === 'landing' ? parsed.resumeRoute : parsed.currentRoute,
    }
  } catch {
    return null
  }
}

export function clearGameState() {
  localStorage.removeItem(STORAGE_KEY)
}
