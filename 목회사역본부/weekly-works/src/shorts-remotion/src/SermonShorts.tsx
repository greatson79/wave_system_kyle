import {
  AbsoluteFill,
  Audio,
  interpolate,
  Series,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

// ── 타입 ──────────────────────────────────────────────
interface SceneTiming {
  id: string;
  label: string;
  text: string;
  color: string;
  fromFrame: number;
  durationInFrames: number;
  audioFile: string | null;
  durationSec: number;
}
interface TimingData {
  totalFrames: number;
  totalDurationSec: number;
  fps: number;
  scenes: SceneTiming[];
}
interface Props { timing: TimingData; }

// ── 씬별 디자인 토큰 (A+C 혼합: 신학적 여정 반영) ─────
const SCENE_THEME: Record<string, {
  bg: string; bgGradient?: string;
  labelColor: string; textColor: string; accentColor: string;
  isDark: boolean;
}> = {
  hook: {
    bg: "#1c1c1e",
    bgGradient: "linear-gradient(160deg, #1c1c1e 60%, #141420 100%)",
    labelColor: "#f0c040", textColor: "#ffffff", accentColor: "#f0c040",
    isDark: true,
  },
  msg1: {
    bg: "#0d1117",
    bgGradient: "linear-gradient(160deg, #0d1117 60%, #07090f 100%)",
    labelColor: "#8888aa", textColor: "#bbbbcc", accentColor: "#8888aa",
    isDark: true,
  },
  msg2: {
    bg: "#120d1f",
    bgGradient: "linear-gradient(160deg, #120d1f 50%, #1a0f2e 100%)",
    labelColor: "#c0a0ff", textColor: "#ffffff", accentColor: "#c0a0ff",
    isDark: true,
  },
  msg3: {
    bg: "#1a1000",
    bgGradient: "linear-gradient(160deg, #1a1000 40%, #2a1800 100%)",
    labelColor: "#f0c040", textColor: "#f0c040", accentColor: "#f0c040",
    isDark: true,
  },
  msg4: {
    bg: "#1f1500",
    bgGradient: "linear-gradient(160deg, #1f1500 40%, #2e1e00 100%)",
    labelColor: "#f0c040", textColor: "#fff8e8", accentColor: "#f0c040",
    isDark: true,
  },
  cta: {
    bg: "#fdf6e3",
    bgGradient: "linear-gradient(160deg, #fdf6e3 40%, #f5e8c0 100%)",
    labelColor: "#1c1c1e", textColor: "#1c1c1e", accentColor: "#8b6914",
    isDark: false,
  },
};

const DEFAULT_THEME = SCENE_THEME["hook"];

// ── 공통 훅 ───────────────────────────────────────────
function useFadeIn(delay = 0, dur = 18) {
  const frame = useCurrentFrame();
  return interpolate(frame, [delay, delay + dur], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });
}
function useSlideUp(delay = 0) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - delay, fps, config: { damping: 200 } });
  return interpolate(s, [0, 1], [36, 0]);
}
function useFadeOut(durationInFrames: number, startOffset = 1.0) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const start = durationInFrames - fps * startOffset;
  return interpolate(frame, [start, durationInFrames], [1, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });
}

// ── 배경 컴포넌트 ──────────────────────────────────────
const SceneBackground: React.FC<{ sceneId: string }> = ({ sceneId }) => {
  const theme = SCENE_THEME[sceneId] ?? DEFAULT_THEME;
  return (
    <AbsoluteFill style={{
      background: theme.bgGradient ?? theme.bg,
    }} />
  );
};

// ── 레이블 태그 ────────────────────────────────────────
const LabelTag: React.FC<{ label: string; sceneId: string; slideY: number }> = ({ label, sceneId, slideY }) => {
  const theme = SCENE_THEME[sceneId] ?? DEFAULT_THEME;
  return (
    <div style={{
      transform: `translateY(${slideY}px)`,
      display: "inline-flex",
      alignItems: "center",
      gap: 10,
      marginBottom: 8,
    }}>
      <div style={{
        width: 4, height: 28, borderRadius: 2,
        backgroundColor: theme.accentColor,
      }} />
      <span style={{
        color: theme.labelColor, fontSize: 26,
        fontWeight: 600, letterSpacing: 3,
        fontFamily: "sans-serif",
      }}>
        {label}
      </span>
    </div>
  );
};

