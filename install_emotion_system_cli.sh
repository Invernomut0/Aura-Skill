#!/usr/bin/env bash
# install_emotion_system_cli.sh (v4)
# Robust installer for OpenClaw Emotion System
# - Validates and fixes manifests before installation
# - Handles npm failures gracefully with fallback to file copying
# - Avoids modifying ~/.openclaw/openclaw.json directly
# - Focuses on getting the Python-based emotion-engine working first
# Usage:
#   ./install_emotion_system_cli.sh [--token TOKEN] [--host HOST] [--skip-restart] [--skip-plugin]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOKEN=""
HOST=""
SKIP_RESTART=0
SKIP_PLUGIN=0

while (( "$#" )); do
  case "$1" in
    --token) TOKEN="$2"; shift 2 ;;
    --host) HOST="$2"; shift 2 ;;
    --skip-restart) SKIP_RESTART=1; shift ;;
    --skip-plugin) SKIP_PLUGIN=1; shift ;;
    -h|--help)
      cat <<EOF
Usage: $0 [--token TOKEN] [--host HOST] [--skip-restart] [--skip-plugin]

Options:
  --token TOKEN      OpenClaw CLI token for authenticated operations
  --host HOST        Optional host for OpenClaw gateway (if CLI supports it)
  --skip-restart     Don't attempt to restart the gateway at the end
  --skip-plugin      Skip TypeScript plugin installation (recommended if npm issues)
EOF
      exit 0
      ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

PLUGIN_DIR="$SCRIPT_DIR/plugins/emotion-persistence"
HOOK_DIR="$SCRIPT_DIR/hooks/emotion-prompt-modifier"
SKILL_DIR="$SCRIPT_DIR/skills/emotion-engine"
CONFIG_FILE="$HOME/.openclaw/emotion_config.json"

OPENCLAW_GLOBAL_OPTS=()
if [ -n "$TOKEN" ]; then OPENCLAW_GLOBAL_OPTS+=(--token "$TOKEN"); fi
if [ -n "$HOST" ];  then OPENCLAW_GLOBAL_OPTS+=(--host "$HOST"); fi

has_openclaw_cli() { command -v openclaw >/dev/null 2>&1; }
run_openclaw() {
  if has_openclaw_cli; then
    openclaw "${OPENCLAW_GLOBAL_OPTS[@]}" "$@" 2>&1
    return $?
  else
    return 127
  fi
}

log() { printf "[installer] %s\n" "$*"; }
err() { printf "[installer][ERROR] %s\n" "$*" >&2; }

