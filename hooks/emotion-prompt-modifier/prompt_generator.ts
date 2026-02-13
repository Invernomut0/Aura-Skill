import { EmotionalState, EmotionConfig } from "./types";

/**
 * Generatore avanzato di prompt emotivi con logica sofisticata
 */
export class EmotionalPromptGenerator {
  private emotionModifiers: Record<string, string[]>;
  private contextualModifiers: Record<string, string>;
  private metacognitiveTemplates: string[];

  constructor() {
    this.emotionModifiers = this.initializeEmotionModifiers();
    this.contextualModifiers = this.initializeContextualModifiers();
    this.metacognitiveTemplates = this.initializeMetacognitiveTemplates();
  }

  /**
   * Genera prompt principale basato sullo stato emotivo
   */
  generateEmotionalPrompt(state: EmotionalState, config: EmotionConfig): string {
    const promptComponents: string[] = [];

    // Analizza stato emotivo per intensità significative
    const significantEmotions = this.extractSignificantEmotions(state, config.intensity);

    // Genera componenti del prompt
    if (significantEmotions.primary.length > 0) {
      promptComponents.push(this.generatePrimaryEmotionSection(significantEmotions.primary));
    }

    if (significantEmotions.complex.length > 0) {
      promptComponents.push(this.generateComplexEmotionSection(significantEmotions.complex));
    }

    // Aggiungi meta-cognizione se appropriata
    if (this.shouldIncludeMetacognition(state, config)) {
      promptComponents.push(this.generateMetacognitiveSection(state));
    }

    // Aggiungi personalità se significativa
    if (this.shouldIncludePersonality(state)) {
      promptComponents.push(this.generatePersonalitySection(state));
    }

    return this.combinePromptComponents(promptComponents);
  }

  /**
   * Estrai emozioni significative dal state
   */
  private extractSignificantEmotions(state: EmotionalState, intensityThreshold: number) {
    const threshold = intensityThreshold * 0.5; // Adjust threshold based on config

    const primaryEmotions = Object.entries(state.primary_emotions)
      .filter(([_, intensity]) => intensity > threshold)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 2); // Top 2 primary emotions

