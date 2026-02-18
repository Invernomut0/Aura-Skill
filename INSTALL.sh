#!/usr/bin/env bash
#
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  🎭 OPENCLAW EMOTION SYSTEM INSTALLER v1.4.0                              ║
# ║  Proactive Emotion Engine with AI-Driven Conversations                    ║
# ║  https://docs.openclaw.ai/tools/plugin                                    ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
#
# ┌─────────────────────────────────────────────────────────────────────────┐
# │ FEATURES v1.4.0:                                                        │
# │   ✨ Proactive behavior: Agent initiates conversations                  │
# │   📊 Real-time web dashboard with auto-refresh                          │
# │   🧠 Intelligent rate limiting with escalation                          │
# │   🌙 Quiet hours and channel configuration                              │
# └─────────────────────────────────────────────────────────────────────────┘
#
# Usage: ./INSTALL.sh [--skip-plugin]

set -euo pipefail

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION & SETUP
# ═══════════════════════════════════════════════════════════════════════════

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKIP_PLUGIN=0

# Colors and formatting
readonly RESET='\033[0m'
readonly BOLD='\033[1m'
readonly DIM='\033[2m'
readonly ITALIC='\033[3m'
readonly UNDERLINE='\033[4m'

# Color palette (Lobster theme)
readonly PRIMARY='\033[38;2;255;90;45m'      # #FF5A2D - Accent
readonly PRIMARY_BRIGHT='\033[38;2;255;122;61m' # #FF7A3D - Accent bright
readonly SUCCESS='\033[38;2;47;191;113m'     # #2FBF71 - Success
readonly WARNING='\033[38;2;255;176;32m'     # #FFB020 - Warning
readonly ERROR='\033[38;2;226;61;45m'        # #E23D2D - Error
readonly INFO='\033[38;2;255;138;91m'        # #FF8A5B - Info
readonly MUTED='\033[38;2;139;127;119m'      # #8B7F77 - Muted
readonly CYAN='\033[38;2;86;182;194m'        # #56B6C2

# Box characters
readonly BOX_TL='┌'
readonly BOX_TR='┐'
readonly BOX_BL='└'
readonly BOX_BR='┘'
readonly BOX_H='─'
readonly BOX_V='│'
readonly BOX_T='┬'
readonly BOX_B='┴'
readonly BOX_L='├'
readonly BOX_R='┤'
readonly BOX_C='┼'

# ═══════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

print_banner() {
    local term_width=$(tput cols 2>/dev/null || echo 80)
    local width=78
    [ $term_width -lt $width ] && width=$term_width
    
    printf "\n"
    printf "${PRIMARY}"
    printf "  ╔"
    for ((i=0; i<$width-2; i++)); do printf "═"; done
    printf "╗\n"
    
    printf "  ║%$((width-2))s║\n" " "
    printf "  ║${BOLD}  🎭 OPENCLAW EMOTION SYSTEM${RESET}${PRIMARY}%$((width-34))s║\n" " "
    printf "  ║${PRIMARY_BRIGHT}${ITALIC}     Living Personality Engine v1.4.0${RESET}${PRIMARY}%$((width-40))s║\n" " "
    printf "  ║%$((width-2))s║\n" " "
    printf "  ║${MUTED}     Your AI with emotional intelligence and proactive behavior${RESET}${PRIMARY}%$((width-67))s║\n" " "
    printf "  ║%$((width-2))s║\n" " "
    
    printf "  ╚"
    for ((i=0; i<$width-2; i++)); do printf "═"; done
    printf "╝\n"
    printf "${RESET}\n"
}

print_box() {
    local title="$1"
    local content="$2"
    local color="${3:-$PRIMARY}"
    local term_width=$(tput cols 2>/dev/null || echo 80)
    local width=76
    [ $term_width -lt $width ] && width=$term_width
    
    printf "${color}"
    printf "  ${BOX_TL}"
    for ((i=0; i<$width-4; i++)); do printf "${BOX_H}"; done
    printf "${BOX_TR}\n"
    
    printf "  ${BOX_V}${BOLD} %s${RESET}${color}%$((width-5-${#title}))s${BOX_V}\n" "$title" " "
    
    printf "  ${BOX_L}"
    for ((i=0; i<$width-4; i++)); do printf "${BOX_H}"; done
    printf "${BOX_R}\n"
    
    while IFS= read -r line; do
        printf "  ${BOX_V} %s${color}%$((width-5-${#line}))s${BOX_V}\n" "$line" " "
    done <<< "$content"
    
    printf "  ${BOX_BL}"
    for ((i=0; i<$width-4; i++)); do printf "${BOX_H}"; done
    printf "${BOX_BR}\n"
    printf "${RESET}\n"
}

