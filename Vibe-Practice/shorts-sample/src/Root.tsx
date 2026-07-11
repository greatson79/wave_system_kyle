import { Composition } from "remotion";
import { SermonShorts } from "./SermonShorts";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="SermonShorts"
      component={SermonShorts}
      durationInFrames={60 * 30} // 60초 @ 30fps
      fps={30}
      width={1080}
      height={1920}
    />
  );
};
