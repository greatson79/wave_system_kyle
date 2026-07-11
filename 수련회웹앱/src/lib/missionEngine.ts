import type { Stage3Response, Stage4Response } from '../types/game'

export function isStage3Complete(
  responses: Stage3Response[],
  teamIds: string[],
  requiredMissionIds: string[],
) {
  return teamIds.every((teamId) => {
    const response = responses.find((item) => item.teamId === teamId)
    if (!response?.completed) {
      return false
    }
    return requiredMissionIds.every((missionId) => Boolean(response.answers[missionId]?.trim()))
  })
}

export function isStage4Complete(responses: Stage4Response[], teamIds: string[]) {
  return teamIds.every((teamId) => {
    const response = responses.find((item) => item.teamId === teamId)
    return Boolean(response?.confirmed && response.finalAnswer.trim())
  })
}