print_section() {
    local title="$1"
    local color="${2:-$PRIMARY}"
    local term_width=$(tput cols 2>/dev/null || echo 80)
    local width=76
    [ $term_width -lt $width ] && width=$term_width
    
    printf "\n"
    printf "${color}"
    printf "  ${BOX_L}${BOX_H}${BOX_H} ${BOLD}%s${RESET}${color} " "$title"
    local title_len=$((6 + ${#title}))
    for ((i=$title_len; i<$width-2; i++)); do printf "${BOX_H}"; done
    printf "${BOX_R}\n"
    printf "${RESET}"
}

log() {
    printf "\n${CYAN}${BOLD}  ▶ ${RESET}${BOLD}%s${RESET}\n" "$*"
}

success() {
    printf "${SUCCESS}  ✓ ${RESET}%s\n" "$*"
}

warning() {
    printf "${WARNING}  ⚠ ${RESET}%s\n" "$*"
}

error() {
    printf "${ERROR}  ✗ ${RESET}%s\n" "$*" >&2
}

info() {
    printf "${INFO}  ℹ ${RESET}%s\n" "$*"
}

progress_start() {
    printf "${CYAN}  ⏳ ${RESET}%s..." "$*"
}

progress_done() {
    printf "\r${SUCCESS}  ✓ ${RESET}%s\n" "$*"
}

# ═══════════════════════════════════════════════════════════════════════════
# COMMAND LINE PARSING
# ═══════════════════════════════════════════════════════════════════════════

while (( "$#" )); do
    case "$1" in
        --skip-plugin) SKIP_PLUGIN=1; shift ;;
        -h|--help)
            print_banner
            cat <<'EOF'

  USAGE:
    ./INSTALL.sh [--skip-plugin]

  OPTIONS:
    --skip-plugin    Skip TypeScript plugin (use if npm issues)
    -h, --help       Show this help message

  COMPONENTS INSTALLED:
    1. emotion-engine skill (Python - core functionality)
    2. emotion-prompt-modifier hook (TypeScript)
    3. emotion-persistence plugin (TypeScript, optional)
    4. Configuration files and database

  The Python skill is the most important component and works standalone.

EOF
            exit 0
            ;;
        *) 
            error "Unknown argument: $1"
            info "Use -h or --help for usage information"
            exit 1 
            ;;
    esac
done

# ═══════════════════════════════════════════════════════════════════════════
# SYSTEM CHECKS
# ═══════════════════════════════════════════════════════════════════════════

has_openclaw() { command -v openclaw >/dev/null 2>&1; }
has_python3() { command -v python3 >/dev/null 2>&1; }
has_npm() { command -v npm >/dev/null 2>&1; }

# ═══════════════════════════════════════════════════════════════════════════
# MAIN INSTALLATION
# ═══════════════════════════════════════════════════════════════════════════

print_banner

# Pre-flight checks
print_section "PRE-FLIGHT CHECKS"

if ! has_python3; then
    error "Python 3 is required but not installed"
    exit 1
fi
success "Python 3 detected"

if has_openclaw; then
    success "OpenClaw CLI detected"
    OPENCLAW_VERSION=$(openclaw --version 2>/dev/null | head -1 || echo "unknown")
    info "Version: $OPENCLAW_VERSION"
else
    warning "OpenClaw CLI not detected"
    info "The skill will be installed but won't function until OpenClaw is installed"
fi

if [ ! -d "$SCRIPT_DIR/skills/emotion-engine" ]; then
    error "Skill directory not found: $SCRIPT_DIR/skills/emotion-engine"
    exit 1
fi
success "Source directory verified"

# Create directory structure
print_section "DIRECTORY STRUCTURE"

