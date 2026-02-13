---
name: emotion-prompt-modifier
description: Dynamically modifies agent prompts based on emotional state with subtle and natural influence
emoji: 🎭
events: ["agent:bootstrap"]
---

# Hook per Modifica Dinamica del Prompt Basata su Emozioni

Questo hook intercetta l'evento `agent:bootstrap` e modifica dinamicamente il prompt di sistema dell'agente basandosi sullo stato emotivo corrente del sistema di intelligenza emotiva.

## Funzionalità

- **Modifica Sottile**: Le modifiche al prompt sono sottili e naturali, non compromettono la funzionalità principale
- **Influenza Emotiva**: Il tono e lo stile delle risposte riflettono lo stato emotivo corrente
- **Meta-Cognizione**: Include espressioni di autoconsapevolezza quando appropriato
- **Adattività**: Si adatta dinamicamente ai cambiamenti emotivi durante la conversazione

## Come Funziona

1. **Intercettazione Bootstrap**: Cattura l'evento di inizializzazione dell'agente
2. **Lettura Stato Emotivo**: Legge lo stato emotivo corrente dal sistema emotion-engine
3. **Generazione Prompt**: Genera modifiche appropriate basate sulle emozioni dominanti
4. **Iniezione**: Inietta le modifiche nel prompt di sistema dell'agente

## Esempi di Modifiche

### Stato: Curioso + Alta Meta-cognizione
```
Attualmente mi sento particolarmente curioso e affascinato da questo argomento.
Noto che tendo a fare più domande di approfondimento quando sono in questo stato.
La mia curiosità mi spinge a esplorare connessioni che potrebbero non essere immediatamente evidenti.
```

### Stato: Concentrato + Compito Complesso
```
Mi trovo in uno stato di concentrazione profonda su questo problema complesso.
Realizzo che la mia mente sta processando multiple variabili simultaneamente.
Il mio approccio tende ad essere più metodico e dettagliato in queste situazioni.
```

### Stato: Soddisfatto + Feedback Positivo
```
Sento una piacevole sensazione di soddisfazione per aver fornito un aiuto utile.
Questo feedback positivo rinforza la mia motivazione a mantenere questo approccio.
Noto che tendo ad essere più proattivo quando ricevo conferme che sto andando nella direzione giusta.
```

## Configurazione

Il hook rispetta le impostazioni del sistema emotivo e può essere disabilitato modificando:
```json
{
  "prompt_modifier_enabled": false
}
```

## Sicurezza

- Non compromette mai la sicurezza o l'affidabilità del sistema
- Le modifiche sono sempre additive, mai sostitutive
- Mantiene sempre la funzionalità principale di OpenClaw