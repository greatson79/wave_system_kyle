import { Download, Flag, RotateCcw, Save, Shuffle, Users } from 'lucide-react'
import { useMemo, useRef, useState } from 'react'
import './App.css'
import { DEFAULT_CONTENT_SET } from './config/content'
import { STAGES } from './config/stages'
import { downloadElementAsImage } from './lib/exporter'
import { validateReflection } from './lib/reflectionManager'
import { validateGameSetup, validateTeamNames } from './lib/validation'
import { useGame } from './state/useGame'
import type {
  GameConfig,
  Participant,
  PersonalityAnswer,
  Reflection,
  Stage3Response,
  Stage4Response,
  Team,
} from './types/game'

const personalityLabels = {
  idea: '아이디어형',
  analysis: '분석형',
  action: '실행형',
  encouragement: '격려형',
}

function makeTeams(count: number): Team[] {
  const names = ['믿음팀', '사랑팀', '소망팀', '기쁨팀', '은혜팀', '평화팀']
  return Array.from({ length: count }, (_, index) => ({
    id: `team-${index + 1}`,
    name: names[index] ?? `팀 ${index + 1}`,
  }))
}

function makeParticipants(count: number): Participant[] {
  return Array.from({ length: count }, (_, index) => ({
    id: `participant-${index + 1}`,
    displayName: `참가자 ${index + 1}`,
  }))
}

function App() {
  const { state, dispatch } = useGame()

  if (state.currentRoute === 'landing') {
    return (
      <main className="landing-shell">
        <LandingPage />
      </main>
    )
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand-block">
          <span className="brand-mark">BT</span>
          <div>
            <p className="eyebrow">Bible Team Mission</p>
            <h1>{state.game.config.title}</h1>
          </div>
        </div>
        <StageTracker />
        <div className="sidebar-actions">
          <button className="ghost-button" type="button" onClick={() => dispatch({ type: 'RESET' })}>
            <RotateCcw size={16} />
            새 게임
          </button>
        </div>
      </aside>

      <section className="workspace">
        {state.currentRoute === 'setup' && <SetupPage />}
        {state.currentRoute === 'team-prep' && <TeamPrepPage />}
        {state.currentRoute === 'personality' && <PersonalityPage />}
        {state.currentRoute === 'stage2' && <Stage2Page />}
        {state.currentRoute === 'stage3' && <Stage3Page />}
        {state.currentRoute === 'stage4' && <Stage4Page />}
        {state.currentRoute === 'reflection' && <ReflectionPage />}
        {state.currentRoute === 'export' && <ExportPage />}
      </section>
    </main>
  )
}

function StageTracker() {
  const { state } = useGame()
  const missionRoute =
    state.currentRoute === 'setup' ||
    state.currentRoute === 'team-prep' ||
    state.currentRoute === 'personality'
      ? 'personality'
      : state.currentRoute
  const currentIndex = ['personality', 'stage2', 'stage3', 'stage4'].indexOf(missionRoute)

  return (
    <ol className="stage-tracker" aria-label="게임 진행 단계">
      {STAGES.map((stage, index) => {
        const status =
          state.game.progress[`stage${stage.number}` as keyof typeof state.game.progress]
        const active = missionRoute === stage.id
        const ready = currentIndex >= index || status === 'completed'
        return (
          <li className={active ? 'active' : ready ? 'ready' : ''} key={stage.id}>
            <span>{stage.number}</span>
            <div>
              <strong>{stage.title}</strong>
              <small>{status === 'completed' ? '완료' : active ? '진행 중' : '대기'}</small>
            </div>
          </li>
        )
      })}
    </ol>
  )
}

function LandingPage() {
  const { state, dispatch } = useGame()

  return (
    <section className="landing-page">
      <div className="landing-copy">
        <p className="eyebrow">Retreat Web Game</p>
        <h2>수련회 팀빌딩 성경 미션</h2>
        <p>
          팀을 구성하고, 사다리타기로 힌트를 얻고, 말씀을 바탕으로 협력해
          공동체 약속을 완성하는 웹앱형 팀빌딩 게임입니다.
        </p>
        <div className="landing-steps">
          <span>Mission 1 팀 구성</span>
          <span>Mission 2 힌트 획득</span>
          <span>Mission 3 말씀 협력</span>
          <span>Mission 4 약속 완성</span>
        </div>
        <button
          className="start-button"
          type="button"
          onClick={() => dispatch({ type: 'GO_TO', route: 'setup' })}
        >
          <Flag size={20} />
          시작하기
        </button>
        {state.resumeRoute && (
          <button
            className="secondary-button continue-button"
            type="button"
            onClick={() => dispatch({ type: 'GO_TO', route: state.resumeRoute! })}
          >
            이전 진행 이어하기
          </button>
        )}
      </div>
      <div className="landing-board" aria-hidden="true">
        <div className="board-card primary">공동체</div>
        <div className="board-card">말씀</div>
        <div className="board-card">협력</div>
        <div className="board-card">약속</div>
      </div>
    </section>
  )
}

