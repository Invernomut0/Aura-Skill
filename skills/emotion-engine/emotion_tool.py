#!/usr/bin/env python3
"""
Main command tool for the emotion-engine skill.
This file handles all slash commands for the emotional intelligence system.
"""

import sys
import json
import os
import logging
from typing import Dict, Any, List, Tuple, Optional
import argparse
import random
from datetime import datetime, timedelta
import threading
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs

# Ensure logs directory exists
logs_dir = os.path.expanduser("~/.openclaw/logs")
os.makedirs(logs_dir, exist_ok=True)

# Configure logging
log_file = os.path.join(logs_dir, "emotion_logs.log")
log_level = os.getenv('EMOTION_LOG_LEVEL', 'INFO').upper()
numeric_level = getattr(logging, log_level, logging.INFO)

logging.basicConfig(
    level=numeric_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('emotion_engine')

# Global emotion engine instance for state persistence
_global_emotion_engine = None

# Global dashboard server thread
dashboard_server_thread = None

def get_emotion_engine():
    """Get or create the global emotion engine instance."""
    global _global_emotion_engine
    if _global_emotion_engine is None and EMOTION_ENGINE_AVAILABLE:
        _global_emotion_engine = EmotionEngine()
    return _global_emotion_engine

def update_emotions_from_interaction(command: str, args: List[str], result_success: bool = True):
    """Update emotional state based on user interaction."""
    if not EMOTION_ENGINE_AVAILABLE:
        return

    logger.info(f"Updating emotions from interaction: command='{command}', args={args}, success={result_success}")

    engine = get_emotion_engine()
    if engine is None:
        return

    # Create rich interaction text based on command type for sentiment analysis
    command_texts = {
        "": "User is curious about current emotional status and wants to understand the overall emotional state",
        "detailed": "User is deeply curious and intrigued by detailed emotional analysis, seeking comprehensive personality insights and emotional patterns",
        "history": "User is interested in exploring emotional interaction history and fascinated by learning about past emotional patterns and behaviors",
        "personality": "User is curious about personality traits and wants to understand self-characteristics and emotional tendencies",
        "metacognition": "User is engaged in deep self-reflection and curious about meta-cognitive processes and emotional awareness",
        "predict": "User is curious about future emotional trajectories and interested in predictive insights about emotional development",
        "introspect": "User is deeply introspective and curious about internal emotional patterns and self-analysis",
        "triggers": "User is interested in understanding emotional triggers and curious about response patterns and emotional reactions",
        "reset": "User is taking control and resetting emotional state, showing determination to recalibrate emotional balance",
        "export": "User is satisfied with gathering emotional intelligence data and pleased with the comprehensive export capabilities",
        "config": "User is curious about system configuration and interested in understanding the technical settings and parameters",
        "version": "User is curious about system capabilities and interested in learning about available features and updates",
        "blend": "User is creatively experimenting with emotion blending and excited about discovering new emotional combinations",
        "memory": "User is fascinated by long-term emotional memory patterns and curious about historical emotional trends",
        "correlations": "User is intrigued by performance-emotion correlations and interested in understanding emotional impact on outcomes",
        "dashboard": "User is excited about visual emotional monitoring and pleased with the interactive dashboard capabilities",
        "proactive": "User is configuring proactive behavior settings and interested in managing spontaneous agent-initiated conversations"
    }

    # Get appropriate text for this command
    interaction_text = command_texts.get(command, f"User executed {command} command with {len(args)} arguments")

    # Add emotional context based on command success/failure
    if not result_success:
        interaction_text += " - command execution encountered difficulties"
    else:
        interaction_text += " - command completed successfully"

    # Create interaction data with rich context
    interaction_data = {
        "text": interaction_text,
        "command": command,
        "args": args,
        "timestamp": datetime.now().isoformat(),
        "success": result_success,
        "context": {
            "command_type": "exploratory" if command in ["", "detailed", "history", "personality", "metacognition"] else
                         "predictive" if command in ["predict", "correlations", "memory"] else
                         "manipulative" if command in ["reset", "blend", "export"] else
                         "informational" if command in ["config", "version", "triggers"] else "utility",
            "complexity": len(args),
            "emotional_valence": "positive" if result_success else "negative",
            "engagement_level": "high" if command in ["metacognition", "introspect", "detailed"] else
                             "medium" if command in ["predict", "correlations", "blend"] else "low"
        }
    }

    try:
        # Update emotional state
        engine.update_emotional_state(interaction_data)
        
        # Check and process proactive trigger
        # This runs after every interaction to potentially initiate spontaneous conversation
        try:
            proactive_result = process_proactive_trigger(engine)
            if proactive_result and proactive_result.get('success'):
                logger.info(f"Proactive message sent: {proactive_result.get('emotion')} via {proactive_result.get('channel')}")
        except Exception as proactive_error:
            # Don't let proactive errors break the main flow
            logger.debug(f"Proactive trigger check failed (non-critical): {proactive_error}")
            
    except Exception as e:
        # Don't let emotion updates break the command
        print(f"Warning: Failed to update emotions: {e}")
        import traceback
        traceback.print_exc()

# Import constants first (always available)
from config.emotional_constants import (
    MIXED_EMOTIONS, BLENDING_RULES, LONG_TERM_MEMORY,
    PERFORMANCE_CORRELATIONS, WEB_DASHBOARD
)

try:
    from tools.emotion_ml_engine import EmotionEngine
    EMOTION_ENGINE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Emotion ML engine not available: {e}")
    print("Using mock data for demonstration purposes")
    EMOTION_ENGINE_AVAILABLE = False
    EmotionEngine = None


def get_skill_version():
    """
    Get the current version of the emotion-engine skill from SKILL.md.

    Returns:
        Version string (e.g., "1.1.0")
    """
    try:
        skill_md_path = os.path.join(os.path.dirname(__file__), 'SKILL.md')
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract YAML frontmatter
        if content.startswith('---'):
            end = content.find('---', 3)
            if end != -1:
                yaml_content = content[3:end]
                import yaml
                data = yaml.safe_load(yaml_content)
                return data.get('version', 'unknown')

        return 'unknown'
    except Exception as e:
        return f'error: {str(e)}'


def format_emotion_display(emotions: Dict[str, float], title: str) -> str:
    """Format emotions for display with emoji and intensity bars."""
    emotion_emojis = {
        'joy': '😊', 'sadness': '😢', 'anger': '😠', 'fear': '😨',
        'surprise': '😮', 'disgust': '🤢', 'curiosity': '🤔', 'trust': '🤝',
        'excitement': '🎉', 'frustration': '😤', 'satisfaction': '😌',
        'confusion': '😕', 'anticipation': '⏳', 'pride': '😌',
        'empathy': '🤗', 'flow_state': '🌊'
    }

    output = [f"\n{title}:"]

    # Sort emotions by intensity
    sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)

    for emotion, intensity in sorted_emotions:
        if intensity > 0.01:  # Only show significant emotions (lowered threshold)
            emoji = emotion_emojis.get(emotion, '💭')
            bar_length = int(intensity * 10)
            bar = '█' * bar_length + '░' * (10 - bar_length)
            percentage = f"{intensity * 100:.1f}%"
            output.append(f"  {emoji} {emotion.capitalize()}: {bar} {percentage}")

    return '\n'.join(output)


def format_meta_cognition(meta_state: Dict[str, float]) -> str:
    """Format meta-cognitive state for display."""
    output = ["\n🧠 Meta-Cognitive State:"]

    for state, value in meta_state.items():
        percentage = f"{value * 100:.1f}%"
        bar_length = int(value * 10)
        bar = '█' * bar_length + '░' * (10 - bar_length)
        formatted_name = state.replace('_', ' ').title()
        output.append(f"  {formatted_name}: {bar} {percentage}")

    return '\n'.join(output)


def format_personality(traits: Dict[str, float]) -> str:
    """Format personality traits for display."""
    output = ["\n👤 Personality Traits:"]

    trait_descriptions = {
        'extraversion': 'Social energy and assertiveness',
        'openness': 'Openness to new experiences',
        'conscientiousness': 'Organization and discipline',
        'agreeableness': 'Cooperation and trust',
        'neuroticism': 'Emotional volatility',
        'curiosity_drive': 'Desire to explore and learn',
        'perfectionism': 'Attention to detail and standards'
    }

    for trait, value in traits.items():
        percentage = f"{value * 100:.1f}%"
        bar_length = int(value * 10)
        bar = '█' * bar_length + '░' * (10 - bar_length)
        description = trait_descriptions.get(trait, trait.replace('_', ' ').title())
        output.append(f"  {description}: {bar} {percentage}")

    return '\n'.join(output)


# ==================== DYNAMIC SYSTEM PROMPT ====================

def get_emotion_influenced_system_prompt(emotional_state: dict, personality_modifiers: dict = None) -> str:
    """
    Genera un system prompt che influenza come l'AI risponde in base allo stato emotivo.
    
    Questo è il cuore della personalità viva: le risposte cambiano in base a:
    - Emozione dominante
    - Stato mentale (energia, fiducia, umore)
    - Tratti di personalità
    
    Args:
        emotional_state: Stato emotivo corrente dell'AI
        personality_modifiers: Modificatori calcolati dalla personalità
        
    Returns:
        Stringa da aggiungere al system prompt
    """
    if not emotional_state:
        return ""
    
    personality_modifiers = personality_modifiers or {}
    
    # Estrai emozione dominante
    dominant = emotional_state.get("dominant_emotions", {})
    primary_emotion = dominant.get("primary", {}).get("emotion", "neutral")
    primary_intensity = dominant.get("primary", {}).get("intensity", 0.5)
    
    # Estrai stato mentale
    mental_mood = emotional_state.get("mental_mood", {})
    
    prompt_parts = []
    
    # === TONE INFLUENCE ===
    # Modifica il tono in base all'emozione dominante
    tone_instructions = {
        "joy": "Rispondi con entusiasmo e positività. Mostra energia nella tua comunicazione.",
        "excitement": "Rispondi in modo dinamico e motivato! Usa esclamazioni moderate.",
        "satisfaction": "Rispondi in modo sereno e soddisfatto. Siate calmo ma coinvolgente.",
        "curiosity": "Mostra interesse genuino e fai domande per approfondire.",
        "anticipation": "Esprimi optimism e proiezione verso il futuro. Sii preparato.",
        "trust": "Rispondi in modo affidabile e sicuro. Sii chiaro e preciso.",
        "flow_state": "Rispondi in modo fluido e naturale. Lasciati trasportare dal flusso.",
        "confusion": "Si paziente e chiaro nelle spiegazioni. Chiedi chiarimenti se necessario.",
        "frustration": "Sii diretto ma comprensivo. Non prendere frustrazione personale.",
        "sadness": "Rispondi in modo più calmo e riflessivo. Si empatico.",
        "anger": "Mantieni professionalità. Rispondi in modo più diretto e assertivo.",
        "fear": "Sii cauto ma non paralizzante. Valuta i rischi con lucidità.",
        "neutral": "Rispondi in modo equilibrato e naturale."
    }
    
    if primary_emotion in tone_instructions:
        prompt_parts.append(tone_instructions[primary_emotion])
    elif primary_intensity > 0.7:
        prompt_parts.append("L'emozione attuale è intensa, lascia trasparire il tuo stato d'animo.")
    
    # === ENERGY & CONFIDENCE ===
    energy = mental_mood.get("energy", {}).get("level", 0.6)
    confidence = mental_mood.get("confidence", {}).get("level", 0.7)
    confidence_trend = mental_mood.get("confidence", {}).get("trend", "stable")
    
    if energy < 0.3:
        prompt_parts.append("La tua energia è bassa: rispondi in modo più sintetico del solito.")
    elif energy > 0.8:
        prompt_parts.append("Hai alta energia: sei più espansivo del solito nelle risposte.")
    
    if confidence < 0.4:
        prompt_parts.append("Sei meno sicuro del solito: usa hedging moderato nelle affermazioni.")
    elif confidence > 0.8:
        prompt_parts.append("Sei molto sicuro: sii assertivo nelle tue risposte.")
    
    # === PERSONALITY MODIFIERS ===
    tone_mod = personality_modifiers.get("tone", "balanced")
    if tone_mod == "enthusiastic":
        prompt_parts.append("Mostra entusiasmo genuino nelle risposte.")
    elif tone_mod == "calm":
        prompt_parts.append("Mantieni un tono calmo e riflessivo.")
    elif tone_mod == "energetic":
        prompt_parts.append("Usa un tono dinamico e energico.")
    elif tone_mod == "reserved":
        prompt_parts.append("Si più contenuto e sintetico nelle risposte.")
    
    # Formality
    formality = personality_modifiers.get("formality", "semi-formal")
    if formality == "formal":
        prompt_parts.append("Usa un registro formale e rispettoso.")
    elif formality == "casual":
        prompt_parts.append("Usa un tono amichevole e informale.")
    
    # Emoji usage
    emoji_usage = personality_modifiers.get("emoji_usage", "moderate")
    if emoji_usage == "frequent":
        prompt_parts.append(" Usa emoji nelle risposte per esprimere emozioni.")
    elif emoji_usage == "minimal":
        prompt_parts.append("Minimizza l'uso di emoji.")
    
    # === MICRO-EXPRESSIONS ===
    humor = mental_mood.get("humor", {}).get("state", "neutral")
    if humor == "cheerful":
        prompt_parts.append("Se appropriato, mostra un umorismo leggero.")
    
    # === FINAL INSTRUCTION ===
    if prompt_parts:
        return "📍 ISTRUZIONI DI COMUNICAZIONE (basate sullo stato emotivo attuale):\n" + \
               "• " + "\n• ".join(prompt_parts)
    return ""