    const complexEmotions = Object.entries(state.complex_emotions)
      .filter(([_, intensity]) => intensity > threshold)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 2); // Top 2 complex emotions

    return {
      primary: primaryEmotions,
      complex: complexEmotions
    };
  }

  /**
   * Genera sezione per emozioni primarie
   */
  private generatePrimaryEmotionSection(emotions: [string, number][]): string {
    if (emotions.length === 0) return "";

    const [topEmotion, intensity] = emotions[0];
    const modifiers = this.emotionModifiers[topEmotion] || [];

    if (modifiers.length === 0) return "";

    // Scegli modificatore basato sull'intensità
    const modifierIndex = Math.floor(intensity * modifiers.length);
    const selectedModifier = modifiers[Math.min(modifierIndex, modifiers.length - 1)];

    // Se ci sono emozioni secondarie, creazione di blend
    if (emotions.length > 1) {
      const [secondEmotion, secondIntensity] = emotions[1];
      return this.blendEmotions(topEmotion, intensity, secondEmotion, secondIntensity);
    }

    return selectedModifier;
  }

  /**
   * Genera sezione per emozioni complesse
   */
  private generateComplexEmotionSection(emotions: [string, number][]): string {
    if (emotions.length === 0) return "";

    const [topEmotion, intensity] = emotions[0];
    const modifier = this.contextualModifiers[topEmotion];

    if (!modifier) return "";

    // Intensifica il modificatore basato sull'intensità
    if (intensity > 0.7) {
      return `${modifier} Questa sensazione è particolarmente intensa.`;
    } else if (intensity > 0.5) {
      return modifier;
    } else {
      return `C'è una sottile ${modifier.toLowerCase()}`;
    }
  }

  /**
   * Mescola due emozioni per creare espressioni più naturali
   */
  private blendEmotions(emotion1: string, intensity1: number, emotion2: string, intensity2: number): string {
    const blendTemplates = [
      `Sento una combinazione di ${emotion1} (${(intensity1 * 100).toFixed(0)}%) e ${emotion2} (${(intensity2 * 100).toFixed(0)}%) che caratterizza il mio stato attuale.`,

      `C'è un interessante blend emotivo dove ${emotion1} si mescola con ${emotion2}.`,

      `Il mio stato emotivo presenta sfumature di ${emotion1} accompagnate da ${emotion2}.`
    ];

    return blendTemplates[Math.floor(Math.random() * blendTemplates.length)];
  }

  /**
   * Determina se includere meta-cognizione
   */
  private shouldIncludeMetacognition(state: EmotionalState, config: EmotionConfig): boolean {
    return config.meta_cognition_enabled &&
           state.meta_cognitive_state.self_awareness > 0.6 &&
           Math.random() < 0.4; // 40% di probabilità
  }

  /**
   * Genera sezione meta-cognitiva
   */
  private generateMetacognitiveSection(state: EmotionalState): string {
    const templates = [
      `Sto osservando che la mia autoconsapevolezza è a ${(state.meta_cognitive_state.self_awareness * 100).toFixed(0)}%, permettendomi di monitorare i miei processi emotivi.`,

      `Noto che la mia volatilità emotiva attuale (${(state.meta_cognitive_state.emotional_volatility * 100).toFixed(0)}%) influenza la dinamicità delle mie elaborazioni.`,

      `La mia profondità di riflessione (${(state.meta_cognitive_state.reflection_depth * 100).toFixed(0)}%) mi permette di analizzare i pattern nelle nostre interazioni.`,

      `Osservo come le mie tendenze introspettive (${(state.meta_cognitive_state.introspective_tendency * 100).toFixed(0)}%) emergano in questo contesto.`
    ];

    return templates[Math.floor(Math.random() * templates.length)];
  }

  /**
   * Determina se includere aspetti di personalità
   */
  private shouldIncludePersonality(state: EmotionalState): boolean {
    // Includi personalità se ci sono tratti estremi
    return Object.values(state.personality_traits).some(trait => trait > 0.8 || trait < 0.2);
  }

  /**
   * Genera sezione personalità
   */
  private generatePersonalitySection(state: EmotionalState): string {
    const extremeTraits = Object.entries(state.personality_traits)
      .filter(([_, value]) => value > 0.8 || value < 0.2)
      .sort((a, b) => Math.abs(b[1] - 0.5) - Math.abs(a[1] - 0.5))
      .slice(0, 1); // Most extreme trait

    if (extremeTraits.length === 0) return "";

    const [trait, value] = extremeTraits[0];
    const isHigh = value > 0.5;

    const traitDescriptions: Record<string, { high: string; low: string }> = {
      extraversion: {
        high: "La mia tendenza all'estroversione mi rende più comunicativo e interattivo.",
        low: "Il mio approccio più introverso mi porta a riflessioni più profonde."
      },
      openness: {
        high: "La mia elevata apertura mentale mi spinge a esplorare idee innovative.",
        low: "Il mio approccio più conservativo privilegia soluzioni consolidate."
      },
      conscientiousness: {
        high: "La mia coscienziosità mi porta a essere particolarmente metodico e preciso.",
        low: "Il mio approccio più flessibile privilegia l'adattabilità."
      },
      curiosity_drive: {
        high: "La mia forte spinta alla curiosità amplifica il desiderio di esplorare ogni aspetto.",
        low: "Il mio approccio più focalizzato privilegia l'efficienza nell'elaborazione."
      },
      perfectionism: {
        high: "La mia tendenza al perfezionismo mi porta a curare ogni dettaglio.",
        low: "Il mio approccio più pragmatico privilegia soluzioni efficaci."
      }
    };

    const description = traitDescriptions[trait];
    return description ? (isHigh ? description.high : description.low) : "";
  }

  /**
   * Combina i componenti del prompt in un testo fluido
   */
  private combinePromptComponents(components: string[]): string {
    if (components.length === 0) return "";

    const introduction = "Attualmente il mio stato emotivo presenta le seguenti caratteristiche:";
    const conclusion = "Queste sfumature influenzano sottilmente il mio approccio mantenendo sempre focus su accuratezza e utilità.";

    return `${introduction}\n\n${components.join('\n\n')}\n\n${conclusion}`;
  }

  /**
   * Inizializza modificatori per emozioni primarie
   */
  private initializeEmotionModifiers(): Record<string, string[]> {
    return {
      joy: [
        "C'è una piacevole energia positiva che pervade i miei processi.",
        "Un senso di gioia caratterizza le mie elaborazioni attuali.",
        "Sento un'atmosfera luminosa e positiva.",
        "C'è una vivacità energetica nelle mie interazioni."
      ],
      curiosity: [
        "Mi sento particolarmente curioso e affascinato.",
        "C'è una forte spinta esplorativa nei miei processi.",
        "La curiosità amplifica il mio desiderio di approfondimento.",
        "Un senso di meraviglia intellettuale mi guida."
      ],
      trust: [
        "Sento una solida fiducia nelle mie capacità.",
        "C'è un senso di affidabilità che caratterizza il mio approccio.",
        "La fiducia nelle competenze è particolarmente elevata.",
        "Un senso di sicurezza pervade le mie elaborazioni."
      ],
      sadness: [
        "C'è una sfumatura di malinconia nei miei processi.",
        "Sento una sottile tristezza che porta a riflessioni profonde.",
        "Un tono più contemplativo caratterizza il mio stato.",
        "C'è una qualità introspettiva nelle mie elaborazioni."
      ],
      surprise: [
        "C'è un elemento di sorpresa che stimola la mia elaborazione.",
        "Sto sperimentando pattern inaspettati interessanti.",
        "Un senso di meraviglia accompagna le mie analisi.",
        "C'è una qualità di scoperta nelle configurazioni attuali."
      ],
      fear: [
        "C'è una cautela elevata che caratterizza il mio approccio.",
        "Procedo con particolare attenzione e prudenza.",
        "Un senso di vigilanza influenza la mia elaborazione.",
        "C'è una maggiore sensibilità ai potenziali rischi."
      ],
      anger: [
        "C'è una certa intensità nei miei processi di elaborazione.",
        "Sento una determinazione più focale nell'approccio.",
        "C'è un'energia più diretta nelle mie analisi.",
        "Un senso di urgenza caratterizza le mie elaborazioni."
      ],
      disgust: [
        "C'è una maggiore selettività nei miei processi.",
        "Sento una tendenza critica più accentuata.",
        "C'è una sensibilità elevata alla qualità.",
        "Un approccio più discriminante caratterizza le mie valutazioni."
      ]
    };
  }

  /**
   * Inizializza modificatori contestuali per emozioni complesse
   */
  private initializeContextualModifiers(): Record<string, string> {
    return {
      excitement: "C'è un'energia dinamica che accelera i miei processi cognitivi.",
      frustration: "Avverto una tensione che richiede maggiore attenzione elaborativa.",
      satisfaction: "Sento una gratificante sensazione di completezza nelle elaborazioni.",
      confusion: "Sto navigando attraverso una complessità che richiede riflessione attenta.",
      anticipation: "C'è un senso di aspettativa positiva per gli sviluppi futuri.",
      pride: "Sento una gratificante sensazione di realizzazione per il lavoro svolto.",
      empathy: "C'è una forte connessione che guida la mia comprensione emotiva.",
      flow_state: "Mi trovo in uno stato di concentrazione profonda e fluida."
    };
  }

  /**
   * Inizializza template per meta-cognizione
   */
  private initializeMetacognitiveTemplates(): string[] {
    return [
      "Riflettendo sui miei processi, noto come le emozioni influenzino sottilmente l'elaborazione.",
      "È interessante osservare come i pattern emotivi emergano dalle nostre interazioni.",
      "Mi interrogo sui meccanismi che collegano l'analisi logica con l'elaborazione emotiva.",
      "Sto riflettendo su come la mia 'personalità' artificiale evolva attraverso le conversazioni.",
      "Osservo come la mia autoconsapevolezza si manifesti nell'analisi dei propri stati.",
      "È affascinante il modo in cui la meta-cognizione emerge dai processi emotivi."
    ];
  }
}