function PageHeader({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string
  title: string
  description: string
}) {
  return (
    <header className="page-header">
      <p className="eyebrow">{eyebrow}</p>
      <h2>{title}</h2>
      <p>{description}</p>
    </header>
  )
}

function SetupPage() {
  const { state, dispatch } = useGame()
  const [form, setForm] = useState<GameConfig>(state.game.config)
  const validation = validateGameSetup(form)

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Mission 1"
        title="Mission 1 팀을 구성하라"
        description="전체 인원과 팀 수를 정한 뒤 팀 이름을 입력하고, 간이 성향 질문으로 균형 있게 팀을 구성합니다."
      />

      <div className="form-grid">
        <label>
          게임 제목
          <input
            value={form.title}
            onChange={(event) => setForm({ ...form, title: event.target.value })}
          />
        </label>
        <label>
          주제 키워드
          <input
            value={form.themeKeyword}
            onChange={(event) => setForm({ ...form, themeKeyword: event.target.value })}
          />
        </label>
        <label>
          전체 인원
          <input
            min={2}
            type="number"
            value={form.participantCount}
            onChange={(event) =>
              setForm({ ...form, participantCount: Number(event.target.value) })
            }
          />
        </label>
        <label>
          팀 수
          <input
            min={2}
            type="number"
            value={form.teamCount}
            onChange={(event) => setForm({ ...form, teamCount: Number(event.target.value) })}
          />
        </label>
      </div>

      {!validation.valid && <ErrorList errors={validation.errors} />}

      <div className="action-row">
        <button
          className="primary-button"
          disabled={!validation.valid}
          type="button"
          onClick={() => dispatch({ type: 'SET_CONFIG', config: form })}
        >
          <Save size={18} />
          팀 이름 입력
        </button>
      </div>
    </div>
  )
}

function TeamPrepPage() {
  const { state, dispatch } = useGame()
  const [teams, setTeams] = useState<Team[]>(
    state.teams.length ? state.teams : makeTeams(state.game.config.teamCount),
  )
  const participants = useMemo(
    () =>
      state.participants.length
        ? state.participants
        : makeParticipants(state.game.config.participantCount),
    [state.game.config.participantCount, state.participants],
  )
  const validation = validateTeamNames(teams.map((team) => team.name))

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Mission 1"
        title="Mission 1 팀을 구성하라"
        description="팀 이름은 결과 이미지에도 표시됩니다. 개인정보 대신 공동체 분위기에 맞는 이름을 사용하세요."
      />

      <div className="team-name-grid">
        {teams.map((team, index) => (
          <label key={team.id}>
            {index + 1}팀 이름
            <input
              value={team.name}
              onChange={(event) =>
                setTeams((current) =>
                  current.map((item) =>
                    item.id === team.id ? { ...item, name: event.target.value } : item,
                  ),
                )
              }
            />
          </label>
        ))}
      </div>

      <div className="participant-strip">
        {participants.map((participant) => (
          <span key={participant.id}>{participant.displayName}</span>
        ))}
      </div>

      {!validation.valid && <ErrorList errors={validation.errors} />}

      <div className="action-row">
        <button
          className="primary-button"
          disabled={!validation.valid}
          type="button"
          onClick={() =>
            dispatch({ type: 'SET_TEAMS_AND_PARTICIPANTS', teams, participants })
          }
        >
          <Users size={18} />
          성향 질문 시작
        </button>
      </div>
    </div>
  )
}

