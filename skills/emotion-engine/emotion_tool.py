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

# Add the tools directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from tools.emotion_ml_engine import EmotionEngine
    from config.emotional_constants import (
        MIXED_EMOTIONS, BLENDING_RULES, LONG_TERM_MEMORY,
        PERFORMANCE_CORRELATIONS, WEB_DASHBOARD
    )
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

        elif args[0] == 'blend':
            # Blend emotions
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

        elif args[0] == 'dashboard':
            # Web dashboard data
            dashboard_data = generate_dashboard_data()

            output = ["🌐 Web Dashboard Data", "=" * 25]
            output.append("Current Emotions:")
            for emotion, intensity in dashboard_data['current_emotions'].items():
                output.append(f"  {emotion.capitalize()}: {intensity:.2f}")

            output.append("\nPerformance Metrics:")
            for metric, value in dashboard_data['performance_metrics'].items():
                output.append(f"  {metric.replace('_', ' ').title()}: {value:.2f}")

            output.append(f"\nRecent History Entries: {len(dashboard_data['recent_history'])}")
            output.append(f"Dashboard URL: http://localhost:{WEB_DASHBOARD['port']}")

            return '\n'.join(output)

        else:
            return f"❌ Unknown emotions command: {args[0]}\n\nAvailable commands:\n  • /emotions\n  • /emotions detailed\n  • /emotions history [n]\n  • /emotions triggers\n  • /emotions personality\n  • /emotions metacognition\n  • /emotions predict [minutes]\n  • /emotions simulate <emotion> [intensity]\n  • /emotions reset [preserve-learning]\n  • /emotions export\n  • /emotions config\n  • /emotions blend [emotion1] [emotion2]\n  • /emotions memory [days]\n  • /emotions correlations\n  • /emotions dashboard"

    except Exception as e:
        return f"❌ Error executing emotions command: {str(e)}\n\nPlease check that the emotional intelligence system is properly configured."


# Version 1.1.0 - Advanced Emotions Functions

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
    parser.add_argument('command', help='Command to execute')
    parser.add_argument('args', nargs='*', help='Command arguments')

    parsed_args = parser.parse_args()

    if parsed_args.command in ('emotions', 'emotion_engine', 'emotion-engine'):
        result = handle_emotions_command(parsed_args.args)
        print(result)
    else:
        print(f"❌ Unknown command: {parsed_args.command}")
        print("Available commands: emotions")


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
            args: List of command arguments

        Returns:
            Command result as string
        """
        try:
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