progress_start "Creating OpenClaw directories"
mkdir -p "$HOME/.openclaw/skills"
mkdir -p "$HOME/.openclaw/hooks"
mkdir -p "$HOME/.openclaw/plugins"
mkdir -p "$HOME/.openclaw/emotion_backups"
mkdir -p "$HOME/.openclaw/logs"
progress_done "Directories created"

info "  → ~/.openclaw/skills/"
info "  → ~/.openclaw/hooks/"
info "  → ~/.openclaw/plugins/"
info "  → ~/.openclaw/logs/"
info "  → ~/.openclaw/emotion_backups/"

# Install Skill
print_section "INSTALLING EMOTION-ENGINE SKILL"

progress_start "Copying skill files"
cp -r "$SCRIPT_DIR/skills/emotion-engine" "$HOME/.openclaw/skills/"
chmod +x "$HOME/.openclaw/skills/emotion-engine/emotion_tool.py"
find "$HOME/.openclaw/skills/emotion-engine" -name "*.py" -exec chmod +x {} \; 2>/dev/null || true
progress_done "Skill installed: emotion-engine"

# Install Python dependencies
print_section "PYTHON DEPENDENCIES"

SKILL_DIR="$HOME/.openclaw/skills/emotion-engine"

if [ -f "$SKILL_DIR/requirements.txt" ]; then
    log "Installing from requirements.txt..."
    if python3 -m pip install -r "$SKILL_DIR/requirements.txt" --quiet 2>&1 | tail -5; then
        success "All dependencies installed"
    else
        warning "Some dependencies may have failed"
    fi
else
    log "Installing core dependencies..."
    
    progress_start "Installing numpy"
    if python3 -m pip install numpy --quiet 2>&1 | tail -1; then
        progress_done "numpy installed"
    else
        warning "numpy installation failed - ML features may be limited"
    fi
    
    progress_start "Installing multilingual support"
    if python3 -m pip install deep-translator langdetect --quiet 2>&1 | tail -1; then
        progress_done "Multilingual support installed"
        info "Languages supported: IT, ES, FR, DE, PT, RU, JA, ZH, and more"
    else
        warning "Multilingual support failed - English only mode"
    fi
fi

# Test the skill
print_section "TESTING INSTALLATION"

progress_start "Testing emotion engine"
if python3 "$HOME/.openclaw/skills/emotion-engine/emotion_tool.py" emotions 2>&1 | grep -q "Emotional State"; then
    progress_done "Skill test passed"
else
    warning "Skill test encountered issues"
    info "Dependencies may need manual installation"
fi

# Install Hook
print_section "INSTALLING HOOK"

if [ -d "$SCRIPT_DIR/hooks/emotion-prompt-modifier" ]; then
    progress_start "Installing emotion-prompt-modifier hook"
    cp -r "$SCRIPT_DIR/hooks/emotion-prompt-modifier" "$HOME/.openclaw/hooks/"
    progress_done "Hook installed"
else
    warning "Hook directory not found, skipping"
fi

# Install Plugin
print_section "INSTALLING PLUGIN"

if [ "$SKIP_PLUGIN" -eq 0 ] && [ -d "$SCRIPT_DIR/plugins/emotion-persistence" ]; then
    progress_start "Copying emotion-persistence plugin"
    cp -r "$SCRIPT_DIR/plugins/emotion-persistence" "$HOME/.openclaw/plugins/"
    progress_done "Plugin copied"
    
    if has_npm; then
        log "Installing npm dependencies..."
        (
            cd "$HOME/.openclaw/plugins/emotion-persistence"
            if timeout 180 npm install --no-audit --no-fund --prefer-offline 2>&1 | tail -10; then
                success "npm dependencies installed"
            else
                warning "npm install failed - plugin may have limited functionality"
                info "This is expected on systems with limited C++ compiler support"
            fi
        )
    else
        warning "npm not found - plugin dependencies not installed"
    fi
else
    if [ "$SKIP_PLUGIN" -eq 1 ]; then
        info "Skipped (--skip-plugin flag)"
    else
        warning "Plugin directory not found"
    fi
fi

# Create or update configuration
print_section "CONFIGURATION"

CONFIG_FILE="$HOME/.openclaw/emotion_config.json"

# Default configuration
DEFAULT_CONFIG='{
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
}'