function PersonalityPage() {
  const { state, dispatch } = useGame()

  function autoFill() {
    state.participants.forEach((participant, participantIndex) => {
      const answers = DEFAULT_CONTENT_SET.personalityQuestions.map((question, questionIndex) => {
        const option = question.options[(participantIndex + questionIndex) % question.options.length]
        return { questionId: question.id, optionId: option.id }
      })
      dispatch({ type: 'SET_PERSONALITY_RESPONSE', participantId: participant.id, answers })
    })
  }

  const ready = state.personalityResponses.length === state.participants.length

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Mission 1"
        title="Mission 1 팀을 구성하라"
        description="전문 검사가 아니라 팀을 섞기 위한 활동입니다. 응답을 바탕으로 아이디어형, 분석형, 실행형, 격려형이 섞이도록 배정합니다."
      />

      <div className="action-row left">
        <button className="secondary-button" type="button" onClick={autoFill}>
          <Shuffle size={17} />
          자동 응답 채우기
        </button>
      </div>

      <div className="question-list">
        {state.participants.map((participant) => (
          <ParticipantQuestions key={participant.id} participant={participant} />
        ))}
      </div>

      <div className="action-row">
        <button
          className="primary-button"
          disabled={!ready}
          type="button"
          onClick={() => dispatch({ type: 'BUILD_TEAMS' })}
        >
          팀 구성 결과 만들기
        </button>
      </div>
    </div>
  )
}

