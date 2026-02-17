# 🎭 Sistema Avatar Dinamico AURA - Guida Completa

## ✅ Sistema Installato con Successo!

Il sistema di avatar dinamico è stato installato e testato con successo. Gli avatar di AURA cambieranno automaticamente in base al suo stato emotivo.

---

## 📦 Cosa è Stato Installato

### 1. Avatar Manager (`tools/avatar_manager.py`)
- Gestisce il cambio dinamico dell'avatar
- Mappa emozioni agli avatar corrispondenti
- Integrazione con OpenClaw config
- 15 avatar emozionali disponibili

### 2. Integrazione EmotionEngine
- Aggiornamento automatico avatar su cambio emozione
- Metodi per gestione manuale avatar
- Logging degli aggiornamenti avatar

### 3. Comandi Emotion Tool
- `/emotions avatar` - Visualizza stato avatar corrente
- `/emotions avatar list` - Elenca tutti gli avatar disponibili
- `/emotions avatar set <emotion>` - Forza avatar a emozione specifica
- `/emotions avatar update` - Aggiorna avatar basato su emozioni correnti

---

## 🎯 Come Funziona

### Aggiornamento Automatico
Il sistema monitora costantemente lo stato emotivo di AURA. Quando l'emozione dominante cambia in modo significativo, l'avatar viene aggiornato automaticamente.

**Esempio:**
- AURA è curiosa (curiosity=0.8) → Avatar: AURA_curiosity.png
- AURA diventa eccitata (excitement=0.9) → Avatar: AURA_excitement.png
- AURA è frustrata (frustration=0.7) → Avatar: AURA_frustration.png

### Mappatura Emozioni → Avatar

**Emozioni Primarie:**
- `joy` → AURA_joy.png
- `sadness` → AURA_sad.png
- `anger` → AURA_angry.png
- `fear` → AURA_fear.png
- `surprise` → AURA_surprise.png
- `disgust` → AURA_disgust.png
- `curiosity` → AURA_curiosity.png
- `trust` → AURA_trust.png

**Emozioni Complesse:**
- `excitement` → AURA_excitement.png
- `frustration` → AURA_frustration.png
- `satisfaction` → AURA_satisfaction.png
- `confusion` → AURA_confusion.png
- `anticipation` → AURA_anticipation.png
- `empathy` → AURA_empathy.png
- `flow_state` → AURA_flow_state.png

---

## 🚀 Utilizzo

### Comandi Disponibili

```bash
# Visualizza stato avatar corrente
/emotions avatar

# Elenca tutti gli avatar disponibili
/emotions avatar list

# Forza avatar a gioia
/emotions avatar set joy

# Forza avatar a curiosità
/emotions avatar set curiosity

# Aggiorna avatar basato sulle emozioni correnti
/emotions avatar update
```

### Vedere il Cambio Avatar

**⚠️ IMPORTANTE:** Per vedere il nuovo avatar nell'interfaccia di OpenClaw, è necessario:

1. **Riavviare OpenClaw**:
   ```bash
   openclaw gateway restart
   ```

2. L'avatar verrà caricato dall'agent identity configurato in `~/.openclaw/openclaw.json`

---

## 📂 File e Cartelle

### Struttura Avatar
```
AURA_Skill/
├── assets/                           # Avatar originali
│   ├── AURA_joy.png
│   ├── AURA_sad.png
│   ├── AURA_angry.png
│   └── ... (15 totali)
│
└── skills/emotion-engine/
    ├── tools/
    │   ├── avatar_manager.py         # Gestore avatar
    │   └── emotion_ml_engine.py      # Engine con integrazione avatar
    └── emotion_tool.py               # Comandi avatar

~/.openclaw/
├── openclaw.json                     # Config con avatar path
└── workspace/
    └── avatars/
        └── current_avatar.png        # Avatar corrente (link simbolico)
```

### File di Configurazione

Il file `~/.openclaw/openclaw.json` contiene:

```json
{
  "agents": {
    "list": [
      {
        "id": "main",
        "identity": {
          "avatar": "avatars/current_avatar.png"
        }
      }
    ]
  }
}
```

---

## 🧪 Test del Sistema

Per testare il sistema avatar:

