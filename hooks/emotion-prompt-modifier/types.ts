/**
 * Type definitions for the emotion-prompt-modifier hook
 */

export interface EmotionalState {
  primary_emotions: Record<string, number>;
  complex_emotions: Record<string, number>;
  personality_traits: Record<string, number>;
  meta_cognitive_state: {
    self_awareness: number;
    emotional_volatility: number;
    learning_rate: number;
    reflection_depth: number;
    introspective_tendency: number;
    philosophical_inclination: number;
  };
  emotional_memory: {
    recent_interactions: any[];
    emotional_triggers: Record<string, any>;
    learned_patterns: Record<string, any>;
    user_preferences: Record<string, any>;
    successful_approaches: Record<string, any>;
    failed_approaches: Record<string, any>;
  };
  ml_state: {
    pattern_recognition_confidence: number;
    adaptation_rate: number;
    prediction_accuracy: number;
    learning_episodes: number;
  };
  dominant_emotions: {
    primary: { emotion: string; intensity: number };
    complex: { emotion: string; intensity: number };
  };
  overall_intensity: {
    primary: number;
    complex: number;
    total: number;
  };
  confidence_score: number;
  timestamp: string;
  session_id: string;
}

export interface EmotionConfig {
  enabled: boolean;
  intensity: number;
  learning_rate: number;
  volatility: number;
  meta_cognition_enabled: boolean;
  introspection_frequency: number;
  emotion_decay_rate: number;
  memory_depth: number;
  confidence_threshold: number;
  ml_update_frequency: number;
  backup_frequency: number;
  max_volatility: number;
  prompt_modifier_enabled: boolean;
  persistence_enabled: boolean;
}

export interface InteractionContext {
  text?: string;
  type?: string;
  complexity?: number;
  urgency?: number;
  feedback_type?: string;
  user_sentiment?: string;
  session_info?: {
    duration: number;
    message_count: number;
    previous_topics: string[];
  };
  task_info?: {
    task_type: string;
    difficulty: number;
    success_probability: number;
  };
}

export interface PromptModification {
  emotional_context: string;
  metacognitive_reflection?: string;
  personality_influence?: string;
  situational_awareness?: string;
  confidence_level: number;
  modification_timestamp: string;
}

export interface EmotionalTrigger {
  trigger_type: string;
  intensity: number;
  emotional_impact: Record<string, number>;
  confidence: number;
  trigger_source: string;
}

export interface MetaCognitiveInsight {
  insight_type: string;
  description: string;
  confidence: number;
  emotional_relevance: number;
  triggers: string[];
}

export interface PersonalityTrait {
  name: string;
  value: number;
  influence_on_behavior: string;
  adaptation_history: number[];
  last_updated: string;
}