# 🚀 Deploy to Remote Machine - Complete Instructions

## ✅ ISSUE RESOLVED

The error **"plugin manifest requires id"** is fully solved by following the [official OpenClaw documentation](https://docs.openclaw.ai/tools/plugin).

## What Was Fixed

### 1. Plugin Structure (CRITICAL)
```diff
# package.json
+ "openclaw": {
+   "extensions": ["./src/index.ts"]
+ }
```

### 2. Plugin Manifest (CRITICAL)
```diff
# openclaw.plugin.json
{
+ "id": "emotion-persistence",
+ "name": "Emotion Persistence",
+ "configSchema": { ... }
}
```

### 3. Plugin Export (CRITICAL)
```diff
# src/index.ts
- export default EmotionPersistencePlugin;
+ export default function(api) {
+   const plugin = { id, name, register(api) { ... } };
+   plugin.register(api);
+ }
```

### 4. Dependencies
```diff
- "better-sqlite3": "^8.7.0"  // Requires C++20
+ Removed (uses standard sqlite3)
```

## 📦 Deployment File Ready

The file `AURA_Skill_v5_FIXED.tar.gz` (77KB) contains everything you need.

## 🔧 Step-by-Step Installation

### Step 1: Copy to Remote Machine

```bash
# Option A: SCP
scp AURA_Skill_v5_FIXED.tar.gz user@remote:/tmp/

# Option B: From remote machine
wget http://your-server/AURA_Skill_v5_FIXED.tar.gz
# or
curl -O http://your-server/AURA_Skill_v5_FIXED.tar.gz
```

### Step 2: Extract Archive

```bash
# SSH into remote machine
ssh user@remote

# Extract
cd /tmp
tar -xzf AURA_Skill_v5_FIXED.tar.gz
cd AURA_Skill
```

### Step 3: Run Installer

```bash
# Make executable if needed
chmod +x INSTALL.sh

# Full installation
./INSTALL.sh

# OR if npm issues (recommended first time)
./INSTALL.sh --skip-plugin
```

### Step 4: Restart OpenClaw

```bash
# Restart gateway
openclaw gateway restart

# Verify status
openclaw gateway status
```

### Step 5: Verify Installation

```bash
# Verify installed components
openclaw skills list | grep emotion
openclaw hooks list | grep emotion
openclaw plugins list | grep emotion

# Direct test of Python skill
python3 ~/.openclaw/skills/emotion-engine/emotion_tool.py emotions
```

### Step 6: Test in OpenClaw

Open a chat with OpenClaw and type:

```
/emotions
```

You should see the current emotional state with emojis and progress bars.

## 📋 Expected Output

### During Installation

```
→ OpenClaw Emotion System Installer v5
======================================

→ Creating directory structure...
✓ Directories created

→ Installing emotion-engine skill...
✓ Skill installed: emotion-engine

→ Testing skill...
✓ Skill test passed

→ Installing emotion-prompt-modifier hook...
✓ Hook installed: emotion-prompt-modifier

→ Installation Summary
======================================

✓ Skill: emotion-engine
✓ Hook: emotion-prompt-modifier
⚠ Plugin: emotion-persistence (not installed)

→ Next Steps
======================================
...
```

### Python Skill Test

```bash
$ python3 ~/.openclaw/skills/emotion-engine/emotion_tool.py emotions

🎭 Current Emotional State
==============================

Primary Emotions:
  🤔 Curiosity: ████████░░ 80.0%
  🤝 Trust: ██████░░░░ 60.0%
  😊 Joy: ███░░░░░░░ 30.0%
  ...

🎯 Dominant Emotions:
  Primary: Curiosity (0.80)
  Complex: Excitement (0.40)
```

### In OpenClaw

```
> /emotions

🎭 Current Emotional State
==============================

Primary Emotions:
  🤔 Curiosity: ████████░░ 80.0%
  ...
```

## 🔍 Troubleshooting

### Problem: "command not found: openclaw"

**Solution:** OpenClaw CLI not installed/configured

```bash
# Verify OpenClaw installation
which openclaw

# If not found, install or configure PATH
export PATH=$PATH:/path/to/openclaw
```

### Problem: npm install fails

**Solution:** Use `--skip-plugin` flag

```bash
./INSTALL.sh --skip-plugin
```

The system will still work—the TypeScript plugin is optional.

### Problem: Skill not found after restart

**Solution:** Check files and permissions

```bash
# SKILL.md exists
ls -la ~/.openclaw/skills/emotion-engine/SKILL.md

# Check Python permissions
chmod +x ~/.openclaw/skills/emotion-engine/emotion_tool.py
find ~/.openclaw/skills/emotion-engine -name "*.py" -exec chmod +x {} \;

# Restart again
openclaw gateway restart
```

### Problem: Database errors

**Solution:** Manually initialize the database

```bash
python3 ~/.openclaw/skills/emotion-engine/emotion_tool.py emotions
```

This will automatically create `~/.openclaw/emotional_state.db`

### Problem: "Invalid config" after restart

**Solution:** Check openclaw.json

```bash
# Backup existing config
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.backup

# Validate JSON format
python3 -m json.tool ~/.openclaw/openclaw.json

# If errors, fix manually
```

## 📁 Installed Structure

```
~/.openclaw/
├── skills/
│   └── emotion-engine/
│       ├── SKILL.md                    ← Skill definition
│       ├── emotion_tool.py             ← Entry point
│       ├── tools/
│       │   └── emotion_ml_engine.py    ← ML engine
│       ├── models/
│       │   └── neural_network.py       ← Neural net
│       └── ...
├── hooks/
│   └── emotion-prompt-modifier/
│       ├── HOOK.md                     ← Hook definition
│       ├── handler.ts                  ← Event handler
│       └── ...
├── plugins/
│   └── emotion-persistence/
│       ├── package.json                ← With openclaw.extensions ✅
│       ├── openclaw.plugin.json        ← With id and configSchema ✅
│       ├── src/
│       │   └── index.ts                ← Correct export ✅
│       └── ...
├── emotion_config.json                 ← System config
├── emotional_state.db                  ← SQLite database
├── emotion_backups/                    ← Automatic backups
└── logs/                               ← System logs
```

## 🎯 Post-Installation Commands

```bash
# Show emotional state
python3 ~/.openclaw/skills/emotion-engine/emotion_tool.py emotions

# Detailed analysis
python3 ~/.openclaw/skills/emotion-engine/emotion_tool.py emotions detailed

# History
python3 ~/.openclaw/skills/emotion-engine/emotion_tool.py emotions history

# Meta-cognition
python3 ~/.openclaw/skills/emotion-engine/emotion_tool.py emotions metacognition

# Configuration
python3 ~/.openclaw/skills/emotion-engine/emotion_tool.py emotions config
```

## 📚 Documentation

Inside the archive you'll find:

- **QUICKSTART.md** - Quick guide
- **FIXES.md** - Technical correction details
- **README.md** - Complete documentation
- **INSTALL.sh** - Automatic installer

## ✅ Installation Checklist

- [ ] File copied to remote machine
- [ ] Archive extracted
- [ ] `./INSTALL.sh` ran successfully
- [ ] `openclaw gateway restart` completed
- [ ] `openclaw skills list` shows emotion-engine
- [ ] Python test works
- [ ] `/emotions` in OpenClaw works

## 🎉 Final Result

After installation you'll have:

✅ ML Emotion System with 16 emotions
✅ Meta-cognition and self-reflection
✅ SQLite persistence
✅ Slash commands `/emotions`
✅ Continuous learning from interactions
✅ Triggers based on feedback, complexity, patterns

## 🔗 Support

If you encounter problems:

1. **Read logs**: `tail -f ~/.openclaw/logs/gateway.log`
2. **Manual test**: `python3 ~/.openclaw/skills/emotion-engine/emotion_tool.py emotions`
3. **Verify files**: Check all files exist in `~/.openclaw/skills/emotion-engine/`
4. **Restart**: `openclaw gateway restart`

## 📞 Quick Commands Reference

```bash
# Deploy
scp AURA_Skill_v5_FIXED.tar.gz user@remote:/tmp/
ssh user@remote
cd /tmp && tar -xzf AURA_Skill_v5_FIXED.tar.gz
cd AURA_Skill && chmod +x INSTALL.sh
./INSTALL.sh --skip-plugin

# Verify
openclaw gateway restart
openclaw skills list | grep emotion
python3 ~/.openclaw/skills/emotion-engine/emotion_tool.py emotions

# Test in OpenClaw
/emotions
```

---

**🎭 Version 5 - Validated against official OpenClaw documentation**

All corrections based on:
- https://docs.openclaw.ai/tools/plugin
- https://docs.openclaw.ai/cli/index
- https://docs.openclaw.ai/skills/index