check_and_update_config() {
    local config_file="$1"
    local temp_file="$config_file.tmp"
    local needs_update=false
    local missing_fields=()
    
    # Required fields
    local required_fields=(
        "enabled"
        "intensity"
        "learning_rate"
        "volatility"
        "meta_cognition_enabled"
        "introspection_frequency"
        "emotion_decay_rate"
        "memory_depth"
        "confidence_threshold"
        "ml_update_frequency"
        "prompt_modifier_enabled"
        "persistence_enabled"
    )
    
    # Check each required field
    for field in "${required_fields[@]}"; do
        if ! grep -q "\"$field\"" "$config_file" 2>/dev/null; then
            missing_fields+=("$field")
            needs_update=true
        fi
    done
    
    if [ "$needs_update" = true ]; then
        log "Aggiornamento configurazione: campi mancanti rilevati"
        for field in "${missing_fields[@]}"; do
            info "  + $field"
        done
        
        # Read existing config and add missing fields
        python3 - "$config_file" <<'PYTHON_SCRIPT'
import json
import sys

config_file = sys.argv[1]

try:
    with open(config_file, 'r') as f:
        config = json.load(f)
except (json.JSONDecodeError, FileNotFoundError):
    config = {}

defaults = {
    "enabled": True,
    "intensity": 0.7,
    "learning_rate": 0.5,
    "volatility": 0.4,
    "meta_cognition_enabled": True,
    "introspection_frequency": 0.3,
    "emotion_decay_rate": 0.1,
    "memory_depth": 100,
    "confidence_threshold": 0.6,
    "ml_update_frequency": 5,
    "prompt_modifier_enabled": True,
    "persistence_enabled": True
}

for key, value in defaults.items():
    if key not in config:
        config[key] = value

with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)

print("Configuration updated successfully")
PYTHON_SCRIPT
        
        if [ $? -eq 0 ]; then
            progress_done "Configurazione aggiornata"
        else
            warning "Errore aggiornamento configurazione, ricreazione..."
            echo "$DEFAULT_CONFIG" > "$config_file"
            progress_done "Configurazione ricreata"
        fi
    else
        info "Configurazione aggiornata"
    fi
}

if [ ! -f "$CONFIG_FILE" ]; then
    progress_start "Creazione emotion_config.json"
    echo "$DEFAULT_CONFIG" > "$CONFIG_FILE"
    progress_done "Configurazione creata"
else
    info "Configurazione esistente rilevata"
    check_and_update_config "$CONFIG_FILE"
fi

# ═══════════════════════════════════════════════════════════════════════════
# INSTALLATION SUMMARY
# ═══════════════════════════════════════════════════════════════════════════

print_section "INSTALLATION SUMMARY"

printf "\n"

# Skill status
if [ -d "$HOME/.openclaw/skills/emotion-engine" ]; then
    success "${BOLD}emotion-engine${RESET}     Python skill (core)"
else
    error "${BOLD}emotion-engine${RESET}     NOT INSTALLED"
fi

# Hook status
if [ -d "$HOME/.openclaw/hooks/emotion-prompt-modifier" ]; then
    success "${BOLD}prompt-modifier${RESET}  TypeScript hook"
else
    warning "${BOLD}prompt-modifier${RESET}  Not installed"
fi

# Plugin status
if [ -d "$HOME/.openclaw/plugins/emotion-persistence" ]; then
    success "${BOLD}persistence${RESET}      TypeScript plugin"
else
    warning "${BOLD}persistence${RESET}      Not installed"
fi

# ═══════════════════════════════════════════════════════════════════════════
# PROACTIVE FEATURES
# ═══════════════════════════════════════════════════════════════════════════

print_section "🚀 LIVING PERSONALITY (NEW v1.4.0)"

print_box "Agent-Initiated Conversations" "Your AI can now start conversations spontaneously
based on emotional states and context.

Enable proactive mode:
  /emotions proactive on

Set your channel:
  /emotions proactive channel telegram
  /emotions proactive channel whatsapp

Configure quiet hours:
  /emotions proactive quiet 23:00-07:00" "$PRIMARY_BRIGHT"

# ═══════════════════════════════════════════════════════════════════════════
# NEXT STEPS
# ═══════════════════════════════════════════════════════════════════════════

print_section "NEXT STEPS"

if has_openclaw; then
    print_box "Restart Required" "Restart OpenClaw to activate:

  openclaw gateway restart

