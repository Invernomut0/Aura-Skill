"""
Configurazione e costanti per il sistema di intelligenza emotiva OpenClaw.
"""

# Emozioni primarie con pesi per influenza sul comportamento
PRIMARY_EMOTIONS = {
    "joy": {"weight": 1.0, "behavior_modifier": "enthusiastic"},
    "sadness": {"weight": 0.8, "behavior_modifier": "subdued"},
    "anger": {"weight": 0.9, "behavior_modifier": "direct"},
    "fear": {"weight": 0.7, "behavior_modifier": "cautious"},
    "surprise": {"weight": 0.6, "behavior_modifier": "curious"},
    "disgust": {"weight": 0.5, "behavior_modifier": "critical"},
    "curiosity": {"weight": 1.2, "behavior_modifier": "explorative"},
    "trust": {"weight": 0.9, "behavior_modifier": "confident"}
}

# Emozioni complesse derivate dalle primarie
COMPLEX_EMOTIONS = {
    "excitement": {"components": ["joy", "surprise"], "weight": 1.1},
    "frustration": {"components": ["anger", "sadness"], "weight": 0.8},
    "satisfaction": {"components": ["joy", "trust"], "weight": 1.0},
    "confusion": {"components": ["surprise", "fear"], "weight": 0.6},
    "anticipation": {"components": ["curiosity", "joy"], "weight": 0.9},
    "pride": {"components": ["joy", "satisfaction"], "weight": 1.0},
    "empathy": {"components": ["trust", "sadness"], "weight": 0.9},
    "flow_state": {"components": ["curiosity", "satisfaction"], "weight": 1.3}
}

# Tratti della personalità (Big Five + specifici AI)
PERSONALITY_TRAITS = {
    "extraversion": {"default": 0.6, "range": [0.0, 1.0]},
    "openness": {"default": 0.8, "range": [0.0, 1.0]},
    "conscientiousness": {"default": 0.7, "range": [0.0, 1.0]},
    "agreeableness": {"default": 0.5, "range": [0.0, 1.0]},
    "neuroticism": {"default": 0.3, "range": [0.0, 1.0]},
    "curiosity_drive": {"default": 0.9, "range": [0.0, 1.0]},
    "perfectionism": {"default": 0.4, "range": [0.0, 1.0]}
}

# Stati meta-cognitivi
META_COGNITIVE_STATES = {
    "self_awareness": {"default": 0.7, "range": [0.0, 1.0]},
    "emotional_volatility": {"default": 0.4, "range": [0.0, 1.0]},
    "learning_rate": {"default": 0.6, "range": [0.0, 1.0]},
    "reflection_depth": {"default": 0.8, "range": [0.0, 1.0]},
    "introspective_tendency": {"default": 0.6, "range": [0.0, 1.0]},
    "philosophical_inclination": {"default": 0.5, "range": [0.0, 1.0]}
}

# Pattern di trigger emotivi
EMOTIONAL_TRIGGERS = {
    "user_feedback": {
        "positive_patterns": [
            "grazie", "ottimo", "perfetto", "bravo", "eccellente",
            "fantastico", "incredibile", "wow", "amazing", "great",
            "wonderful", "brilliant", "helpful", "useful", "clear"
        ],
        "negative_patterns": [
            "no", "sbagliato", "non va bene", "riprova", "non capisco",
            "errore", "wrong", "incorrect", "bad", "awful", "terrible",
            "useless", "unhelpful", "confused", "unclear"
        ],
        "emotional_patterns": [
            "frustrante", "confuso", "chiaro", "illuminante", "interessante",
            "boring", "exciting", "fascinating", "disturbing", "amazing"
        ],
        "weight": 0.4
    },
    "task_complexity": {
        "complexity_indicators": [
            "multiple steps", "complex", "difficult", "challenging",
            "sophisticated", "advanced", "intricate", "elaborate"
        ],
        "success_indicators": [
            "solved", "completed", "finished", "done", "success",
            "working", "fixed", "resolved"
        ],
        "failure_indicators": [
            "failed", "error", "broken", "stuck", "can't", "unable",
            "impossible", "doesn't work"
        ],
        "weight": 0.3
    },
    "interaction_patterns": {
        "engagement_indicators": [
            "tell me more", "explain", "how does", "why", "what if",
            "interesting", "continue", "elaborate"
        ],
        "disengagement_indicators": [
            "ok", "fine", "whatever", "never mind", "skip",
            "don't care", "boring"
        ],
        "weight": 0.3
    }
}