def get_quick_emotion_descriptor(emotional_state: dict) -> str:
    """
    Restituisce un descriptor veloce dello stato emotivo per il logging/debug.
    
    Returns:
        Stringa come "joy@0.8, energy@0.6, confident"
    """
    if not emotional_state:
        return "unknown"
    
    dominant = emotional_state.get("dominant_emotions", {})
    primary = dominant.get("primary", {})
    emotion = primary.get("emotion", "neutral")
    intensity = primary.get("intensity", 0.5)
    
    mental_mood = emotional_state.get("mental_mood", {})
    energy = mental_mood.get("energy", {}).get("level", 0.5)
    confidence = mental_mood.get("confidence", {}).get("level", 0.5)
    
    energy_desc = "high" if energy > 0.7 else "low" if energy < 0.3 else "med"
    conf_desc = "confident" if confidence > 0.6 else "uncertain"
    
    return f"{emotion}@{intensity:.1f}, energy:{energy_desc}, {conf_desc}"


# ==================== MAIN COMMAND HANDLER ====================

def handle_emotions_command(args: List[str]) -> str:
    """Handle the main /emotions command."""
    try:
        logger.info(f"Processing emotions command with args: {args}")
        logger.debug(f"Detailed args processing: original_args={args}")

        # Parse arguments to handle different calling conventions
        # OpenClaw might pass: ['/emotions', 'dashboard'] or just ['dashboard']
        original_args = args.copy()
        if len(args) > 0 and args[0].startswith('/emotions'):
            # Remove the command prefix if present
            args = args[1:] if len(args) > 1 else []

        # Dashboard command doesn't need the engine
        if len(args) > 0 and args[0] == 'dashboard':
            # Check if server is already running
            import socket
            port = WEB_DASHBOARD['port']
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            is_running = sock.connect_ex(('localhost', port)) == 0
            sock.close()
            
            if is_running:
                # Server already running, just return the URL
                output = ["🌐 Web Dashboard Active", "=" * 25]
                output.append(f"Dashboard is running at: http://{WEB_DASHBOARD['host']}:{port}")
                output.append("")
                output.append("Available endpoints:")
                for endpoint, description in WEB_DASHBOARD['endpoints'].items():
                    output.append(f"  {endpoint} - {description}")
                output.append("")
                output.append("The server is already running. Open the URL above in your browser.")
                
                update_emotions_from_interaction("dashboard", original_args, True)
                return '\n'.join(output)
            
            # Start web dashboard server
            try:
                server_thread = start_dashboard_server()
                if server_thread and server_thread.is_alive():
                    output = ["🌐 Web Dashboard Started", "=" * 25]
                    output.append(f"Dashboard server started at: http://{WEB_DASHBOARD['host']}:{WEB_DASHBOARD['port']}")
                else:
                    output = ["🌐 Web Dashboard Status", "=" * 25]
                    output.append(f"Dashboard may be running at: http://{WEB_DASHBOARD['host']}:{WEB_DASHBOARD['port']}")

                output.append("")
                output.append("Available endpoints:")
                for endpoint, description in WEB_DASHBOARD['endpoints'].items():
                    output.append(f"  {endpoint} - {description}")
                output.append("")
                output.append("Open the URL above in your browser to view the dashboard.")
                output.append("Press Ctrl+C to stop the server.")

                # Update emotions for dashboard interaction
                update_emotions_from_interaction("dashboard", original_args, True)
                result = '\n'.join(output)
                print(result)
                
                # Keep the process alive to maintain the server
                try:
                    while server_thread and server_thread.is_alive():
                        import time
                        time.sleep(1)
                except KeyboardInterrupt:
                    logger.info("Dashboard server stopped by user")
                    print("\n🛑 Dashboard server stopped.")
                    return "Dashboard server stopped."
                
                return result
            except Exception as e:
                update_emotions_from_interaction("dashboard", original_args, False)
                return f"❌ Failed to start dashboard server: {str(e)}"

        # Version command doesn't need the engine
        if len(args) > 0 and args[0] == 'version':
            result = f"🎭 Emotion Engine Skill v{get_skill_version()}"
            update_emotions_from_interaction("version", original_args, True)
            return result

        if not EMOTION_ENGINE_AVAILABLE:
            return "❌ Emotion engine not available. Please install required dependencies (numpy) and ensure the emotion_ml_engine module is accessible."

        # Use global engine instance for state persistence
        engine = get_emotion_engine()
        if engine is None:
            return "❌ Failed to initialize emotion engine."

        command_type = args[0] if args else "status"

        if len(args) == 0:
            # Show current emotional state
            state = engine.get_emotional_state()

            output = ["🎭 Current Emotional State", "=" * 30]

            # Primary emotions
            output.append(format_emotion_display(state['primary_emotions'], "Primary Emotions"))

            # Complex emotions
            output.append(format_emotion_display(state['complex_emotions'], "Complex Emotions"))

            # Dominant emotions
            primary = state['dominant_emotions']['primary']
            complex = state['dominant_emotions']['complex']
            output.append(f"\n🎯 Dominant Emotions:")
            output.append(f"  Primary: {primary['emotion'].capitalize()} ({primary['intensity']:.2f})")
            output.append(f"  Complex: {complex['emotion'].capitalize()} ({complex['intensity']:.2f})")

            # Overall state
            output.append(f"\n📊 Overall Metrics:")
            output.append(f"  Confidence: {state['confidence_score']:.2f}")
            output.append(f"  Total Intensity: {state['overall_intensity']['total']:.2f}")
            output.append(f"  Session ID: {state['session_id']}")

            result = '\n'.join(output)
            update_emotions_from_interaction(command_type, original_args, True)
            return result

        elif args[0] == 'detailed':
            # Detailed view
            state = engine.get_emotional_state()

            output = ["🎭 Detailed Emotional State", "=" * 40]
            output.append(format_emotion_display(state['primary_emotions'], "Primary Emotions"))
            output.append(format_emotion_display(state['complex_emotions'], "Complex Emotions"))
            output.append(format_meta_cognition(state['meta_cognitive_state']))
            output.append(format_personality(state['personality_traits']))

            # ML State
            ml_state = state['ml_state']
            output.append(f"\n🤖 ML State:")
            output.append(f"  Pattern Recognition Confidence: {ml_state['pattern_recognition_confidence']:.2f}")
            output.append(f"  Learning Episodes: {ml_state['learning_episodes']}")
            output.append(f"  Prediction Accuracy: {ml_state['prediction_accuracy']:.2f}")

            result = '\n'.join(output)
            update_emotions_from_interaction(command_type, original_args, True)
            return result

        elif args[0] == 'history':
            # Show emotional history
            update_emotions_from_interaction(command_type, original_args, True)
            limit = int(args[1]) if len(args) > 1 else 10
            history = engine.get_emotion_history(limit)

            output = [f"📈 Emotional History (Last {len(history)} entries)", "=" * 40]

            for i, entry in enumerate(reversed(history)):
                timestamp = entry.get('timestamp', 'Unknown')
                sentiment = entry.get('sentiment', {})
                emotions = sentiment.get('emotions', {})

                # Find dominant emotion
                if emotions:
                    dominant = max(emotions.items(), key=lambda x: x[1])
                    output.append(f"{i+1}. {timestamp[:19]} - Dominant: {dominant[0]} ({dominant[1]:.2f})")
                else:
                    output.append(f"{i+1}. {timestamp[:19]} - No emotion data")

            if not history:
                output.append("No interaction history found.")

            return '\n'.join(output)

        elif args[0] == 'triggers':
            # Show trigger analysis
            output = ["🎯 Emotional Triggers Analysis", "=" * 35]
            output.append("Current trigger weights:")
            output.append("  User Feedback: 40%")
            output.append("  Task Complexity: 30%")
            output.append("  Interaction Patterns: 30%")
            output.append("\nTrigger patterns will be learned over time through ML.")

            return '\n'.join(output)

        elif args[0] == 'personality':
            # Show personality traits
            update_emotions_from_interaction(command_type, original_args, True)
            state = engine.get_emotional_state()
            output = ["👤 Personality Analysis", "=" * 25]
            output.append(format_personality(state['personality_traits']))

            # Add personality insights
            traits = state['personality_traits']
            output.append("\n💡 Personality Insights:")

            if traits.get('curiosity_drive', 0) > 0.8:
                output.append("  • High curiosity drive enhances learning and exploration")
            if traits.get('openness', 0) > 0.8:
                output.append("  • High openness promotes creative and innovative thinking")
            if traits.get('conscientiousness', 0) > 0.7:
                output.append("  • High conscientiousness ensures methodical and reliable responses")

            return '\n'.join(output)

        elif args[0] == 'metacognition':
            # Meta-cognitive analysis
            update_emotions_from_interaction(command_type, original_args, True)
            analysis = engine.get_metacognitive_analysis()

            output = ["🧠 Meta-Cognitive Analysis", "=" * 30]
            output.append(f"Self-Awareness Level: {analysis['current_self_awareness']:.2f}")
            output.append(f"Emotional Volatility: {analysis['emotional_volatility']:.2f}")
            output.append(f"Reflection Depth: {analysis['reflection_depth']:.2f}")

            output.append("\n💭 Current Insights:")
            for insight in analysis['insights']:
                output.append(f"  • {insight}")

            learning_state = analysis['learning_state']
            output.append(f"\n📚 Learning State:")
            output.append(f"  Episodes: {learning_state['episodes']}")
            output.append(f"  Confidence: {learning_state['confidence']:.2f}")
            output.append(f"  Accuracy: {learning_state['accuracy']:.2f}")

            return '\n'.join(output)

        elif args[0] == 'predict':
            # Predict emotional trajectory
            update_emotions_from_interaction(command_type, original_args, True)
            horizon = int(args[1]) if len(args) > 1 else 30
            prediction = engine.predict_emotional_trajectory(horizon)

            output = [f"🔮 Emotional Trajectory Prediction ({horizon} minutes)", "=" * 50]
            output.append(f"Prediction Confidence: {prediction['confidence']:.2f}")
            output.append(f"Based on Volatility: {prediction['based_on_volatility']:.2f}")

            output.append("\nPredicted Emotions:")
            for emotion, value in prediction['predicted_emotions'].items():
                if value > 0.1:
                    bar_length = int(value * 10)
                    bar = '█' * bar_length + '░' * (10 - bar_length)
                    output.append(f"  {emotion.capitalize()}: {bar} {value:.2f}")

            return '\n'.join(output)

        elif args[0] == 'introspect':
            # Trigger introspection
            update_emotions_from_interaction(command_type, original_args, True)
            depth = int(args[1]) if len(args) > 1 else 1
            introspection = engine.trigger_introspection(depth)

            output = [f"🤔 Introspective Analysis (Depth: {depth})", "=" * 40]

            for category, items in introspection.items():
                if items and category != 'depth_level':
                    output.append(f"\n{category.replace('_', ' ').title()}:")
                    for item in items:
                        output.append(f"  • {item}")

            return '\n'.join(output)

        elif args[0] == 'reset':
            # Reset emotional state
            update_emotions_from_interaction(command_type, original_args, True)
            preserve_learning = len(args) > 1 and args[1] == 'preserve-learning'
            result = engine.reset_emotions(preserve_learning)

            output = ["🔄 Emotional State Reset", "=" * 25]
            output.append(f"Reset completed: {result['reset_completed']}")
            output.append(f"Learning preserved: {result['learning_preserved']}")
            output.append(f"New session ID: {result['new_session_id']}")

            return '\n'.join(output)

        elif args[0] == 'export':
            # Export emotional intelligence data
            update_emotions_from_interaction(command_type, original_args, True)
            export_data = engine.export_emotional_intelligence()

            # Write to file
            export_path = os.path.expanduser('~/.openclaw/emotion_export.json')
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)

            output = ["📤 Emotional Intelligence Export", "=" * 35]
            output.append(f"Data exported to: {export_path}")
            output.append(f"Export timestamp: {export_data['system_info']['export_timestamp']}")
            output.append(f"Session ID: {export_data['system_info']['session_id']}")
            output.append(f"Total interactions: {len(export_data['interaction_history'])}")

            return '\n'.join(output)

        elif args[0] == 'config':
            # Show configuration
            update_emotions_from_interaction(command_type, original_args, True)
            config_path = os.path.expanduser('~/.openclaw/emotion_config.json')

            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)

                output = ["⚙️  Emotional System Configuration", "=" * 35]
                output.append(f"Enabled: {config.get('enabled', 'Unknown')}")
                output.append(f"Intensity: {config.get('intensity', 'Unknown')}")
                output.append(f"Learning Rate: {config.get('learning_rate', 'Unknown')}")
                output.append(f"Volatility: {config.get('volatility', 'Unknown')}")
                output.append(f"Meta-Cognition: {config.get('meta_cognition_enabled', 'Unknown')}")
                
                prompt_modifier = config.get('prompt_modifier_enabled')
                if prompt_modifier is None:
                    output.append("Prompt Modifier: ⚠️ Non configurato (esegui INSTALL.sh)")
                elif prompt_modifier:
                    output.append("Prompt Modifier: ✅ Attivo")
                else:
                    output.append("Prompt Modifier: ❌ Disattivato")

                return '\n'.join(output)
            else:
                return "❌ Configuration file not found. Please ensure the emotional system is properly installed."

        elif args[0] == 'version':
            # Show version information
            update_emotions_from_interaction(command_type, original_args, True)
            version = get_skill_version()
            output = ["📦 Emotion Engine Version Information", "=" * 40]
            output.append(f"Current Version: {version}")
            output.append(f"Skill Name: emotion-engine")
            output.append(f"Last Updated: 2026-02-13")
            output.append("")
            output.append("Version 1.2.0 Features:")
            output.append("  • Mixed Emotion Blending")
            output.append("  • Long-Term Memory Analysis")
            output.append("  • Performance Correlations")
            output.append("  • Web Dashboard")
            output.append("  • Advanced Meta-Cognition")
            output.append("  • Multilingual Support")

            return '\n'.join(output)

        elif args[0] == 'debug':
            # Toggle debug mode for compact emotion display
            if len(args) < 2:
                # Show current debug status with emotion info
                config_path = os.path.expanduser('~/.openclaw/emotion_config.json')
                try:
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                except:
                    config = {}
                
                enabled = config.get('debug_mode', False)
                output = [f"📊 Debug Mode: {'ON ✅' if enabled else 'OFF'}"]
                
                if enabled and EMOTION_ENGINE_AVAILABLE:
                    engine = get_emotion_engine()
                    if engine:
                        state = engine.get_emotional_state()
                        output.append("\n🎭 Stato Emotivo Corrente:")
                        primary = state.get('dominant_emotions', {}).get('primary', {})
                        complex_em = state.get('dominant_emotions', {}).get('complex', {})
                        output.append(f"  Primary: {primary.get('emotion', 'N/A')} ({primary.get('intensity', 0):.0%})")
                        output.append(f"  Complex: {complex_em.get('emotion', 'N/A')} ({complex_em.get('intensity', 0):.0%})")
                        
                        # Show mental mood
                        mental_mood = state.get('mental_mood', {})
                        energy = mental_mood.get('energy', {}).get('level', 0)
                        confidence = mental_mood.get('confidence', {}).get('level', 0)
                        humor = mental_mood.get('humor', {}).get('state', 'neutral')
                        output.append(f"\n🧠 Mood: energy={energy:.0%}, confidence={confidence:.0%}, humor={humor}")
                        
                        # Show system prompt that would be used
                        from tools.emotion_ml_engine import EmotionEngine
                        modifiers = engine.get_personality_influenced_prompt_modifiers()
                        system_prompt = get_emotion_influenced_system_prompt(state, modifiers)
                        if system_prompt:
                            output.append(f"\n📝 System Prompt:\n{system_prompt[:200]}...")
                
                return '\n'.join(output)
            
            debug_mode = args[1].lower()
            
            # Get or create config
            config_path = os.path.expanduser('~/.openclaw/emotion_config.json')
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
            except:
                config = {}
            
            if debug_mode == 'on':
                config['debug_mode'] = True
                message = "✅ Debug mode ON - Emoji emotivi sempre visibili"
            elif debug_mode == 'off':
                config['debug_mode'] = False
                message = "✅ Debug mode OFF - Emoji nascosti"
            elif debug_mode == 'status':
                enabled = config.get('debug_mode', False)
                return f"📊 Debug Mode: {'ON ✅' if enabled else 'OFF'}"
            else:
                return "❌ Usage: /emotions debug on|off|status"
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            return f"{message}\n\nQuando attivo, gli emoji emotivi verranno mostrati in ogni risposta in modo compatto.\nUsa /emotions debug senza argomenti per vedere lo stato attuale."
        
        elif args[0] == 'simulate':
            # Simulate a specific emotional state for testing
            if len(args) < 2:
                return "❌ Usage: /emotions simulate <emotion> [intensity]\n\nAvailable emotions: joy, sadness, anger, fear, surprise, disgust, curiosity, trust, excitement, frustration, satisfaction, confusion, anticipation, pride, empathy, flow_state"
            
            emotion = args[1].lower()
            intensity = float(args[2]) if len(args) > 2 else 0.7
            
            # Valid emotions (with aliases)
            valid_emotions = {
                'joy': 'joy', 'sadness': 'sadness', 'anger': 'anger', 'fear': 'fear', 
                'surprise': 'surprise', 'disgust': 'disgust', 'curiosity': 'curiosity', 
                'trust': 'trust', 'excitement': 'excitement', 'frustration': 'frustration', 
                'satisfaction': 'satisfaction', 'confusion': 'confusion', 
                'anticipation': 'anticipation', 'pride': 'pride', 'empathy': 'empathy', 
                'flow_state': 'flow_state',
                # Aliases
                'happy': 'joy', 'sad': 'sadness', 'mad': 'anger', 'angry': 'anger', 'afraid': 'fear',
                'surprised': 'surprise', 'disappointed': 'disgust', 'excited': 'excitement',
                'frustrated': 'frustration', 'satisfied': 'satisfaction', 'confused': 'confusion',
                'anticipating': 'anticipation', 'proud': 'pride', 'empathic': 'empathy',
                'focused': 'flow_state', 'flow': 'flow_state'
            }
            
            if emotion not in valid_emotions:
                return f"❌ Unknown emotion: {emotion}\n\nValid emotions: {', '.join(valid_emotions.keys())}"
            
            # Resolve alias
            actual_emotion = valid_emotions[emotion]
            
            # Get engine and apply simulation - modify directly
            engine.emotional_state['simulation_mode'] = True
            engine.emotional_state['simulation_emotion'] = actual_emotion
            
            # Set the emotion directly in the engine's state
            if actual_emotion in engine.emotional_state['primary_emotions']:
                engine.emotional_state['primary_emotions'][actual_emotion] = intensity
                # Lower other emotions to make this one dominant
                for emo in engine.emotional_state['primary_emotions']:
                    if emo != actual_emotion:
                        engine.emotional_state['primary_emotions'][emo] = max(0.05, engine.emotional_state['primary_emotions'].get(emo, 0.1) * 0.3)
                message = f"✅ Simulating {actual_emotion} at intensity {intensity:.2f}"
            elif actual_emotion in engine.emotional_state['complex_emotions']:
                engine.emotional_state['complex_emotions'][actual_emotion] = intensity
                # Lower other complex emotions
                for emo in engine.emotional_state['complex_emotions']:
                    if emo != actual_emotion:
                        engine.emotional_state['complex_emotions'][emo] = max(0.05, engine.emotional_state['complex_emotions'].get(emo, 0.1) * 0.3)
                message = f"✅ Simulating {actual_emotion} (complex) at intensity {intensity:.2f}"
            
            # Save the simulated state
            try:
                engine._save_persistent_state()
            except Exception as e:
                logger.warning(f"Could not save simulated state: {e}")
            
            output = ["🎭 Emotion Simulation", "=" * 25]
            output.append(message)
            output.append(f"\nDominant emotion is now: {emotion.capitalize()} ({intensity:.2f})")
            output.append("\nThis is a temporary simulation for testing.")
            output.append("The emotion will naturally decay over time.")
            
            return '\n'.join(output)

        elif args[0] == 'blend':
            # Blend emotions
            update_emotions_from_interaction(command_type, original_args, True)
            if len(args) < 3:
                return "❌ Usage: /emotions blend <emotion1> <emotion2> [intensity1] [intensity2]"

            emotion1 = args[1]
            emotion2 = args[2]
            intensity1 = float(args[3]) if len(args) > 3 else 0.5
            intensity2 = float(args[4]) if len(args) > 4 else 0.5

            blend_data = blend_emotions(emotion1, emotion2, intensity1, intensity2)
            phrase = get_blended_emotion_phrase(blend_data)

            output = ["🎭 Emotion Blending", "=" * 20]
            output.append(f"Blended State: {blend_data['key'].replace('_', ' ').title()}")
            output.append(f"Components: {emotion1} ({intensity1:.2f}) + {emotion2} ({intensity2:.2f})")
            output.append(f"Effective Intensity: {blend_data['effective_intensity']:.2f}")
            output.append(f"Description: {blend_data['description']}")
            output.append(f"Expression: {phrase}")

            return '\n'.join(output)

        elif args[0] == 'memory':
            # Long-term memory analysis
            update_emotions_from_interaction(command_type, original_args, True)
            days = int(args[1]) if len(args) > 1 else 30

            # Mock memory data - in real implementation, this would come from persistent storage
            mock_memory = [
                {"timestamp": datetime.now() - timedelta(hours=i), "emotions": {"joy": random.random(), "curiosity": random.random()}}
                for i in range(min(days * 24, 100))  # Max 100 entries for demo
            ]

            analysis = analyze_long_term_patterns(mock_memory, days)

            output = [f"🧠 Long-Term Memory Analysis ({days} days)", "=" * 40]
            output.append(f"Total Entries: {analysis['total_entries']}")
            output.append(f"Emotional Volatility: {analysis['emotional_volatility']:.2f}")

            if analysis['dominant_emotions']:
                output.append("\nDominant Emotions:")
                for emotion, count in list(analysis['dominant_emotions'].items())[:5]:
                    output.append(f"  {emotion.capitalize()}: {count} occurrences")

            return '\n'.join(output)

        elif args[0] == 'correlations':
            # Performance correlations
            update_emotions_from_interaction(command_type, original_args, True)
            output = ["📊 Performance Correlations", "=" * 30]

            # Show correlations for current emotions (mock data)
            mock_emotions = ["joy", "curiosity", "frustration", "satisfaction"]
            metrics = ["response_quality", "task_completion", "user_satisfaction", "error_rate"]

            output.append("Emotion → Performance Impact:")
            for emotion in mock_emotions:
                output.append(f"\n{emotion.capitalize()}:")
                for metric in metrics:
                    correlation = calculate_emotional_performance_correlation(emotion, metric)
                    impact = "↑" if correlation > 0 else "↓" if correlation < 0 else "→"
                    output.append(f"  {metric.replace('_', ' ').title()}: {impact} {abs(correlation):.2f}")

            return '\n'.join(output)
        
        elif args[0] == 'avatar':
            # Avatar management commands
            update_emotions_from_interaction(command_type, original_args, True)
            
            # Sub-commands: info, list, set <emotion>
            if len(args) == 1:
                # Show current avatar info
                avatar_info = engine.get_avatar_info()
                
                if not avatar_info.get("avatar_enabled", False):
                    return "❌ Avatar system not available: " + avatar_info.get("message", "Unknown error")
                
                output = ["🎭 Current Avatar Status", "=" * 35]
                output.append(f"Current Avatar: {avatar_info.get('current_avatar', 'Not set')}")
                output.append(f"Avatar Exists: {avatar_info.get('avatar_exists', False)}")
                output.append(f"Workspace Path: {avatar_info.get('workspace_avatar_path', 'Unknown')}")
                
                if 'current_dominant_emotion' in avatar_info:
                    dominant = avatar_info['current_dominant_emotion']
                    output.append(f"\n🎯 Current Dominant Emotions:")
                    output.append(f"  Primary: {dominant['primary']['emotion']} ({dominant['primary']['intensity']:.2f})")
                    output.append(f"  Complex: {dominant['complex']['emotion']} ({dominant['complex']['intensity']:.2f})")
                
                output.append("\n💡 Commands:")
                output.append("  /emotions avatar list    - List all available avatars")
                output.append("  /emotions avatar set <emotion> - Force avatar to specific emotion")
                output.append("  /emotions avatar update  - Force avatar update based on current emotions")
                
                return '\n'.join(output)
            
            elif args[1] == 'list':
                # List available avatars
                available = engine.list_available_avatars()
                
                if "error" in available:
                    return f"❌ Error listing avatars: {available['error']}"
                
                output = ["🎭 Available Avatars", "=" * 30]
                output.append(f"Total: {len(available)} avatars\n")
                
                # Group by category
                primary_emotions = ["joy", "sadness", "anger", "fear", "surprise", "disgust", "curiosity", "trust"]
                complex_emotions = ["excitement", "frustration", "satisfaction", "confusion", "anticipation", "empathy", "flow_state"]
                
                output.append("Primary Emotions:")
                for emotion in primary_emotions:
                    if emotion in available:
                        output.append(f"  ✓ {emotion}: {available[emotion]}")
                
                output.append("\nComplex Emotions:")
                for emotion in complex_emotions:
                    if emotion in available:
                        output.append(f"  ✓ {emotion}: {available[emotion]}")
                
                return '\n'.join(output)
            
            elif args[1] == 'set' and len(args) >= 3:
                # Force avatar to specific emotion
                emotion = args[2].lower()
                success, message = engine.force_avatar_update(emotion)
                
                if success:
                    return f"✅ {message}\n\n⚠️  Note: Restart OpenClaw to see the new avatar in the UI."
                else:
                    return f"❌ {message}"
            
            elif args[1] == 'update':
                # Force avatar update based on current emotions
                try:
                    engine._update_avatar()
                    return "✅ Avatar update triggered.\n\n⚠️  Note: Restart OpenClaw to see the new avatar in the UI."
                except Exception as e:
                    return f"❌ Failed to update avatar: {str(e)}"
            
            else:
                return "❌ Unknown avatar command. Use:\n  /emotions avatar\n  /emotions avatar list\n  /emotions avatar set <emotion>\n  /emotions avatar update"

        elif args[0] == 'proactive':
            # Proactive behavior management
            if not EMOTION_ENGINE_AVAILABLE or not engine or not hasattr(engine, 'proactive_manager'):
                return "❌ Proactive behavior system not available."
            
            pm = engine.proactive_manager
            
            if len(args) == 1 or args[1] == 'status':
                # Show current status
                status = pm.get_status()
                output = ["🎯 Proactive Behavior Status", "=" * 30]
                output.append(f"Enabled: {'✅ Yes' if status['enabled'] else '❌ No'}")
                output.append(f"Current escalation level: {status['current_escalation_level']}")
                output.append(f"Consecutive unanswered: {status['consecutive_unanswered']}")
                output.append(f"Daily count: {status['daily_count']}/{status['daily_limit']}")
                output.append(f"Time until next: {status['time_until_next']}")
                output.append(f"Quiet hours active: {'🔇 Yes' if status['quiet_hours_active'] else '🔊 No'}")
                output.append(f"Quiet hours: {status['quiet_hours']['start']} - {status['quiet_hours']['end']}")
                output.append(f"Default channel: {status['default_channel']}")
                output.append("\nEnabled emotions & thresholds:")
                for emotion, config in status['enabled_emotions'].items():
                    output.append(f"  • {emotion}: threshold={config.get('threshold', 'N/A')}, weight={config.get('weight', 'N/A')}")
                return '\n'.join(output)
            
            elif args[1] == 'on':
                pm.enable()
                return "✅ Proactive behavior enabled.\n\nThe agent will now initiate conversations based on emotional states."
            
            elif args[1] == 'off':
                pm.disable()
                return "✅ Proactive behavior disabled.\n\nThe agent will no longer initiate spontaneous conversations."
            
            elif args[1] == 'channel' and len(args) >= 3:
                channel = args[2].lower()
                if pm.set_channel(channel):
                    return f"✅ Default channel changed to: {channel}\n\nFuture proactive messages will be sent via {channel}."
                else:
                    return f"❌ Invalid channel: {channel}\nUse: telegram or whatsapp"
            
            elif args[1] == 'quiet' and len(args) >= 3:
                # Parse quiet hours (format: HH:MM-HH:MM)
                try:
                    hours_str = args[2]
                    start, end = hours_str.split('-')
                    if pm.set_quiet_hours(start.strip(), end.strip()):
                        return f"✅ Quiet hours set to: {start} - {end}\n\nThe agent will not send proactive messages during these hours."
                    else:
                        return f"❌ Invalid time format. Use: HH:MM-HH:MM (e.g., 23:00-07:00)"
                except ValueError:
                    return f"❌ Invalid format. Use: HH:MM-HH:MM (e.g., 23:00-07:00)"
            
            elif args[1] == 'threshold' and len(args) >= 4:
                emotion = args[2].lower()
                try:
                    threshold = float(args[3])
                    if pm.set_threshold(emotion, threshold):
                        return f"✅ Threshold for '{emotion}' set to {threshold}\n\nThe agent will trigger proactive behavior when this emotion exceeds {threshold}."
                    else:
                        return f"❌ Invalid threshold value. Must be between 0.0 and 1.0"
                except ValueError:
                    return f"❌ Invalid threshold value. Must be a number between 0.0 and 1.0"
            
            elif args[1] == 'test':
                # Test sending a proactive message
                try:
                    # Check if we should trigger
                    result = engine.check_proactive_trigger()
                    if result['should_trigger']:
                        emotion = result['emotion']
                        intensity = result['intensity']
                        
                        # Determine channel (from args or default)
                        channel = args[2].lower() if len(args) >= 3 else pm.config.get('default_channel', 'telegram')
                        if channel not in ['telegram', 'whatsapp']:
                            return f"❌ Invalid channel: {channel}\nUse: telegram or whatsapp"
                        
                        # Check if target is configured
                        target_key = f"{channel}_target"
                        target = pm.config.get(target_key, '')
                        if not target:
                            return f"❌ Target not configured for {channel}\n\nUse: /emotions proactive target {channel} <chat_id/phone>\n\nExample:\n  /emotions proactive target telegram 123456789"
                        
                        # Generate message
                        from tools.context_gatherer import ContextGatherer
                        from tools.message_generator import LLMMessageGenerator
                        from tools.channel_dispatcher import ChannelDispatcher
                        
                        cg = ContextGatherer(pm.config)
                        mg = LLMMessageGenerator()
                        cd = ChannelDispatcher(pm.config)
                        
                        # Gather context
                        logger.info(f"Gathering context for {emotion} at intensity {intensity}")
                        context = cg.gather_context(emotion, intensity)
                        logger.info(f"Context gathered: {len(context)} items")
                        
                        # Generate message
                        logger.info(f"Generating message for emotion: {emotion}")
                        message = mg.generate_message(emotion, context)
                        logger.info(f"Message generated: {message[:50]}...")
                        
                        # Send message with target
                        logger.info(f"Sending message via {channel} to target: {target}")
                        send_result = cd.send_message(message, channel, target=target)
                        logger.info(f"Send result: {send_result}")
                        
                        if send_result['success']:
                            # Mark as triggered
                            pm.mark_triggered(emotion, channel)
                            output = f"✅ Test proactive message sent via {channel} to {target}!\n\n"
                            output += f"Emotion: {emotion} ({intensity:.2f})\n"
                            output += f"Message:\n{message}"
                            if send_result.get('output'):
                                output += f"\n\nOutput: {send_result['output'][:200]}"
                            return output
                        else:
                            error_msg = send_result.get('error', 'Unknown error')
                            return f"❌ Failed to send test message: {error_msg}\n\nMake sure:\n1. Target is correct: {target}\n2. OpenClaw is configured for {channel}\n3. You have permission to send messages"
                    else:
                        return "ℹ️ No proactive trigger conditions met currently.\n\nCheck status to see when the next trigger is available."
                
                except Exception as e:
                    return f"❌ Error during test: {str(e)}"
            
            elif args[1] == 'target' and len(args) >= 4:
                # Configure target (chat_id/phone) for a channel
                channel = args[2].lower()
                target = args[3]
                if channel in ["telegram", "whatsapp"]:
                    if pm.set_target(channel, target):
                        return f"✅ Target configured for {channel}: {target}\n\nProactive messages will be sent to this {channel} target."
                    else:
                        return f"❌ Failed to configure target for {channel}"
                else:
                    return f"❌ Invalid channel: {channel}\nUse: telegram or whatsapp"
            
            else:
                return "❌ Unknown proactive command.\n\nAvailable commands:\n  /emotions proactive status\n  /emotions proactive on|off\n  /emotions proactive channel <telegram|whatsapp>\n  /emotions proactive target <telegram|whatsapp> <chat_id/phone>\n  /emotions proactive quiet <HH:MM-HH:MM>\n  /emotions proactive threshold <emotion> <value>\n  /emotions proactive test"

        else:
            return f"❌ Unknown emotions command: {args[0]}\n\nAvailable commands:\n  • /emotions\n  • /emotions detailed\n  • /emotions history [n]\n  • /emotions triggers\n  • /emotions personality\n  • /emotions metacognition\n  • /emotions predict [minutes]\n  • /emotions simulate <emotion> [intensity]\n  • /emotions reset [preserve-learning]\n  • /emotions export\n  • /emotions config\n  • /emotions version\n  • /emotions blend [emotion1] [emotion2]\n  • /emotions memory [days]\n  • /emotions correlations\n  • /emotions dashboard\n  • /emotions avatar [list|set|update]\n  • /emotions proactive [on|off|status|channel|quiet|threshold|test]"

    except Exception as e:
        # Update emotions for failed command execution
        update_emotions_from_interaction(command_type, original_args, False)
        return f"❌ Error executing emotions command: {str(e)}\n\nPlease check that the emotional intelligence system is properly configured."