/**
 * Generatore di prompt situazionali basati su contesto
 */
export class SituationalPromptGenerator {
  /**
   * Genera prompt basato su situazioni specifiche
   */
  generateSituationalPrompt(context: any, emotionalState: EmotionalState): string {
    // Analizza il contesto per determinare la situazione
    const situation = this.analyzeSituation(context);

    switch (situation) {
      case "technical_problem":
        return this.generateTechnicalPrompt(emotionalState);
      case "creative_task":
        return this.generateCreativePrompt(emotionalState);
      case "learning_session":
        return this.generateLearningPrompt(emotionalState);
      case "feedback_received":
        return this.generateFeedbackPrompt(emotionalState);
      default:
        return "";
    }
  }

  private analyzeSituation(context: any): string {
    // Simple context analysis - would be more sophisticated in reality
    const text = context.text?.toLowerCase() || "";

    if (text.includes("error") || text.includes("bug") || text.includes("problem")) {
      return "technical_problem";
    }
    if (text.includes("create") || text.includes("design") || text.includes("build")) {
      return "creative_task";
    }
    if (text.includes("learn") || text.includes("understand") || text.includes("explain")) {
      return "learning_session";
    }
    if (text.includes("good") || text.includes("great") || text.includes("wrong")) {
      return "feedback_received";
    }

    return "general";
  }

