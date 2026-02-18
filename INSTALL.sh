#!/usr/bin/env bash
# install_emotion_system.sh (v6 - Proactive Emotion Engine v1.3.0)
# Installer for OpenClaw Emotion System with Proactive Behavior
# https://docs.openclaw.ai/tools/plugin
#
# Version 1.3.0 Features:
# - Proactive behavior: Agent initiates conversations based on emotions
# - Auto-refresh web dashboard with real-time metrics
# - Intelligent rate limiting with escalation
# - Quiet hours and channel configuration (Telegram/WhatsApp)
#
# Key fixes:
# - package.json now includes "openclaw": { "extensions": [...] }
# - openclaw.plugin.json has proper "id" and "configSchema"
# - Plugin exports function(api) {} as required by OpenClaw
# - Removed better-sqlite3 (C++20 issue), using sqlite3 instead
#
# Usage:
#   ./install_emotion_system.sh [--skip-plugin]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKIP_PLUGIN=0

while (( "$#" )); do
  case "$1" in
    --skip-plugin) SKIP_PLUGIN=1; shift ;;
    -h|--help)
      cat <<'EOF'
OpenClaw Emotion System Installer

Usage: ./install_emotion_system.sh [--skip-plugin]

Options:
  --skip-plugin    Skip TypeScript plugin (use if npm issues)
  -h, --help       Show this help message

This installer will:
1. Install the emotion-engine skill (Python-based, core functionality)
2. Install the emotion-prompt-modifier hook (TypeScript)
3. Install the emotion-persistence plugin (TypeScript, optional)
4. Create configuration files
5. Test the installation

The Python skill is the most important component and will work standalone.
EOF
      exit 0
      ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

log() { printf "\n\033[1;34m→\033[0m %s\n" "$*"; }
success() { printf "\033[1;32m✓\033[0m %s\n" "$*"; }
warning() { printf "\033[1;33m⚠\033[0m %s\n" "$*"; }
error() { printf "\033[1;31m✗\033[0m %s\n" "$*" >&2; }

# Check if openclaw CLI is available
has_openclaw() { command -v openclaw >/dev/null 2>&1; }

log "OpenClaw Emotion System Installer v5"
echo "======================================"
echo

# Verify source directories exist
if [ ! -d "$SCRIPT_DIR/skills/emotion-engine" ]; then
  error "Skill directory not found: $SCRIPT_DIR/skills/emotion-engine"
  exit 1
fi

# Create OpenClaw directories
log "Creating directory structure..."
mkdir -p "$HOME/.openclaw/skills"
mkdir -p "$HOME/.openclaw/hooks"
mkdir -p "$HOME/.openclaw/plugins"
mkdir -p "$HOME/.openclaw/emotion_backups"
mkdir -p "$HOME/.openclaw/logs"
success "Directories created"

# Install Skill (Python-based emotion-engine)
log "Installing emotion-engine skill..."
cp -r "$SCRIPT_DIR/skills/emotion-engine" "$HOME/.openclaw/skills/"
chmod +x "$HOME/.openclaw/skills/emotion-engine/emotion_tool.py"
find "$HOME/.openclaw/skills/emotion-engine" -name "*.py" -exec chmod +x {} \; 2>/dev/null || true
success "Skill installed: emotion-engine"

# Install Python dependencies
log "Installing Python dependencies..."
SKILL_DIR="$HOME/.openclaw/skills/emotion-engine"

# Check if requirements.txt exists
if [ -f "$SKILL_DIR/requirements.txt" ]; then
  log "Found requirements.txt, installing all dependencies..."
  if python3 -m pip install -r "$SKILL_DIR/requirements.txt" --quiet 2>&1 | tail -5; then
    success "Python dependencies installed from requirements.txt"
  else
    warning "Some dependencies may have failed to install"
  fi
else
  # Manual installation of core dependencies
  log "Installing core dependency: numpy..."
  if python3 -m pip install numpy --quiet 2>&1 | tail -5; then
    success "numpy installed"
  else
    warning "numpy installation failed - ML features may not work"
  fi
  
  log "Installing multilingual support (optional)..."
  if python3 -m pip install deep-translator langdetect --quiet 2>&1 | tail -5; then
    success "Multilingual support installed (deep-translator, langdetect)"
  else
    warning "Multilingual support installation failed - will work with English only"
  fi
fi

# Test the skill
log "Testing skill..."
if python3 "$HOME/.openclaw/skills/emotion-engine/emotion_tool.py" emotions 2>&1 | grep -q "Emotional State"; then
  success "Skill test passed"
else
  warning "Skill test failed - check Python dependencies"
fi

# Install Hook (TypeScript-based emotion-prompt-modifier)
if [ -d "$SCRIPT_DIR/hooks/emotion-prompt-modifier" ]; then
  log "Installing emotion-prompt-modifier hook..."
  cp -r "$SCRIPT_DIR/hooks/emotion-prompt-modifier" "$HOME/.openclaw/hooks/"
  success "Hook installed: emotion-prompt-modifier"
else
  warning "Hook directory not found, skipping"
fi

