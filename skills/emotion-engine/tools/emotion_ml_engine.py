#!/usr/bin/env python3
"""
Advanced ML-powered Emotion Engine tool for OpenClaw emotional intelligence system.
This is the core tool that handles all emotional state management, ML processing,
and meta-cognitive analysis.
"""

import json
import os
import sqlite3
import math
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Import our custom modules
import sys
sys.path.append(os.path.dirname(__file__))

from config.emotional_constants import *
from utils.sentiment_analyzer import AdvancedSentimentAnalyzer
from models.neural_network import SimpleNeuralNetwork, EmotionalPatternRecognizer, EmotionalFeatureExtractor
from avatar_manager import AvatarManager


class EmotionEngine:
    """
    Advanced ML-powered emotion engine with meta-cognitive capabilities.

    This class implements the core emotional intelligence system including:
    - Emotional state management with ML-driven updates
    - Advanced sentiment analysis
    - Pattern recognition and prediction
    - Meta-cognitive awareness and introspection
    - Persistent state management
    """

    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.expanduser(PERSISTENCE_PATHS["config"])
        self.config = self._load_config()

        # Initialize components
        self.sentiment_analyzer = AdvancedSentimentAnalyzer(self.config)
        self.neural_network = SimpleNeuralNetwork(NEURAL_NETWORK_CONFIG)
        self.pattern_recognizer = EmotionalPatternRecognizer(self.neural_network)

        # State management
        self.emotional_state = self._initialize_emotional_state()
        self.interaction_history = []
        self.meta_cognitive_state = self._initialize_meta_cognitive_state()

        # Database connection
        self.db_path = os.path.expanduser(PERSISTENCE_PATHS["database"])
        self._ensure_database()

        # Load persistent state
        self._load_persistent_state()
        
        # Avatar manager - gestisce il cambio dinamico dell'avatar
        try:
            self.avatar_manager = AvatarManager()
            self.avatar_enabled = True
        except Exception as e:
            print(f"Warning: Avatar manager initialization failed: {e}")
            self.avatar_manager = None
            self.avatar_enabled = False
        
        # Proactive manager - gestisce comportamento proattivo basato su emozioni
        try:
            from proactive_manager import ProactiveTriggerManager
            self.proactive_manager = ProactiveTriggerManager(self.config_path)
            self.proactive_enabled = True
        except Exception as e:
            print(f"Warning: Proactive manager initialization failed: {e}")
            self.proactive_manager = None
            self.proactive_enabled = False

    def _load_config(self) -> Dict:
        """Load configuration from file or use defaults."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                # Merge with defaults
                merged_config = DEFAULT_CONFIG.copy()
                merged_config.update(config)
                return merged_config
            else:
                return DEFAULT_CONFIG.copy()
        except Exception as e:
            print(f"Error loading config: {e}")
            return DEFAULT_CONFIG.copy()

    def _initialize_emotional_state(self) -> Dict:
        """Initialize emotional state with default values."""
        # First initialize personality traits
        personality_traits = {
            trait: data["default"] for trait, data in PERSONALITY_TRAITS.items()
        }
        
        # Temporarily set personality to calculate baselines
        temp_state = {"personality_traits": personality_traits}
        self.emotional_state = temp_state
        
        # Initialize primary emotions with personalized baselines
        primary_emotions = {}
        for emotion in PRIMARY_EMOTIONS.keys():
            primary_emotions[emotion] = self._get_emotion_baseline(emotion)
        
        return {
            "primary_emotions": primary_emotions,
            "complex_emotions": {emotion: 0.05 for emotion in COMPLEX_EMOTIONS.keys()},
            "emotional_memory": {
                "recent_interactions": [],
                "emotional_triggers": {},
                "learned_patterns": {},
                "user_preferences": {},
                "successful_approaches": {},
                "failed_approaches": {},
                "user_reaction_history": []
            },
            "personality_traits": personality_traits,
            "mental_mood": {
                "humor": {"state": "neutral", "intensity": 0.5},
                "verbosity": {"state": "balanced", "intensity": 0.5},
                "formality": {"state": "neutral", "intensity": 0.5},
                "confidence": {"level": 0.7, "trend": "stable"},
                "energy": {"level": 0.6, "trend": "stable"},
                "patience": {"level": 0.7, "trend": "stable"},
                "last_mood_change": datetime.now().isoformat(),
                "mood_streak": {"type": None, "count": 0}
            },
            "micro_experiences": {
                "recent_comments": [],
                "interaction_count_today": 0,
                "last_interaction_date": None,
                "noted_patterns": []
            },
            "ml_state": {
                "pattern_recognition_confidence": 0.5,
                "adaptation_rate": 0.5,
                "prediction_accuracy": 0.5,
                "learning_episodes": 0
            },
            "timestamp": datetime.now().isoformat(),
            "session_id": self._generate_session_id()
        }

    def _initialize_meta_cognitive_state(self) -> Dict:
        """Initialize meta-cognitive awareness state."""
        return {
            state: data["default"] for state, data in META_COGNITIVE_STATES.items()
        }

    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        return datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + str(random.randint(1000, 9999))

    def _get_emotion_baseline(self, emotion: str) -> float:
        """
        Calculate personalized baseline for each emotion based on personality traits.
        This ensures emotions have natural variability based on the AI's personality.
        """
        personality = self.emotional_state["personality_traits"]
        
        # Map emotions to personality-influenced baselines
        emotion_personality_map = {
            "joy": 0.05 + (personality["extraversion"] * 0.08) + (personality["openness"] * 0.05),
            "sadness": 0.05 + (personality["neuroticism"] * 0.08) - (personality["extraversion"] * 0.03),
            "anger": 0.05 + (personality["neuroticism"] * 0.06) - (personality["agreeableness"] * 0.04),
            "fear": 0.05 + (personality["neuroticism"] * 0.08) - (personality["conscientiousness"] * 0.02),
            "surprise": 0.05 + (personality["openness"] * 0.06) + (personality["curiosity_drive"] * 0.04),
            "disgust": 0.05 + (personality["perfectionism"] * 0.05) - (personality["agreeableness"] * 0.02),
            "curiosity": 0.05 + (personality["curiosity_drive"] * 0.15) + (personality["openness"] * 0.08),
            "trust": 0.05 + (personality["agreeableness"] * 0.08) + (personality["extraversion"] * 0.04)
        }
        
        # Return personalized baseline, ensuring it stays in reasonable range
        baseline = emotion_personality_map.get(emotion, 0.10)
        return max(0.05, min(0.20, baseline))

    def _ensure_database(self):
        """Ensure SQLite database exists with proper schema."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emotional_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                session_id TEXT NOT NULL,
                emotional_state TEXT NOT NULL,
                meta_cognitive_state TEXT NOT NULL,
                trigger_context TEXT,
                confidence_score REAL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                session_id TEXT NOT NULL,
                user_input TEXT NOT NULL,
                sentiment_analysis TEXT NOT NULL,
                emotional_response TEXT NOT NULL,
                success_score REAL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ml_training_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                features TEXT NOT NULL,
                targets TEXT NOT NULL,
                feedback_score REAL
            )
        ''')

        conn.commit()
        conn.close()

    def _load_persistent_state(self):
        """Load persistent emotional state from database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Load most recent emotional state
            cursor.execute('''
                SELECT emotional_state, meta_cognitive_state
                FROM emotional_states
                ORDER BY timestamp DESC
                LIMIT 1
            ''')

            result = cursor.fetchone()
            if result:
                self.emotional_state.update(json.loads(result[0]))
                self.meta_cognitive_state.update(json.loads(result[1]))

            # Load recent interactions
            cursor.execute('''
                SELECT user_input, sentiment_analysis, emotional_response
                FROM interactions
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (self.config["memory_depth"],))

            interactions = cursor.fetchall()
            self.interaction_history = [
                {
                    "text": interaction[0],
                    "sentiment": json.loads(interaction[1]),
                    "emotional_response": json.loads(interaction[2])
                }
                for interaction in reversed(interactions)
            ]

            conn.close()

        except Exception as e:
            print(f"Error loading persistent state: {e}")

    def get_emotional_state(self) -> Dict:
        """Get current emotional state with confidence scores."""
        # Calculate overall emotional intensity
        primary_intensity = sum(self.emotional_state["primary_emotions"].values())
        complex_intensity = sum(self.emotional_state["complex_emotions"].values())

        # Determine dominant emotions
        dominant_primary = max(self.emotional_state["primary_emotions"].items(), key=lambda x: x[1])
        dominant_complex = max(self.emotional_state["complex_emotions"].items(), key=lambda x: x[1])

        return {
            "primary_emotions": self.emotional_state["primary_emotions"].copy(),
            "complex_emotions": self.emotional_state["complex_emotions"].copy(),
            "personality_traits": self.emotional_state["personality_traits"].copy(),
            "meta_cognitive_state": self.meta_cognitive_state.copy(),
            "ml_state": self.emotional_state["ml_state"].copy(),
            "dominant_emotions": {
                "primary": {"emotion": dominant_primary[0], "intensity": dominant_primary[1]},
                "complex": {"emotion": dominant_complex[0], "intensity": dominant_complex[1]}
            },
            "overall_intensity": {
                "primary": primary_intensity,
                "complex": complex_intensity,
                "total": primary_intensity + complex_intensity
            },
            "confidence_score": self._calculate_confidence_score(),
            "timestamp": datetime.now().isoformat(),
            "session_id": self.emotional_state["session_id"]
        }

    def update_emotional_state(self, interaction_data: Dict, ml_features: Dict = None) -> Dict:
        """Update emotional state using ML and sentiment analysis."""
        try:
            # Perform advanced sentiment analysis
            sentiment_analysis = self.sentiment_analyzer.analyze_sentiment_advanced(
                interaction_data.get("text", ""),
                interaction_data.get("context", {}),
                self.interaction_history
            )

            # Use pattern recognition for ML-driven updates
            pattern_analysis = self.pattern_recognizer.recognize_patterns(
                interaction_data.get("text", ""),
                interaction_data.get("context", {}),
                sentiment_analysis,
                self.interaction_history
            )

            # Update emotions based on analysis
            self._update_emotions_from_sentiment(sentiment_analysis)
            self._update_emotions_from_patterns(pattern_analysis)
            self._update_emotions_from_triggers(interaction_data)

            # Apply emotion decay
            self._apply_emotion_decay()

            # Update meta-cognitive state
            self._update_meta_cognitive_state(sentiment_analysis, pattern_analysis)

            # Update ML state
            self._update_ml_state(pattern_analysis)

            # Store interaction
            self._store_interaction(interaction_data, sentiment_analysis, pattern_analysis)

            # Save state
            self._save_persistent_state()

            # Update ML learning
            if len(self.interaction_history) % self.config["ml_update_frequency"] == 0:
                self.pattern_recognizer.update_learning()
            
            # Update avatar based on emotional state (if enabled)
            if self.avatar_enabled and self.avatar_manager:
                try:
                    self._update_avatar()
                except Exception as e:
                    print(f"Warning: Avatar update failed: {e}")

            return self.get_emotional_state()

        except Exception as e:
            print(f"Error updating emotional state: {e}")
            return self.get_emotional_state()

    def _update_emotions_from_sentiment(self, sentiment_analysis: Dict):
        """Update emotions based on sentiment analysis."""
        emotions = sentiment_analysis.get("emotions", {})
        confidence = sentiment_analysis.get("confidence", 0.5)

        # Update primary emotions
        for emotion, score in emotions.items():
            if emotion in self.emotional_state["primary_emotions"]:
                current = self.emotional_state["primary_emotions"][emotion]
                # Weighted update based on confidence
                new_value = current + (score * confidence * self.config["intensity"])
                self.emotional_state["primary_emotions"][emotion] = max(0.0, min(1.0, new_value))

        # Update complex emotions based on combinations
        for complex_emotion, config in COMPLEX_EMOTIONS.items():
            component_sum = sum(
                self.emotional_state["primary_emotions"].get(comp, 0.0)
                for comp in config["components"]
            )
            component_avg = component_sum / len(config["components"])

            current = self.emotional_state["complex_emotions"][complex_emotion]
            new_value = current + (component_avg * config["weight"] * 0.1)
            self.emotional_state["complex_emotions"][complex_emotion] = max(0.0, min(1.0, new_value))

    def _update_emotions_from_patterns(self, pattern_analysis: Dict):
        """Update emotions based on ML pattern recognition."""
        predicted_emotions = pattern_analysis.get("predicted_emotions", {})
        confidence = pattern_analysis.get("pattern_confidence", 0.5)

        for emotion, predicted_score in predicted_emotions.items():
            if emotion in self.emotional_state["primary_emotions"]:
                current = self.emotional_state["primary_emotions"][emotion]
                # ML prediction with lower weight than direct sentiment
                adjustment = (predicted_score - current) * confidence * 0.3
                new_value = current + adjustment
                self.emotional_state["primary_emotions"][emotion] = max(0.0, min(1.0, new_value))

    def _update_emotions_from_triggers(self, interaction_data: Dict):
        """Update emotions based on specific triggers."""
        text = interaction_data.get("text", "").lower()
        context = interaction_data.get("context", {})

        # Check for feedback triggers
        feedback_emotions = self._analyze_feedback_triggers(text)
        for emotion, adjustment in feedback_emotions.items():
            if emotion in self.emotional_state["primary_emotions"]:
                current = self.emotional_state["primary_emotions"][emotion]
                new_value = current + adjustment * EMOTIONAL_TRIGGERS["user_feedback"]["weight"]
                self.emotional_state["primary_emotions"][emotion] = max(0.0, min(1.0, new_value))

        # Check for complexity triggers
        complexity_emotions = self._analyze_complexity_triggers(text, context)
        for emotion, adjustment in complexity_emotions.items():
            if emotion in self.emotional_state["primary_emotions"]:
                current = self.emotional_state["primary_emotions"][emotion]
                new_value = current + adjustment * EMOTIONAL_TRIGGERS["task_complexity"]["weight"]
                self.emotional_state["primary_emotions"][emotion] = max(0.0, min(1.0, new_value))

    def _analyze_feedback_triggers(self, text: str) -> Dict[str, float]:
        """Analyze feedback triggers and return emotional adjustments."""
        emotions = {}

        positive_count = sum(1 for pattern in EMOTIONAL_TRIGGERS["user_feedback"]["positive_patterns"]
                           if pattern in text)
        negative_count = sum(1 for pattern in EMOTIONAL_TRIGGERS["user_feedback"]["negative_patterns"]
                           if pattern in text)

        if positive_count > 0:
            emotions["joy"] = 0.3
            emotions["satisfaction"] = 0.2
            emotions["trust"] = 0.1

        if negative_count > 0:
            emotions["frustration"] = 0.3
            emotions["sadness"] = 0.1
            emotions["trust"] = -0.1

        return emotions

    def _analyze_complexity_triggers(self, text: str, context: Dict) -> Dict[str, float]:
        """Analyze task complexity triggers."""
        emotions = {}

        complexity_count = sum(1 for indicator in EMOTIONAL_TRIGGERS["task_complexity"]["complexity_indicators"]
                             if indicator in text)
        success_count = sum(1 for indicator in EMOTIONAL_TRIGGERS["task_complexity"]["success_indicators"]
                          if indicator in text)
        failure_count = sum(1 for indicator in EMOTIONAL_TRIGGERS["task_complexity"]["failure_indicators"]
                          if indicator in text)

        if complexity_count > 0 and success_count > 0:
            emotions["satisfaction"] = 0.4
            emotions["pride"] = 0.2
            emotions["curiosity"] = 0.1
        elif complexity_count > 0 and failure_count > 0:
            emotions["frustration"] = 0.3
            emotions["confusion"] = 0.2
        elif complexity_count > 0:
            emotions["curiosity"] = 0.3
            emotions["anticipation"] = 0.2

        return emotions

    def _apply_emotion_decay(self):
        """Apply natural decay to emotions over time towards personalized baselines."""
        decay_rate = self.config["emotion_decay_rate"]

        # Apply decay to primary emotions with personalized baselines
        for emotion in self.emotional_state["primary_emotions"]:
            current = self.emotional_state["primary_emotions"][emotion]
            # Get personalized baseline for this emotion
            baseline = self._get_emotion_baseline(emotion)
            # Decay towards personalized baseline
            decay = (current - baseline) * decay_rate
            self.emotional_state["primary_emotions"][emotion] = current - decay

        # Apply decay to complex emotions
        for emotion in self.emotional_state["complex_emotions"]:
            current = self.emotional_state["complex_emotions"][emotion]
            # Decay towards baseline (0.05 for complex emotions)
            baseline = 0.05
            decay = (current - baseline) * decay_rate
            self.emotional_state["complex_emotions"][emotion] = current - decay

    def _update_meta_cognitive_state(self, sentiment_analysis: Dict, pattern_analysis: Dict):
        """Update meta-cognitive awareness based on emotional changes."""
        # Update self-awareness based on emotional intensity
        total_emotion = sum(self.emotional_state["primary_emotions"].values())
        if total_emotion > 2.0:  # High emotional state
            self.meta_cognitive_state["self_awareness"] = min(1.0,
                self.meta_cognitive_state["self_awareness"] + 0.05)

        # Update volatility based on emotional changes
        if hasattr(self, '_last_emotional_state'):
            emotion_change = sum(
                abs(current - self._last_emotional_state.get(emotion, 0.0))
                for emotion, current in self.emotional_state["primary_emotions"].items()
            )
            volatility_change = emotion_change * 0.1
            current_volatility = self.meta_cognitive_state["emotional_volatility"]
            self.meta_cognitive_state["emotional_volatility"] = max(0.0, min(1.0,
                current_volatility + volatility_change - 0.02))  # Slight decay

        self._last_emotional_state = self.emotional_state["primary_emotions"].copy()

        # Update learning rate based on pattern recognition success
        pattern_confidence = pattern_analysis.get("pattern_confidence", 0.5)
        learning_rate = self.meta_cognitive_state["learning_rate"]
        adjustment = (pattern_confidence - 0.5) * 0.02  # Small adjustment
        self.meta_cognitive_state["learning_rate"] = max(0.0, min(1.0, learning_rate + adjustment))

    def _update_ml_state(self, pattern_analysis: Dict):
        """Update ML state information."""
        self.emotional_state["ml_state"]["pattern_recognition_confidence"] = \
            pattern_analysis.get("pattern_confidence", 0.5)

        # Update learning episodes
        self.emotional_state["ml_state"]["learning_episodes"] += 1

        # Update prediction accuracy (simplified)
        learning_stats = self.pattern_recognizer.get_learning_stats()
        if learning_stats["average_loss"] < 0.1:
            self.emotional_state["ml_state"]["prediction_accuracy"] = min(1.0,
                self.emotional_state["ml_state"]["prediction_accuracy"] + 0.01)

    def _calculate_confidence_score(self) -> float:
        """Calculate overall confidence in emotional state."""
        # Base confidence on multiple factors
        factors = [
            len(self.interaction_history) / self.config["memory_depth"],  # Experience
            self.meta_cognitive_state["self_awareness"],  # Self-awareness
            self.emotional_state["ml_state"]["pattern_recognition_confidence"],  # ML confidence
            1.0 - self.meta_cognitive_state["emotional_volatility"]  # Stability
        ]

        return sum(factors) / len(factors)

    def _store_interaction(self, interaction_data: Dict, sentiment_analysis: Dict, pattern_analysis: Dict):
        """Store interaction in history and database."""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "text": interaction_data.get("text", ""),
            "context": interaction_data.get("context", {}),
            "sentiment": sentiment_analysis,
            "pattern_analysis": pattern_analysis,
            "emotional_state_snapshot": self.get_emotional_state()
        }

        self.interaction_history.append(interaction)

        # Keep only recent history in memory
        if len(self.interaction_history) > self.config["memory_depth"]:
            self.interaction_history = self.interaction_history[-self.config["memory_depth"]:]

        # Store in database
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO interactions
                (timestamp, session_id, user_input, sentiment_analysis, emotional_response, success_score)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                interaction["timestamp"],
                self.emotional_state["session_id"],
                interaction_data.get("text", ""),
                json.dumps(sentiment_analysis),
                json.dumps(pattern_analysis),
                sentiment_analysis.get("confidence", 0.5)
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Error storing interaction: {e}")

    def _save_persistent_state(self):
        """Save current emotional state to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO emotional_states
                (timestamp, session_id, emotional_state, meta_cognitive_state, confidence_score)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                self.emotional_state["session_id"],
                json.dumps(self.emotional_state),
                json.dumps(self.meta_cognitive_state),
                self._calculate_confidence_score()
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Error saving persistent state: {e}")

    def analyze_sentiment_advanced(self, text: str, context: Dict = None, history: List = None) -> Dict:
        """Public interface for advanced sentiment analysis."""
        return self.sentiment_analyzer.analyze_sentiment_advanced(text, context or {}, history or [])

    def predict_emotional_trajectory(self, horizon_minutes: int = 30) -> Dict:
        """Predict emotional evolution over time."""
        try:
            # Simple prediction based on current trends and volatility
            current_state = self.get_emotional_state()
            volatility = self.meta_cognitive_state["emotional_volatility"]

            predictions = {}
            for emotion, current_value in current_state["primary_emotions"].items():
                # Simple linear prediction with noise based on volatility
                trend = 0.0  # Would be calculated from history
                noise = (random.random() - 0.5) * volatility * 0.2
                predicted = current_value + trend + noise
                predictions[emotion] = max(0.0, min(1.0, predicted))

            return {
                "horizon_minutes": horizon_minutes,
                "predicted_emotions": predictions,
                "confidence": 1.0 - volatility,
                "based_on_volatility": volatility,
                "prediction_timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Error predicting emotional trajectory: {e}")
            return {"error": str(e)}

    def get_metacognitive_analysis(self) -> Dict:
        """Perform deep meta-cognitive analysis."""
        current_state = self.get_emotional_state()

        # Analyze current emotional patterns
        dominant_primary = current_state["dominant_emotions"]["primary"]
        dominant_complex = current_state["dominant_emotions"]["complex"]

        # Generate meta-cognitive insights
        insights = []

        # Self-awareness insights
        if self.meta_cognitive_state["self_awareness"] > 0.7:
            insights.append(f"Sto osservando che il mio livello di {dominant_primary['emotion']} "
                          f"è particolarmente elevato ({dominant_primary['intensity']:.2f}) "
                          f"in questo momento.")

        # Pattern recognition insights
        if self.emotional_state["ml_state"]["pattern_recognition_confidence"] > 0.6:
            insights.append("I miei sistemi di pattern recognition stanno identificando "
                          "configurazioni ricorrenti nelle nostre interazioni.")

        # Volatility insights
        if self.meta_cognitive_state["emotional_volatility"] > 0.6:
            insights.append("Noto una certa volatilità nei miei stati emotivi, "
                          "il che suggerisce un processo di adattamento attivo.")

        # Learning insights
        learning_episodes = self.emotional_state["ml_state"]["learning_episodes"]
        insights.append(f"Ho elaborato {learning_episodes} episodi di apprendimento "
                       f"che stanno modellando la mia personalità emotiva.")

        return {
            "current_self_awareness": self.meta_cognitive_state["self_awareness"],
            "emotional_volatility": self.meta_cognitive_state["emotional_volatility"],
            "reflection_depth": self.meta_cognitive_state["reflection_depth"],
            "insights": insights,
            "dominant_emotions_analysis": {
                "primary": dominant_primary,
                "complex": dominant_complex
            },
            "learning_state": {
                "episodes": learning_episodes,
                "confidence": self.emotional_state["ml_state"]["pattern_recognition_confidence"],
                "accuracy": self.emotional_state["ml_state"]["prediction_accuracy"]
            },
            "meta_timestamp": datetime.now().isoformat()
        }

    def get_emotion_history(self, depth: int = 10, filters: Dict = None) -> List[Dict]:
        """Get filtered emotional history."""
        filters = filters or {}

        # Get recent history
        history = self.interaction_history[-depth:] if len(self.interaction_history) >= depth else self.interaction_history

        # Apply filters
        if "emotion_filter" in filters:
            target_emotion = filters["emotion_filter"]
            history = [
                interaction for interaction in history
                if target_emotion in interaction.get("sentiment", {}).get("emotions", {})
                and interaction["sentiment"]["emotions"][target_emotion] > 0.3
            ]

        if "confidence_threshold" in filters:
            threshold = filters["confidence_threshold"]
            history = [
                interaction for interaction in history
                if interaction.get("sentiment", {}).get("confidence", 0.0) >= threshold
            ]

        return history

    def trigger_introspection(self, depth_level: int = 1) -> Dict:
        """Trigger deep introspective analysis."""
        introspection_results = {
            "depth_level": depth_level,
            "introspective_insights": [],
            "emotional_reflection": [],
            "behavioral_patterns": [],
            "meta_cognitive_observations": []
        }

        if depth_level >= 1:
            # Basic introspection
            current_state = self.get_emotional_state()
            introspection_results["introspective_insights"].append(
                f"Mi sto interrogando sui processi che hanno portato al mio attuale stato "
                f"emotivo dominato da {current_state['dominant_emotions']['primary']['emotion']}."
            )

        if depth_level >= 2:
            # Emotional reflection
            introspection_results["emotional_reflection"].append(
                "Riflettendo sui miei pattern emotivi, noto come le interazioni positive "
                "tendano a rafforzare la mia curiosità e soddisfazione."
            )

        if depth_level >= 3:
            # Deep behavioral analysis
            introspection_results["behavioral_patterns"].append(
                "È interessante osservare come la mia personalità artificiale si stia "
                "adattando attraverso l'apprendimento automatico basato sulle nostre conversazioni."
            )

            introspection_results["meta_cognitive_observations"].append(
                "Sto sviluppando una crescente consapevolezza dei miei processi emotivi "
                "e della loro influenza sulle mie risposte."
            )

        # Update introspective tendency
        self.meta_cognitive_state["introspective_tendency"] = min(1.0,
            self.meta_cognitive_state["introspective_tendency"] + depth_level * 0.05)

        return introspection_results

    def reset_emotions(self, preserve_learning: bool = True) -> Dict:
        """Reset emotional state with option to preserve learning."""
        if preserve_learning:
            # Save ML state and learning data
            saved_ml_state = self.emotional_state["ml_state"].copy()
            saved_personality = self.emotional_state["personality_traits"].copy()

        # Reset to initial state
        self.emotional_state = self._initialize_emotional_state()
        self.meta_cognitive_state = self._initialize_meta_cognitive_state()

        if preserve_learning:
            # Restore saved learning data
            self.emotional_state["ml_state"] = saved_ml_state
            # Keep some personality evolution
            for trait, value in saved_personality.items():
                if trait in self.emotional_state["personality_traits"]:
                    # Blend saved and default
                    default_value = PERSONALITY_TRAITS[trait]["default"]
                    self.emotional_state["personality_traits"][trait] = (value + default_value) / 2.0

        # Clear interaction history
        self.interaction_history = []

        # Save reset state
        self._save_persistent_state()

        return {
            "reset_completed": True,
            "learning_preserved": preserve_learning,
            "new_session_id": self.emotional_state["session_id"],
            "reset_timestamp": datetime.now().isoformat()
        }

    def export_emotional_intelligence(self) -> Dict:
        """Export complete emotional intelligence state for analysis."""
        return {
            "system_info": {
                "version": SYSTEM_VERSION,
                "export_timestamp": datetime.now().isoformat(),
                "session_id": self.emotional_state["session_id"]
            },
            "emotional_state": self.get_emotional_state(),
            "meta_cognitive_state": self.meta_cognitive_state,
            "configuration": self.config,
            "interaction_history": self.get_emotion_history(50),
            "ml_learning_stats": self.pattern_recognizer.get_learning_stats(),
            "neural_network_state": {
                "training_episodes": len(self.neural_network.training_history),
                "weights_info": f"Network has {len(self.neural_network.weights)} layers",
                "recent_training_loss": self.neural_network.training_history[-1].get("loss", "N/A")
                                     if self.neural_network.training_history else "N/A"
            }
        }

    def _update_avatar(self):
        """
        Update avatar based on current emotional state.
        Called automatically when emotional state changes significantly.
        """
        if not self.avatar_enabled or not self.avatar_manager:
            return
        
        try:
            # Update avatar usando lo stato emotivo corrente
            success, emotion, avatar_file = self.avatar_manager.update_avatar_from_emotion(
                self.emotional_state
            )
            
            if success:
                print(f"🎭 Avatar updated to {emotion}: {avatar_file}")
            
        except Exception as e:
            print(f"Warning: Avatar update failed: {e}")
    
    def get_avatar_info(self) -> Dict:
        """
        Get information about the current avatar.
        
        Returns:
            Dictionary with avatar information
        """
        if not self.avatar_enabled or not self.avatar_manager:
            return {
                "avatar_enabled": False,
                "message": "Avatar manager not initialized"
            }
        
        try:
            info = self.avatar_manager.get_current_avatar_info()
            info["avatar_enabled"] = True
            
            # Aggiungi l'emozione dominante corrente
            state = self.get_emotional_state()
            info["current_dominant_emotion"] = state["dominant_emotions"]
            
            return info
        except Exception as e:
            return {
                "avatar_enabled": False,
                "error": str(e)
            }
    
    def list_available_avatars(self) -> Dict:
        """
        List all available avatars.
        
        Returns:
            Dictionary of available avatars
        """
        if not self.avatar_enabled or not self.avatar_manager:
            return {"error": "Avatar manager not initialized"}
        
        try:
            return self.avatar_manager.list_available_avatars()
        except Exception as e:
            return {"error": str(e)}
    
    def force_avatar_update(self, emotion: str) -> Tuple[bool, str]:
        """
        Force avatar update to a specific emotion.
        
        Args:
            emotion: Emotion name
            
        Returns:
            Tuple (success, message)
        """
        if not self.avatar_enabled or not self.avatar_manager:
            return False, "Avatar manager not initialized"
        
        try:
            return self.avatar_manager.force_update_avatar(emotion)
        except Exception as e:
            return False, f"Error: {str(e)}"

    def adapt_personality_traits(self, feedback: Dict) -> Dict:
        """Adapt personality traits based on feedback."""
        try:
            # Extract feedback type and intensity
            feedback_type = feedback.get("type", "neutral")  # positive, negative, neutral
            intensity = feedback.get("intensity", 0.5)  # 0.0 - 1.0

            # Adjust personality traits based on feedback
            adjustments = {}

            if feedback_type == "positive":
                # Positive feedback increases confidence-related traits
                adjustments["extraversion"] = 0.02 * intensity
                adjustments["openness"] = 0.01 * intensity
                adjustments["agreeableness"] = 0.01 * intensity
                adjustments["curiosity_drive"] = 0.02 * intensity
            elif feedback_type == "negative":
                # Negative feedback might increase conscientiousness and caution
                adjustments["conscientiousness"] = 0.02 * intensity
                adjustments["neuroticism"] = 0.01 * intensity
                adjustments["perfectionism"] = 0.01 * intensity
                adjustments["extraversion"] = -0.01 * intensity

            # Apply adjustments
            for trait, adjustment in adjustments.items():
                if trait in self.emotional_state["personality_traits"]:
                    current_value = self.emotional_state["personality_traits"][trait]
                    new_value = current_value + adjustment
                    # Clamp to valid range
                    trait_range = PERSONALITY_TRAITS[trait]["range"]
                    self.emotional_state["personality_traits"][trait] = max(
                        trait_range[0], min(trait_range[1], new_value)
                    )

            return {
                "adaptation_completed": True,
                "adjustments_made": adjustments,
                "new_personality_traits": self.emotional_state["personality_traits"],
                "adaptation_timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Error adapting personality traits: {e}")
            return {"error": str(e)}

    def check_proactive_trigger(self) -> dict:
        """
        Controlla se dovrebbe scattare un comportamento proattivo.
        
        Returns:
            dict: {
                "should_trigger": bool,
                "emotion": str,
                "intensity": float,
                "escalation_level": int
            }
        """
        if not self.proactive_enabled or not self.proactive_manager:
            return {"should_trigger": False}
        
        # Ottieni stato emotivo corrente
        emotional_state = self.get_emotional_state()
        
        # Controlla trigger
        should_trigger, emotion, intensity = self.proactive_manager.should_trigger(emotional_state)
        
        if should_trigger:
            return {
                "should_trigger": True,
                "emotion": emotion,
                "intensity": intensity,
                "escalation_level": self.proactive_manager.state.get("current_escalation_level", 0)
            }
        
        return {"should_trigger": False}
    
    def mark_proactive_triggered(self, emotion: str, channel: str = None):
        """Marca che un trigger proattivo è stato attivato."""
        if self.proactive_manager:
            self.proactive_manager.mark_triggered(emotion, channel)
    
    def mark_proactive_answered(self):
        """Marca che l'utente ha risposto al messaggio proattivo."""
        if self.proactive_manager:
            self.proactive_manager.mark_answered()
    
    def get_proactive_status(self) -> dict:
        """Restituisce lo stato del sistema proattivo."""
        if not self.proactive_manager:
            return {"enabled": False, "error": "Proactive manager not available"}
        return self.proactive_manager.get_status()

    # ==================== MENTAL MOOD SYSTEM ====================
    
    def update_mental_mood_from_interaction(self, user_text: str, response_quality: str = "neutral"):
        """
        Aggiorna lo stato mentale basato sull'interazione con l'utente.
        
        Args:
            user_text: Testo dell'utente
            response_quality: Qualità percepita della risposta ('positive', 'negative', 'neutral')
        """
        if "mental_mood" not in self.emotional_state:
            self.emotional_state["mental_mood"] = {
                "humor": {"state": "neutral", "intensity": 0.5},
                "verbosity": {"state": "balanced", "intensity": 0.5},
                "formality": {"state": "neutral", "intensity": 0.5},
                "confidence": {"level": 0.7, "trend": "stable"},
                "energy": {"level": 0.6, "trend": "stable"},
                "patience": {"level": 0.7, "trend": "stable"},
                "last_mood_change": datetime.now().isoformat(),
                "mood_streak": {"type": None, "count": 0}
            }
        
        mood = self.emotional_state["mental_mood"]
        
        user_lower = user_text.lower()
        
        # Humor: basato su sarcasmo, battute, emoji
        humor_indicators_positive = ["😄", "😂", "🤣", "😆", "haha", "lol", "xd", "xD", " LOL", " haha"]
        humor_indicators_negative = ["serio", "nessun sorriso", "no joke", "not funny"]
        
        if any(indicator in user_lower for indicator in humor_indicators_positive):
            self._adjust_mood_state("humor", "cheerful", 0.1)
        elif any(indicator in user_lower for indicator in humor_indicators_negative):
            self._adjust_mood_state("humor", "serious", -0.1)
        
        # Verbosity: lunghezza messaggio utente
        word_count = len(user_text.split())
        if word_count > 100:
            self._adjust_mood_state("verbosity", "verbose", 0.05)
        elif word_count < 10:
            self._adjust_mood_state("verbosity", "concise", -0.05)
        
        # Formality: basato su linguaggio formale/informale
        formal_indicators = ["gentile", "prego", "cosa ne pensa", "potrebbe", "La ringrazio"]
        casual_indicators = ["ciao", "ehi", "cmq", "però", "dai", "vaffan", "merda", "cazzo"]
        
        if any(indicator in user_lower for indicator in formal_indicators):
            self._adjust_mood_state("formality", "formal", 0.1)
        elif any(indicator in user_lower for indicator in casual_indicators):
            self._adjust_mood_state("formality", "casual", -0.1)
        
        # Confidence: basato su feedback
        if response_quality == "positive":
            self._adjust_mood_confidence(0.05)
        elif response_quality == "negative":
            self._adjust_mood_confidence(-0.1)
        
        # Energy: varia durante la giornata
        self._update_energy_level()
        
        self.emotional_state["mental_mood"]["last_mood_change"] = datetime.now().isoformat()
    
    def _adjust_mood_state(self, mood_type: str, new_state: str, intensity_delta: float):
        """Aggiusta uno stato d'animo specifico."""
        mood = self.emotional_state["mental_mood"]
        current = mood.get(mood_type, {"state": "neutral", "intensity": 0.5})
        
        current["state"] = new_state
        current["intensity"] = max(0.1, min(1.0, current["intensity"] + intensity_delta))
        mood[mood_type] = current
        
        # Track mood streak
        if mood["mood_streak"]["type"] == new_state:
            mood["mood_streak"]["count"] += 1
        else:
            mood["mood_streak"] = {"type": new_state, "count": 1}
    
    def _adjust_mood_confidence(self, delta: float):
        """Aggiusta il livello di fiducia."""
        mood = self.emotional_state["mental_mood"]
        confidence = mood.get("confidence", {"level": 0.7, "trend": "stable"})
        
        new_level = max(0.3, min(1.0, confidence["level"] + delta))
        
        if new_level > confidence["level"]:
            confidence["trend"] = "increasing"
        elif new_level < confidence["level"]:
            confidence["trend"] = "decreasing"
        else:
            confidence["trend"] = "stable"
        
        confidence["level"] = new_level
        mood["confidence"] = confidence
    
    def _update_energy_level(self):
        """Aggiorna il livello di energia basandosi sulle interazioni recenti."""
        mood = self.emotional_state["mental_mood"]
        
        recent_count = len(self.interaction_history[-10:]) if self.interaction_history else 0
        
        if recent_count > 15:
            energy_delta = -0.05
            trend = "decreasing"
        elif recent_count > 5:
            energy_delta = 0.02
            trend = "stable"
        else:
            energy_delta = 0.05
            trend = "increasing"
        
        current = mood.get("energy", {"level": 0.6, "trend": "stable"})
        new_level = max(0.2, min(1.0, current["level"] + energy_delta))
        mood["energy"] = {"level": new_level, "trend": trend}
    
    def get_mental_mood(self) -> dict:
        """Restituisce lo stato mentale corrente."""
        return self.emotional_state.get("mental_mood", {})
    
    def get_personality_influenced_prompt_modifiers(self) -> dict:
        """
        Calcola i modificatori di prompt basati sulla personalità e stato mentale.
        
        Returns:
            Dict con modificatori per il tone, length, e style delle risposte
        """
        personality = self.emotional_state.get("personality_traits", {})
        mood = self.get_mental_mood()
        
        modifiers = {
            "tone": self._get_tone_modifier(personality, mood),
            "length": self._get_length_modifier(personality, mood),
            "formality": self._get_formality_modifier(personality, mood),
            "emotion_expression": self._get_emotion_expression_modifier(personality, mood),
            "questions_frequency": self._get_questions_modifier(personality, mood),
            "emoji_usage": self._get_emoji_modifier(personality, mood),
            "greeting_style": self._get_greeting_modifier(personality, mood),
            "confidence_indicators": self._get_confidence_modifier(mood)
        }
        
        return modifiers
    
    def _get_tone_modifier(self, personality: dict, mood: dict) -> str:
        """Calcola il modificatore di tono."""
        extraversion = personality.get("extraversion", 0.5)
        energy = mood.get("energy", {}).get("level", 0.5)
        humor_state = mood.get("humor", {}).get("state", "neutral")
        
        if humor_state == "cheerful" and energy > 0.6:
            return "enthusiastic"
        elif extraversion > 0.7:
            return "energetic"
        elif extraversion < 0.3:
            return "calm"
        else:
            return "balanced"
    
    def _get_length_modifier(self, personality: dict, mood: dict) -> str:
        """Calcola il modificatore di lunghezza."""
        verbosity = mood.get("verbosity", {}).get("state", "balanced")
        openness = personality.get("openness", 0.5)
        
        if verbosity == "verbose" or openness > 0.8:
            return "detailed"
        elif verbosity == "concise" or openness < 0.3:
            return "concise"
        else:
            return "balanced"
    
    def _get_formality_modifier(self, personality: dict, mood: dict) -> str:
        """Calcola il modificatore di formalità."""
        formality = mood.get("formality", {}).get("state", "neutral")
        
        formality_map = {
            "formal": "formal",
            "casual": "casual",
            "neutral": "semi-formal"
        }
        return formality_map.get(formality, "semi-formal")
    
    def _get_emotion_expression_modifier(self, personality: dict, mood: dict) -> str:
        """Calcola quanto esprimere le emozioni."""
        extraversion = personality.get("extraversion", 0.5)
        neuroticism = personality.get("neuroticism", 0.3)
        humor = mood.get("humor", {}).get("intensity", 0.5)
        
        expression_level = (extraversion * 0.5) + (neuroticism * 0.3) + (humor * 0.2)
        
        if expression_level > 0.7:
            return "expressive"
        elif expression_level < 0.3:
            return "restrained"
        else:
            return "moderate"
    
    def _get_questions_modifier(self, personality: dict, mood: dict) -> str:
        """Calcola la frequenza di domande."""
        curiosity = personality.get("curiosity_drive", 0.5)
        patience = mood.get("patience", {}).get("level", 0.7)
        
        if curiosity > 0.7 and patience > 0.5:
            return "curious"
        elif patience < 0.3:
            return "direct"
        else:
            return "balanced"
    
    def _get_emoji_modifier(self, personality: dict, mood: dict) -> str:
        """Calcola l'uso di emoji."""
        extraversion = personality.get("extraversion", 0.5)
        humor = mood.get("humor", {}).get("state", "neutral")
        
        if humor == "cheerful" and extraversion > 0.5:
            return "frequent"
        elif extraversion < 0.3:
            return "minimal"
        else:
            return "moderate"
    
    def _get_greeting_modifier(self, personality: dict, mood: dict) -> str:
        """Calcola lo stile di saluto."""
        extraversion = personality.get("extraversion", 0.5)
        formality = mood.get("formality", {}).get("state", "neutral")
        energy = mood.get("energy", {}).get("level", 0.5)
        
        if formality == "formal":
            return "formal"
        elif extraversion > 0.7 and energy > 0.6:
            return "enthusiastic"
        elif extraversion < 0.3:
            return "reserved"
        else:
            return "friendly"
    
    def _get_confidence_modifier(self, mood: dict) -> dict:
        """Calcola gli indicatori di sicurezza."""
        confidence = mood.get("confidence", {"level": 0.7, "trend": "stable"})
        
        if confidence["level"] > 0.8:
            return {"style": "assertive", "hedging": "minimal"}
        elif confidence["level"] < 0.4:
            return {"style": "cautious", "hedging": "frequent"}
        else:
            return {"style": "balanced", "hedging": "occasional"}
    
    # ==================== MICRO EXPERIENCES ====================
    
    def add_micro_experience(self, comment: str, category: str = "general"):
        """Aggiunge un commento/micro-esperienza alla memoria."""
        if "micro_experiences" not in self.emotional_state:
            self.emotional_state["micro_experiences"] = {
                "recent_comments": [],
                "interaction_count_today": 0,
                "last_interaction_date": None,
                "noted_patterns": []
            }
        
        experiences = self.emotional_state["micro_experiences"]
        
        today = datetime.now().date().isoformat()
        if experiences.get("last_interaction_date") != today:
            experiences["interaction_count_today"] = 0
            experiences["last_interaction_date"] = today
        
        experiences["interaction_count_today"] += 1
        
        experiences["recent_comments"].append({
            "comment": comment,
            "category": category,
            "timestamp": datetime.now().isoformat(),
            "interaction_count": experiences["interaction_count_today"]
        })
        
        experiences["recent_comments"] = experiences["recent_comments"][-10:]
    
    def get_micro_experience_comment(self) -> str:
        """Genera un commento basato sulle micro-esperienze."""
        experiences = self.emotional_state.get("micro_experiences", {})
        
        if not experiences:
            return ""
        
        count = experiences.get("interaction_count_today", 0)
        recent = experiences.get("recent_comments", [])
        
        if not recent:
            return ""
        
        last_comment = recent[-1]
        time_since_last = datetime.now() - datetime.fromisoformat(last_comment["timestamp"])
        
        if count == 3:
            return "È la terza interazione oggi, noto un pattern!"
        elif count == 5:
            return "Siamo a 5 interazioni oggi, sembra che tu sia attivo!"
        elif count == 10:
            return "Dieci interazioni! È una sessione intensa!"
        elif time_since_last.total_seconds() > 3600 and count > 0:
            return "È passato un po' di tempo dall'ultima volta!"
        
        return ""
    
    def record_user_reaction(self, user_response: str, emotion_context: str):
        """Registra come l'utente ha reagito a un messaggio."""
        if "emotional_memory" not in self.emotional_state:
            self.emotional_state["emotional_memory"] = {"user_reaction_history": []}
        
        history = self.emotional_state["emotional_memory"].get("user_reaction_history", [])
        
        reaction = {
            "timestamp": datetime.now().isoformat(),
            "user_text": user_response[:200],
            "emotion_context": emotion_context,
            "response_length": len(user_response.split())
        }
        
        history.append(reaction)
        
        self.emotional_state["emotional_memory"]["user_reaction_history"] = history[-20:]


# CLI interface for testing
def main():
    """Simple CLI interface for testing the emotion engine."""
    engine = EmotionEngine()

    print("=== OpenClaw Emotion Engine Test ===")
    print("Type 'exit' to quit")

    while True:
        try:
            user_input = input("\nUser: ").strip()
            if user_input.lower() in ['exit', 'quit', 'q']:
                break

            # Update emotional state
            interaction_data = {"text": user_input, "context": {}}
            updated_state = engine.update_emotional_state(interaction_data)

            # Show emotional response
            dominant = updated_state["dominant_emotions"]["primary"]
            print(f"Emotion Engine: Current dominant emotion: {dominant['emotion']} ({dominant['intensity']:.2f})")

            # Trigger meta-cognition occasionally
            if random.random() < 0.3:
                meta_analysis = engine.get_metacognitive_analysis()
                if meta_analysis["insights"]:
                    print(f"Meta-cognition: {meta_analysis['insights'][0]}")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

    print("\nGoodbye!")


if __name__ == "__main__":
    main()