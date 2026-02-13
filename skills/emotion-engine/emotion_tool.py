#!/usr/bin/env python3
"""
Main command tool for the emotion-engine skill.
This file handles all slash commands for the emotional intelligence system.
"""

import sys
import json
import os
from typing import Dict, Any, List, Tuple
import argparse
import random
from datetime import datetime, timedelta
import threading
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs

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
        "dashboard": "User is excited about visual emotional monitoring and pleased with the interactive dashboard capabilities"
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
    except Exception as e:
        # Don't let emotion updates break the command
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


def handle_emotions_command(args: List[str]) -> str:
    """Handle the main /emotions command."""
    try:
        # Parse arguments to handle different calling conventions
        # OpenClaw might pass: ['/emotions', 'dashboard'] or just ['dashboard']
        original_args = args.copy()
        if len(args) > 0 and args[0].startswith('/emotions'):
            # Remove the command prefix if present
            args = args[1:] if len(args) > 1 else []

        # Dashboard command doesn't need the engine
        if len(args) > 0 and args[0] == 'dashboard':
            # Start web dashboard server
            try:
                server_thread = start_dashboard_server()
                if server_thread and server_thread.is_alive():
                    output = ["🌐 Web Dashboard Active", "=" * 25]
                    output.append(f"Dashboard is running at: http://{WEB_DASHBOARD['host']}:{WEB_DASHBOARD['port']}")
                else:
                    output = ["🌐 Web Dashboard Started", "=" * 25]
                    output.append(f"Dashboard server started at: http://{WEB_DASHBOARD['host']}:{WEB_DASHBOARD['port']}")

                output.append("")
                output.append("Available endpoints:")
                for endpoint, description in WEB_DASHBOARD['endpoints'].items():
                    output.append(f"  {endpoint} - {description}")
                output.append("")
                output.append("Open the URL above in your browser to view the dashboard.")

                # Update emotions for dashboard interaction
                update_emotions_from_interaction("dashboard", original_args, True)
                return '\n'.join(output)
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
                output.append(f"Prompt Modifier: {config.get('prompt_modifier_enabled', 'Unknown')}")

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

        else:
            return f"❌ Unknown emotions command: {args[0]}\n\nAvailable commands:\n  • /emotions\n  • /emotions detailed\n  • /emotions history [n]\n  • /emotions triggers\n  • /emotions personality\n  • /emotions metacognition\n  • /emotions predict [minutes]\n  • /emotions simulate <emotion> [intensity]\n  • /emotions reset [preserve-learning]\n  • /emotions export\n  • /emotions config\n  • /emotions version\n  • /emotions blend [emotion1] [emotion2]\n  • /emotions memory [days]\n  • /emotions correlations\n  • /emotions dashboard"

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
        dashboard_data = generate_dashboard_data()

        html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Emotion Engine Dashboard</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        .card {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        .card h3 {{
            margin-top: 0;
            color: #ffd700;
        }}
        .emotion-bar {{
            display: flex;
            align-items: center;
            margin: 10px 0;
        }}
        .emotion-label {{
            width: 120px;
            font-weight: bold;
        }}
        .emotion-value {{
            flex: 1;
            height: 20px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            overflow: hidden;
            margin-left: 10px;
        }}
        .emotion-fill {{
            height: 100%;
            background: linear-gradient(90deg, #4CAF50, #FFC107, #FF5722);
            border-radius: 10px;
        }}
        .metric {{
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 10px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
        }}
        .status {{
            text-align: center;
            margin-top: 20px;
            padding: 15px;
            background: rgba(0, 255, 0, 0.2);
            border-radius: 10px;
            border: 1px solid rgba(0, 255, 0, 0.3);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 Emotion Engine Dashboard</h1>
            <p>Real-time emotional intelligence monitoring</p>
        </div>

        <div class="dashboard-grid">
            <div class="card">
                <h3>Current Emotions</h3>"""

        # Generate emotion bars
        emotion_html = ""
        for emotion, intensity in dashboard_data['current_emotions'].items():
            emotion_html += f'''
                <div class="emotion-bar">
                    <span class="emotion-label">{emotion.title()}</span>
                    <div class="emotion-value">
                        <div class="emotion-fill" style="width: {intensity*100}%"></div>
                    </div>
                    <span>{intensity:.2f}</span>
                </div>'''

        html_template += emotion_html + """
            </div>

            <div class="card">
                <h3>Performance Metrics</h3>"""

        # Generate performance metrics
        metrics_html = ""
        for metric, value in dashboard_data['performance_metrics'].items():
            metrics_html += f'''
                <div class="metric">
                    <span>{metric.replace("_", " ").title()}</span>
                    <span>{value:.2f}</span>
                </div>'''

        html_template += metrics_html + """
            </div>

            <div class="card">
                <h3>Memory Patterns</h3>
                <div class="metric">
                    <span>Dominant Trend</span>
                    <span>""" + dashboard_data['memory_patterns']['dominant_trend'].replace("_", " ").title() + """</span>
                </div>
                <div class="metric">
                    <span>Volatility Index</span>
                    <span>""" + f"{dashboard_data['memory_patterns']['volatility_index']:.2f}" + """</span>
                </div>
            </div>

            <div class="card">
                <h3>System Status</h3>
                <div class="metric">
                    <span>History Entries</span>
                    <span>""" + str(len(dashboard_data['recent_history'])) + """</span>
                </div>
                <div class="metric">
                    <span>Active Correlations</span>
                    <span>""" + str(len(dashboard_data['correlations'])) + """</span>
                </div>
                <div class="metric">
                    <span>Version</span>
                    <span>""" + get_skill_version() + """</span>
                </div>
            </div>
        </div>

        <div class="status">
            <h3>✅ Dashboard Active</h3>
            <p>Emotion Engine is running and monitoring in real-time</p>
            <p>Last updated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
        </div>
    </div>
</body>
</html>"""

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_template.encode('utf-8'))

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

    if dashboard_server_thread and dashboard_server_thread.is_alive():
        return dashboard_server_thread  # Server already running

    def run_server():
        try:
            print(f"Starting server on {WEB_DASHBOARD['host']}:{WEB_DASHBOARD['port']}")
            with socketserver.TCPServer((WEB_DASHBOARD['host'], WEB_DASHBOARD['port']), DashboardHTTPRequestHandler) as httpd:
                print(f"🌐 Dashboard server started at http://{WEB_DASHBOARD['host']}:{WEB_DASHBOARD['port']}")
                httpd.serve_forever()
        except Exception as e:
            print(f"❌ Failed to start dashboard server: {e}")
            import traceback
            traceback.print_exc()

    dashboard_server_thread = threading.Thread(target=run_server, daemon=True)
    dashboard_server_thread.start()
    return dashboard_server_thread


def generate_dashboard_data() -> Dict[str, Any]:
    """
    Generate data for the web dashboard.

    Returns:
        Dashboard data dictionary
    """
    # This would integrate with the actual emotion engine
    # For now, return mock data structure
    return {
        "current_emotions": {
            "joy": 0.7,
            "curiosity": 0.6,
            "satisfaction": 0.4
        },
        "recent_history": [
            {"timestamp": "2024-01-01T10:00:00", "emotions": {"joy": 0.8, "curiosity": 0.5}},
            {"timestamp": "2024-01-01T11:00:00", "emotions": {"joy": 0.6, "satisfaction": 0.7}}
        ],
        "performance_metrics": {
            "response_quality": 0.85,
            "task_completion": 0.92,
            "user_satisfaction": 0.78
        },
        "correlations": {
            "joy_response_quality": 0.15,
            "curiosity_task_completion": 0.18
        },
        "memory_patterns": {
            "dominant_trend": "increasing_satisfaction",
            "volatility_index": 0.3
        }
    }


def main():
    """Main entry point for the emotion-engine skill."""
    parser = argparse.ArgumentParser(description='OpenClaw Emotional Intelligence System')
    parser.add_argument('command', help='Command or subcommand to execute')
    parser.add_argument('args', nargs='*', help='Command arguments')

    parsed_args = parser.parse_args()

    # List of valid subcommands that handle_emotions_command recognizes
    valid_subcommands = {
        'detailed', 'history', 'triggers', 'personality', 'metacognition',
        'predict', 'introspect', 'reset', 'export', 'config', 'version',
        'blend', 'memory', 'correlations', 'dashboard', 'simulate',
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