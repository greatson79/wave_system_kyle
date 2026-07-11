import type { GameItem } from '../types/content'
import type { ItemAssignment, Team } from '../types/game'

function seededIndex(seed: number, index: number, length: number) {
  return Math.abs((seed * 31 + index * 17) % length)
}

export function assignItems(teams: Team[], items: GameItem[], seed = Date.now()): ItemAssignment[] {
  if (items.length === 0) return []

  return teams.map((team, index) => ({
    teamId: team.id,
    itemId: items[seededIndex(seed, index, items.length)].id,
  }))
}
