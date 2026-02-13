#!/bin/bash

# OpenClaw Emotional Intelligence System - Setup Script

echo "🎭 Setting up OpenClaw Emotional Intelligence System..."
echo "=================================================="

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p ~/.openclaw/emotion_backups
mkdir -p ~/.openclaw/logs

# Set permissions
echo "🔐 Setting permissions..."
chmod +x skills/emotion-engine/emotion_tool.py
chmod +x hooks/emotion-prompt-modifier/handler.ts

# Initialize database (if Python environment is available)
echo "🗄️  Initializing database..."
if command -v python3 &> /dev/null; then
    cd skills/emotion-engine
    python3 -c "
import sys
import os
sys.path.append('.')
from tools.emotion_ml_engine import EmotionEngine

try:
    engine = EmotionEngine()
    print('✅ Database initialized successfully')

    # Create initial state
    initial_state = engine.get_emotional_state()
    print(f'✅ Initial emotional state created: Session {initial_state[\"session_id\"]}')

except Exception as e:
    print(f'⚠️  Database initialization warning: {e}')
    print('   The system will initialize automatically on first use.')
"
    cd ../..
else
    echo "⚠️  Python3 not found. Database will be initialized on first use."
fi

# Check configuration
echo "⚙️  Checking configuration..."
if [ -f ~/.openclaw/emotion_config.json ]; then
    echo "✅ Emotion configuration found"
else
    echo "❌ Emotion configuration missing"
fi

if [ -f ~/.openclaw/openclaw.json ]; then
    echo "✅ OpenClaw configuration found"
else
    echo "❌ OpenClaw configuration missing"
fi

# Check Python dependencies
echo "🐍 Checking Python dependencies..."
if command -v python3 &> /dev/null; then
    if python3 -c "import numpy" 2>/dev/null; then
        echo "✅ numpy installed"
    else
        echo "⚠️  numpy missing - install with: pip install numpy"
    fi
    
    if python3 -c "import deep_translator" 2>/dev/null; then
        echo "✅ Multilingual support available (deep-translator)"
    else
        echo "💡 Optional: Install multilingual support with: pip install deep-translator langdetect"
    fi
else
    echo "⚠️  Python3 not found"
fi

# Install Node.js dependencies (if available)
echo "📦 Installing dependencies..."
if command -v npm &> /dev/null; then
    if [ -d plugins/emotion-persistence ]; then
        cd plugins/emotion-persistence
        npm install --silent
        echo "✅ Plugin dependencies installed"
        cd ../..
    fi
else
    echo "⚠️  npm not found. Node.js dependencies will need to be installed manually."
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Available commands:"
echo "  • /emotions              - Show current emotional state"
echo "  • /emotions detailed     - Detailed emotional analysis"
echo "  • /emotions history      - Show interaction history"
echo "  • /emotions metacognition - Meta-cognitive analysis"
echo "  • /emotions predict      - Predict emotional trajectory"
echo "  • /emotions config       - Show configuration"
echo ""
echo "💡 Multilingual Support: Write in any language (IT, ES, FR, DE, etc.)"
echo "   The system automatically translates for emotion analysis."
echo ""
echo "The system is now ready to use. It will learn and adapt through interactions."
echo ""
echo "To test the system:"
echo "  python3 skills/emotion-engine/emotion_tool.py emotions"
echo ""
echo "To test multilingual support:"
echo "  python3 skills/emotion-engine/test_multilingual.py"
echo ""
echo "Logs will be written to: ~/.openclaw/logs/"
echo "Database location: ~/.openclaw/emotional_state.db"
echo "Backups directory: ~/.openclaw/emotion_backups/"