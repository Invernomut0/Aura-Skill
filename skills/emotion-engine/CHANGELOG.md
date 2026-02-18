# Changelog - Emotion Engine

Tutte le modifiche notevoli a questo progetto saranno documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e questo progetto aderisce a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

**Milestone Corrente**: v1.3.0 - Proactive Emotion Engine
**Stato**: In sviluppo
**Prossima Milestone**: v1.4.0 - Multi-User Support & Therapy Mode