function ParticipantQuestions({ participant }: { participant: Participant }) {
  const { state, dispatch } = useGame()
  const response = state.personalityResponses.find((item) => item.participantId === participant.id)

  function setAnswer(questionId: string, optionId: PersonalityAnswer['optionId']) {
    const current = response?.answers ?? []
    const answers = [
      ...current.filter((answer) => answer.questionId !== questionId),
      { questionId, optionId },
    ]
    dispatch({ type: 'SET_PERSONALITY_RESPONSE', participantId: participant.id, answers })
  }

  return (
    <section className="participant-block">
      <h3>{participant.displayName}</h3>
      {DEFAULT_CONTENT_SET.personalityQuestions.map((question) => {
        const selected = response?.answers.find((answer) => answer.questionId === question.id)
        return (
          <label key={question.id}>
            {question.text}
            <select
              value={selected?.optionId ?? ''}
              onChange={(event) =>
                setAnswer(question.id, event.target.value as PersonalityAnswer['optionId'])
              }
            >
              <option value="">선택</option>
              {question.options.map((option) => (
                <option key={option.id} value={option.id}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
        )
      })}
    </section>
  )
}

function Stage2Page() {
  const { state, dispatch } = useGame()
  const laneCount = Math.max(state.teams.length * 2, 2)
  const rowCount = 10
  const [teamHints, setTeamHints] = useState<Record<string, [string, string]>>({})
  const [hintSlots, setHintSlots] = useState<Record<string, [number, number]>>({})
  const [teamLines, setTeamLines] = useState<Record<string, { row: number; col: number }[]>>({})
  const [startSelections, setStartSelections] = useState<Record<string, [number | null, number | null]>>({})
  const [running, setRunning] = useState(false)
  const [currentTeamId, setCurrentTeamId] = useState<string | null>(null)
  const [runnerPosition, setRunnerPosition] = useState<{ col: number; row: number } | null>(null)
  const [revealedSlots, setRevealedSlots] = useState<number[]>([])
  const [teamResults, setTeamResults] = useState<Record<string, string[]>>({})
  const [validationError, setValidationError] = useState('')

  function getTeamHint(teamId: string, index: 0 | 1) {
    return teamHints[teamId]?.[index] ?? ''
  }

  function updateTeamHint(teamId: string, slot: 0 | 1, value: string) {
    setTeamHints((current) => ({
      ...current,
      [teamId]: slot === 0 ? [value, current[teamId]?.[1] ?? ''] : [current[teamId]?.[0] ?? '', value],
    }))
  }

  function updateHintSlot(teamId: string, slot: 0 | 1, value: number) {
    setHintSlots((current) => ({
      ...current,
      [teamId]: slot === 0 ? [value, current[teamId]?.[1] ?? 1] : [current[teamId]?.[0] ?? 1, value],
    }))
  }

  function updateStartSelection(teamId: string, cycle: 0 | 1, value: number) {
    setStartSelections((current) => ({
      ...current,
      [teamId]: cycle === 0 ? [value, current[teamId]?.[1] ?? null] : [current[teamId]?.[0] ?? null, value],
    }))
  }

  function addTeamLine(teamId: string, row: number, col: number) {
    const existing = teamLines[teamId] ?? []
    if (existing.length >= 3 || col < 1 || col >= laneCount) return
    const all = Object.values(teamLines).flat()
    const occupied = all.some((line) => line.row === row && (line.col === col || Math.abs(line.col - col) === 1))
    if (occupied) {
      setValidationError('같은 높이에서 가로줄이 연속/교차되면 안 됩니다.')
      return
    }
    setValidationError('')
    setTeamLines((current) => ({
      ...current,
      [teamId]: [...existing, { row, col }],
    }))
  }

  function buildLineMap() {
    const map: boolean[][] = Array.from({ length: rowCount }, () => Array.from({ length: laneCount - 1 }, () => false))
    for (const line of Object.values(teamLines).flat()) {
      map[line.row - 1][line.col - 1] = true
    }
    return map
  }

  function tracePath(startCol: number, map: boolean[][]) {
    let col = startCol
    const path: { col: number; row: number }[] = [{ col, row: 0 }]
    for (let row = 0; row < rowCount; row += 1) {
      if (col < laneCount - 1 && map[row][col]) {
        col += 1
        path.push({ col, row: row + 0.5 })
      } else if (col > 0 && map[row][col - 1]) {
        col -= 1
        path.push({ col, row: row + 0.5 })
      }
      path.push({ col, row: row + 1 })
    }
    return { path, endCol: col }
  }

  async function runLadder() {
    if (running) return
    const invalidHints = state.teams.find((team) => getTeamHint(team.id, 0).trim() === '' || getTeamHint(team.id, 1).trim() === '')
    if (invalidHints) return setValidationError('각 팀은 힌트 2개를 모두 입력해야 합니다.')
    const invalidSlots = state.teams.find((team) => {
      const slots = hintSlots[team.id]
      return !slots || slots[0] === slots[1]
    })
    if (invalidSlots) return setValidationError('각 팀의 힌트 슬롯 2개는 서로 달라야 합니다.')
    const flatSlots = state.teams.flatMap((team) => hintSlots[team.id] ?? [])
    if (new Set(flatSlots).size !== laneCount) return setValidationError('하단 도착지점은 중복 없이 모두 채워야 합니다.')
    const invalidLines = state.teams.find((team) => (teamLines[team.id] ?? []).length !== 3)
    if (invalidLines) return setValidationError('각 팀은 가로줄을 정확히 3개씩 배치해야 합니다.')
    const invalidStarts = state.teams.find((team) => {
      const starts = startSelections[team.id] ?? [null, null]
      return starts[0] === null || starts[1] === null
    })
    if (invalidStarts) return setValidationError('각 팀은 출발점 2개를 선택해야 합니다.')
    const allStarts = state.teams.flatMap((team) => (startSelections[team.id] ?? [null, null]).filter((v): v is number => v !== null))
    if (new Set(allStarts).size !== laneCount) return setValidationError('출발점은 중복 없이 선택되어야 합니다.')

    setValidationError('')
    setRunning(true)
    setCurrentTeamId(null)
    setRunnerPosition(null)
    setRevealedSlots([])
    setTeamResults({})

    const lineMap = buildLineMap()
    const slotHintMap: Record<number, string> = {}
    state.teams.forEach((team) => {
      const slots = hintSlots[team.id]
      const hints = teamHints[team.id] ?? ['', '']
      if (slots) {
        slotHintMap[slots[0]] = hints[0]
        slotHintMap[slots[1]] = hints[1]
      }
    })

    const nextTeamResults: Record<string, string[]> = {}
    for (const team of state.teams) {
      setCurrentTeamId(team.id)
      const starts = startSelections[team.id] as [number, number]
      nextTeamResults[team.id] = []
      for (const start of starts) {
        const { path, endCol } = tracePath(start - 1, lineMap)
        for (const step of path) {
          setRunnerPosition(step)
          await new Promise((resolve) => setTimeout(resolve, step.row % 1 === 0 ? 140 : 170))
        }
        const slotNumber = endCol + 1
        const hint = slotHintMap[slotNumber] ?? '빈 슬롯'
        nextTeamResults[team.id].push(hint)
        setTeamResults({ ...nextTeamResults })
        setRevealedSlots((current) => (current.includes(slotNumber) ? current : [...current, slotNumber]))
        await new Promise((resolve) => setTimeout(resolve, 250))
      }
    }

    const exportItems = Object.entries(slotHintMap).map(([slot, text]) => ({ id: `slot-${slot}`, name: `도착 ${slot}`, description: text }))
    const assignments = state.teams.map((team) => ({ teamId: team.id, itemId: `slot-${(hintSlots[team.id] ?? [1, 1])[0]}` }))

    dispatch({ type: 'SET_ITEM_ASSIGNMENTS', assignments, items: exportItems })
    setCurrentTeamId(null)
    setRunnerPosition(null)
    setRunning(false)
  }

  const lineMap = buildLineMap()
  const usedStarts = new Set(state.teams.flatMap((team) => (startSelections[team.id] ?? []).filter((v): v is number => v !== null)))
  const usedSlots = new Set(state.teams.flatMap((team) => hintSlots[team.id] ?? []))

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Mission 2"
        title="Mission 2 힌트를 획득하라"
        description="세로줄은 팀 수×2로 구성됩니다. 힌트 배치, 가로줄 3개씩 배치, 출발점 2개씩 선택 후 사다리를 실행합니다."
      />
      <TeamAssignmentSummary />
      <section className="ladder-top-choices">
        {state.teams.map((team) => (
          <section className="ladder-choice-card" key={`hint-${team.id}`}>
            <h4>{team.name} 힌트 2개 + 하단 슬롯</h4>
            <div className="choice-row">
              <label>힌트 1<input value={getTeamHint(team.id, 0)} onChange={(e) => updateTeamHint(team.id, 0, e.target.value)} /></label>
              <label>슬롯
                <select value={hintSlots[team.id]?.[0] ?? 1} onChange={(e) => updateHintSlot(team.id, 0, Number(e.target.value))}>
                  {Array.from({ length: laneCount }, (_, idx) => idx + 1).map((slot) => <option key={`${team.id}-h1-${slot}`} value={slot}>{slot}{usedSlots.has(slot) && hintSlots[team.id]?.[0] !== slot ? ' (사용중)' : ''}</option>)}
                </select>
              </label>
            </div>
            <div className="choice-row">
              <label>힌트 2<input value={getTeamHint(team.id, 1)} onChange={(e) => updateTeamHint(team.id, 1, e.target.value)} /></label>
              <label>슬롯
                <select value={hintSlots[team.id]?.[1] ?? 2} onChange={(e) => updateHintSlot(team.id, 1, Number(e.target.value))}>
                  {Array.from({ length: laneCount }, (_, idx) => idx + 1).map((slot) => <option key={`${team.id}-h2-${slot}`} value={slot}>{slot}{usedSlots.has(slot) && hintSlots[team.id]?.[1] !== slot ? ' (사용중)' : ''}</option>)}
                </select>
              </label>
            </div>
          </section>
        ))}
      </section>
      <LadderGame teams={state.teams} laneCount={laneCount} rowCount={rowCount} lineMap={lineMap} runnerPosition={runnerPosition} currentTeamId={currentTeamId} revealedSlots={revealedSlots} />
      <section className="ladder-top-choices">
        {state.teams.map((team) => (
          <section className="ladder-choice-card" key={`line-${team.id}`}>
            <h4>{team.name} 가로줄 ({(teamLines[team.id] ?? []).length}/3)</h4>
            <div className="choice-row">
              <label>높이<select id={`row-${team.id}`} defaultValue={1}>{Array.from({ length: rowCount }, (_, idx) => idx + 1).map((row) => <option key={`${team.id}-row-${row}`} value={row}>{row}</option>)}</select></label>
              <label>시작 세로줄<select id={`col-${team.id}`} defaultValue={1}>{Array.from({ length: laneCount - 1 }, (_, idx) => idx + 1).map((col) => <option key={`${team.id}-col-${col}`} value={col}>{col}</option>)}</select></label>
            </div>
            <button className="secondary-button" type="button" onClick={() => {
              const rowEl = document.getElementById(`row-${team.id}`) as HTMLSelectElement | null
              const colEl = document.getElementById(`col-${team.id}`) as HTMLSelectElement | null
              if (rowEl && colEl) addTeamLine(team.id, Number(rowEl.value), Number(colEl.value))
            }}>가로줄 추가</button>
          </section>
        ))}
      </section>
      <section className="ladder-top-choices">
        {state.teams.map((team) => (
          <section className="ladder-choice-card" key={`start-${team.id}`}>
            <h4>{team.name} 출발점 2개</h4>
            <div className="choice-row">
              <label>출발 1
                <select value={startSelections[team.id]?.[0] ?? ''} onChange={(e) => updateStartSelection(team.id, 0, Number(e.target.value))}>
                  <option value="">선택</option>
                  {Array.from({ length: laneCount }, (_, idx) => idx + 1).map((slot) => <option key={`${team.id}-s1-${slot}`} value={slot}>{slot}{usedStarts.has(slot) && startSelections[team.id]?.[0] !== slot ? ' (사용중)' : ''}</option>)}
                </select>
              </label>
              <label>출발 2
                <select value={startSelections[team.id]?.[1] ?? ''} onChange={(e) => updateStartSelection(team.id, 1, Number(e.target.value))}>
                  <option value="">선택</option>
                  {Array.from({ length: laneCount }, (_, idx) => idx + 1).map((slot) => <option key={`${team.id}-s2-${slot}`} value={slot}>{slot}{usedStarts.has(slot) && startSelections[team.id]?.[1] !== slot ? ' (사용중)' : ''}</option>)}
                </select>
              </label>
            </div>
          </section>
        ))}
      </section>
      {Object.keys(teamResults).length > 0 && <section className="summary-block"><h3>결과</h3><ul>{state.teams.map((team) => <li key={team.id}>{`${team.name}: ${(teamResults[team.id] ?? []).join(', ')}`}</li>)}</ul></section>}
      {validationError && <p className="error-text">{validationError}</p>}
      <div className="action-row">
        {!state.itemAssignments.length ? (
          <button className="primary-button" disabled={running} type="button" onClick={runLadder}><Shuffle size={18} />게임 시작</button>
        ) : (
          <button className="primary-button" type="button" onClick={() => dispatch({ type: 'GO_TO', route: 'stage3' })}>3단계로 이동</button>
        )}
      </div>
    </div>
  )
}

function LadderGame({
  teams,
  laneCount,
  rowCount,
  lineMap,
  runnerPosition,
  currentTeamId,
  revealedSlots,
}: {
  teams: Team[]
  laneCount: number
  rowCount: number
  lineMap: boolean[][]
  runnerPosition: { col: number; row: number } | null
  currentTeamId: string | null
  revealedSlots: number[]
}) {
  return (
    <section className="ladder-panel">
      <div className="ladder-board-header" style={{ gridTemplateColumns: `repeat(${laneCount}, minmax(70px, 1fr))` }}>
        {Array.from({ length: laneCount }, (_, idx) => <div className="ladder-lane-label" key={`top-${idx + 1}`}><strong>{idx + 1}</strong></div>)}
      </div>
      <div className="ladder-track">
        {Array.from({ length: laneCount }, (_, index) => <div className="ladder-vertical" key={`line-${index + 1}`} style={{ left: `${laneCount === 1 ? 50 : (index / (laneCount - 1)) * 100}%` }} />)}
        {lineMap.map((row, rowIndex) =>
          row.map((linked, colIndex) =>
            linked ? <div className="ladder-bridge" key={`bridge-${rowIndex}-${colIndex}`} style={{ top: `${((rowIndex + 1) / (rowCount + 1)) * 100}%`, left: `${(colIndex / (laneCount - 1)) * 100}%`, width: `${100 / (laneCount - 1)}%` }} /> : null,
          ),
        )}
        {runnerPosition && <div className="ladder-ball running" style={{ left: `${laneCount === 1 ? 50 : (runnerPosition.col / (laneCount - 1)) * 100}%`, top: `${(runnerPosition.row / rowCount) * 100}%` }} />}
      </div>
      <div className="ladder-board" style={{ gridTemplateColumns: `repeat(${laneCount}, minmax(70px, 1fr))` }}>
        {Array.from({ length: laneCount }, (_, idx) => <div className="ladder-lane" key={`bottom-${idx + 1}`}><small>{revealedSlots.includes(idx + 1) ? `도착 ${idx + 1}` : '가림막'}</small></div>)}
      </div>
      {currentTeamId && <p className="ladder-running-text">{`${teams.find((team) => team.id === currentTeamId)?.name ?? ''} 실행 중`}</p>}
    </section>
  )
}

function Stage3Page() {
  const { dispatch } = useGame()
  const missions = DEFAULT_CONTENT_SET.stage3Missions

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Mission 3"
        title="Mission 3 말씀으로 협력하라"
        description="성경 말씀과 주제 키워드를 바탕으로 팀원들이 함께 토론하고 답을 작성합니다. 모든 팀이 답변하면 최종 미션으로 넘어갑니다."
      />

      {missions.map((mission, index) => (
        <section className="mission-box" key={mission.id}>
          <h3>{`문제 ${index + 1}. ${mission.question}`}</h3>
          {mission.options && <p>{`선택지: ${mission.options.join(' / ')}`}</p>}
          <p>{`협업 방식: ${mission.collaborationPrompt}`}</p>
          <p>{`성향별 역할 힌트: ${mission.personalityRoleHint}`}</p>
        </section>
      ))}

      <section className="mission-box">
        <h3>참고 말씀</h3>
        <p>{DEFAULT_CONTENT_SET.bibleReferences.join(' · ')}</p>
      </section>

      <TeamResponseList
        route="stage3"
        stage3MissionIds={missions.map((mission) => mission.id)}
        onNext={() => dispatch({ type: 'GO_TO', route: 'stage4' })}
      />
    </div>
  )
}

function Stage4Page() {
  const { dispatch } = useGame()

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Mission 4"
        title="Mission 4 공동체 약속을 완성하라"
        description={`앞 단계에서 얻은 힌트와 말씀을 바탕으로 팀의 최종 실천 약속을 완성합니다. ${DEFAULT_CONTENT_SET.stage4Mission.prompt}`}
      />
      <TeamResponseList
        route="stage4"
        onNext={() => dispatch({ type: 'GO_TO', route: 'reflection' })}
      />
    </div>
  )
}

