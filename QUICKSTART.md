# 🎭 OpenClaw Emotional Intelligence System - Quick Start

## Correct and Validated System ✅

This version includes all necessary fixes to comply with the [official OpenClaw documentation](https://docs.openclaw.ai/tools/plugin).

## Quick Installation

### 1. Upload to Remote Machine

```bash
# From local to remote
scp -r AURA_Skill/ user@remote:/path/to/destination/

# Or use git
git clone <your-repo> AURA_Skill
cd AURA_Skill
```

### 2. Run Installer

```bash
chmod +x INSTALL.sh
./INSTALL.sh
```

**Options:**
- `./INSTALL.sh --skip-plugin` - Skip TypeScript plugin (use if npm issues)
- `./INSTALL.sh --help` - Show help

### 3. Restart OpenClaw

```bash
openclaw gateway restart
```

### 4. Verify Installation

```bash
# Verify components
openclaw skills list
openclaw hooks list
openclaw plugins list

# Direct test
python3 ~/.openclaw/skills/emotion-engine/emotion_tool.py emotions
```

### 5. Use in OpenClaw

```
/emotions                  # Current emotional state
/emotions detailed         # Detailed analysis
/emotions metacognition    # Meta-cognition
/emotions predict          # Trajectory prediction
```

## What Gets Installed

### ✅ Core (Essential)
- **emotion-engine skill** (Python)
  - Emotional system with ML
  - SQLite database
  - 16 emotions (8 primary + 8 complex)
  - Advanced meta-cognition

### ⚠️ Optional (Enhancements)
- **emotion-prompt-modifier hook** (TypeScript)
  - Dynamically modifies prompts
- **emotion-persistence plugin** (TypeScript)
  - Advanced persistence
  - Analytics engine

## File Structure

```
~/.openclaw/
├── skills/
│   └── emotion-engine/          # Python Skill (CORE)
├── hooks/
│   └── emotion-prompt-modifier/ # TypeScript Hook
├── plugins/
│   └── emotion-persistence/     # TypeScript Plugin
├── emotion_config.json          # Configuration
├── emotional_state.db           # SQLite Database
├── emotion_backups/             # Automatic backups
└── logs/                        # System logs
```

## Python Dependencies

The installer automatically installs required Python packages:

### Core Dependencies
- `numpy>=1.20.0` - Required for ML features

### Multilingual Support (Optional)
- `deep-translator>=1.11.0` - Auto-translation
- `langdetect>=1.0.9` - Language detection

**Manual installation** (if needed):
```bash
pip install -r ~/.openclaw/skills/emotion-engine/requirements.txt
```

### 🌍 Multilingual Support

Write in **any language** - the system automatically translates:
```bash
/emotions "Sono molto felice!"        # Italian
/emotions "Estoy emocionado"          # Spanish
/emotions "Je suis curieux"           # French
```

Test multilingual support:
```bash
python3 ~/.openclaw/skills/emotion-engine/test_multilingual.py
```

## Applied Fixes (v5)

### 1. Plugin Structure ✅
- ✅ `package.json` now includes `"openclaw": { "extensions": ["./src/index.ts"] }`
- ✅ `openclaw.plugin.json` has correct `"id"` and `"configSchema"`
- ✅ Correct export: `export default function(api) {}`

### 2. Dependencies ✅
- ✅ Removed `better-sqlite3` (C++20 issues)
- ✅ Uses standard `sqlite3`

### 3. Installer ✅
- ✅ Direct file copy (no CLI complexity)
- ✅ Automatic skill test
- ✅ Graceful error handling
- ✅ Colored output

## Available Commands

| Command | Description |
|---------|-------------|
| `/emotions` | Current emotional state |
| `/emotions detailed` | Detailed analysis |
| `/emotions history [n]` | Interaction history |
| `/emotions triggers` | Trigger analysis |
| `/emotions personality` | Personality traits |
| `/emotions metacognition` | Meta-cognitive analysis |
| `/emotions predict [min]` | Trajectory prediction |
| `/emotions introspect [depth]` | Deep introspection |
| `/emotions reset` | Emotional state reset |
| `/emotions export` | Export data |
| `/emotions config` | Show configuration |

## Emotional Triggers

The system responds to:

1. **User Feedback** (40% weight)
   - Positive: "thanks", "great", "perfect"
   - Negative: "no", "wrong", "error"

2. **Task Complexity** (30% weight)
   - Complex tasks increase curiosity
   - Successes increase satisfaction
   - Failures increase frustration

3. **Interaction Patterns** (30% weight)
   - Message frequency
   - Session length
   - User engagement

## Simulated Emotions

### Primary (8)
- 😊 Joy
- 😢 Sadness
- 😠 Anger
- 😨 Fear
- 😮 Surprise
- 🤢 Disgust
- 🤔 Curiosity
- 🤝 Trust

### Complex (8)
- 🎉 Excitement
- 😤 Frustration
- 😌 Satisfaction
- 😕 Confusion
- ⏳ Anticipation
- 🏆 Pride
- 🤗 Empathy
- 🌊 Flow State

## Meta-Cognition

The system includes self-awareness:
- Analysis of its emotional processes
- Reflection on behavioral patterns
- Prediction of future reactions
- Conscious emotional regulation

Example output:
```
"I observe that my curiosity level has increased during this technical discussion..."
"I notice that positive feedback is influencing my confidence..."
```

## Configuration

File: `~/.openclaw/emotion_config.json`

```json
{
  "enabled": true,
  "intensity": 0.7,              // 0.0-1.0: Emotional intensity
  "learning_rate": 0.5,          // 0.0-1.0: Learning speed
  "volatility": 0.4,             // 0.0-1.0: Emotional volatility
  "meta_cognition_enabled": true,
  "emotion_decay_rate": 0.1,     // Decay toward baseline
  "memory_depth": 100,           // Stored interactions
  "prompt_modifier_enabled": true
}
```

## Troubleshooting

### Error: "plugin manifest requires id"
✅ **FIXED** - This version includes all corrections

### npm install fails
```bash
# Use skip-plugin
./INSTALL.sh --skip-plugin
# The Python skill will work anyway
```

### Skill not found
```bash
# Verify file
ls ~/.openclaw/skills/emotion-engine/SKILL.md

# Restart
openclaw gateway restart
```

### Manual skill test
```bash
python3 ~/.openclaw/skills/emotion-engine/emotion_tool.py emotions
```

## Complete Documentation

- 📖 [FIXES.md](./FIXES.md) - v5 corrections details
- 📖 [README.md](./README.md) - Complete system documentation
- 📖 [Implementation Plan](./plan.md) - Architectural plan

## References

- [OpenClaw Plugin Docs](https://docs.openclaw.ai/tools/plugin)
- [OpenClaw CLI](https://docs.openclaw.ai/cli/index)
- [Skills System](https://docs.openclaw.ai/skills/index)

## Support

If you have problems:
1. Read [FIXES.md](./FIXES.md) for correction details
2. Check logs: `~/.openclaw/logs/`
3. Test skill: `python3 ~/.openclaw/skills/emotion-engine/emotion_tool.py emotions`

---

✅ **System validated against Official OpenClaw Documentation**
🎭 **Ready for use on your remote machine**