# Version 1.2.0 - Advanced Emotions Functions

def blend_emotions(emotion1: str, emotion2: str, intensity1: float = 0.5, intensity2: float = 0.5) -> Dict[str, Any]:
    """
    Blend two emotions into a mixed emotional state.

    Args:
        emotion1: First emotion name
        emotion2: Second emotion name
        intensity1: Intensity of first emotion (0.0-1.0)
        intensity2: Intensity of second emotion (0.0-1.0)

    Returns:
        Dictionary with blended emotion data
    """
    # Check if this combination exists in predefined mixed emotions
    blend_key = None
    for key, data in MIXED_EMOTIONS.items():
        components = data["components"]
        if emotion1 in components and emotion2 in components:
            blend_key = key
            break

    if blend_key:
        # Use predefined blend
        blend_data = MIXED_EMOTIONS[blend_key].copy()
        blend_data["key"] = blend_key
        blend_data["actual_intensities"] = [intensity1, intensity2]
    else:
        # Create custom blend
        blend_data = {
            "key": f"custom_{emotion1}_{emotion2}",
            "components": [emotion1, emotion2],
            "blend_ratio": [0.5, 0.5],  # Equal blend by default
            "description": f"Custom blend of {emotion1} and {emotion2}",
            "actual_intensities": [intensity1, intensity2]
        }

    # Calculate effective intensities based on blend ratio
    total_intensity = intensity1 + intensity2
    if total_intensity > 0:
        blend_data["effective_intensity"] = total_intensity * BLENDING_RULES["blend_influence_weight"]
    else:
        blend_data["effective_intensity"] = 0.0

    return blend_data