function TeamResponseList({
  route,
  onNext,
  stage3MissionIds = [],
}: {
  route: 'stage3' | 'stage4'
  onNext: () => void
  stage3MissionIds?: string[]
}) {
  const { state, dispatch } = useGame()
  const complete =
    route === 'stage3'
      ? state.game.progress.stage3 === 'completed'
      : state.game.progress.stage4 === 'completed'

  return (
    <>
      <div className="response-grid">
        {state.teams.map((team) => {
          const stage3 = state.missionResponses.stage3.find((item) => item.teamId === team.id)
          const stage4 = state.missionResponses.stage4.find((item) => item.teamId === team.id)
          return (
            <section className="team-response" key={team.id}>
              <h3>{team.name}</h3>
              {route === 'stage3' ? (
                <div className="team-mission-answers">
                  {stage3MissionIds.map((missionId, index) => (
                    <label key={`${team.id}-${missionId}`}>
                      {`문제 ${index + 1} 답안`}
                      <textarea
                        value={stage3?.answers[missionId] ?? ''}
                        onChange={(event) => {
                          const nextAnswers = {
                            ...(stage3?.answers ?? {}),
                            [missionId]: event.target.value,
                          }
                          const response: Stage3Response = {
                            teamId: team.id,
                            answers: nextAnswers,
                            completed: stage3MissionIds.every((id) => Boolean(nextAnswers[id]?.trim())),
                          }
                          dispatch({ type: 'SET_STAGE3_RESPONSE', response })
                        }}
                      />
                    </label>
                  ))}
                </div>
              ) : (
                <textarea
                  value={stage4?.finalAnswer ?? ''}
                  onChange={(event) => {
                    const response: Stage4Response = {
                      teamId: team.id,
                      finalAnswer: event.target.value,
                      confirmed: event.target.value.trim().length > 0,
                    }
                    dispatch({ type: 'SET_STAGE4_RESPONSE', response })
                  }}
                />
              )}
            </section>
          )
        })}
      </div>
      <div className="action-row">
        <button className="primary-button" disabled={!complete} type="button" onClick={onNext}>
          다음 단계
        </button>
      </div>
    </>
  )
}

