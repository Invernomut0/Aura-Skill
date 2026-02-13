"""
Advanced sentiment analysis with ML capabilities for OpenClaw emotional intelligence.
"""

import re
import json
import math
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from datetime import datetime, timedelta

class AdvancedSentimentAnalyzer:
    """
    Multi-level sentiment analysis system that combines:
    - Linguistic analysis (content, tone, complexity)
    - Contextual analysis (topic, urgency, expectations)
    - Behavioral analysis (interaction patterns, response time)
    - Performance analysis (success rate, follow-ups)
    - ML-driven pattern recognition
    """

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.emotional_lexicon = self._build_emotional_lexicon()
        self.context_patterns = self._build_context_patterns()
        self.behavioral_indicators = self._build_behavioral_indicators()
        self.history = []

    def _build_emotional_lexicon(self) -> Dict[str, Dict]:
        """Build comprehensive emotional lexicon with sentiment scores."""
        return {
            # Positive emotions
            "joy": {
                "keywords": ["happy", "felice", "gioia", "allegro", "content", "pleased", "delighted"],
                "score": 0.8,
                "arousal": 0.7,
                "valence": 0.9
            },
            "excitement": {
                "keywords": ["excited", "eccitato", "thrilled", "enthusiastic", "energetic"],
                "score": 0.9,
                "arousal": 0.9,
                "valence": 0.8
            },
            "satisfaction": {
                "keywords": ["satisfied", "soddisfatto", "pleased", "content", "fulfilled"],
                "score": 0.7,
                "arousal": 0.4,
                "valence": 0.8
            },

            # Negative emotions
            "frustration": {
                "keywords": ["frustrated", "frustrato", "annoyed", "irritated", "upset"],
                "score": -0.6,
                "arousal": 0.7,
                "valence": 0.2
            },
            "confusion": {
                "keywords": ["confused", "confuso", "puzzled", "unclear", "lost"],
                "score": -0.3,
                "arousal": 0.5,
                "valence": 0.4
            },
            "anger": {
                "keywords": ["angry", "arrabbiato", "mad", "furious", "outraged"],
                "score": -0.8,
                "arousal": 0.9,
                "valence": 0.1
            },

            # Neutral/Complex emotions
            "curiosity": {
                "keywords": ["curious", "curioso", "interested", "intrigued", "wondering"],
                "score": 0.5,
                "arousal": 0.6,
                "valence": 0.7
            },
            "surprise": {
                "keywords": ["surprised", "sorpreso", "amazed", "shocked", "unexpected"],
                "score": 0.2,
                "arousal": 0.8,
                "valence": 0.5
            }
        }

    def _build_context_patterns(self) -> Dict[str, Dict]:
        """Build patterns for contextual analysis."""
        return {
            "technical_discussion": {
                "indicators": ["api", "code", "function", "algorithm", "implementation"],
                "emotion_modifier": {"curiosity": 0.3, "satisfaction": 0.2}
            },
            "problem_solving": {
                "indicators": ["solve", "fix", "debug", "error", "issue", "problem"],
                "emotion_modifier": {"frustration": 0.2, "satisfaction": 0.4}
            },
            "learning": {
                "indicators": ["learn", "understand", "explain", "how", "why", "what"],
                "emotion_modifier": {"curiosity": 0.4, "confusion": 0.1}
            },
            "creative_work": {
                "indicators": ["create", "design", "build", "make", "innovative"],
                "emotion_modifier": {"excitement": 0.3, "flow_state": 0.2}
            },
            "urgent_request": {
                "indicators": ["urgent", "quickly", "asap", "immediately", "rush"],
                "emotion_modifier": {"stress": 0.3, "focus": 0.2}
            }
        }

    def _build_behavioral_indicators(self) -> Dict[str, Dict]:
        """Build indicators for behavioral analysis."""
        return {
            "engagement_high": {
                "indicators": ["tell me more", "explain", "elaborate", "continue", "interesting"],
                "emotions": {"curiosity": 0.4, "engagement": 0.3}
            },
            "engagement_low": {
                "indicators": ["ok", "fine", "whatever", "skip", "don't care"],
                "emotions": {"boredom": 0.3, "disengagement": 0.4}
            },
            "satisfaction_high": {
                "indicators": ["perfect", "exactly", "great", "wonderful", "brilliant"],
                "emotions": {"satisfaction": 0.5, "joy": 0.3}
            },
            "satisfaction_low": {
                "indicators": ["not quite", "almost", "close but", "nearly", "sort of"],
                "emotions": {"mild_frustration": 0.2, "patience": 0.1}
            }
        }

    def analyze_sentiment_advanced(self, text: str, context: Dict = None, history: List = None) -> Dict:
        """
        Perform advanced multi-level sentiment analysis.

        Args:
            text: The text to analyze
            context: Additional context information
            history: Previous interaction history

        Returns:
            Dict with comprehensive sentiment analysis results
        """
        context = context or {}
        history = history or []

        # Level 1: Linguistic Analysis
        linguistic_analysis = self._analyze_linguistic(text)

        # Level 2: Contextual Analysis
        contextual_analysis = self._analyze_contextual(text, context)

        # Level 3: Behavioral Analysis
        behavioral_analysis = self._analyze_behavioral(text, history)

        # Level 4: Performance Analysis
        performance_analysis = self._analyze_performance(context, history)

        # Level 5: Pattern Recognition
        pattern_analysis = self._analyze_patterns(text, history)

        # Combine all analyses
        combined_sentiment = self._combine_analyses(
            linguistic_analysis,
            contextual_analysis,
            behavioral_analysis,
            performance_analysis,
            pattern_analysis
        )

        # Store for future pattern recognition
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "text": text,
            "context": context,
            "sentiment": combined_sentiment
        })

        return combined_sentiment

    def _analyze_linguistic(self, text: str) -> Dict:
        """Analyze linguistic features of the text."""
        text_lower = text.lower()

        # Basic sentiment scoring
        sentiment_score = 0.0
        emotion_scores = defaultdict(float)

        for emotion, data in self.emotional_lexicon.items():
            for keyword in data["keywords"]:
                if keyword in text_lower:
                    sentiment_score += data["score"]
                    emotion_scores[emotion] += 0.3

        # Analyze text complexity
        complexity = self._calculate_text_complexity(text)

        # Analyze emotional intensity
        intensity = self._calculate_emotional_intensity(text)

        # Check for negations
        negation_modifier = self._check_negations(text)

        return {
            "sentiment_score": sentiment_score * negation_modifier,
            "emotion_scores": dict(emotion_scores),
            "complexity": complexity,
            "intensity": intensity,
            "negation_modifier": negation_modifier,
            "word_count": len(text.split()),
            "sentence_count": len(re.split(r'[.!?]+', text))
        }

    def _analyze_contextual(self, text: str, context: Dict) -> Dict:
        """Analyze contextual factors."""
        text_lower = text.lower()

        # Identify context type
        context_type = "general"
        context_confidence = 0.0

        for ctx_type, data in self.context_patterns.items():
            matches = sum(1 for indicator in data["indicators"] if indicator in text_lower)
            if matches > 0:
                confidence = matches / len(data["indicators"])
                if confidence > context_confidence:
                    context_type = ctx_type
                    context_confidence = confidence

        # Apply context-specific emotion modifiers
        emotion_modifiers = {}
        if context_type in self.context_patterns:
            emotion_modifiers = self.context_patterns[context_type].get("emotion_modifier", {})

        # Analyze urgency
        urgency = self._analyze_urgency(text, context)

        # Analyze topic complexity
        topic_complexity = self._analyze_topic_complexity(text, context)

        return {
            "context_type": context_type,
            "context_confidence": context_confidence,
            "emotion_modifiers": emotion_modifiers,
            "urgency": urgency,
            "topic_complexity": topic_complexity
        }

    def _analyze_behavioral(self, text: str, history: List) -> Dict:
        """Analyze behavioral patterns."""
        text_lower = text.lower()

        # Analyze engagement level
        engagement = self._calculate_engagement(text, history)

        # Analyze conversation flow
        flow_quality = self._calculate_flow_quality(history)

        # Analyze user interaction patterns
        interaction_patterns = self._analyze_interaction_patterns(history)

        # Check for behavioral indicators
        behavioral_emotions = defaultdict(float)
        for behavior_type, data in self.behavioral_indicators.items():
            matches = sum(1 for indicator in data["indicators"] if indicator in text_lower)
            if matches > 0:
                for emotion, score in data["emotions"].items():
                    behavioral_emotions[emotion] += score * (matches / len(data["indicators"]))

        return {
            "engagement": engagement,
            "flow_quality": flow_quality,
            "interaction_patterns": interaction_patterns,
            "behavioral_emotions": dict(behavioral_emotions)
        }

    def _analyze_performance(self, context: Dict, history: List) -> Dict:
        """Analyze performance indicators."""
        # Analyze success rate of recent interactions
        success_rate = self._calculate_success_rate(history)

        # Analyze response effectiveness
        response_effectiveness = self._calculate_response_effectiveness(history)

        # Analyze task completion rate
        task_completion = self._calculate_task_completion(context, history)

        return {
            "success_rate": success_rate,
            "response_effectiveness": response_effectiveness,
            "task_completion": task_completion
        }

    def _analyze_patterns(self, text: str, history: List) -> Dict:
        """Analyze patterns using simple ML techniques."""
        if not history or len(history) < 5:
            return {"pattern_confidence": 0.0, "predicted_emotions": {}}

        # Simple pattern recognition based on recent history
        recent_history = history[-10:] if len(history) >= 10 else history

        # Analyze emotional trends
        emotional_trends = self._calculate_emotional_trends(recent_history)

        # Predict likely emotions based on patterns
        predicted_emotions = self._predict_emotions_simple(text, emotional_trends)

        return {
            "pattern_confidence": 0.7 if len(recent_history) >= 5 else 0.3,
            "predicted_emotions": predicted_emotions,
            "emotional_trends": emotional_trends
        }

    def _combine_analyses(self, linguistic: Dict, contextual: Dict,
                         behavioral: Dict, performance: Dict, pattern: Dict) -> Dict:
        """Combine all analysis results into final sentiment."""

        # Initialize with ALL primary emotions at base level
        # This ensures all emotions are always present in the result
        from config.emotional_constants import PRIMARY_EMOTIONS
        emotions = {emotion: 0.0 for emotion in PRIMARY_EMOTIONS.keys()}
        
        # Add base emotions from linguistic analysis
        for emotion, score in linguistic["emotion_scores"].items():
            if emotion in emotions:
                emotions[emotion] += score

        # Apply contextual modifiers
        for emotion, modifier in contextual["emotion_modifiers"].items():
            if emotion in emotions:
                emotions[emotion] += modifier

        # Add behavioral emotions
        for emotion, score in behavioral["behavioral_emotions"].items():
            if emotion in emotions:
                emotions[emotion] += score

        # Add predicted emotions from patterns
        for emotion, score in pattern["predicted_emotions"].items():
            if emotion in emotions:
                emotions[emotion] += score * 0.5  # Lower weight for predictions

        # Calculate overall sentiment
        overall_sentiment = linguistic["sentiment_score"]
        if performance["success_rate"] > 0.7:
            overall_sentiment += 0.2
        elif performance["success_rate"] < 0.3:
            overall_sentiment -= 0.2

        # Calculate confidence score
        confidence = self._calculate_confidence(linguistic, contextual, behavioral, pattern)

        # Normalize emotion scores
        emotions = {k: max(0.0, min(1.0, v)) for k, v in emotions.items()}

        return {
            "overall_sentiment": max(-1.0, min(1.0, overall_sentiment)),
            "emotions": dict(emotions),
            "confidence": confidence,
            "analysis_components": {
                "linguistic": linguistic,
                "contextual": contextual,
                "behavioral": behavioral,
                "performance": performance,
                "pattern": pattern
            },
            "timestamp": datetime.now().isoformat()
        }

    def _calculate_text_complexity(self, text: str) -> float:
        """Calculate text complexity score."""
        words = text.split()
        if not words:
            return 0.0

        avg_word_length = sum(len(word) for word in words) / len(words)
        sentence_count = len(re.split(r'[.!?]+', text))
        avg_sentence_length = len(words) / max(sentence_count, 1)

        # Normalize to 0-1 range
        complexity = min(1.0, (avg_word_length / 10.0 + avg_sentence_length / 20.0) / 2.0)
        return complexity

    def _calculate_emotional_intensity(self, text: str) -> float:
        """Calculate emotional intensity based on caps, punctuation, etc."""
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        exclamation_count = text.count('!')
        question_count = text.count('?')

        intensity = min(1.0, caps_ratio * 2 + (exclamation_count + question_count) / 10.0)
        return intensity

    def _check_negations(self, text: str) -> float:
        """Check for negations that might flip sentiment."""
        negation_words = ["not", "no", "never", "none", "nothing", "nobody", "nowhere",
                         "non", "niente", "nessuno", "mai", "nulla"]

        text_lower = text.lower()
        negation_count = sum(1 for word in negation_words if word in text_lower)

        # Simple negation handling
        if negation_count % 2 == 1:  # Odd number of negations
            return -0.5
        return 1.0

    def _analyze_urgency(self, text: str, context: Dict) -> float:
        """Analyze urgency level."""
        urgent_words = ["urgent", "quickly", "asap", "immediately", "rush", "now",
                       "urgente", "subito", "velocemente", "presto"]

        text_lower = text.lower()
        urgency_score = sum(1 for word in urgent_words if word in text_lower)

        return min(1.0, urgency_score / 3.0)

    def _analyze_topic_complexity(self, text: str, context: Dict) -> float:
        """Analyze topic complexity."""
        complex_indicators = ["algorithm", "implementation", "architecture", "system",
                             "complex", "advanced", "sophisticated", "intricate"]

        text_lower = text.lower()
        complexity_score = sum(1 for indicator in complex_indicators if indicator in text_lower)

        return min(1.0, complexity_score / 4.0)

    def _calculate_engagement(self, text: str, history: List) -> float:
        """Calculate user engagement level."""
        if not history:
            return 0.5  # Neutral baseline

        recent_history = history[-5:] if len(history) >= 5 else history

        # Simple engagement calculation based on message length and frequency
        avg_length = sum(len(msg.get("text", "")) for msg in recent_history) / len(recent_history)
        normalized_length = min(1.0, avg_length / 100.0)  # Normalize to 0-1

        return normalized_length

    def _calculate_flow_quality(self, history: List) -> float:
        """Calculate conversation flow quality."""
        if len(history) < 2:
            return 0.5

        # Simple flow quality based on consistent interaction
        return 0.7  # Placeholder - could be more sophisticated

    def _analyze_interaction_patterns(self, history: List) -> Dict:
        """Analyze user interaction patterns."""
        if not history:
            return {}

        # Analyze timing patterns, message frequency, etc.
        return {
            "message_frequency": len(history),
            "average_message_length": sum(len(msg.get("text", "")) for msg in history) / len(history)
        }

    def _calculate_success_rate(self, history: List) -> float:
        """Calculate success rate of recent interactions."""
        if not history:
            return 0.5

        # Simple success rate calculation
        return 0.7  # Placeholder - would need more sophisticated tracking

    def _calculate_response_effectiveness(self, history: List) -> float:
        """Calculate response effectiveness."""
        return 0.6  # Placeholder

    def _calculate_task_completion(self, context: Dict, history: List) -> float:
        """Calculate task completion rate."""
        return 0.5  # Placeholder

    def _calculate_emotional_trends(self, history: List) -> Dict:
        """Calculate emotional trends from history."""
        if not history:
            return {}

        # Simple trend calculation
        recent_emotions = defaultdict(list)
        for interaction in history:
            sentiment = interaction.get("sentiment", {})
            emotions = sentiment.get("emotions", {})
            for emotion, score in emotions.items():
                recent_emotions[emotion].append(score)

        # Calculate trends (simple average)
        trends = {}
        for emotion, scores in recent_emotions.items():
            trends[emotion] = sum(scores) / len(scores) if scores else 0.0

        return trends

    def _predict_emotions_simple(self, text: str, trends: Dict) -> Dict:
        """Simple emotion prediction based on trends."""
        # Very basic prediction - could use ML here
        predicted = {}
        for emotion, trend_score in trends.items():
            if trend_score > 0.5:
                predicted[emotion] = trend_score * 0.8  # Continuation of trend

        return predicted

    def _calculate_confidence(self, linguistic: Dict, contextual: Dict,
                            behavioral: Dict, pattern: Dict) -> float:
        """Calculate overall confidence in the analysis."""
        # Combine confidence from different sources
        confidences = [
            min(1.0, linguistic.get("word_count", 0) / 20.0),  # More words = more confident
            contextual.get("context_confidence", 0.0),
            behavioral.get("engagement", 0.0),
            pattern.get("pattern_confidence", 0.0)
        ]

        return sum(confidences) / len(confidences)