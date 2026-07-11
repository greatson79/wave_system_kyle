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

// ── 색상 ──────────────────────────────────────────────
const DARK_BG = "#1a1a2e";
const ACCENT = "#e8c547";
const WHITE = "#ffffff";
const GRAY = "#aaaaaa";

// ── 공통 훅 ───────────────────────────────────────────
function useFadeIn(delayFrames = 0, durationFrames = 15) {
  const frame = useCurrentFrame();
  return interpolate(frame, [delayFrames, delayFrames + durationFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
}

function useSlideUp(delayFrames = 0) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - delayFrames, fps, config: { damping: 200 } });
  return interpolate(s, [0, 1], [40, 0]);
}

// ── Scene 1: 훅 (0~5초) ───────────────────────────────
const HookScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fade = useFadeIn(0, 20);
  const slideY = useSlideUp(0);

  const underlineW = interpolate(frame, [fps * 1.5, fps * 3], [0, 100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: DARK_BG,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "80px 60px",
        gap: 32,
      }}
    >
      <div style={{ opacity: fade, transform: `translateY(${slideY}px)`,
        color: ACCENT, fontSize: 30, fontWeight: 600, letterSpacing: 3,
        fontFamily: "sans-serif" }}>
        빌립보서 3:7-14
      </div>

      <div style={{ opacity: fade, transform: `translateY(${slideY}px)`,
        color: WHITE, fontSize: 60, fontWeight: 800, lineHeight: 1.35,
        textAlign: "center", fontFamily: "sans-serif" }}>
        충분히 해냈다는 느낌,
        <br />
        당신은 받아본 적
        <br />
        <span style={{ color: ACCENT, position: "relative", display: "inline-block" }}>
          있습니까?
          <div style={{
            position: "absolute", bottom: -6, left: 0,
            height: 4, width: `${underlineW}%`,
            backgroundColor: ACCENT, borderRadius: 2,
          }} />
        </span>
      </div>
    </AbsoluteFill>
  );
};

// ── Scene 2: 메시지 슬라이드 (5~50초) ─────────────────
type Slide = { label: string; text: string; color: string };

const SLIDES: Slide[] = [
  { label: "우리의 본능", text: "끊임없이 쌓습니다\n직장에서, 가정에서, 교회에서\n그 목록이 든든할수록\n더 안전하다고 느낍니다", color: GRAY },
  { label: "바울의 고백", text: "완벽한 이력서를\n배설물이라고 불렀습니다\n더 나은 것을 발견했기 때문입니다", color: WHITE },
  { label: "복음의 선언", text: "쌓으라는 말이 아닙니다\n출처가 바뀌었다는\n선언입니다", color: ACCENT },
  { label: "이미 받아들여졌습니다", text: "충분히 해냈는지\n증명하지 않아도 되는 사람으로\n이미 받아들여졌습니다", color: WHITE },
];

const SLIDE_DURATION_SEC = 11; // 45초 / 4슬라이드 ≈ 11초

const MessageSlide: React.FC<{ slide: Slide }> = ({ slide }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fadeIn = useFadeIn(0, 18);
  const fadeOut = interpolate(
    frame,
    [fps * (SLIDE_DURATION_SEC - 1.5), fps * SLIDE_DURATION_SEC],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const slideY = useSlideUp(0);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: DARK_BG,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "80px 60px",
        gap: 28,
        opacity: Math.min(fadeIn, fadeOut),
      }}
    >
      <div style={{ opacity: 0.7, transform: `translateY(${slideY}px)`,
        color: ACCENT, fontSize: 26, fontWeight: 600, letterSpacing: 3,
        fontFamily: "sans-serif" }}>
        {slide.label}
      </div>
      <div style={{ transform: `translateY(${slideY}px)`,
        color: slide.color, fontSize: 56, fontWeight: 800,
        lineHeight: 1.45, textAlign: "center",
        fontFamily: "sans-serif", whiteSpace: "pre-line" }}>
        {slide.text}
      </div>
    </AbsoluteFill>
  );
};

// ── Scene 3: CTA (50~60초) ────────────────────────────
const CTAScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fade = useFadeIn(0, 20);
  const scale = spring({ frame, fps, config: { damping: 200 } });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0f0f1e",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "80px 60px",
        gap: 44,
      }}
    >
      <div style={{ opacity: fade, transform: `scale(${scale})`,
        color: ACCENT, fontSize: 38, fontWeight: 700,
        letterSpacing: 5, fontFamily: "sans-serif" }}>
        디딤교회
      </div>

      <div style={{ opacity: fade, color: WHITE, fontSize: 56,
        fontWeight: 800, lineHeight: 1.4, textAlign: "center",
        fontFamily: "sans-serif" }}>
        오늘 예배에서<br />
        <span style={{ color: ACCENT }}>함께 만나요</span>
      </div>

      <div style={{ opacity: fade * 0.7, color: GRAY, fontSize: 28,
        fontFamily: "sans-serif", letterSpacing: 2 }}>
        2026. 04. 26 주일예배
      </div>

      <div style={{ position: "absolute", bottom: 80, width: "70%",
        height: 2, backgroundColor: ACCENT, opacity: fade * 0.4 }} />
    </AbsoluteFill>
  );
};

// ── 메인 컴포지션 ──────────────────────────────────────
export const SermonShorts: React.FC = () => {
  const { fps } = useVideoConfig();
  const slideDuration = Math.round(SLIDE_DURATION_SEC * fps);

  return (
    <>
      {/* 전체 나레이션 오디오 */}
      <Audio src={staticFile("narration.mp3")} />

      <Series>
        {/* Scene 1: 훅 — 5초 */}
        <Series.Sequence durationInFrames={fps * 5} premountFor={fps}>
          <HookScene />
        </Series.Sequence>

        {/* Scene 2: 메시지 슬라이드 × 4 — 각 11초 */}
        {SLIDES.map((slide, i) => (
          <Series.Sequence
            key={i}
            durationInFrames={slideDuration}
            premountFor={fps}
          >
            <MessageSlide slide={slide} />
          </Series.Sequence>
        ))}

        {/* Scene 3: CTA — 나머지 */}
        <Series.Sequence durationInFrames={fps * 11} premountFor={fps}>
          <CTAScene />
        </Series.Sequence>
      </Series>
    </>
  );
};