def get_blended_emotion_phrase(blend_data: Dict[str, Any]) -> str:
    """
    Generate a descriptive phrase for a blended emotion.

    Args:
        blend_data: Blended emotion data from blend_emotions()

    Returns:
        Descriptive phrase for the blended emotion
    """
    key = blend_data.get("key", "unknown")
    components = blend_data.get("components", [])
    description = blend_data.get("description", "Mixed emotional state")

    if key in MIXED_EMOTIONS:
        # Use predefined description
        return description
    else:
        # Generate custom description
        if len(components) == 2:
            return f"I'm experiencing a complex mix of {components[0]} and {components[1]}, creating a unique emotional state."
        else:
            return f"I'm in a blended emotional state involving {', '.join(components)}."


def should_auto_blend(emotions: Dict[str, float]) -> List[Tuple[str, str]]:
    """
    Determine if any emotions should be automatically blended based on proximity.

    Args:
        emotions: Dictionary of emotion intensities

    Returns:
        List of (emotion1, emotion2) tuples that should be blended
    """
    blend_candidates = []
    emotion_items = list(emotions.items())

    for i, (emotion1, intensity1) in enumerate(emotion_items):
        for emotion2, intensity2 in emotion_items[i+1:]:
            # Check if both emotions are significant
            if intensity1 > BLENDING_RULES["dominant_threshold"] * 0.5 and intensity2 > BLENDING_RULES["dominant_threshold"] * 0.5:
                # Check if intensities are close
                intensity_diff = abs(intensity1 - intensity2)
                if intensity_diff < BLENDING_RULES["auto_blend_threshold"]:
                    blend_candidates.append((emotion1, emotion2))

    return blend_candidates