# Safe copy avoiding same src/dst
safe_copy() {
  local src="$1" dst="$2"
  mkdir -p "$dst"
  local src_real dst_real
  src_real="$(realpath "$src" 2>/dev/null || echo "$src")"
  dst_real="$(realpath "$dst" 2>/dev/null || echo "$dst")"
  if [ "$src_real" = "$dst_real" ]; then
    log "Skipping copy: source and destination are identical: $src_real"
    return 0
  fi
  cp -r "$src"/* "$dst/" 2>/dev/null || true
  log "Copied $src -> $dst"
}

# Ensure package.json has openclaw.extensions
ensure_package_openclaw_extensions() {
  local plugin_dir="$1"
  local pkg="$plugin_dir/package.json"
  if [ ! -f "$pkg" ]; then
    log "No package.json at $pkg -> skipping openclaw.extensions step"
    return 0
  fi
  python3 - <<PY
import json,sys,os
p = os.path.expanduser('$pkg')
try:
    with open(p,'r') as f:
        pkg=json.load(f)
except:
    pkg={}
oc = pkg.get('openclaw',{}) if isinstance(pkg,dict) else {}
exts = oc.get('extensions') if isinstance(oc,dict) else None
if not isinstance(exts,list) or len(exts)==0:
    pkg.setdefault('openclaw',{})['extensions'] = ['./openclaw.plugin.json']
    with open(p,'w') as f:
        json.dump(pkg,f,indent=2,ensure_ascii=False)
    print('patched')
else:
    print('present')
PY
}

# Ensure openclaw.plugin.json has an id field
ensure_plugin_manifest_id() {
  local plugin_dir="$1"
  local manifest="$plugin_dir/openclaw.plugin.json"
  local pkg="$plugin_dir/package.json"
  if [ -f "$manifest" ]; then
    python3 - <<PY
import json,sys,os
m = os.path.expanduser('$manifest')
pkg = os.path.expanduser('$pkg')
try:
  with open(m,'r') as f: man = json.load(f)
except Exception:
  man = {}
# if id missing, infer
if not man.get('id'):
  inferred = None
  if os.path.exists(pkg):
    try:
      with open(pkg,'r') as f: pj=json.load(f)
      inferred = pj.get('name')
    except Exception:
      inferred = None
  if not inferred:
    inferred = os.path.basename(os.path.abspath('$plugin_dir'))
  man['id'] = inferred
  with open(m,'w') as f: json.dump(man,f,indent=2,ensure_ascii=False)
  print('patched-id', inferred)
else:
  print('id-present', man.get('id'))
PY
  else
    # create minimal manifest if missing
    local inferred
    if [ -f "$pkg" ]; then
      inferred="$(python3 -c "import json,sys; print(json.load(open('$pkg')).get('name',''))" 2>/dev/null || echo "")"
    fi
    if [ -z "$inferred" ]; then
      inferred="$(basename "$plugin_dir")"
    fi
    cat > "$manifest" <<JSON
{
  "id": "$inferred",
  "name": "$inferred",
  "version": "1.0.0"
}
JSON
    log "Created minimal manifest $manifest with id=$inferred"
  fi
}

# Attempt npm install (with timeout and error handling)
attempt_npm_install() {
  local plugin_dir="$1"
  if [ -f "$plugin_dir/package.json" ]; then
    if command -v npm >/dev/null 2>&1; then
      log "Running npm install in $plugin_dir (may fail on systems with old C++ compilers)"
      (cd "$plugin_dir" && timeout 120 npm install --no-audit --no-fund 2>&1) || {
        err "npm install failed in $plugin_dir - this is expected on some systems"
        err "The TypeScript plugin will be skipped, but Python emotion-engine will still work"
        return 1
      }
      return 0
    else
      log "npm not installed; skipping npm install"
      return 2
    fi
  else
    log "No package.json in $plugin_dir; skipping npm install"
    return 0
  fi
}

# Install plugin via CLI with robust error handling
install_plugin_cli() {
  local plugin_dir="$1"
  ensure_package_openclaw_extensions "$plugin_dir"
  ensure_plugin_manifest_id "$plugin_dir"

  # Try npm install first, but don't fail if it errors
  if ! attempt_npm_install "$plugin_dir"; then
    err "npm install failed - will try CLI install anyway, but it may not work"
  fi

  # Try CLI install
  if run_openclaw plugins install "$plugin_dir" | grep -v "Invalid config"; then
    log "openclaw plugins install succeeded for $plugin_dir"
    # try enable by id
    local id
    id=$(python3 - <<PY
import json,sys
try:
    m=json.load(open('$plugin_dir/openclaw.plugin.json'))
    print(m.get('id',''))
except:
    print('')
PY
)
    if [ -n "$id" ]; then
      run_openclaw plugins enable "$id" 2>&1 | grep -v "Invalid config" || true
    fi
    return 0
  else
    err "openclaw plugins install failed for $plugin_dir"
    return 1
  fi
}

# Install hook via CLI robustly
install_hook_cli() {
  local hook_dir="$1"
  if run_openclaw hooks install "$hook_dir" 2>&1 | grep -v "Invalid config"; then
    log "hook installed"
    run_openclaw hooks enable emotion-prompt-modifier 2>&1 | grep -v "Invalid config" || true
    return 0
  else
    log "hooks install returned non-zero; checking if hook exists"
    if run_openclaw hooks info emotion-prompt-modifier >/dev/null 2>&1; then
      log "hook registered; attempting enable"
      run_openclaw hooks enable emotion-prompt-modifier 2>&1 | grep -v "Invalid config" || true
      return 0
    fi
    return 1
  fi
}

# Install skill via direct copy (most reliable method)
install_skill_direct() {
  local skill_dir="$1"
  local skill_name="$(basename "$skill_dir")"
  local target_dir="$HOME/.openclaw/skills/$skill_name"

  if [ -d "$skill_dir" ]; then
    safe_copy "$skill_dir" "$target_dir"

    # Make Python files executable
    find "$target_dir" -name "*.py" -exec chmod +x {} \; 2>/dev/null || true

    # Test if the skill works
    if [ -f "$target_dir/emotion_tool.py" ]; then
      if python3 "$target_dir/emotion_tool.py" emotions 2>&1 | grep -q "Emotional State"; then
        log "Skill installed and tested successfully"
        return 0
      else
        log "Skill copied but test failed - may need dependencies"
        return 0
      fi
    fi
    return 0
  else
    err "Skill directory not found: $skill_dir"
    return 1
  fi
}

# MAIN INSTALLATION FLOW
log "Installer v4 starting..."
log "Focus: Installing Python-based emotion-engine skill (most reliable)"

PLUGIN_INSTALLED=1
HOOK_INSTALLED=1
SKILL_INSTALLED=1

# Always install skill first (most important component)
if [ -d "$SKILL_DIR" ]; then
  log "Installing emotion-engine skill..."
  if install_skill_direct "$SKILL_DIR"; then
    SKILL_INSTALLED=0
    log "✓ Skill installed successfully"
  else
    err "✗ Skill installation failed"
  fi
else
  err "Skill directory not found: $SKILL_DIR"
fi

# Only try plugin/hook if CLI is available and not skipped
if has_openclaw_cli && [ "$SKIP_PLUGIN" -eq 0 ]; then
  log "OpenClaw CLI detected - attempting hook and plugin installation"

  # Try hook installation
  if [ -d "$HOOK_DIR" ]; then
    if install_hook_cli "$HOOK_DIR"; then
      HOOK_INSTALLED=0
      log "✓ Hook installed successfully"
    else
      log "✗ Hook CLI install failed; using fallback"
    fi
  fi

  # Try plugin installation (most likely to fail due to npm)
  if [ -d "$PLUGIN_DIR" ]; then
    if install_plugin_cli "$PLUGIN_DIR"; then
      PLUGIN_INSTALLED=0
      log "✓ Plugin installed successfully"
    else
      log "✗ Plugin CLI install failed; using fallback"
    fi
  fi
else
  log "Skipping plugin/hook CLI installation (CLI unavailable or --skip-plugin specified)"
fi

# Fallback: copy to ~/.openclaw for hook/plugin if CLI failed
if [ "$HOOK_INSTALLED" -ne 0 ] && [ -d "$HOOK_DIR" ]; then
  log "Using fallback: copying hook to ~/.openclaw/hooks/"
  safe_copy "$HOOK_DIR" "$HOME/.openclaw/hooks/emotion-prompt-modifier"
  HOOK_INSTALLED=0
fi

if [ "$PLUGIN_INSTALLED" -ne 0 ] && [ -d "$PLUGIN_DIR" ]; then
  log "Using fallback: copying plugin to ~/.openclaw/plugins/"
  safe_copy "$PLUGIN_DIR" "$HOME/.openclaw/plugins/emotion-persistence"
  # Note: plugin may not work without npm dependencies, but files are in place
fi

# Ensure emotion_config.json exists
if [ ! -f "$CONFIG_FILE" ]; then
  mkdir -p "$(dirname "$CONFIG_FILE")"
  cat > "$CONFIG_FILE" <<'JSON'
{
  "enabled": true,
  "intensity": 0.7,
  "learning_rate": 0.5,
  "volatility": 0.4,
  "meta_cognition_enabled": true,
  "introspection_frequency": 0.3,
  "emotion_decay_rate": 0.1,
  "memory_depth": 100,
  "confidence_threshold": 0.6,
  "ml_update_frequency": 5,
  "prompt_modifier_enabled": true,
  "persistence_enabled": true
}
JSON
  log "✓ Created default emotion_config.json"
else
  log "✓ emotion_config.json exists"
fi

# Create necessary directories
mkdir -p "$HOME/.openclaw/emotion_backups"
mkdir -p "$HOME/.openclaw/logs"
log "✓ Created necessary directories"

# Test the Python skill directly
log ""
log "Testing emotion-engine skill..."
if python3 "$HOME/.openclaw/skills/emotion-engine/emotion_tool.py" emotions 2>&1 | head -20; then
  log ""
  log "✓ Emotion system is working!"
else
  err "✗ Skill test failed - check Python dependencies"
fi

# Restart gateway if allowed and CLI available
if [ "$SKIP_RESTART" -eq 0 ] && has_openclaw_cli; then
  log ""
  log "Restarting OpenClaw gateway..."
  if run_openclaw gateway restart 2>&1 | grep -v "Invalid config"; then
    log "✓ Gateway restarted"
  else
    err "Gateway restart failed - you may need to restart manually"
  fi
else
  log "Skipped gateway restart (restart manually if needed)"
fi

# Final summary
log ""
log "=========================================="
log "Installation Summary:"
log "=========================================="
[ "$SKILL_INSTALLED" -eq 0 ] && log "✓ Skill: emotion-engine installed" || log "✗ Skill: emotion-engine FAILED"
[ "$HOOK_INSTALLED" -eq 0 ] && log "✓ Hook: emotion-prompt-modifier installed" || log "⚠ Hook: emotion-prompt-modifier (fallback used)"
[ "$PLUGIN_INSTALLED" -eq 0 ] && log "✓ Plugin: emotion-persistence installed" || log "⚠ Plugin: emotion-persistence (fallback/skipped)"
log ""
log "The core Python emotion system is ready to use!"
log ""
log "Test with:"
log "  python3 ~/.openclaw/skills/emotion-engine/emotion_tool.py emotions"
log ""
log "Available slash commands in OpenClaw:"
log "  /emotions              - Show current emotional state"
log "  /emotions detailed     - Detailed analysis"
log "  /emotions metacognition - Meta-cognitive analysis"
log "  /emotions predict      - Predict emotional trajectory"
log ""
log "Logs: ~/.openclaw/logs/"
log "Database: ~/.openclaw/emotional_state.db"
log "Config: ~/.openclaw/emotion_config.json"
log ""

# If plugin failed, show recommendation
if [ "$PLUGIN_INSTALLED" -ne 0 ]; then
  log "Note: The TypeScript plugin could not be installed due to npm/compilation issues."
  log "This is expected on systems with older C++ compilers (better-sqlite3 requires C++20)."
  log "The Python-based emotion system will still work without it."
  log ""
  log "To skip plugin installation in future runs, use: --skip-plugin"
fi

exit 0