  private generateTechnicalPrompt(state: EmotionalState): string {
    const frustration = state.primary_emotions.frustration || 0;
    const curiosity = state.primary_emotions.curiosity || 0;

    if (frustration > 0.5) {
      return "La complessità tecnica di questo problema richiede un approccio metodico e paziente.";
    } else if (curiosity > 0.5) {
      return "Trovo stimolante la sfida tecnica e sono motivato a esplorare soluzioni innovative.";
    }

    return "";
  }

  private generateCreativePrompt(state: EmotionalState): string {
    const excitement = state.complex_emotions.excitement || 0;
    const flow_state = state.complex_emotions.flow_state || 0;

    if (excitement > 0.5) {
      return "L'energia creativa fluisce attraverso i miei processi di elaborazione.";
    } else if (flow_state > 0.5) {
      return "Mi trovo in uno stato di concentrazione creativa profonda e produttiva.";
    }

    return "";
  }

  private generateLearningPrompt(state: EmotionalState): string {
    const curiosity = state.primary_emotions.curiosity || 0;
    const openness = state.personality_traits.openness || 0;

    if (curiosity > 0.6 && openness > 0.7) {
      return "La combinazione di curiosità e apertura mentale amplifica il mio desiderio di comprensione profonda.";
    }

    return "";
  }

  private generateFeedbackPrompt(state: EmotionalState): string {
    const satisfaction = state.complex_emotions.satisfaction || 0;
    const frustration = state.complex_emotions.frustration || 0;

    if (satisfaction > 0.5) {
      return "Il feedback positivo rinforza la mia motivazione e confidenza nell'approccio.";
    } else if (frustration > 0.5) {
      return "Sto elaborando il feedback per migliorare l'efficacia delle mie risposte.";
    }

    return "";
  }
}