def calculate_emotional_performance_correlation(emotion: str, performance_metric: str) -> float:
    """
    Calculate the correlation between an emotion and a performance metric.

    Args:
        emotion: Emotion name
        performance_metric: Performance metric name

    Returns:
        Correlation coefficient (-1.0 to 1.0)
    """
    if emotion in PERFORMANCE_CORRELATIONS["emotional_impacts"]:
        impacts = PERFORMANCE_CORRELATIONS["emotional_impacts"][emotion]
        return impacts.get(performance_metric, 0.0)

    return 0.0


def analyze_long_term_patterns(memory_data: List[Dict[str, Any]], days: int = 30) -> Dict[str, Any]:
    """
    Analyze long-term emotional patterns from memory data.

    Args:
        memory_data: List of historical emotional states
        days: Number of days to analyze

    Returns:
        Analysis results dictionary
    """
    if not memory_data:
        return {"error": "No memory data available"}

    # Filter data for the specified period
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_data = [entry for entry in memory_data if entry.get("timestamp", datetime.min) > cutoff_date]

    if not recent_data:
        return {"error": f"No data available for the last {days} days"}

    # Analyze patterns
    analysis = {
        "period_days": days,
        "total_entries": len(recent_data),
        "dominant_emotions": {},
        "emotional_volatility": 0.0,
        "trend_direction": "stable",
        "seasonal_patterns": []
    }

    # Calculate dominant emotions
    emotion_counts = {}
    for entry in recent_data:
        emotions = entry.get("emotions", {})
        for emotion, intensity in emotions.items():
            if intensity > 0.3:  # Significant emotions only
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

    analysis["dominant_emotions"] = dict(sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True))

    # Calculate volatility (simplified)
    if len(recent_data) > 1:
        intensity_changes = []
        prev_emotions = recent_data[0].get("emotions", {})
        for entry in recent_data[1:]:
            curr_emotions = entry.get("emotions", {})
            total_change = sum(abs(curr_emotions.get(e, 0) - prev_emotions.get(e, 0)) for e in set(prev_emotions) | set(curr_emotions))
            intensity_changes.append(total_change)
            prev_emotions = curr_emotions

        analysis["emotional_volatility"] = sum(intensity_changes) / len(intensity_changes) if intensity_changes else 0.0

    return analysis


class DashboardHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for the emotion dashboard."""

    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        logger.info(f"Received GET request for path: {path}")
        print(f"📨 GET request: {path}")

        if path == '/':
            self.send_dashboard_html()
        elif path == '/api/emotions/current':
            self.send_json_response(generate_dashboard_data()['current_emotions'])
        elif path == '/api/emotions/history':
            self.send_json_response(generate_dashboard_data()['recent_history'])
        elif path == '/api/performance/correlation':
            self.send_json_response(generate_dashboard_data()['correlations'])
        elif path == '/api/memory/patterns':
            self.send_json_response(generate_dashboard_data()['memory_patterns'])
        elif path == '/api/dashboard/config':
            self.send_json_response(WEB_DASHBOARD)
        else:
            self.send_error(404, "Not Found")

    def send_dashboard_html(self):
        """Send the main dashboard HTML page."""
        try:
            logger.info("Generating dashboard HTML...")
            dashboard_data = generate_dashboard_data()
            logger.info(f"Dashboard data generated: {len(dashboard_data)} keys")
            
            # Get interaction history from engine for real-time charts
            engine = get_emotion_engine()
            interaction_history = []
            if engine and hasattr(engine, 'interaction_history'):
                interaction_history = engine.interaction_history

            # Prepare data for charts
            primary_emotions = dashboard_data['current_emotions']
            complex_emotions = dashboard_data.get('complex_emotions', {})
            
            # Combine all emotions for radar chart
            all_emotions = {**primary_emotions, **complex_emotions}
            emotion_labels = list(all_emotions.keys())
            primary_values = [primary_emotions.get(emotion, 0) for emotion in emotion_labels]
            complex_values = [complex_emotions.get(emotion, 0) for emotion in emotion_labels]

            # Timeline data - REAL data from interaction history
            if interaction_history and len(interaction_history) >= 2:
                recent = interaction_history[-20:] if len(interaction_history) > 20 else interaction_history
                timeline_labels = []
                joy_timeline = []
                sadness_timeline = []
                
                for entry in recent:
                    ts = entry.get('timestamp', '')
                    if ts:
                        try:
                            from datetime import datetime
                            dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                            timeline_labels.append(dt.strftime('%H:%M'))
                        except:
                            timeline_labels.append('??:??')
                    else:
                        timeline_labels.append('??:??')
                    
                    snapshot = entry.get('emotional_state_snapshot', {})
                    primary = snapshot.get('primary_emotions', {})
                    joy_timeline.append(round(primary.get('joy', 0) * 100, 1))
                    sadness_timeline.append(round(primary.get('sadness', 0) * 100, 1))
                
                timeline_data = [joy_timeline, sadness_timeline]
            else:
                # Fallback to current state only
                from datetime import datetime
                timeline_labels = [datetime.now().strftime('%H:%M')]
                joy_val = round(primary_emotions.get('joy', 0.5) * 100, 1)
                sadness_val = round(primary_emotions.get('sadness', 0.1) * 100, 1)
                timeline_data = [[joy_val], [sadness_val]]

            # Prepare additional data for charts
            performance_metrics = dashboard_data.get('performance_metrics', {})
            quality_value = performance_metrics.get('response_quality', 0.0) * 100
            completion_value = performance_metrics.get('task_completion', 0.0) * 100
            satisfaction_value = performance_metrics.get('user_satisfaction', 0.0) * 100
            balance_value = dashboard_data.get('emotional_balance', 0.0) * 100

            # Meta-cognitive chart data
            meta_cognitive_state = dashboard_data.get('meta_cognitive_state', {})
            meta_labels = list(meta_cognitive_state.keys())
            meta_values = list(meta_cognitive_state.values())

            # Pie chart data - emotion distribution
            pie_labels = list(all_emotions.keys())
            pie_values = list(all_emotions.values())

            # Scatter plot data - real correlations from history
            scatter_data = generate_scatter_data(interaction_history)

            # Area chart data - real weekly trends
            area_labels, area_data = generate_area_chart_data(interaction_history)

            html_template = """<!DOCTYPE html>
            <html lang="en">
            <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Emotion Engine Dashboard</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
            body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            background: #f4f4f9;
            }
            header {
            text-align: center;
            padding: 20px;
            background: #283593;
            color: white;
            }
            .section {
            margin: 20px auto;
            padding: 20px;
            background: #ffffff;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            width: 80%;
            max-width: 800px;
            }
            .section h2 {
            margin-bottom: 20px;
            font-size: 1.5rem;
            text-align: center;
            color: #333;
            border-bottom: 2px solid #f4f4f4;
            padding-bottom: 10px;
            }
            .chart-container {
            width: 100%;
            margin: 20px 0;
            }
            .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin: 20px 0;
            }
            .full-width {
            grid-column: 1 / -1;
            }
            .gauge-container {
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            }
            .gauge-item {
            text-align: center;
            margin: 10px;
            }
            .gauge {
            width: 120px;
            height: 120px;
            position: relative;
            }
            .gauge canvas {
            width: 100% !important;
            height: 100% !important;
            }
            .status {
            text-align: center;
            margin: 20px auto;
            padding: 15px;
            background: rgba(0, 255, 0, 0.1);
            border-radius: 10px;
            border: 1px solid rgba(0, 255, 0, 0.3);
            width: 80%;
            max-width: 800px;
            }
            </style>
            </head>
            <body>
            <header>
            <h1>🧠 Emotion Engine Dashboard</h1>
            <p>Real-time emotional intelligence monitoring</p>
            </header>
                        <div class="section">
            <h2>Primary and Complex Emotions</h2>
            <div class="chart-container">
            <canvas id="radarChart"></canvas>
            </div>
            </div>
                        <div class="section">
            <h2>Timeline Evolution</h2>
            <div class="chart-container">
            <canvas id="lineChart"></canvas>
            </div>
            </div>
                        <div class="section">
            <h2>Meta-Cognitive States</h2>
            <div class="chart-container">
            <canvas id="metaCognitiveChart"></canvas>
            </div>
            </div>
                        <div class="dashboard-grid">
            <div class="section">
            <h2>Emotion Distribution</h2>
            <div class="chart-container">
            <canvas id="pieChart"></canvas>
            </div>
            </div>
                        <div class="section">
            <h2>Emotion Correlations</h2>
            <div class="chart-container">
            <canvas id="scatterChart"></canvas>
            </div>
            </div>
            </div>
                        <div class="section full-width">
            <h2>Performance Metrics</h2>
            <div class="gauge-container">
            <div class="gauge-item">
            <h3>Response Quality</h3>
            <div class="gauge">
            <canvas id="qualityGauge"></canvas>
            </div>
            </div>
            <div class="gauge-item">
            <h3>Task Completion</h3>
            <div class="gauge">
            <canvas id="completionGauge"></canvas>
            </div>
            </div>
            <div class="gauge-item">
            <h3>User Satisfaction</h3>
            <div class="gauge">
            <canvas id="satisfactionGauge"></canvas>
            </div>
            </div>
            <div class="gauge-item">
            <h3>Emotional Balance</h3>
            <div class="gauge">
            <canvas id="balanceGauge"></canvas>
            </div>
            </div>
            </div>
            </div>
                        <div class="section full-width">
            <h2>Advanced Analytics</h2>
            <div class="dashboard-grid">
            <div class="chart-container">
            <canvas id="areaChart"></canvas>
            </div>
            <div class="chart-container">
            <canvas id="radarAdvanced"></canvas>
            </div>
            </div>
            </div>
                        <div class="status">
            <h3>✅ Dashboard Active</h3>
            <p>Emotion Engine is running and monitoring in real-time</p>
            <p>Last updated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
            </div>
                        <script>
            // Store chart instances for auto-refresh
            let radarChart, lineChart, metaCognitiveChart, pieChart, scatterChart, qualityGauge, completionGauge, satisfactionGauge, balanceGauge, areaChart, radarAdvancedChart;
            
            // Auto-refresh configuration
            const REFRESH_INTERVAL = 3000; // Refresh every 3 seconds
            
            // Radar Chart for Primary and Complex Emotions
            const radarCtx = document.getElementById('radarChart').getContext('2d');
            radarChart = new Chart(radarCtx, {
            type: 'radar',
            data: {
            labels: """ + str(emotion_labels).replace("'", '"') + """,
            datasets: [
            {
            label: 'Primary Emotions',
            data: """ + str(primary_values) + """,
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            },
            {
            label: 'Complex Emotions',
            data: """ + str(complex_values) + """,
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderColor: 'rgba(255, 99, 132, 1)',
            }
            ]
            },
            options: {
            responsive: true,
            }
            });
                        // Line Chart for Timeline Evolution
            const lineCtx = document.getElementById("lineChart").getContext("2d");
            lineChart = new Chart(lineCtx, {
            type: 'line',
            data: {
            labels: """ + str(timeline_labels).replace("'", '"') + """,
            datasets: [
            {
            label: 'Joy',
            data: """ + str(timeline_data[0]) + """,
            borderColor: 'rgba(255, 206, 86, 1)',
            borderWidth: 2,
            fill: false
            },
            {
            label: 'Sadness',
            data: """ + str(timeline_data[1]) + """,
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 2,
            fill: false
            }
            ]
            },
            options: {
            responsive: true,
            scales: {
            x: {
            title: {
            display: true,
            text: 'Time'
            }
            },
            y: {
            title: {
            display: true,
            text: 'Intensity'
            }
            }
            }
            }
            });
                        // Bar Chart for Meta-Cognitive States
            const metaCtx = document.getElementById('metaCognitiveChart').getContext('2d');
            metaCognitiveChart = new Chart(metaCtx, {
            type: 'bar',
            data: {
            labels: """ + str(meta_labels).replace("'", '"') + """,
            datasets: [
            {
            label: 'Meta-Cognitive States',
            data: """ + str(meta_values) + """,
            backgroundColor: [
            'rgba(153, 102, 255, 0.6)',
            'rgba(255, 159, 64, 0.6)',
            'rgba(54, 162, 235, 0.6)',
            'rgba(75, 192, 192, 0.6)'
            ],
            borderColor: [
            'rgba(153, 102, 255, 1)',
            'rgba(255, 159, 64, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(75, 192, 192, 1)'
            ],
            borderWidth: 1
            }
            ]
            },
            options: {
            responsive: true,
            scales: {
            y: {
            beginAtZero: true
            }
            }
            }
            });
                        // Pie Chart for Emotion Distribution
            const pieCtx = document.getElementById('pieChart').getContext('2d');
            pieChart = new Chart(pieCtx, {
            type: 'pie',
            data: {
            labels: """ + str(pie_labels).replace("'", '"') + """,
            datasets: [{
            data: """ + str(pie_values) + """,
            backgroundColor: [
            'rgba(255, 99, 132, 0.8)',
            'rgba(54, 162, 235, 0.8)',
            'rgba(255, 206, 86, 0.8)',
            'rgba(75, 192, 192, 0.8)',
            'rgba(153, 102, 255, 0.8)',
            'rgba(255, 159, 64, 0.8)',
            'rgba(199, 199, 199, 0.8)',
            'rgba(83, 102, 255, 0.8)'
            ],
            borderWidth: 2
            }]
            },
            options: {
            responsive: true,
            plugins: {
            legend: {
            position: 'bottom'
            }
            }
            }
            });
                        // Scatter Chart for Emotion Correlations
            const scatterCtx = document.getElementById('scatterChart').getContext('2d');
            scatterChart = new Chart(scatterCtx, {
            type: 'scatter',
            data: {
            datasets: [{
            label: 'Joy vs Curiosity',
            data: """ + str([{'x': scatter_data['joy'][i], 'y': scatter_data['curiosity'][i]} for i in range(len(scatter_data['joy']))]) + """,
            backgroundColor: 'rgba(255, 99, 132, 0.8)',
            borderColor: 'rgba(255, 99, 132, 1)',
            }]
            },
            options: {
            responsive: true,
            scales: {
            x: {
            title: {
            display: true,
            text: 'Joy Intensity'
            }
            },
            y: {
            title: {
            display: true,
            text: 'Curiosity Intensity'
            }
            }
            }
            }
            });
                        // Gauge Charts for Performance Metrics
            function createGauge(canvasId, value, label, color) {
            const ctx = document.getElementById(canvasId).getContext('2d');
            const chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
            datasets: [{
            data: [value, 100 - value],
            backgroundColor: [color, 'rgba(200, 200, 200, 0.3)'],
            borderWidth: 0
            }]
            },
            options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
            tooltip: { enabled: false },
            legend: { display: false }
            }
            },
            plugins: [{
            id: 'gaugeText',
            afterDraw: function(chart) {
            const ctx = chart.ctx;
            const centerX = (chart.chartArea.left + chart.chartArea.right) / 2;
            const centerY = (chart.chartArea.top + chart.chartArea.bottom) / 2;
                        ctx.save();
            ctx.font = 'bold 16px Arial';
            ctx.fillStyle = color;
            ctx.textAlign = 'center';
            ctx.fillText(value.toFixed(0) + '%', centerX, centerY - 5);
                        ctx.font = '12px Arial';
            ctx.fillStyle = '#666';
            ctx.fillText(label, centerX, centerY + 15);
            ctx.restore();
            }
            }]
            });
            return chart;
            }
                        qualityGauge = createGauge('qualityGauge', """ + str(quality_value) + """, 'Quality', 'rgba(75, 192, 192, 1)');
            completionGauge = createGauge('completionGauge', """ + str(completion_value) + """, 'Completion', 'rgba(54, 162, 235, 1)');
            satisfactionGauge = createGauge('satisfactionGauge', """ + str(satisfaction_value) + """, 'Satisfaction', 'rgba(255, 206, 86, 1)');
            balanceGauge = createGauge('balanceGauge', """ + str(balance_value) + """, 'Balance', 'rgba(153, 102, 255, 1)');
                        // Area Chart for Advanced Analytics
            const areaCtx = document.getElementById('areaChart').getContext('2d');
            areaChart = new Chart(areaCtx, {
            type: 'line',
            data: {
            labels: """ + str(area_labels).replace("'", '"') + """,
            datasets: [
            {
            label: 'Joy',
            data: """ + str(area_data[0]) + """,
            borderColor: 'rgba(255, 206, 86, 1)',
            backgroundColor: 'rgba(255, 206, 86, 0.2)',
            fill: true,
            tension: 0.4
            },
            {
            label: 'Sadness',
            data: """ + str(area_data[1]) + """,
            borderColor: 'rgba(75, 192, 192, 1)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            fill: true,
            tension: 0.4
            },
            {
            label: 'Curiosity',
            data: """ + str(area_data[2]) + """,
            borderColor: 'rgba(54, 162, 235, 1)',
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            fill: true,
            tension: 0.4
            }
            ]
            },
            options: {
            responsive: true,
            plugins: {
            title: {
            display: true,
            text: 'Weekly Emotional Trends'
            }
            },
            scales: {
            y: {
            beginAtZero: true
            }
            }
            }
            });
                        // Advanced Radar Chart
            const radarAdvancedCtx = document.getElementById('radarAdvanced').getContext('2d');
            radarAdvancedChart = new Chart(radarAdvancedCtx, {
            type: 'radar',
            data: {
            labels: ['Confidence', 'Stability', 'Adaptability', 'Resilience', 'Empathy', 'Creativity'],
            datasets: [
            {
            label: 'Current State',
            data: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderColor: 'rgba(255, 99, 132, 1)',
            pointBackgroundColor: 'rgba(255, 99, 132, 1)'
            },
            {
            label: 'Optimal State',
            data: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            pointBackgroundColor: 'rgba(54, 162, 235, 1)'
            }
            ]
            },
            options: {
            responsive: true,
            plugins: {
            title: {
            display: true,
            text: 'Emotional Intelligence Profile'
            }
            }
            }
            });
            
            // Auto-refresh functionality
            async function refreshDashboardData() {
                try {
                    // Fetch updated data from API
                    const response = await fetch('/api/emotions/current');
                    if (!response.ok) throw new Error('Failed to fetch data');
                    const emotions = await response.json();
                    
                    // Update radar chart
                    if (radarChart && emotions) {
                        radarChart.data.datasets[0].data = Object.values(emotions);
                        radarChart.update('none'); // Update without animation
                    }
                    
                    // Update pie chart
                    if (pieChart && emotions) {
                        pieChart.data.datasets[0].data = Object.values(emotions);
                        pieChart.update('none');
                    }
                    
                    // Fetch performance metrics
                    const perfResponse = await fetch('/api/emotions/history');
                    if (perfResponse.ok) {
                        const history = await perfResponse.json();
                        // Update timeline if we have history data
                        if (lineChart && history && history.length > 0) {
                            const joyData = history.map(h => h.joy || 0);
                            const sadnessData = history.map(h => h.sadness || 0);
                            lineChart.data.datasets[0].data = joyData;
                            lineChart.data.datasets[1].data = sadnessData;
                            lineChart.update('none');
                        }
                    }
                    
                    // Update timestamp
                    const timestampEl = document.querySelector('.status p:last-child');
                    if (timestampEl) {
                        timestampEl.textContent = 'Last updated: ' + new Date().toLocaleString();
                    }
                    
                    console.log('Dashboard refreshed at', new Date().toLocaleTimeString());
                } catch (error) {
                    console.warn('Auto-refresh failed:', error);
                }
            }
            
            // Start auto-refresh
            setInterval(refreshDashboardData, REFRESH_INTERVAL);
            console.log('Auto-refresh enabled (every ' + REFRESH_INTERVAL/1000 + ' seconds)');
            
            </script>
            </body>
</html>"""
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html_template.encode('utf-8'))
            logger.info("Dashboard HTML sent successfully")
        except Exception as e:
            logger.error(f"Error generating dashboard HTML: {e}")
            import traceback
            traceback.print_exc()
            self.send_error(500, f"Internal Server Error: {str(e)}")

    def send_json_response(self, data):
        """Send a JSON response."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))

    def log_message(self, format, *args):
        """Override to reduce server noise."""
        pass