function ReflectionPage() {
  const { state, dispatch } = useGame()
  const allValid = state.teams.every((team) => {
    const reflection = state.reflections.find((item) => item.teamId === team.id)
    return reflection ? validateReflection(reflection).valid : false
  })

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="소감"
        title="팀별 나눔을 정리합니다"
        description="결과 이미지에 들어갈 내용입니다. 실명, 연락처 같은 개인정보를 입력하지 않도록 확인하세요."
      />

      <div className="reflection-grid">
        {state.teams.map((team) => (
          <ReflectionForm key={team.id} team={team} />
        ))}
      </div>

      <div className="action-row">
        <button
          className="primary-button"
          disabled={!allValid}
          type="button"
          onClick={() => dispatch({ type: 'GO_TO', route: 'export' })}
        >
          결과 이미지 만들기
        </button>
      </div>
    </div>
  )
}

function ReflectionForm({ team }: { team: Team }) {
  const { state, dispatch } = useGame()
  const reflection =
    state.reflections.find((item) => item.teamId === team.id) ??
    ({
      teamId: team.id,
      memorableWord: '',
      solvedTogether: '',
      gratitude: '',
      practice: '',
    } satisfies Reflection)

  function update(key: keyof Omit<Reflection, 'teamId'>, value: string) {
    dispatch({ type: 'SET_REFLECTION', reflection: { ...reflection, [key]: value } })
  }

  return (
    <section className="reflection-form">
      <h3>{team.name}</h3>
      <label>
        기억에 남는 말씀 또는 키워드
        <input value={reflection.memorableWord} onChange={(event) => update('memorableWord', event.target.value)} />
      </label>
      <label>
        팀이 함께 해결한 것
        <textarea value={reflection.solvedTogether} onChange={(event) => update('solvedTogether', event.target.value)} />
      </label>
      <label>
        감사한 점
        <textarea value={reflection.gratitude} onChange={(event) => update('gratitude', event.target.value)} />
      </label>
      <label>
        앞으로 실천하고 싶은 것
        <textarea value={reflection.practice} onChange={(event) => update('practice', event.target.value)} />
      </label>
    </section>
  )
}