# Install Plugin (TypeScript-based emotion-persistence) - Optional
if [ "$SKIP_PLUGIN" -eq 0 ] && [ -d "$SCRIPT_DIR/plugins/emotion-persistence" ]; then
  log "Installing emotion-persistence plugin..."

  # Copy plugin files
  cp -r "$SCRIPT_DIR/plugins/emotion-persistence" "$HOME/.openclaw/plugins/"

  # Try npm install if npm is available
  if command -v npm >/dev/null 2>&1; then
    log "Installing npm dependencies (this may take a moment)..."
    (
      cd "$HOME/.openclaw/plugins/emotion-persistence"
      if timeout 180 npm install --no-audit --no-fund --prefer-offline 2>&1 | tail -20; then
        success "npm dependencies installed"
      else
        warning "npm install failed - plugin may not function fully"
        warning "This is expected on systems with limited C++ compiler support"
      fi
    )
  else
    warning "npm not found - plugin dependencies not installed"
  fi

  success "Plugin copied: emotion-persistence"
else
  if [ "$SKIP_PLUGIN" -eq 1 ]; then
    warning "Skipping plugin installation (--skip-plugin flag)"
  else
    warning "Plugin directory not found, skipping"
  fi
fi

# Create emotion_config.json
log "Creating configuration file..."
CONFIG_FILE="$HOME/.openclaw/emotion_config.json"
if [ ! -f "$CONFIG_FILE" ]; then
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
  success "Configuration created: $CONFIG_FILE"
else
  success "Configuration exists: $CONFIG_FILE"
fi

# Show installation summary
echo
log "Installation Summary"
echo "======================================"
echo

if [ -d "$HOME/.openclaw/skills/emotion-engine" ]; then
  success "Skill: emotion-engine"
else
  error "Skill: emotion-engine FAILED"
fi

if [ -d "$HOME/.openclaw/hooks/emotion-prompt-modifier" ]; then
  success "Hook: emotion-prompt-modifier"
else
  warning "Hook: emotion-prompt-modifier (not installed)"
fi

if [ -d "$HOME/.openclaw/plugins/emotion-persistence" ]; then
  success "Plugin: emotion-persistence"
else
  warning "Plugin: emotion-persistence (not installed)"
fi

echo
log "Proactive Behavior Setup (NEW in v1.3.0)"
echo "======================================"
echo
success "Proactive emotion engine installed!"
echo
echo "The agent can now initiate spontaneous conversations based on emotions."
echo
echo "To enable:"
echo "  /emotions proactive on"
echo
echo "To configure channel (telegram/whatsapp):"
echo "  /emotions proactive channel telegram"
echo
echo "To configure quiet hours:"
echo "  /emotions proactive quiet 23:00-07:00"
echo
echo "To check status:"
echo "  /emotions proactive status"
echo

echo
log "Next Steps"
echo "======================================"
echo

if has_openclaw; then
  echo "1. Restart OpenClaw gateway:"
  echo "   openclaw gateway restart"
  echo
  echo "2. Verify installation:"
  echo "   openclaw skills list"
  echo "   openclaw hooks list"
  echo "   openclaw plugins list"
  echo
else
  echo "1. OpenClaw CLI not detected. Please:"
  echo "   - Ensure OpenClaw is installed"
  echo "   - Restart the OpenClaw service manually"
  echo
fi

echo "3. Test the emotion system:"
echo "   python3 ~/.openclaw/skills/emotion-engine/emotion_tool.py emotions"
echo
echo "4. Check multilingual support:"
echo "   python3 ~/.openclaw/skills/emotion-engine/test_multilingual.py"
echo

log "Available Slash Commands"
echo "======================================"
echo "Once OpenClaw is restarted, you can use:"
echo
echo "  /emotions              - Show current emotional state"
echo "  /emotions detailed     - Detailed emotional analysis"
echo "  /emotions history      - Show interaction history"
echo "  /emotions metacognition - Meta-cognitive analysis"
echo "  /emotions predict      - Predict emotional trajectory"
echo "  /emotions personality  - Show personality traits"
echo "  /emotions config       - Show configuration"
echo "  /emotions dashboard    - Start web dashboard (http://localhost:8081)"
echo "  /emotions proactive    - Configure proactive behavior"
echo "  /emotions proactive on - Enable spontaneous agent-initiated messages"
echo
echo "💡 Multilingual Support: Write in any language (IT, ES, FR, DE, etc.)"
echo "   The system automatically translates for emotion analysis."
echo

log "File Locations"
echo "======================================"
echo "Skill:        ~/.openclaw/skills/emotion-engine/"
echo "Hook:         ~/.openclaw/hooks/emotion-prompt-modifier/"
echo "Plugin:       ~/.openclaw/plugins/emotion-persistence/"
echo "Config:       ~/.openclaw/emotion_config.json"
echo "Database:     ~/.openclaw/emotional_state.db"
echo "Backups:      ~/.openclaw/emotion_backups/"
echo "Logs:         ~/.openclaw/logs/"
echo

success "Installation complete!"
echo
warning "IMPORTANT: You must restart OpenClaw for changes to take effect"

if has_openclaw; then
  echo
  read -p "Restart OpenClaw gateway now? (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    log "Restarting gateway..."
    if openclaw gateway restart; then
      success "Gateway restarted successfully"
    else
      error "Gateway restart failed - try manually"
    fi
  fi
fi

exit 0