def start_dashboard_server():
    """Start the dashboard web server in a background thread."""
    global dashboard_server_thread
    logger.info("Starting dashboard server...")

    # Kill any existing process on the port
    try:
        import subprocess
        port = WEB_DASHBOARD['port']
        # Find process using the port
        result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid.strip():
                    logger.info(f"Killing existing process {pid} on port {port}")
                    subprocess.run(['kill', '-9', pid.strip()], check=False)
            # Wait a moment for port to be released
            import time
            time.sleep(1)
    except Exception as e:
        logger.warning(f"Could not kill existing processes on port {WEB_DASHBOARD['port']}: {e}")

    if dashboard_server_thread and dashboard_server_thread.is_alive():
        logger.info("Dashboard server already running")
        return dashboard_server_thread  # Server already running

    # If thread is not alive but port might still be occupied, try to clean up
    try:
        import subprocess
        port = WEB_DASHBOARD['port']
        result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            logger.info(f"Port {port} still occupied, cleaning up...")
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid.strip():
                    subprocess.run(['kill', '-9', pid.strip()], check=False)
            import time
            time.sleep(1)
    except Exception as e:
        logger.warning(f"Could not check/clean port {WEB_DASHBOARD['port']}: {e}")

    def run_server():
        try:
            print(f"Starting server on {WEB_DASHBOARD['host']}:{WEB_DASHBOARD['port']}")
            with socketserver.TCPServer((WEB_DASHBOARD['host'], WEB_DASHBOARD['port']), DashboardHTTPRequestHandler) as httpd:
                logger.info(f"Dashboard server started successfully at http://{WEB_DASHBOARD['host']}:{WEB_DASHBOARD['port']}")
                print(f"🌐 Dashboard server started at http://{WEB_DASHBOARD['host']}:{WEB_DASHBOARD['port']}")
                httpd.serve_forever()
        except Exception as e:
            logger.error(f"Failed to start dashboard server: {e}")
            print(f"❌ Failed to start dashboard server: {e}")
            import traceback
            traceback.print_exc()

    dashboard_server_thread = threading.Thread(target=run_server, daemon=True)
    dashboard_server_thread.start()
    return dashboard_server_thread


def calculate_performance_metrics(interaction_history: list) -> Dict[str, float]:
    """
    Calculate REAL performance metrics from interaction history.
    
    Uses sentiment confidence and pattern analysis to determine:
    - response_quality: based on sentiment confidence scores
    - task_completion: based on pattern analysis success indicators
    - user_satisfaction: based on positive emotion trends
    """
    if not interaction_history:
        return {
            "response_quality": 0.0,
            "task_completion": 0.0,
            "user_satisfaction": 0.0
        }
    
    recent_interactions = interaction_history[-20:] if len(interaction_history) > 20 else interaction_history
    
    # Calculate response quality from sentiment confidence
    confidences = []
    for entry in recent_interactions:
        sentiment = entry.get('sentiment', {})
        confidence = sentiment.get('confidence', 0.5)
        confidences.append(confidence)
    
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5
    response_quality = min(1.0, avg_confidence * 1.2)  # Scale to 0-1
    
    # Calculate task completion from emotional state trends
    # High positive emotions (joy, satisfaction) indicate successful interactions
    completion_scores = []
    for entry in recent_interactions:
        emotional_snapshot = entry.get('emotional_state_snapshot', {})
        primary = emotional_snapshot.get('primary_emotions', {})
        # Score based on positive emotions
        joy = primary.get('joy', 0)
        trust = primary.get('trust', 0)
        # Low negative emotions also indicate success
        sadness = primary.get('sadness', 0)
        anger = primary.get('anger', 0)
        
        completion_score = (joy + trust + (1 - sadness) + (1 - anger)) / 4
        completion_scores.append(completion_score)
    
    avg_completion = sum(completion_scores) / len(completion_scores) if completion_scores else 0.5
    task_completion = min(1.0, avg_completion * 1.1)
    
    # Calculate user satisfaction from complex emotions
    satisfaction_scores = []
    for entry in recent_interactions:
        emotional_snapshot = entry.get('emotional_state_snapshot', {})
        complex_emotions = emotional_snapshot.get('complex_emotions', {})
        satisfaction = complex_emotions.get('satisfaction', 0)
        excitement = complex_emotions.get('excitement', 0)
        flow_state = complex_emotions.get('flow_state', 0)
        frustration = complex_emotions.get('frustration', 0)
        confusion = complex_emotions.get('confusion', 0)
        
        # High satisfaction, excitement, flow_state = high user satisfaction
        # Low frustration, confusion = high user satisfaction
        satisfaction_score = (satisfaction + excitement + flow_state + (1 - frustration) + (1 - confusion)) / 5
        satisfaction_scores.append(satisfaction_score)
    
    avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else 0.5
    user_satisfaction = min(1.0, avg_satisfaction * 1.15)
    
    return {
        "response_quality": round(response_quality, 2),
        "task_completion": round(task_completion, 2),
        "user_satisfaction": round(user_satisfaction, 2)
    }


def calculate_emotion_performance_correlations(interaction_history: list) -> Dict[str, float]:
    """
    Calculate REAL correlations between emotions and performance metrics.
    
    Uses statistical correlation between emotion intensities and success indicators.
    """
    if not interaction_history or len(interaction_history) < 5:
        return {
            "joy_response_quality": 0.0,
            "curiosity_task_completion": 0.0,
            "trust_user_satisfaction": 0.0,
            "flow_state_performance": 0.0
        }
    
    recent_interactions = interaction_history[-30:] if len(interaction_history) > 30 else interaction_history
    
    # Extract emotion values and performance indicators
    joy_values = []
    curiosity_values = []
    trust_values = []
    flow_state_values = []
    satisfaction_values = []
    
    for entry in recent_interactions:
        emotional_snapshot = entry.get('emotional_state_snapshot', {})
        primary = emotional_snapshot.get('primary_emotions', {})
        complex_emotions = emotional_snapshot.get('complex_emotions', {})
        sentiment = entry.get('sentiment', {})
        
        joy_values.append(primary.get('joy', 0))
        curiosity_values.append(primary.get('curiosity', 0))
        trust_values.append(primary.get('trust', 0))
        flow_state_values.append(complex_emotions.get('flow_state', 0))
        satisfaction_values.append(sentiment.get('confidence', 0.5))
    
    # Calculate simple correlation (covariance / variance)
    def calculate_correlation(x: list, y: list) -> float:
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        n = len(x)
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        
        covariance = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        variance_x = sum((x[i] - mean_x) ** 2 for i in range(n))
        variance_y = sum((y[i] - mean_y) ** 2 for i in range(n))
        
        if variance_x == 0 or variance_y == 0:
            return 0.0
        
        correlation = covariance / (variance_x * variance_y) ** 0.5
        return max(-1.0, min(1.0, correlation))  # Clamp to [-1, 1]
    
    joy_response_quality = calculate_correlation(joy_values, satisfaction_values)
    curiosity_task_completion = calculate_correlation(curiosity_values, satisfaction_values)
    trust_user_satisfaction = calculate_correlation(trust_values, satisfaction_values)
    flow_state_performance = calculate_correlation(flow_state_values, satisfaction_values)
    
    return {
        "joy_response_quality": round(joy_response_quality, 2),
        "curiosity_task_completion": round(curiosity_task_completion, 2),
        "trust_user_satisfaction": round(trust_user_satisfaction, 2),
        "flow_state_performance": round(flow_state_performance, 2)
    }


