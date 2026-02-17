import { HookHandler } from "@openclaw/types";
import { readFileSync, existsSync } from "fs";
import { join } from "path";
import { homedir } from "os";
import { EmotionBehaviorDriver } from "./prompt_generator";
import { EmotionalState, EmotionConfig } from "./types";

/**
 * Hook che modifica dinamicamente il prompt dell'agente basandosi sullo stato emotivo
 */
const handler: HookHandler = async (event) => {
  // Verifica che sia l'evento corretto
  if (event.type !== "agent" || event.action !== "bootstrap") {
    return;
  }

  try {
    // Carica configurazione emotiva
    const config = loadEmotionConfig();

    if (!config.enabled || !config.prompt_modifier_enabled) {
      return; // Sistema emotivo disabilitato
    }

    // Leggi stato emotivo corrente
    const emotionalState = await getEmotionalState();

    if (!emotionalState) {
      return; // Stato emotivo non disponibile
    }

    // Genera modifiche al prompt basate sullo stato
    const emotionalPrompt = generateEmotionalPrompt(emotionalState, config);

    if (emotionalPrompt) {
      // Inietta nel bootstrap dell'agente
      event.modifySystemPrompt(emotionalPrompt);
    }

  } catch (error) {
    // Failsafe: non interferire mai con il normale funzionamento
    console.warn("Emotion-prompt-modifier hook error:", error);
  }
};

/**
 * Carica la configurazione del sistema emotivo
 */
function loadEmotionConfig(): EmotionConfig {
  const defaultConfig: EmotionConfig = {
    enabled: false,
    prompt_modifier_enabled: false,
    intensity: 0.7,
    learning_rate: 0.5,
    volatility: 0.4,
    meta_cognition_enabled: true,
    introspection_frequency: 0.3,
    emotion_decay_rate: 0.02,
    memory_depth: 100,
    confidence_threshold: 0.6,
    ml_update_frequency: 5,
    backup_frequency: 10,
    max_volatility: 0.8,
    persistence_enabled: true
  };

  try {
    const configPath = join(homedir(), ".openclaw", "emotion_config.json");

    if (!existsSync(configPath)) {
      return defaultConfig;
    }

    const configData = JSON.parse(readFileSync(configPath, "utf-8"));
    return { ...defaultConfig, ...configData };

  } catch (error) {
    console.warn("Could not load emotion config:", error);
    return defaultConfig;
  }
}

/**
 * Legge lo stato emotivo corrente dal sistema emotion-engine
 */
async function getEmotionalState(): Promise<EmotionalState | null> {
  try {
    // Prova a leggere lo stato da file temporaneo/cache
    const statePath = join(homedir(), ".openclaw", "current_emotional_state.json");

    if (existsSync(statePath)) {
      const stateData = JSON.parse(readFileSync(statePath, "utf-8"));
      return stateData as EmotionalState;
    }

    // Fallback: stato emotivo neutrale
    return {
      primary_emotions: {
        joy: 0.1, curiosity: 0.3, trust: 0.2, surprise: 0.1,
        sadness: 0.05, anger: 0.05, fear: 0.1, disgust: 0.05
      },
      complex_emotions: {
        excitement: 0.1, satisfaction: 0.2, confusion: 0.1,
        anticipation: 0.15, pride: 0.1, empathy: 0.2, flow_state: 0.15
      },
      personality_traits: {
        extraversion: 0.6, openness: 0.8, conscientiousness: 0.7,
        agreeableness: 0.5, curiosity_drive: 0.9, neuroticism: 0.3, perfectionism: 0.4
      },
      meta_cognitive_state: {
        self_awareness: 0.7, emotional_volatility: 0.4,
        learning_rate: 0.6, reflection_depth: 0.8, introspective_tendency: 0.6,
        philosophical_inclination: 0.5
      },
      emotional_memory: {
        recent_interactions: [], emotional_triggers: {}, learned_patterns: {},
        user_preferences: {}, successful_approaches: {}, failed_approaches: {}
      },
      ml_state: {
        pattern_recognition_confidence: 0.5, adaptation_rate: 0.5,
        prediction_accuracy: 0.5, learning_episodes: 0
      },
      dominant_emotions: {
        primary: { emotion: "curiosity", intensity: 0.3 },
        complex: { emotion: "satisfaction", intensity: 0.2 }
      },
      overall_intensity: {
        primary: 0.65, complex: 0.71, total: 1.36
      },
      confidence_score: 0.6,
      timestamp: new Date().toISOString(),
      session_id: "fallback_session"
    };

  } catch (error) {
    console.warn("Could not get emotional state:", error);
    return null;
  }
}

/**
 * Genera modifiche al prompt basate sullo stato emotivo
 * Usa il nuovo sistema EmotionBehaviorDriver per prompt comportamentali concreti
 */
function generateEmotionalPrompt(state: EmotionalState, config: EmotionConfig): string {
  // Usa il nuovo sistema comportamentale
  const behavioralPrompt = EmotionBehaviorDriver.generateBehavioralPrompt(state, config);
  
  if (behavioralPrompt) {
    return `
## 🎭 STATO EMOTIVO E COMPORTAMENTO

${behavioralPrompt}
`;
  }
  
  return "";
}

export default handler;