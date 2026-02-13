#!/usr/bin/env python3
"""
Main command tool for the emotion-engine skill.
This file handles all slash commands for the emotional intelligence system.
"""

import sys
import json
import os
from typing import Dict, Any, List
import argparse

# Add the tools directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from tools.emotion_ml_engine import EmotionEngine
except ImportError as e:
    print(f"Error importing emotion engine: {e}")
    print("Please ensure all dependencies are installed")
    sys.exit(1)


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
        if intensity > 0.1:  # Only show significant emotions
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
        engine = EmotionEngine()

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

            return '\n'.join(output)

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

            return '\n'.join(output)

        elif args[0] == 'history':
            # Show emotional history
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
            preserve_learning = len(args) > 1 and args[1] == 'preserve-learning'
            result = engine.reset_emotions(preserve_learning)

            output = ["🔄 Emotional State Reset", "=" * 25]
            output.append(f"Reset completed: {result['reset_completed']}")
            output.append(f"Learning preserved: {result['learning_preserved']}")
            output.append(f"New session ID: {result['new_session_id']}")

            return '\n'.join(output)

        elif args[0] == 'export':
            # Export emotional intelligence data
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

        else:
            return f"❌ Unknown emotions command: {args[0]}\n\nAvailable commands:\n  • /emotions\n  • /emotions detailed\n  • /emotions history [n]\n  • /emotions triggers\n  • /emotions personality\n  • /emotions metacognition\n  • /emotions predict [minutes]\n  • /emotions introspect [depth]\n  • /emotions reset [preserve-learning]\n  • /emotions export\n  • /emotions config"

    except Exception as e:
        return f"❌ Error executing emotions command: {str(e)}\n\nPlease check that the emotional intelligence system is properly configured."


def main():
    """Main entry point for the emotion-engine skill."""
    parser = argparse.ArgumentParser(description='OpenClaw Emotional Intelligence System')
    parser.add_argument('command', help='Command to execute')
    parser.add_argument('args', nargs='*', help='Command arguments')

    parsed_args = parser.parse_args()

    if parsed_args.command in ('emotions', 'emotion_engine', 'emotion-engine'):
        result = handle_emotions_command(parsed_args.args)
        print(result)
    else:
        print(f"❌ Unknown command: {parsed_args.command}")
        print("Available commands: emotions")


if __name__ == '__main__':
    main()