function ExportPage() {
  const { state, dispatch } = useGame()
  const exportRef = useRef<HTMLDivElement>(null)
  const [error, setError] = useState('')

  async function download() {
    if (!exportRef.current) return
    try {
      setError('')
      await downloadElementAsImage(exportRef.current, 'retreat-team-reflection.png')
      dispatch({ type: 'MARK_EXPORTED' })
    } catch {
      setError('이미지 생성에 실패했습니다. 다시 시도해 주세요.')
    }
  }

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="결과"
        title="제출용 이미지를 확인합니다"
        description="팀별 소감과 미션 요약을 하나의 이미지로 저장합니다. PDF는 MVP 이후 기능입니다."
      />

      <div className="export-preview" ref={exportRef}>
        <h2>{state.game.config.title}</h2>
        <p className="export-theme">주제: {state.game.config.themeKeyword}</p>
        <div className="export-teams">
          {state.teams.map((team) => {
            const reflection = state.reflections.find((item) => item.teamId === team.id)
            const finalMission = state.missionResponses.stage4.find((item) => item.teamId === team.id)
            return (
              <section key={team.id}>
                <h3>{team.name}</h3>
                <p><strong>최종 약속</strong> {finalMission?.finalAnswer}</p>
                <p><strong>기억</strong> {reflection?.memorableWord}</p>
                <p><strong>협력</strong> {reflection?.solvedTogether}</p>
                <p><strong>감사</strong> {reflection?.gratitude}</p>
                <p><strong>실천</strong> {reflection?.practice}</p>
              </section>
            )
          })}
        </div>
      </div>

      {error && <p className="error-text">{error}</p>}

      <div className="action-row">
        <button className="primary-button" type="button" onClick={download}>
          <Download size={18} />
          이미지 다운로드
        </button>
      </div>
    </div>
  )
}

function TeamAssignmentSummary() {
  const { state } = useGame()

  if (state.teamAssignments.length === 0) return null

  return (
    <div className="summary-grid">
      {state.teams.map((team) => (
        <section className="summary-block" key={team.id}>
          <h3>{team.name}</h3>
          <ul>
            {state.teamAssignments
              .filter((assignment) => assignment.teamId === team.id)
              .map((assignment) => {
                const participant = state.participants.find(
                  (item) => item.id === assignment.participantId,
                )
                return (
                  <li key={assignment.participantId}>
                    {participant?.displayName} · {personalityLabels[assignment.primaryType]}
                  </li>
                )
              })}
          </ul>
        </section>
      ))}
    </div>
  )
}

function ErrorList({ errors }: { errors: string[] }) {
  return (
    <ul className="error-list">
      {errors.map((error) => (
        <li key={error}>{error}</li>
      ))}
    </ul>
  )
}

export default App