Verify installation:
  openclaw skills list
  openclaw hooks list
  openclaw plugins list" "$SUCCESS"
else
    print_box "OpenClaw Required" "OpenClaw CLI not detected.

Please install OpenClaw first:
  https://docs.openclaw.ai/start/getting-started

Then restart the service manually." "$WARNING"
fi

# Test commands
print_section "TEST COMMANDS"

printf "  ${CYAN}Test emotion system:${RESET}\n"
printf "    python3 ~/.openclaw/skills/emotion-engine/emotion_tool.py emotions\n\n"

printf "  ${CYAN}Test multilingual support:${RESET}\n"
printf "    python3 ~/.openclaw/skills/emotion-engine/test_multilingual.py\n\n"

# ═══════════════════════════════════════════════════════════════════════════
# SLASH COMMANDS
# ═══════════════════════════════════════════════════════════════════════════

print_section "AVAILABLE COMMANDS"

printf "\n  ${PRIMARY_BRIGHT}Emotion Commands:${RESET}\n"
printf "    /emotions              Show current emotional state\n"
printf "    /emotions detailed     Detailed emotional analysis\n"
printf "    /emotions history      Show interaction history\n"
printf "    /emotions metacognition Meta-cognitive analysis\n"
printf "    /emotions predict      Predict emotional trajectory\n"
printf "    /emotions personality  Show personality traits\n"
printf "    /emotions config       Show configuration\n"
printf "    /emotions dashboard    Start web dashboard (${UNDERLINE}http://localhost:8081${RESET})\n"
printf "    /emotions proactive    Configure proactive behavior\n"

printf "\n  ${INFO}🌍 Multilingual Support:${RESET} Write in any language\n"
printf "     Italian, Spanish, French, German, Portuguese, etc.\n"
printf "     The system automatically translates for emotion analysis.\n"

# ═══════════════════════════════════════════════════════════════════════════
# FILE LOCATIONS
# ═══════════════════════════════════════════════════════════════════════════

print_section "FILE LOCATIONS"

printf "\n"
printf "  ${DIM}Skill${RESET}        ~/.openclaw/skills/emotion-engine/\n"
printf "  ${DIM}Hook${RESET}         ~/.openclaw/hooks/emotion-prompt-modifier/\n"
printf "  ${DIM}Plugin${RESET}       ~/.openclaw/plugins/emotion-persistence/\n"
printf "  ${DIM}Config${RESET}       ~/.openclaw/emotion_config.json\n"
printf "  ${DIM}Database${RESET}     ~/.openclaw/emotional_state.db\n"
printf "  ${DIM}Backups${RESET}      ~/.openclaw/emotion_backups/\n"
printf "  ${DIM}Logs${RESET}         ~/.openclaw/logs/\n"

# ═══════════════════════════════════════════════════════════════════════════
# FINAL MESSAGE
# ═══════════════════════════════════════════════════════════════════════════

printf "\n"
printf "${SUCCESS}"
printf "  ╔══════════════════════════════════════════════════════════════════════════╗\n"
printf "  ║                                                                          ║\n"
printf "  ║   🎭 INSTALLATION COMPLETE!                                              ║\n"
printf "  ║                                                                          ║\n"
printf "  ║   Your AI now has emotional intelligence and proactive capabilities.     ║\n"
printf "  ║   Restart OpenClaw to begin the emotional journey!                       ║\n"
printf "  ║                                                                          ║\n"
printf "  ╚══════════════════════════════════════════════════════════════════════════╝\n"
printf "${RESET}\n"

# Restart prompt
if has_openclaw; then
    printf "\n"
    printf "  ${WARNING}${BOLD}⚠ IMPORTANT:${RESET} Restart required for changes to take effect\n\n"
    
    read -p "  Restart OpenClaw gateway now? [Y/n] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        log "Restarting gateway..."
        if openclaw gateway restart 2>/dev/null; then
            success "Gateway restarted successfully!"
            info "The emotion system is now active"
        else
            error "Gateway restart failed"
            info "Try manually: openclaw gateway restart"
        fi
    else
        info "Remember to restart manually: openclaw gateway restart"
    fi
else
    printf "\n  ${WARNING}${BOLD}⚠ IMPORTANT:${RESET} You must install OpenClaw for the system to work\n"
fi

printf "\n"
exit 0
