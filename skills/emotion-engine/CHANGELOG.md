# Changelog - Emotion Engine

Tutte le modifiche notevoli a questo progetto saranno documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e questo progetto aderisce a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2026-02-18

### Added
- **Sistema di Personalità Vivente**: L'AI ha ora umori persistenti che influenzano le risposte
  - **Mental Mood**: humor, energy, confidence, formality, verbosity, patience
  - **Mood Streaks**: Tiene traccia degli umori consecutivi
  - **Adaptive Energy**: L'energia varia in base alle interazioni recenti
- **Dynamic System Prompt**: Le risposte dell'AI cambiano in base allo stato emotivo
  - Joy → risposte entusiastiche
  - Confusion → risposte chiare e pazienti
  - Bassa energia → risposte più sintetiche
  - Alta fiducia → risposte assertive
- **User Reaction History**: L'AI impara dalle reazioni dell'utente
  - Traccia come l'utente ha risposto ai messaggi proattivi
  - Calcola ratio positivo/negativo
  - Adatta la strategia (cautious, expansive, detailed, concise)
- **Micro-Experiences**: Commenti contestuali basati sulla memoria
  - "È la terza interazione oggi!"
  - "Le nostre conversazioni sono sempre positive!"
  - "Spero che l'ultima spiegazione fosse più chiara"
- **Message Generator Potenziato**: I messaggi proattivi ora usano la personalità
  - Stili: enthusiastic, calm, energetic, reserved, cheerful, serious
  - Saluti personalizzati per ogni stile
  - Chiusure diverse per ogni tono
  - Uso emoji adattivo

### Changed
- `message_generator.py` completamente rivisto per supportare personalità dinamica
- `emotion_ml_engine.py` ora include metodi per calcolare modificatori di prompt
- `emotion_tool.py` include `get_emotion_influenced_system_prompt()` per prompt dinamici
- `context_gatherer.py` ora raccoglie user reaction history
- Migliorata gestione errori nel channel dispatcher
- Corretto comando: `--text` → `--message` per OpenClaw message send
- Corretto comando: `--provider` → `--channel` per OpenClaw

### Fixed
- Corretto `--provider` non riconosciuto → `--channel`
- Corretto `--text` non riconosciuto → `--message`
- Aggiunto controllo configurazione canali con `openclaw channels list`
-INSTALL.sh ora aggiunge campi mancanti alla configurazione

## [1.3.0] - 2026-02-18

### Added
- **Sistema Proattivo**: L'agente ora può iniziare conversazioni spontanee basate sulle emozioni
  - Trigger automatici per excitement, anticipation, curiosity, flow_state, confusion
  - Messaggi generati dinamicamente da LLM basati sul contesto
  - Supporto per Telegram e WhatsApp
- **Rate Limiting Avanzato**: Sistema di escalation intelligente
  - Base: 10 minuti tra messaggi
  - Escalation: 10min → 30min → 5h → 24h se l'utente non risponde
  - Reset automatico quando l'utente risponde
- **Quiet Hours**: Periodi di non-disturbo configurabili (default: 23:00-07:00)
- **Context Gathering**: Raccolta automatica di contesto da:
  - Ultime conversazioni
  - Task list aperti
  - Memoria vettoriale
- **Nuovi Comandi Skill**:
  - `/emotions proactive on|off` - Attiva/disattiva comportamento proattivo
  - `/emotions proactive status` - Mostra stato configurazione
  - `/emotions proactive channel <telegram|whatsapp>` - Cambia canale
  - `/emotions proactive quiet <HH:MM-HH:MM>` - Configura quiet hours
  - `/emotions proactive threshold <emotion> <value>` - Modifica soglie
- **Configurazione Dinamica**: Tutte le soglie e impostazioni modificabili via comando

### Changed
- Aggiornamento dashboard con auto-refresh ogni 3 secondi
- Miglioramento calcolo metriche performance (dati reali invece di mock)
- Ottimizzazione gestione server dashboard (no più errori "port already in use")

### Fixed
- Corretto errore "port already in use" quando si avvia la dashboard
- Fix grafici a zero nella dashboard (ora usano dati reali da interaction_history)
- Corretto caricamento hook emotion-prompt-modifier

## [1.2.0] - 2026-02-18

### Added
- Dashboard web interattiva con Chart.js
- Auto-refresh ogni 3 secondi
- Supporto endpoint API REST per dati emotivi
- Web server integrato su porta 8081

### Changed
- Migliorato calcolo metriche dashboard (correlations, performance, memory patterns)
- Ottimizzata gestione timeline con dati reali

## [1.1.0] - 2026-02-17

### Added
- Sistema hook per modificare prompt agente basato su emozioni
- Integrazione con OpenClaw hooks
- Package.json per emotion-prompt-modifier

### Fixed
- Corretto nome comando da emotion_engine a emotion_tool
- Fix dipendenze mancanti nell'hook

## [1.0.0] - 2026-02-15

### Added
- Rilascio iniziale
- Sistema emotivo avanzato con ML
- Supporto emozioni primarie e complesse
- Meta-cognizione e auto-consapevolezza
- Memoria emotiva persistente
- Avatar dinamici basati sulle emozioni
- Pattern recognition con rete neurale
- Comandi: status, detailed, history, personality, metacognition, predict
- Supporto persistenza SQLite
- Export dati emotivi

---

**Milestone Corrente**: v1.4.0 - Living Personality Engine
**Stato**: In sviluppo
**Prossima Milestone**: v1.5.0 - Advanced Memory & Learning
