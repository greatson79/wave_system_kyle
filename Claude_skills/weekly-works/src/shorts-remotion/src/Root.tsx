import { Composition } from "remotion";
import { SermonShorts } from "./SermonShorts";
import timingData from "../public/timing.json";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="SermonShorts"
      component={SermonShorts}
      durationInFrames={timingData.totalFrames}
      fps={timingData.fps}
      width={1080}
      height={1920}
      defaultProps={{ timing: timingData }}
    />
  );
};
