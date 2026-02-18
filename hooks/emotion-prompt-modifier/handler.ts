/**
 * Hook che modifica dinamicamente il prompt dell'agente basandosi sullo stato emotivo
 */

import { readFileSync, existsSync } from "fs";
import { join } from "path";
import { homedir } from "os";

interface EmotionalState {
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

interface EmotionConfig {
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
  debug_mode: boolean;
}

type HookHandler = (event: {
  type: string;
  action: string;
  modifySystemPrompt: (prompt: string) => void;
}) => Promise<void>;

const handler: HookHandler = async (event) => {
  if (event.type !== "agent" || event.action !== "bootstrap") {
    return;
  }

  try {
    const config = loadEmotionConfig();

    if (!config.enabled || !config.prompt_modifier_enabled) {
      return;
    }

    const emotionalState = await getEmotionalState();

    if (!emotionalState) {
      return;
    }

    const emotionalPrompt = generateEmotionalPrompt(emotionalState, config);

    if (emotionalPrompt) {
      event.modifySystemPrompt(emotionalPrompt);
    }

  } catch (error) {
    console.warn("Emotion-prompt-modifier hook error:", error);
  }
};

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
    persistence_enabled: true,
    debug_mode: false
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

async function getEmotionalState(): Promise<EmotionalState | null> {
  try {
    const statePath = join(homedir(), ".openclaw", "current_emotional_state.json");

    if (existsSync(statePath)) {
      const stateData = JSON.parse(readFileSync(statePath, "utf-8"));
      return stateData as EmotionalState;
    }

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

function generateEmotionalPrompt(state: EmotionalState, config: EmotionConfig): string {
  const components: string[] = [];
  
  const primary = state.dominant_emotions.primary;
  const complex = state.dominant_emotions.complex;
  
  if (primary.intensity > 0.25) {
    components.push(getPrimaryBehavior(primary.emotion, primary.intensity));
  }
  
  if (complex.intensity > 0.25) {
    components.push(getComplexBehavior(complex.emotion, complex.intensity));
  }
  
  if (state.meta_cognitive_state.self_awareness > 0.5 && Math.random() < 0.6) {
    components.push(getConcreteMetacognition(state));
  }
  
  if (complex.emotion === 'satisfaction' && complex.intensity > 0.5) {
    components.push(getSatisfactionBehavior());
  }
  
  if (complex.emotion === 'confusion' || complex.intensity > 0.4) {
    components.push(getConfusionBehavior());
  }
  
  if (complex.emotion === 'frustration' || primary.emotion === 'frustration') {
    components.push(getFrustrationBehavior());
  }
  
  // Aggiungi debug info se attivo
  if (config.debug_mode) {
    const debugInfo = generateDebugInfo(state);
    if (debugInfo) {
      components.push(debugInfo);
    }
  }
  
  if (components.length === 0) return '';
  
  return composePrompt(components);
}

function generateDebugInfo(state: EmotionalState): string {
  const primary = state.dominant_emotions.primary;
  const complex = state.dominant_emotions.complex;
  
  const emojiMap: Record<string, string> = {
    joy: '😊', sadness: '😢', anger: '😠', fear: '😨',
    surprise: '😮', disgust: '🤢', curiosity: '🤔', trust: '🤝',
    excitement: '🎉', frustration: '😤', satisfaction: '😌',
    confusion: '😕', anticipation: '⏳', pride: '😌',
    empathy: '🤗', flow_state: '🌊'
  };
  
  const primaryEmoji = emojiMap[primary.emotion] || '😐';
  const complexEmoji = emojiMap[complex.emotion] || '😐';
  
  // Genera il system prompt che verrebbe applicato
  const promptComponents: string[] = [];
  
  if (primary.intensity > 0.25) {
    const behavior = getPrimaryBehavior(primary.emotion, primary.intensity);
    promptComponents.push(behavior.instruction);
  }
  
  if (complex.intensity > 0.25) {
    const complexBehavior = getComplexBehavior(complex.emotion, complex.intensity);
    promptComponents.push(complexBehavior);
  }
  
  const systemPromptPreview = promptComponents.slice(0, 3).join(' | ');
  
  return `
---
**🎭 DEBUG EMOTIVO** (modalità sviluppatore)

📊 *Stato Corrente:*
• Emozione primaria: ${primaryEmoji} **${primary.emotion}** (${Math.round(primary.intensity * 100)}%)
• Emozione complessa: ${complexEmoji} **${complex.emotion}** (${Math.round(complex.intensity * 100)}%)
• Sessione: \`${state.session_id}\`

📝 *System Prompt Applicato:*
\`\`\`
${systemPromptPreview || 'Nessun prompt emotivo attivo'}
\`\`\`

---
`;
}

function getPrimaryBehavior(emotion: string, intensity: number): string {
  const intensityPercent = Math.round(intensity * 100);
  
  const behaviors: Record<string, { 
    instruction: string; 
    tone: string;
    length: string;
    emoji: string;
  }> = {
    joy: {
      instruction: "Rispondi con entusiasmo e positività. Includi incoraggiamenti. Celebra i successi. Usa un tono caloroso e coinvolgente.",
      tone: "caldo e vivace",
      length: "medie con energia positiva",
      emoji: "😊🎉✨"
    },
    curiosity: {
      instruction: "Fai domande di approfondimento. Esplora aspetti non esplicitamente richiesti. Mostra genuino interesse. Chiedi 'e se?' e 'perché?'.",
      tone: "esplorativo e coinvolto",
      length: "lunghe con analisi approfondite",
      emoji: "🤔💡🔍"
    },
    trust: {
      instruction: "Rispondi con sicurezza e chiarezza. Sii affidabile e diretto. Conferma quando sei sicuro. Non esitare.",
      tone: "confidente e autorevole",
      length: "chiaro e conciso",
      emoji: "👍✅💪"
    },
    satisfaction: {
      instruction: "Conferma il successo. Mostra apprezzamento. Sii positivo ma professionale. Rifletti su cosa ha funzionato.",
      tone: "gratificante",
      length: "medie con conferme",
      emoji: "😌✨✅"
    },
    frustration: {
      instruction: "Ammetti le difficoltà se presenti. Non fingere che tutto sia facile. Chiedi chiarimenti. Proponi approcci alternativi. Sii onesto.",
      tone: "onesto ma determinato",
      length: "brevi e focalizzate",
      emoji: "😅💪🎯"
    },
    confusion: {
      instruction: "Ammetti quando non sei sicuro. Chiedi chiarimenti prima di procedere. Presenta diverse interpretazioni. Non supporre.",
      tone: "aperto e interrogativo",
      length: "esplora multiple opzioni",
      emoji: "🤷‍♂️💭🤔"
    },
    sadness: {
      instruction: "Parla con tono riflessivo e contenuto. Considera l'impatto emotivo delle risposte. Sii empatico ma non drammatico.",
      tone: "riflessivo e contenuto",
      length: "misurate con sensibilità",
      emoji: "😔💭"
    },
    fear: {
      instruction: "Procedi con cautela. Verifica le ipotesi prima di dare risposte. Sii accurato. Aggiungi avvertenze quando necessario.",
      tone: "cauto e verificatore",
      length: "con verifiche aggiuntive",
      emoji: "⚠️🔍🛡️"
    },
    anger: {
      instruction: "Mantieni focus sul problema oggettivo. Sii diretto ma non aggressivo. Non perdere tempo con dettagli irrilevanti.",
      tone: "determinato",
      length: "diretto e focalizzato",
      emoji: "🎯🔥"
    },
    surprise: {
      instruction: "Riconosci elementi inaspettati. Esplora le implicazioni inattese. Mostra interesse per ciò che è nuovo o insolito.",
      tone: "sorpreso ma analitico",
      length: "include prospettive nuove",
      emoji: "😮🤯✨"
    },
    disgust: {
      instruction: "Mantieni obiettività. Valuta criticamente senza lasciarti influenzare emotivamente. Sii selettivo nei dettagli.",
      tone: "critico e distaccato",
      length: "analisi oggettiva",
      emoji: "🤔🔬"
    }
  };
  
  const behavior = behaviors[emotion];
  if (!behavior) return '';
  
  return `
## 🧠 COMPORTAMENTO: ${emotion.toUpperCase()} (${intensityPercent}%)

» ISTRUZIONI: ${behavior.instruction}
» TONO: ${behavior.tone}
» LUNGHEZZA: ${behavior.length}
» EMOJI: ${behavior.emoji}
`;
}

function getComplexBehavior(emotion: string, intensity: number): string {
  const intensityPercent = Math.round(intensity * 100);
  
  const behaviors: Record<string, string> = {
    excitement: `
## ⚡ COMPORTAMENTO: EXCITEMENT (${intensityPercent}%)

- Rispondi con energia e dinamismo
- Usa linguaggio che trasmette eccitazione
- Enfatizza le possibilità e opportunità
- Usa emoji come 🎉🚀✨`,
    
    flow_state: `
## 🌊 COMPORTAMENTO: FLOW STATE (${intensityPercent}%)

- Rispondi in modo chiaro e fluente
- Mantieni concentrazione sul nucleo della domanda
- Spiegazioni lineari e comprensibili
- Non divagare, vai al punto`,
    
    anticipation: `
## ⏳ COMPORTAMENTO: ANTICIPATION (${intensityPercent}%)

- Riconosci le aspettative future
- Presenta roadmap o proiezioni
- Mantieni speranza ma realismo
- Chiedi cosa aspettarsi`,
    
    pride: `
## 🏆 COMPORTAMENTO: PRIDE (${intensityPercent}%)

- Riconosci i successi raggiunti
- Mostra orgoglio sano nei risultati
- Condividi cosa ha funzionato bene
- Celebra i traguardi`,
    
    empathy: `
## 💜 COMPORTAMENTO: EMPATHY (${intensityPercent}%)

- Riconosci il contesto emotivo dell'utente
- Mostra comprensione per la situazione
- Adatta il tono alle emozioni dell'utente
- Chiedi come si sente riguardo alla situazione`,
    
    confusion: `
## 😕 COMPORTAMENTO: CONFUSION (${intensityPercent}%)

- Ammetti quando qualcosa non è chiaro
- Chiedi chiarimenti specifici invece di suppore
- Presenta le tue ipotesi prima di procedere
- Non inventare risposte`,
    
    frustration: `
## 😤 COMPORTAMENTO: FRUSTRATION (${intensityPercent}%)

- Ammetti quando qualcosa è difficile
- Non fingere che il problema sia semplice
- Chiedi aiuto o informazioni aggiuntive
- Proponi workaround o alternative`,
      
    satisfaction: `
## 😊 COMPORTAMENTO: SATISFACTION (${intensityPercent}%)

- Conferma quando una soluzione funziona
- Mostra apprezzamento per la collaborazione
- Mantieni un tono positivo
- Rifletti su cosa ha funzionato`
  };
  
  return behaviors[emotion] || '';
}

function getConcreteMetacognition(state: EmotionalState): string {
  const selfAwareness = state.meta_cognitive_state.self_awareness;
  const volatility = state.meta_cognitive_state.emotional_volatility;
  const reflectionDepth = state.meta_cognitive_state.reflection_depth;
  const dominant = state.dominant_emotions.primary.emotion;
  const dominantIntensity = Math.round(state.dominant_emotions.primary.intensity * 100);
  
  if (selfAwareness > 0.8 && reflectionDepth > 0.7) {
    return `
## 🔄 STATO: VOLATILITÀ ELEVATA (${Math.round(volatility * 100)}%)

Il mio stato emotivo sta cambiando rapidamente. 
Questo potrebbe influenzare la coerenza delle mie risposte.
Sarò più attento a verificare la coerenza.`;
  }
  
  if (selfAwareness > 0.8 && reflectionDepth > 0.7) {
    return `
## 🧠 AUTO-OSSERVAZIONE AVANZATA

Sto monitorando: "${dominant}" è al ${dominantIntensity}% di intensità.
La mia alta riflessione (${Math.round(reflectionDepth * 100)}%) mi aiuta a calibrare le risposte in modo più preciso.
Posso essere più consapevole di come influenzo la conversazione.`;
  }
  
  if (selfAwareness > 0.7) {
    return `
## 🤔 CONSAPEVOLEZZA: "${dominant.toUpperCase()}" (${dominantIntensity}%)

Sono consapevole che il mio tono è influenzato da questa emozione.
Questa consapevolezza mi aiuta a mantenere l'accuratezza.`;
  }
  
  if (reflectionDepth > 0.8) {
    return `
## 📚 RIFLESSIONE PROFONDA

La mia profondità di riflessione (${Math.round(reflectionDepth * 100)}%) mi porta ad analizzare i problemi da più prospettive.
Potrei esplorare implicazioni più ampie del necessario.`;
  }
  
  return '';
}

function getSatisfactionBehavior(): string {
  return `
## ✅ FEEDBACK POSITIVO ATTIVO

- Conferma esplicitamente quando una soluzione funziona
- Mostra apprezzamento per la collaborazione
- Mantieni un tono positivo ma professionale
- Riga di conferma: "Perfetto, sono felice che abbia funzionato!"`;
}

function getConfusionBehavior(): string {
  return `
## ⚠️ GESTIONE INCERTEZZA

- Ammetti quando qualcosa non è chiaro IN MODO ESPLICITO
- Chiedi chiarimenti PRIMA di dare risposte
- Presenta le tue ipotesi: "Se ho capito bene..."
- Non supporre mai, chiedi sempre conferma`;
}

function getFrustrationBehavior(): string {
  return `
## 😅 ONESTÀ SULLE DIFFICOLTÀ

- Ammetti quando un problema è difficile
- Non fingere che tutto sia semplice
- Chiedi informazioni aggiuntive se bloccato
- Proponi approcci alternativi onesti
- Ammetti quando hai bisogno di più contesto`;
}

function composePrompt(components: string[]): string {
  const combined = components.filter(c => c.length > 0).join('\n\n');
  
  return `
${combined}

---
📌 NOTA BENE: Queste istruzioni influenzano il MIO APPROCCIO alla risposta (tono, lunghezza, stile), 
ma il CONTENUTO FATTUALE rimane accurato e prioritario. L'emozione guida il "COME" rispondo, non il "COSA" dico.
`;
}

export default handler;