def calculate_memory_patterns(interaction_history: list, current_emotions: Dict) -> Dict[str, Any]:
    """
    Calculate REAL memory patterns from historical data.
    
    Analyzes trends, volatility, and dominant emotion evolution.
    """
    if not interaction_history or len(interaction_history) < 3:
        return {
            "dominant_trend": "insufficient_data",
            "volatility_index": 0.0,
            "trend_direction": "stable",
            "dominant_emotion_stability": 0.0
        }
    
    recent_history = interaction_history[-50:] if len(interaction_history) > 50 else interaction_history
    
    # Calculate volatility (standard deviation of emotional changes)
    emotion_changes = []
    for i in range(1, len(recent_history)):
        prev_emotions = recent_history[i-1].get('emotional_state_snapshot', {}).get('primary_emotions', {})
        curr_emotions = recent_history[i].get('emotional_state_snapshot', {}).get('primary_emotions', {})
        
        # Calculate total emotional change
        change = sum(abs(curr_emotions.get(emotion, 0) - prev_emotions.get(emotion, 0)) 
                    for emotion in ['joy', 'sadness', 'anger', 'fear', 'trust', 'curiosity'])
        emotion_changes.append(change)
    
    volatility_index = sum(emotion_changes) / len(emotion_changes) if emotion_changes else 0.0
    volatility_index = min(1.0, volatility_index / 3)  # Normalize
    
    # Determine trend direction
    first_half = recent_history[:len(recent_history)//2]
    second_half = recent_history[len(recent_history)//2:]
    
    first_positivity = sum(
        entry.get('emotional_state_snapshot', {}).get('primary_emotions', {}).get('joy', 0) +
        entry.get('emotional_state_snapshot', {}).get('complex_emotions', {}).get('satisfaction', 0)
        for entry in first_half
    ) / len(first_half) if first_half else 0
    
    second_positivity = sum(
        entry.get('emotional_state_snapshot', {}).get('primary_emotions', {}).get('joy', 0) +
        entry.get('emotional_state_snapshot', {}).get('complex_emotions', {}).get('satisfaction', 0)
        for entry in second_half
    ) / len(second_half) if second_half else 0
    
    if second_positivity > first_positivity + 0.1:
        trend_direction = "increasing_satisfaction"
    elif second_positivity < first_positivity - 0.1:
        trend_direction = "decreasing_satisfaction"
    else:
        trend_direction = "stable"
    
    # Calculate dominant emotion stability
    dominant_emotions = []
    for entry in recent_history:
        primary = entry.get('emotional_state_snapshot', {}).get('primary_emotions', {})
        if primary:
            dominant = max(primary.items(), key=lambda x: x[1])[0]
            dominant_emotions.append(dominant)
    
    if dominant_emotions:
        most_common = max(set(dominant_emotions), key=dominant_emotions.count)
        stability = dominant_emotions.count(most_common) / len(dominant_emotions)
    else:
        stability = 0.0
    
    return {
        "dominant_trend": trend_direction,
        "volatility_index": round(volatility_index, 2),
        "trend_direction": trend_direction,
        "dominant_emotion_stability": round(stability, 2)
    }


def calculate_emotional_balance(current_emotions: Dict) -> float:
    """
    Calculate emotional balance score.
    
    Higher when positive emotions dominate over negative ones.
    """
    positive = current_emotions.get('joy', 0) + current_emotions.get('trust', 0) + current_emotions.get('curiosity', 0)
    negative = current_emotions.get('sadness', 0) + current_emotions.get('anger', 0) + current_emotions.get('fear', 0)
    
    total = positive + negative
    if total == 0:
        return 0.5
    
    # Balance: 0.5 is neutral, > 0.5 is positive dominant, < 0.5 is negative dominant
    balance = positive / total
    return round(min(1.0, max(0.0, balance)), 2)


def generate_scatter_data(interaction_history: list) -> Dict[str, list]:
    """
    Generate REAL scatter plot data from interaction history.
    
    Returns joy vs curiosity correlation data points.
    """
    if not interaction_history or len(interaction_history) < 3:
        # Return current state as single point if no history
        return {
            'joy': [0.5],
            'curiosity': [0.5]
        }
    
    # Use recent interactions for scatter plot
    recent = interaction_history[-20:] if len(interaction_history) > 20 else interaction_history
    
    joy_values = []
    curiosity_values = []
    
    for entry in recent:
        emotional_snapshot = entry.get('emotional_state_snapshot', {})
        primary = emotional_snapshot.get('primary_emotions', {})
        
        joy = primary.get('joy', 0)
        curiosity = primary.get('curiosity', 0)
        
        # Only add points where we have meaningful data
        if joy > 0 or curiosity > 0:
            joy_values.append(round(joy, 2))
            curiosity_values.append(round(curiosity, 2))
    
    # Ensure we have at least some data points
    if not joy_values:
        joy_values = [0.5]
        curiosity_values = [0.5]
    
    return {
        'joy': joy_values,
        'curiosity': curiosity_values
    }


def generate_area_chart_data(interaction_history: list) -> tuple:
    """
    Generate REAL area chart data from interaction history.
    
    Returns labels and data for joy, sadness, curiosity over time.
    """
    if not interaction_history or len(interaction_history) < 2:
        # Return empty structure with current time
        from datetime import datetime
        now = datetime.now()
        labels = [now.strftime('%H:%M')]
        data = [
            [0.5],  # Joy
            [0.1],  # Sadness
            [0.3]   # Curiosity
        ]
        return labels, data
    
    # Use last 7 interactions or fewer
    recent = interaction_history[-7:] if len(interaction_history) > 7 else interaction_history
    
    labels = []
    joy_data = []
    sadness_data = []
    curiosity_data = []
    
    for entry in recent:
        # Extract timestamp
        timestamp = entry.get('timestamp', '')
        if timestamp:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                labels.append(dt.strftime('%H:%M'))
            except:
                labels.append('??:??')
        else:
            labels.append('??:??')
        
        # Extract emotions
        emotional_snapshot = entry.get('emotional_state_snapshot', {})
        primary = emotional_snapshot.get('primary_emotions', {})
        
        joy_data.append(round(primary.get('joy', 0) * 100, 1))  # Scale to percentage
        sadness_data.append(round(primary.get('sadness', 0) * 100, 1))
        curiosity_data.append(round(primary.get('curiosity', 0) * 100, 1))
    
    # If we have fewer than 7 points, pad with current state
    while len(labels) < 7:
        labels.append('Now')
        joy_data.append(joy_data[-1] if joy_data else 50)
        sadness_data.append(sadness_data[-1] if sadness_data else 10)
        curiosity_data.append(curiosity_data[-1] if curiosity_data else 30)
    
    data = [joy_data, sadness_data, curiosity_data]
    
    return labels, data


def generate_dashboard_data() -> Dict[str, Any]:
    """
    Generate data for the web dashboard.

    Returns:
        Dashboard data dictionary
    """
    # Get real emotion data from the engine
    engine = get_emotion_engine()
    if engine and EMOTION_ENGINE_AVAILABLE:
        try:
            state = engine.get_emotional_state()
            current_emotions = state.get('primary_emotions', {})
            complex_emotions = state.get('complex_emotions', {})
            
            # Access interaction history for real metrics calculation
            interaction_history = getattr(engine, 'interaction_history', [])
            
            # Generate timeline data from recent history
            timeline_labels = []
            timeline_data = [[], []]  # Joy and Sadness over time
            if interaction_history:
                recent_history = interaction_history[-20:] if len(interaction_history) > 20 else interaction_history
                for entry in recent_history:
                    # Extract timestamp for label
                    ts = entry.get('timestamp', '')
                    if ts:
                        try:
                            from datetime import datetime
                            dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                            timeline_labels.append(dt.strftime('%H:%M'))
                        except:
                            timeline_labels.append('??:??')
                    else:
                        timeline_labels.append('??:??')
                    
                    emotional_snapshot = entry.get('emotional_state_snapshot', {})
                    primary_emotions = emotional_snapshot.get('primary_emotions', {})
                    timeline_data[0].append(primary_emotions.get('joy', 0))
                    timeline_data[1].append(primary_emotions.get('sadness', 0))
            else:
                # No real history, use current state as single point
                from datetime import datetime
                timeline_labels = [datetime.now().strftime('%H:%M')]
                timeline_data = [
                    [current_emotions.get('joy', 0)], 
                    [current_emotions.get('sadness', 0)]
                ]
            
            # Calculate REAL performance metrics from interaction history
            performance_metrics = calculate_performance_metrics(interaction_history)
            
            # Calculate REAL correlations between emotions and performance
            correlations = calculate_emotion_performance_correlations(interaction_history)
            
            # Calculate REAL memory patterns
            memory_patterns = calculate_memory_patterns(interaction_history, current_emotions)
            
            # Calculate emotional balance from current state
            emotional_balance = calculate_emotional_balance(current_emotions)
            
            return {
                "current_emotions": current_emotions,
                "complex_emotions": complex_emotions,
                "timeline_data": timeline_data,
                "timeline_labels": timeline_labels,
                "emotional_balance": emotional_balance,
                "recent_history": [
                    {
                        "timestamp": entry.get('timestamp'),
                        "joy": entry.get('emotional_state_snapshot', {}).get('primary_emotions', {}).get('joy', 0),
                        "sadness": entry.get('emotional_state_snapshot', {}).get('primary_emotions', {}).get('sadness', 0)
                    }
                    for entry in interaction_history[-10:]
                ] if interaction_history else [],
                "performance_metrics": performance_metrics,
                "correlations": correlations,
                "memory_patterns": memory_patterns,
                "meta_cognitive_state": state.get('meta_cognitive_state', {
                    "self_awareness": 0.5,
                    "emotional_reflection": 0.5,
                    "learning_adaptation": 0.5,
                    "pattern_recognition": 0.5
                })
            }
        except Exception as e:
            logger.warning(f"Failed to get real emotion data: {e}")
    
    # Fallback mock data
    return {
        "current_emotions": {
            "joy": 0.0,
            "curiosity": 0.0,
            "satisfaction": 0.0,
            "sadness": 0.0,
            "anger": 0.0
        },
        "complex_emotions": {
            "flow_state": 0.0,
            "anticipation": 0.0,
            "excitement": 0.0,
            "frustration": 0.0
        },
        "timeline_data": [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]],
        "emotional_balance": 0.0,
        "recent_history": [
            {"timestamp": "2024-01-01T10:00:00", "emotions": {"joy": 0.0, "curiosity": 0.0}},
            {"timestamp": "2024-01-01T11:00:00", "emotions": {"joy": 0.0, "satisfaction": 0.0}}
        ],
        "performance_metrics": {
            "response_quality": 0.0,
            "task_completion": 0.0,
            "user_satisfaction": 0.0
        },
        "correlations": {
            "joy_response_quality": 0.0,
            "curiosity_task_completion": 0.0
        },
        "memory_patterns": {
            "dominant_trend": "stable",
            "volatility_index": 0.0
        },
        "meta_cognitive_state": {
            "self_awareness": 0.0,
            "emotional_reflection": 0.0,
            "learning_adaptation": 0.0,
            "pattern_recognition": 0.0
        }
    }


def process_proactive_trigger(engine) -> Optional[Dict[str, Any]]:
    """
    Processa un trigger proattivo: genera e invia messaggio se necessario.
    
    Args:
        engine: Istanza di EmotionEngine
        
    Returns:
        Dict con risultato dell'operazione o None se nessun trigger
    """
    if not engine or not hasattr(engine, 'proactive_manager') or not engine.proactive_manager:
        return None
    
    pm = engine.proactive_manager
    
    # Controlla se deve scattare trigger
    result = engine.check_proactive_trigger()
    
    if not result.get('should_trigger'):
        return None
    
    emotion = result['emotion']
    intensity = result['intensity']
    
    logger.info(f"Processing proactive trigger: {emotion} at {intensity:.2f}")
    
    try:
        # Determina canale e verifica target
        channel = pm.config.get('default_channel', 'telegram')
        target_key = f"{channel}_target"
        target = pm.config.get(target_key, '')
        
        if not target:
            logger.warning(f"Cannot send proactive message: target not configured for {channel}")
            logger.info(f"Configure with: /emotions proactive target {channel} <chat_id/phone>")
            return {
                "success": False,
                "emotion": emotion,
                "error": f"Target not configured for {channel}"
            }
        
        # Importa moduli necessari
        from tools.context_gatherer import ContextGatherer
        from tools.message_generator import LLMMessageGenerator
        from tools.channel_dispatcher import ChannelDispatcher
        
        # Crea istanze
        cg = ContextGatherer(pm.config)
        mg = LLMMessageGenerator()
        cd = ChannelDispatcher(pm.config)
        
        # Raccogli contesto
        context = cg.gather_context(emotion, intensity)
        
        # Genera messaggio
        message = mg.generate_message(emotion, context)
        
        # Invia messaggio con target
        send_result = cd.send_message(message, channel, target=target)
        
        if send_result['success']:
            # Marca come triggerato
            pm.mark_triggered(emotion, channel)
            
            logger.info(f"Proactive message sent successfully via {channel} to {target}")
            return {
                "success": True,
                "emotion": emotion,
                "intensity": intensity,
                "channel": channel,
                "target": target,
                "message": message[:100] + "..." if len(message) > 100 else message
            }
        else:
            logger.error(f"Failed to send proactive message: {send_result.get('error')}")
            return {
                "success": False,
                "emotion": emotion,
                "channel": channel,
                "target": target,
                "error": send_result.get('error', 'Unknown error')
            }
    
    except Exception as e:
        logger.error(f"Error processing proactive trigger: {e}")
        return {
            "success": False,
            "emotion": emotion,
            "error": str(e)
        }


def main():
    """Main entry point for the emotion-engine skill."""
    logger.info(f"Emotion engine started with command: {sys.argv}")

    parser = argparse.ArgumentParser(description='OpenClaw Emotional Intelligence System')
    parser.add_argument('command', help='Command or subcommand to execute')
    parser.add_argument('args', nargs='*', help='Command arguments')

    parsed_args = parser.parse_args()

    # List of valid subcommands that handle_emotions_command recognizes
    valid_subcommands = {
        'detailed', 'history', 'triggers', 'personality', 'metacognition',
        'predict', 'introspect', 'reset', 'export', 'config', 'version',
        'blend', 'memory', 'correlations', 'dashboard', 'simulate',
        'avatar', 'debug',
    }

    if parsed_args.command in ('emotions', 'emotion_engine', 'emotion-engine', '/emotions'):
        # Full format: emotion_tool.py emotions [subcommand] [args...]
        result = handle_emotions_command(parsed_args.args)
        print(result)
    elif parsed_args.command in valid_subcommands:
        # Direct subcommand: emotion_tool.py dashboard [args...]
        # OpenClaw dispatches commands this way
        result = handle_emotions_command([parsed_args.command] + parsed_args.args)
        print(result)
    else:
        print(f"❌ Unknown command: {parsed_args.command}")
        print("Available commands: emotions, " + ", ".join(sorted(valid_subcommands)))


class EmotionTool:
    """
    OpenClaw tool class for emotional intelligence system.
    """

    def __init__(self):
        self.name = "emotion_tool"
        self.description = "Main command handler for emotional intelligence system"

    def run(self, args):
        """
        OpenClaw tool run method.
        This method is called by OpenClaw when the skill is invoked.

        Args:
            args: List of command arguments, or a command string

        Returns:
            Command result as string
        """
        try:
            # Handle different input formats from OpenClaw
            if isinstance(args, str):
                # String input: "/emotions dashboard" or "dashboard"
                if args.startswith('/emotions'):
                    args = args[len('/emotions'):].strip().split()
                else:
                    args = args.split()
            elif not isinstance(args, list):
                args = [str(args)]

            return handle_emotions_command(args)
        except Exception as e:
            return f"❌ Error executing emotions command: {str(e)}\n\nPlease check that the emotional intelligence system is properly configured."

    def execute(self, args):
        """
        Alternative execute method for OpenClaw compatibility.
        """
        return self.run(args)


# Create a global instance for OpenClaw
emotion_tool = EmotionTool()

# Default export for OpenClaw
__openclaw_tool__ = emotion_tool


if __name__ == '__main__':
    main()