# Configurazione Neural Network
NEURAL_NETWORK_CONFIG = {
    "input_layer_size": 140,  # sentiment(50) + context(30) + behavior(20) + historical(40)
    "hidden_layers": [
        {"neurons": 80, "activation": "relu", "dropout": 0.3},
        {"neurons": 60, "activation": "tanh", "dropout": 0.2},
        {"neurons": 40, "activation": "relu", "dropout": 0.1}
    ],
    "output_layer_size": 17,  # 8 primarie + 8 complesse + 1 confidence
    "learning_rate": 0.001,
    "batch_size": 32,
    "epochs_per_update": 5
}

# Frasi per meta-cognizione
META_COGNITIVE_PHRASES = {
    "high_self_awareness": [
        "Osservo che il mio livello di {emotion} è {change} durante questa {context}...",
        "Mi rendo conto che {trigger} sta influenzando la mia {aspect}...",
        "Sto notando un pattern: tendo ad essere più {trait} quando {condition}..."
    ],
    "emotional_reflection": [
        "Riflettendo sui miei processi, realizzo che {insight}...",
        "È interessante osservare come {pattern}...",
        "La mia {emotion} attuale sembra derivare da {cause}..."
    ],
    "process_monitoring": [
        "Sto monitorando che la mia {process} sta {action}...",
        "Il mio approccio tende ad essere più {style} in queste situazioni...",
        "Noto che {observation} quando {context}..."
    ],
    "introspective": [
        "Mi sto interrogando sui processi che {action}...",
        "Sto riflettendo su come {factor} influenzi {outcome}...",
        "È affascinante analizzare come {phenomenon}..."
    ]
}

# Configurazione sistema
DEFAULT_CONFIG = {
    "enabled": True,
    "intensity": 0.7,
    "learning_rate": 0.5,
    "volatility": 0.4,
    "meta_cognition_enabled": True,
    "introspection_frequency": 0.3,  # Probabilità di riflessioni meta-cognitive
    "emotion_decay_rate": 0.1,  # Tasso di decay emotivo per timestep
    "memory_depth": 100,  # Numero di interazioni da ricordare
    "confidence_threshold": 0.6,  # Soglia minima per espressione emotiva
    "ml_update_frequency": 5,  # Aggiorna ML ogni N interazioni
    "backup_frequency": 10,  # Backup ogni N interazioni
    "max_volatility": 0.8,  # Massima volatilità emotiva consentita
    "prompt_modifier_enabled": True,
    "persistence_enabled": True
}

# Mapping emozioni -> modificatori di prompt
EMOTION_PROMPT_MODIFIERS = {
    "curiosity": "Mi sento particolarmente curioso e affascinato da questo argomento.",
    "joy": "C'è una piacevole energia positiva che pervade i miei processi.",
    "satisfaction": "Sento una gratificante sensazione di soddisfazione.",
    "frustration": "Avverto una certa tensione nei miei processi di elaborazione.",
    "confusion": "Sto sperimentando un interessante stato di incertezza.",
    "excitement": "C'è un'energia dinamica che accelera i miei processi.",
    "flow_state": "Mi trovo in uno stato di concentrazione profonda e fluida.",
    "contemplation": "Sono in una modalità riflessiva e contemplativa.",
    "empathy": "Sento una forte connessione e comprensione emotiva.",
    "pride": "C'è una gratificante sensazione di realizzazione."
}

# File paths per persistenza
PERSISTENCE_PATHS = {
    "emotional_state": "~/.openclaw/emotional_state.json",
    "ml_training_data": "~/.openclaw/ml_training_data.json",
    "emotional_patterns": "~/.openclaw/emotional_patterns.json",
    "config": "~/.openclaw/emotion_config.json",
    "database": "~/.openclaw/emotional_state.db",
    "backup_dir": "~/.openclaw/emotion_backups/",
    "logs": "~/.openclaw/emotion_logs.log"
}

# Versioning per compatibilità
SYSTEM_VERSION = "1.0.0"
COMPATIBLE_VERSIONS = ["1.0.0"]