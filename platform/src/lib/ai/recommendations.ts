export interface RecommendationRequest {
  currentMood: string;
  targetMood: string;
  preferences?: string[];
  context?: string;
}

export interface RecommendationResult {
  title: string;
  reason: string;
}