// ── 훅 씬 ─────────────────────────────────────────────
const HookScene: React.FC<{ scene: SceneTiming }> = ({ scene }) => {
  const theme = SCENE_THEME[scene.id] ?? DEFAULT_THEME;
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fadeIn = useFadeIn(0, 20);
  const fadeOut = useFadeOut(scene.durationInFrames, 1.2);
  const slideY = useSlideUp(0);
  const underlineW = interpolate(frame, [fps * 1.0, fps * 2.5], [0, 100], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });
  const lines = scene.text.split("|");

  return (
    <AbsoluteFill style={{ opacity: Math.min(fadeIn, fadeOut) }}>
      <SceneBackground sceneId={scene.id} />
      <AbsoluteFill style={{
        display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center",
        padding: "80px 64px", gap: 20,
      }}>
        <LabelTag label={scene.label} sceneId={scene.id} slideY={slideY} />
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 6, marginTop: 12 }}>
          {lines.slice(0, -1).map((line, i) => (
            <div key={i} style={{
              transform: `translateY(${slideY}px)`,
              color: theme.textColor, fontSize: 58, fontWeight: 800,
              lineHeight: 1.3, textAlign: "center", fontFamily: "sans-serif",
            }}>{line}</div>
          ))}
          <div style={{ position: "relative", display: "inline-block", marginTop: 4 }}>
            <span style={{
              color: theme.accentColor, fontSize: 58,
              fontWeight: 800, fontFamily: "sans-serif",
            }}>
              {lines[lines.length - 1]}
            </span>
            <div style={{
              position: "absolute", bottom: -8, left: 0,
              height: 4, width: `${underlineW}%`,
              backgroundColor: theme.accentColor, borderRadius: 2,
            }} />
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ── 메시지 씬 ─────────────────────────────────────────
const MessageScene: React.FC<{ scene: SceneTiming }> = ({ scene }) => {
  const theme = SCENE_THEME[scene.id] ?? DEFAULT_THEME;
  const fadeIn = useFadeIn(0, 18);
  const fadeOut = useFadeOut(scene.durationInFrames, 1.2);
  const slideY = useSlideUp(0);

  return (
    <AbsoluteFill style={{ opacity: Math.min(fadeIn, fadeOut) }}>
      <SceneBackground sceneId={scene.id} />
      <AbsoluteFill style={{
        display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center",
        padding: "80px 64px", gap: 24,
      }}>
        <LabelTag label={scene.label} sceneId={scene.id} slideY={slideY} />
        <div style={{
          transform: `translateY(${slideY}px)`,
          color: theme.textColor, fontSize: 52, fontWeight: 800,
          lineHeight: 1.55, textAlign: "center",
          fontFamily: "sans-serif", whiteSpace: "pre-line",
          marginTop: 8,
        }}>
          {scene.text}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ── CTA 씬 (밝은 반전) ────────────────────────────────
const CTAScene: React.FC<{ scene: SceneTiming }> = ({ scene }) => {
  const theme = SCENE_THEME[scene.id] ?? DEFAULT_THEME;
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fade = useFadeIn(0, 24);
  const scale = spring({ frame, fps, config: { damping: 200 } });
  const slideY = useSlideUp(0);
  const [church, main, date] = scene.text.split("|");

  return (
    <AbsoluteFill style={{ opacity: fade }}>
      <SceneBackground sceneId={scene.id} />
      <AbsoluteFill style={{
        display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center",
        padding: "80px 64px", gap: 40,
      }}>
        {/* 상단 구분선 */}
        <div style={{
          width: "50%", height: 2,
          backgroundColor: theme.accentColor, opacity: 0.5,
          transform: `translateY(${slideY}px)`,
        }} />

        {/* 교회명 */}
        <div style={{
          transform: `scale(${scale})`,
          color: theme.accentColor, fontSize: 36,
          fontWeight: 700, letterSpacing: 6,
          fontFamily: "sans-serif",
        }}>
          {church}
        </div>

        {/* 메인 문구 */}
        <div style={{
          transform: `translateY(${slideY}px)`,
          color: theme.textColor, fontSize: 56,
          fontWeight: 800, lineHeight: 1.4,
          textAlign: "center", fontFamily: "sans-serif",
          whiteSpace: "pre-line",
        }}>
          {main?.replace("\\n", "\n")}
        </div>

        {/* 날짜 */}
        <div style={{
          transform: `translateY(${slideY}px)`,
          color: theme.textColor, fontSize: 26,
          fontFamily: "sans-serif", letterSpacing: 2, opacity: 0.6,
        }}>
          {date}
        </div>

        {/* 하단 구분선 */}
        <div style={{
          width: "50%", height: 2,
          backgroundColor: theme.accentColor, opacity: 0.5,
        }} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ── 씬 라우터 ─────────────────────────────────────────
const SceneRouter: React.FC<{ scene: SceneTiming }> = ({ scene }) => {
  if (scene.id === "hook") return <HookScene scene={scene} />;
  if (scene.id === "cta") return <CTAScene scene={scene} />;
  return <MessageScene scene={scene} />;
};

// ── 메인 컴포지션 ──────────────────────────────────────
export const SermonShorts: React.FC<Props> = ({ timing }) => {
  return (
    <>
      <Series>
        {timing.scenes.map((scene) => (
          <Series.Sequence
            key={scene.id}
            durationInFrames={scene.durationInFrames}
            premountFor={30}
          >
            {scene.audioFile && (
              <Audio src={staticFile(scene.audioFile)} />
            )}
            <SceneRouter scene={scene} />
          </Series.Sequence>
        ))}
      </Series>
    </>
  );
};
