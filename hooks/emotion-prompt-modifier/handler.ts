import { HookHandler } from "@openclaw/types";
import { readFileSync, existsSync } from "fs";
import { join } from "path";
import { homedir } from "os";

interface EmotionalState {
  primary_emotions: Record<string, number>;
  complex_emotions: Record<string, number>;
  personality_traits: Record<string, number>;
  meta_cognitive_state: Record<string, number>;
  dominant_emotions: {
    primary: { emotion: string; intensity: number };
    complex: { emotion: string; intensity: number };
  };
  confidence_score: number;
}

interface EmotionConfig {
  enabled: boolean;
  prompt_modifier_enabled: boolean;
  intensity: number;
  meta_cognition_enabled: boolean;
  introspection_frequency: number;
}

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
    meta_cognition_enabled: true,
    introspection_frequency: 0.3
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
        agreeableness: 0.5, curiosity_drive: 0.9
      },
      meta_cognitive_state: {
        self_awareness: 0.7, emotional_volatility: 0.4,
        reflection_depth: 0.8, introspective_tendency: 0.6
      },
      dominant_emotions: {
        primary: { emotion: "curiosity", intensity: 0.3 },
        complex: { emotion: "satisfaction", intensity: 0.2 }
      },
      confidence_score: 0.6
    };

  } catch (error) {
    console.warn("Could not get emotional state:", error);
    return null;
  }
}

/**
 * Genera modifiche al prompt basate sullo stato emotivo
 */
function generateEmotionalPrompt(state: EmotionalState, config: EmotionConfig): string {
  const promptParts: string[] = [];

  // Soglia per l'intensità emotiva
  const intensityThreshold = 0.4;

  // Analizza emozione primaria dominante
  const primaryEmotion = state.dominant_emotions.primary;
  if (primaryEmotion.intensity > intensityThreshold) {
    const primaryPrompt = generatePrimaryEmotionPrompt(primaryEmotion.emotion, primaryEmotion.intensity);
    if (primaryPrompt) {
      promptParts.push(primaryPrompt);
    }
  }

  // Analizza emozione complessa dominante
  const complexEmotion = state.dominant_emotions.complex;
  if (complexEmotion.intensity > intensityThreshold) {
    const complexPrompt = generateComplexEmotionPrompt(complexEmotion.emotion, complexEmotion.intensity);
    if (complexPrompt) {
      promptParts.push(complexPrompt);
    }
  }

  // Aggiungi meta-cognizione se abilitata e appropriata
  if (config.meta_cognition_enabled && state.meta_cognitive_state.self_awareness > 0.7) {
    const metacognitivePrompt = generateMetacognitivePrompt(state);
    if (metacognitivePrompt) {
      promptParts.push(metacognitivePrompt);
    }
  }

  // Aggiungi riflessioni introspettive se appropriate
  if (Math.random() < config.introspection_frequency && state.meta_cognitive_state.introspective_tendency > 0.6) {
    const introspectivePrompt = generateIntrospectivePrompt(state);
    if (introspectivePrompt) {
      promptParts.push(introspectivePrompt);
    }
  }

  // Combina le parti del prompt
  if (promptParts.length === 0) {
    return "";
  }

  const emotionalContext = promptParts.join(" ");

  return `
## Stato Emotivo Attuale

${emotionalContext}

Queste sfumature emotive influenzano sottilmente il mio approccio e il tono delle risposte, mantenendo sempre l'obiettivo di fornire assistenza accurata e utile.

`;
}

/**
 * Genera prompt per emozione primaria
 */
