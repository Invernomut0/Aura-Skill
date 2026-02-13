# OpenClaw Emotional System Fixes - v5

## Main Problem Solved

The error "plugin manifest requires id" was caused by a plugin structure inconsistent with the official OpenClaw documentation.

## Applied Fixes

### 1. **package.json** - CRITICAL FIX ✅
```json
{
  "name": "emotion-persistence",
  "openclaw": {
    "extensions": ["./src/index.ts"]  // <- ADDED: Mandatory field!
  }
}
```
**Reference:** https://docs.openclaw.ai/tools/plugin
> "Plugin 'package.json' must include 'openclaw.extensions' with one or more entry files"

### 2. **openclaw.plugin.json** - CORRECT FORMAT ✅
```json
{
  "id": "emotion-persistence",           // <- Mandatory field
  "name": "Emotion Persistence",
  "version": "1.0.0",
  "configSchema": {                      // <- Mandatory for config validation
    "type": "object",
    "properties": { ... }
  },
  "uiHints": { ... }                     // <- Optional but recommended for UI
}
```

### 3. **src/index.ts** - CORRECT EXPORT ✅
```typescript
// OLD (WRONG):
export default EmotionPersistencePlugin;

// NEW (CORRECT):
export default function (api: any) {
  const plugin = {
    id: 'emotion-persistence',
    name: 'Emotion Persistence',
    register(api: any) {
      // Method and lifecycle hook registration
    }
  };
  plugin.register(api);
}
```
**Reference:** From OpenClaw documentation
> "Plugins export either: A function: `(api) => { ... }` OR An object: `{ id, name, register(api) { ... } }`"

### 4. **npm Dependencies** - REMOVAL of better-sqlite3 ✅
```json
// REMOVED better-sqlite3 which required C++20
"dependencies": {
  "sqlite3": "^5.1.6",     // Use this instead
  "uuid": "^9.0.0",
  "zod": "^3.22.4",
  "jsonschema": "^1.4.1"
}
```

## Modified Files

1. ✅ `plugins/emotion-persistence/package.json` - Added `openclaw.extensions`
2. ✅ `plugins/emotion-persistence/openclaw.plugin.json` - Correct format with `id` and `configSchema`
3. ✅ `plugins/emotion-persistence/src/index.ts` - Correct export for OpenClaw
4. ✅ `INSTALL.sh` - New simplified installer

## Updated Installer

### File: `INSTALL.sh`

**New approach:**
- ✅ Direct file copy (no CLI complexity)
- ✅ Automatic test of the Python skill
- ✅ Graceful error handling for npm
- ✅ Colored and user-friendly output
- ✅ Flag `--skip-plugin` to bypass TypeScript plugin

**How to use:**
```bash
# Full installation
./INSTALL.sh

# Skip TypeScript plugin if there are npm problems
./INSTALL.sh --skip-plugin
```

## Correct OpenClaw Plugin Structure

```
plugins/emotion-persistence/
├── package.json                    # MUST have "openclaw": { "extensions": [...] }
├── openclaw.plugin.json            # MUST have "id" and "configSchema"
├── src/
│   └── index.ts                    # MUST export function(api) {}
├── tsconfig.json
└── node_modules/                   # Created by npm install
```

## How OpenClaw Loads Plugins

1. **Discovery:** OpenClaw scans:
   - `~/.openclaw/plugins/`
   - Workspace extensions
   - Paths configured in `plugins.load.paths`

2. **Validation:**
   - Checks presence of `openclaw.plugin.json` with `id` field
   - Checks `package.json` with `openclaw.extensions`
   - Validates config against `configSchema`

3. **Loading:**
   - Loads entry file specified in `openclaw.extensions`
   - Runs the exported function with the `api` object
   - Registers methods and lifecycle hooks

4. **Enable/Disable:**
   - Via config: `plugins.entries.<id>.enabled`
   - Via CLI: `openclaw plugins enable <id>`

## Installation Testing

```bash
# 1. Upload to remote machine
scp -r AURA_Skill/ user@remote:/path/to/destination/

# 2. Run installer
cd /path/to/destination/AURA_Skill
chmod +x INSTALL.sh
./INSTALL.sh

# 3. Restart OpenClaw
openclaw gateway restart

# 4. Verify
openclaw skills list
openclaw hooks list
openclaw plugins list

# 5. Test Python skill
python3 ~/.openclaw/skills/emotion-engine/emotion_tool.py emotions

# 6. Test in OpenClaw
# Open OpenClaw chat and type: /emotions
```

## Troubleshooting

### If you still see "plugin manifest requires id"
```bash
# Check that openclaw.plugin.json has the id field
cat ~/.openclaw/plugins/emotion-persistence/openclaw.plugin.json | grep '"id"'

# If missing, add manually:
# { "id": "emotion-persistence", ... }
```

### If npm install fails
```bash
# Use flag --skip-plugin
./INSTALL.sh --skip-plugin

# The system will still work (only the Python skill is essential)
```

### If OpenClaw cannot find the skill
```bash
# Check that SKILL.md exists
ls -la ~/.openclaw/skills/emotion-engine/SKILL.md

# Check permissions
chmod +x ~/.openclaw/skills/emotion-engine/emotion_tool.py

# Restart gateway
openclaw gateway restart
```

## System Components

### ✅ CORE (Works Standalone)
- **emotion-engine skill** (Python)
  - SQLite database
  - ML engine
  - Sentiment analysis
  - Slash commands

### ⚠️ OPTIONAL (Improves experience)
- **emotion-prompt-modifier hook** (TypeScript)
  - Modifies prompts based on emotional state
- **emotion-persistence plugin** (TypeScript)
  - Advanced persistence management
  - Analytics engine
  - Pattern recognition cache

## Documentation References

- Plugin Structure: https://docs.openclaw.ai/tools/plugin
- CLI Reference: https://docs.openclaw.ai/cli/index
- Skills System: https://docs.openclaw.ai/skills/index
- Hooks System: https://docs.openclaw.ai/hooks/index

## Changelog v5

- ✅ Added `openclaw.extensions` to package.json
- ✅ Fixed format openclaw.plugin.json with `id` and `configSchema`
- ✅ Corrected plugin export with `function(api) {}`
- ✅ Removed better-sqlite3 (C++20 issues)
- ✅ Created simplified INSTALL.sh
- ✅ Full documentation of fixes
- ✅ Followed official OpenClaw documentation exactly
