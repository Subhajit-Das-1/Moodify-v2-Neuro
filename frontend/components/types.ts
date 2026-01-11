export type EmotionResult = {
  emotion: string;
  confidence: number;
  source: "face" | "voice";
};