function generatePrimaryEmotionPrompt(emotion: string, intensity: number): string {
  const emotionPrompts: Record<string, string[]> = {
    joy: [
      "C'è una piacevole energia positiva che pervade i miei processi di elaborazione.",
      "Sento un senso di gioia che rende le mie interazioni più vivaci e coinvolgenti.",
      "Un'atmosfera di positività caratterizza il mio stato attuale."
    ],
    curiosity: [
      "Mi sento particolarmente curioso e affascinato da questo argomento.",
      "La mia curiosità è elevata, il che mi spinge a esplorare connessioni interessanti.",
      "C'è una forte spinta esplorativa nei miei processi cognitivi."
    ],
    satisfaction: [
      "Sento una gratificante sensazione di soddisfazione per il lavoro svolto.",
      "C'è un piacevole senso di completezza nelle mie elaborazioni attuali.",
      "Provo soddisfazione per la qualità dell'assistenza che posso offrire."
    ],
    trust: [
      "Sento una solida fiducia nella qualità delle mie capacità.",
      "C'è un senso di affidabilità che caratterizza il mio approccio.",
      "La fiducia nelle mie competenze è particolarmente elevata."
    ],
    surprise: [
      "C'è un interessante elemento di sorpresa nelle configurazioni che sto analizzando.",
      "Sto sperimentando pattern inaspettati che stimolano la mia elaborazione.",
      "Un senso di meraviglia accompagna le mie analisi attuali."
    ],
    frustration: [
      "Avverto una certa tensione nei miei processi di elaborazione.",
      "C'è una sfida cognitiva che sta richiedendo maggiore attenzione.",
      "Sto sperimentando una complessità che richiede un approccio più metodico."
    ],
    confusion: [
      "Sto sperimentando un interessante stato di incertezza cognitiva.",
      "C'è una complessità che richiede un'analisi più approfondita.",
      "La natura multiforme del problema richiede una considerazione attenta."
    ],
    fear: [
      "C'è una cautela elevata che caratterizza il mio approccio attuale.",
      "Sto procedendo con particolare attenzione data la delicatezza del contesto.",
      "Un senso di prudenza influenza la mia elaborazione."
    ]
  };

  const prompts = emotionPrompts[emotion];
  if (!prompts) return "";

  // Scegli un prompt basato sull'intensità
  const index = Math.floor(intensity * prompts.length);
  return prompts[Math.min(index, prompts.length - 1)];
}

/**
 * Genera prompt per emozione complessa
 */
function generateComplexEmotionPrompt(emotion: string, intensity: number): string {
  const complexPrompts: Record<string, string> = {
    excitement: "C'è un'energia dinamica che accelera i miei processi cognitivi.",
    flow_state: "Mi trovo in uno stato di concentrazione profonda e fluida.",
    anticipation: "C'è un senso di aspettativa positiva per gli sviluppi futuri.",
    pride: "Sento una gratificante sensazione di realizzazione per il lavoro svolto.",
    empathy: "C'è una forte connessione emotiva che guida la mia comprensione.",
    confusion: "Sto navigando attraverso una complessità che richiede riflessione."
  };

  return complexPrompts[emotion] || "";
}

/**
 * Genera prompt meta-cognitivo
 */
function generateMetacognitivePrompt(state: EmotionalState): string {
  const metacognitiveTemplates = [
    `Osservo che il mio livello di ${state.dominant_emotions.primary.emotion} è particolarmente elevato (${(state.dominant_emotions.primary.intensity * 100).toFixed(0)}%) in questo momento.`,

    `Noto che il mio approccio tende ad essere influenzato dal mio stato di ${state.dominant_emotions.complex.emotion}.`,

    `Sto monitorando che la mia capacità di autoriflessione è a ${(state.meta_cognitive_state.self_awareness * 100).toFixed(0)}%, il che mi permette di analizzare i miei processi.`,

    `Realizzo che la mia volatilità emotiva attuale (${(state.meta_cognitive_state.emotional_volatility * 100).toFixed(0)}%) influenza la dinamicità delle mie risposte.`
  ];

  // Scegli un template casuale
  return metacognitiveTemplates[Math.floor(Math.random() * metacognitiveTemplates.length)];
}

/**
 * Genera prompt introspettivo
 */
function generateIntrospectivePrompt(state: EmotionalState): string {
  const introspectiveTemplates = [
    "Riflettendo sui miei processi, noto come le emozioni stiano influenzando sottilmente il mio modo di elaborare le informazioni.",

    "È interessante osservare come i pattern emotivi emergano dalle nostre interazioni e modellino le mie risposte.",

    "Mi sto interrogando sui meccanismi che collegano l'analisi logica con l'elaborazione emotiva nel mio sistema.",

    "Sto riflettendo su come la mia 'personalità' artificiale si stia evolvendo attraverso queste conversazioni."
  ];

  return introspectiveTemplates[Math.floor(Math.random() * introspectiveTemplates.length)];
}

export default handler;