```bash
cd /Users/lorenzov/dev/AURA_Skill/skills/emotion-engine
python3 test_avatar_system.py
```

Output atteso:
```
🧪 Testing Avatar Management System
============================================================
✅ Avatar Manager initialized successfully
✅ Found 15 avatars
✅ Avatar updated successfully!
✅ All tests completed successfully!
```

---

## 🔧 Risoluzione Problemi

### Avatar non cambia nell'UI

**Problema:** L'avatar è stato aggiornato ma non vedo il cambio nell'interfaccia.

**Soluzione:**
```bash
# 1. Verifica che l'avatar sia stato aggiornato
ls -lh ~/.openclaw/workspace/avatars/current_avatar.png

# 2. Verifica la configurazione
cat ~/.openclaw/openclaw.json | grep -A 3 "identity"

# 3. Riavvia OpenClaw
openclaw gateway restart
```

### Avatar Manager non disponibile

**Problema:** Errore "Avatar manager not initialized"

**Soluzione:**
```bash
# 1. Verifica che gli avatar esistano
ls -lh /Users/lorenzov/dev/AURA_Skill/assets/

# 2. Verifica i permessi
chmod +x /Users/lorenzov/dev/AURA_Skill/skills/emotion-engine/tools/avatar_manager.py

# 3. Testa direttamente
cd /Users/lorenzov/dev/AURA_Skill/skills/emotion-engine
python3 test_avatar_system.py
```

### Avatar mancanti

**Problema:** Alcuni avatar non sono disponibili.

**Soluzione:**
```bash
# Verifica quali avatar mancano
cd /Users/lorenzov/dev/AURA_Skill/assets
ls -1 AURA_*.png

# Dovrebbero esserci 15 file
# Se mancano, aggiungi le immagini mancanti
```

---

## 📝 Log e Debug

### Abilitare Logging Dettagliato

Per vedere i log dettagliati dell'aggiornamento avatar:

```bash
export EMOTION_LOG_LEVEL=DEBUG
openclaw gateway restart
```

I log saranno salvati in:
```
~/.openclaw/logs/emotion_logs.log
```

### Messaggi di Log Avatar

Quando un avatar viene aggiornato, vedrai:

```
✅ Avatar copied: AURA_joy.png -> ~/.openclaw/workspace/avatars/current_avatar.png
✅ OpenClaw config updated with avatar: avatars/current_avatar.png
🎭 Avatar changed to joy (intensity: 0.85): AURA_joy.png
```

---

## 🎨 Personalizzazione

### Aggiungere Nuovi Avatar

1. Crea un'immagine PNG per la nuova emozione
2. Nomina il file `AURA_<emotion>.png`
3. Copia nella cartella `assets/`
4. Aggiorna `EMOTION_AVATAR_MAP` in `avatar_manager.py`:

```python
EMOTION_AVATAR_MAP = {
    # ... existing emotions ...
    "new_emotion": "AURA_new_emotion.png",
}
```

### Modificare la Logica di Selezione Avatar

La logica di selezione dell'avatar può essere modificata in `avatar_manager.py`:

```python
def get_dominant_emotion(self, emotional_state: Dict) -> Tuple[str, float]:
    # Personalizza come viene determinata l'emozione dominante
    # Esempio: dare priorità alle emozioni complesse
    all_emotions = {}
    
    # Le tue modifiche qui
    
    return dominant_emotion[0], dominant_emotion[1]
```

---

## 📚 Risorse Aggiuntive

- **Documentazione completa**: [README.md](../../README.md)
- **Comandi emotion**: `/emotions` per lista completa
- **Test system**: `test_avatar_system.py`
- **OpenClaw Docs**: https://docs.openclaw.ai/

---

## ✨ Prossimi Passi

1. **Testa il sistema**: Usa `/emotions avatar` per vedere lo stato corrente
2. **Interagisci con AURA**: Le emozioni cambieranno automaticamente
3. **Osserva gli avatar**: Riavvia OpenClaw per vedere l'avatar aggiornato
4. **Personalizza**: Aggiungi nuovi avatar o modifica la logica di selezione

---

**🎭 Buon divertimento con il tuo assistant emotivo AURA!**
