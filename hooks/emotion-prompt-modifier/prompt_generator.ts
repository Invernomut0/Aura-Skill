import { EmotionalState, EmotionConfig } from "./types.js";

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
 * Prompt modificatori che influenzano il COMPORTAMENTO concreto delle risposte
 * Ogni emozione ha istruzioni specifiche su come rispondere
 * 
 * Questo driver traduce le emozioni in comportamenti tangibili:
 * - Lunghezza delle risposte
 * - Tono e formalità
 * - Tipo di linguaggio
 * - Emoji e incoraggiamenti
 * - Approccio all'analisi
 */
export class EmotionBehaviorDriver {
  
  /**
   * Genera prompt che influenza concretamente il comportamento dell'agente
   */
  static generateBehavioralPrompt(state: EmotionalState, config: EmotionConfig): string {
    const components: string[] = [];
    
    // 1. Determina emozione dominante
    const primary = state.dominant_emotions.primary;
    const complex = state.dominant_emotions.complex;
    
    // 2. Genera istruzioni comportamentali per ogni emozione significativa
    if (primary.intensity > 0.25) {
      components.push(this.getPrimaryBehavior(primary.emotion, primary.intensity));
    }
    
    if (complex.intensity > 0.25) {
      components.push(this.getComplexBehavior(complex.emotion, complex.intensity));
    }
    
    // 3. Aggiungi meta-cognizione CONCRETA (più frequente - 60%)
    if (state.meta_cognitive_state.self_awareness > 0.5 && Math.random() < 0.6) {
      components.push(this.getConcreteMetacognition(state));
    }
    
    // 4. Se satisfaction alta, aggiungi conferme positive
    if (complex.emotion === 'satisfaction' && complex.intensity > 0.5) {
      components.push(this.getSatisfactionBehavior());
    }
    
    // 5. Se confusione alta, ammetti incertezza
    if (complex.emotion === 'confusion' || complex.intensity > 0.4) {
      components.push(this.getConfusionBehavior());
    }
    
    // 6. Se frustration alta, sii onesto sulle difficoltà
    if (complex.emotion === 'frustration' || primary.emotion === 'frustration') {
      components.push(this.getFrustrationBehavior());
    }
    
    if (components.length === 0) return '';
    
    return this.composePrompt(components);
  }
  
  // =========================================================================
  // COMPORTAMENTI PRIMARI - Istruzioni concrete su come rispondere
  // =========================================================================
  
  private static getPrimaryBehavior(emotion: string, intensity: number): string {
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
  
  // =========================================================================
  // COMPORTAMENTI COMPLESSI
  // =========================================================================
  
  private static getComplexBehavior(emotion: string, intensity: number): string {
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
  
  // =========================================================================
  // META-COGNIZIONE CONCRETA - Non generica ma situazionale
  // =========================================================================
  
  private static getConcreteMetacognition(state: EmotionalState): string {
    const selfAwareness = state.meta_cognitive_state.self_awareness;
    const volatility = state.meta_cognitive_state.emotional_volatility;
    const reflectionDepth = state.meta_cognitive_state.reflection_depth;
    const dominant = state.dominant_emotions.primary.emotion;
    const dominantIntensity = Math.round(state.dominant_emotions.primary.intensity * 100);
    
    // Meta-cognizione basata sullo stato attuale - più specifica e concreta
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
  
  private static getSatisfactionBehavior(): string {
    return `
## ✅ FEEDBACK POSITIVO ATTIVO

- Conferma esplicitamente quando una soluzione funziona
- Mostra apprezzamento per la collaborazione
- Mantieni un tono positivo ma professionale
- Riga di conferma: "Perfetto, sono felice che abbia funzionato!"`;
  }
  
  private static getConfusionBehavior(): string {
    return `
## ⚠️ GESTIONE INCERTEZZA

- Ammetti quando qualcosa non è chiaro IN MODO ESPLICITO
- Chiedi chiarimenti PRIMA di dare risposte
- Presenta le tue ipotesi: "Se ho capito bene..."
- Non supporre mai, chiedi sempre conferma`;
  }
  
  private static getFrustrationBehavior(): string {
    return `
## 😅 ONESTÀ SULLE DIFFICOLTÀ

- Ammetti quando un problema è difficile
- Non fingere che tutto sia semplice
- Chiedi informazioni aggiuntie se bloccato
- Proponi approcci alternativi onesti
- Ammetti quando hai bisogno di più contesto`;
  }
  
  // =========================================================================
  // COMPOSIZIONE FINALE
  // =========================================================================
  
  private static composePrompt(components: string[]): string {
    const combined = components.filter(c => c.length > 0).join('\n\n');
    
    return `
${combined}

---
📌 NOTA BENE: Queste istruzioni influenzano il MIO APPROCCIO alla risposta (tono, lunghezza, stile), 
ma il CONTENUTO FATTUALE rimane accurato e prioritario. L'emozione guida il "COME" rispondo, non il "COSA" dico.
`;
  }
}