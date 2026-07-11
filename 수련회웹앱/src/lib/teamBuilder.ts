import type { PersonalityQuestion } from '../types/content'
import type {
  PersonalityAnswer,
  PersonalityResult,
  PersonalityScores,
  PersonalityType,
  Team,
  TeamAssignment,
} from '../types/game'

const personalityTypes: PersonalityType[] = ['idea', 'analysis', 'action', 'encouragement']

function emptyScores(): PersonalityScores {
  return {
    idea: 0,
    analysis: 0,
    action: 0,
    encouragement: 0,
  }
}

export function scorePersonalityResponses(
  participantId: string,
  answers: PersonalityAnswer[],
  questions: PersonalityQuestion[],
): PersonalityResult {
  const scores = emptyScores()

  answers.forEach((answer) => {
    const question = questions.find((item) => item.id === answer.questionId)
    const option = question?.options.find((item) => item.id === answer.optionId)
    if (option) scores[option.scoreType] += 1
  })

  const primaryType = personalityTypes.reduce((current, next) =>
    scores[next] > scores[current] ? next : current,
  )

  return { participantId, primaryType, scores }
}

export function buildBalancedTeams(
  teams: Team[],
  results: PersonalityResult[],
): TeamAssignment[] {
  const buckets = new Map<string, TeamAssignment[]>()
  teams.forEach((team) => buckets.set(team.id, []))

  const ordered = [...results].sort((a, b) =>
    a.primaryType.localeCompare(b.primaryType) || a.participantId.localeCompare(b.participantId),
  )

  ordered.forEach((result) => {
    const target = teams.reduce((best, team) => {
      const bestCount = buckets.get(best.id)?.length ?? 0
      const teamCount = buckets.get(team.id)?.length ?? 0
      return teamCount < bestCount ? team : best
    }, teams[0])

    buckets.get(target.id)?.push({
      teamId: target.id,
      participantId: result.participantId,
      primaryType: result.primaryType,
    })
  })

  return teams.flatMap((team) => buckets.get(team.id) ?? [])
}
