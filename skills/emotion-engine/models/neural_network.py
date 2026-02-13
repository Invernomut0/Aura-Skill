"""
Neural Network implementation for emotional intelligence in OpenClaw.
Simplified but effective neural network for pattern recognition and emotional prediction.
"""

import json
import math
import random
import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from datetime import datetime


class SimpleNeuralNetwork:
    """
    A simplified neural network implementation for emotional intelligence.
    Uses basic feedforward architecture with backpropagation.
    """

    def __init__(self, config: Dict):
        self.config = config
        self.input_size = config.get("input_layer_size", 140)
        self.hidden_layers = config.get("hidden_layers", [
            {"neurons": 80, "activation": "relu", "dropout": 0.3},
            {"neurons": 60, "activation": "tanh", "dropout": 0.2},
            {"neurons": 40, "activation": "relu", "dropout": 0.1}
        ])
        self.output_size = config.get("output_layer_size", 17)
        self.learning_rate = config.get("learning_rate", 0.001)

        self.weights = []
        self.biases = []
        self.training_history = []
        self._initialize_network()

    def _initialize_network(self):
        """Initialize network weights and biases."""
        # Input to first hidden layer
        layer_sizes = [self.input_size] + [layer["neurons"] for layer in self.hidden_layers] + [self.output_size]

        for i in range(len(layer_sizes) - 1):
            # Xavier initialization
            limit = math.sqrt(6.0 / (layer_sizes[i] + layer_sizes[i + 1]))
            weight_matrix = [[random.uniform(-limit, limit) for _ in range(layer_sizes[i + 1])]
                           for _ in range(layer_sizes[i])]
            bias_vector = [0.0 for _ in range(layer_sizes[i + 1])]

            self.weights.append(weight_matrix)
            self.biases.append(bias_vector)

    def _activation_function(self, x: float, activation_type: str) -> float:
        """Apply activation function."""
        if activation_type == "relu":
            return max(0.0, x)
        elif activation_type == "tanh":
            return math.tanh(x)
        elif activation_type == "sigmoid":
            return 1.0 / (1.0 + math.exp(-max(-500, min(500, x))))  # Clamp to prevent overflow
        else:
            return x  # Linear

    def _activation_derivative(self, x: float, activation_type: str) -> float:
        """Compute derivative of activation function."""
        if activation_type == "relu":
            return 1.0 if x > 0 else 0.0
        elif activation_type == "tanh":
            tanh_x = math.tanh(x)
            return 1.0 - tanh_x * tanh_x
        elif activation_type == "sigmoid":
            sig_x = self._activation_function(x, "sigmoid")
            return sig_x * (1.0 - sig_x)
        else:
            return 1.0  # Linear

    def forward_pass(self, input_vector: List[float]) -> Tuple[List[float], List[List[float]]]:
        """
        Perform forward pass through the network.
        Returns output and intermediate activations.
        """
        if len(input_vector) != self.input_size:
            raise ValueError(f"Input size mismatch: expected {self.input_size}, got {len(input_vector)}")

        activations = [input_vector]
        current_input = input_vector

        # Forward through hidden layers
        for i, layer_config in enumerate(self.hidden_layers):
            layer_output = []
            for j in range(len(self.weights[i][0])):
                # Compute weighted sum
                weighted_sum = sum(current_input[k] * self.weights[i][k][j] for k in range(len(current_input)))
                weighted_sum += self.biases[i][j]

                # Apply activation
                activated = self._activation_function(weighted_sum, layer_config["activation"])
                layer_output.append(activated)

            activations.append(layer_output)
            current_input = layer_output

        # Output layer (linear activation)
        final_output = []
        output_layer_idx = len(self.hidden_layers)
        for j in range(self.output_size):
            weighted_sum = sum(current_input[k] * self.weights[output_layer_idx][k][j]
                             for k in range(len(current_input)))
            weighted_sum += self.biases[output_layer_idx][j]
            final_output.append(weighted_sum)

        activations.append(final_output)
        return final_output, activations

    def backward_pass(self, activations: List[List[float]], target: List[float]) -> None:
        """Perform backward pass and update weights."""
        if len(target) != self.output_size:
            raise ValueError(f"Target size mismatch: expected {self.output_size}, got {len(target)}")

        # Compute output layer error
        output = activations[-1]
        output_errors = [target[i] - output[i] for i in range(self.output_size)]

        # Backpropagate errors
        layer_errors = [output_errors]

        # Compute errors for hidden layers
        for i in range(len(self.hidden_layers) - 1, -1, -1):
            current_errors = []
            next_layer_errors = layer_errors[0]
            layer_config = self.hidden_layers[i]

            for j in range(len(activations[i + 1])):
                error = 0.0
                for k in range(len(next_layer_errors)):
                    error += next_layer_errors[k] * self.weights[i + 1][j][k]

                # Apply activation derivative
                pre_activation = activations[i + 1][j]  # This is post-activation, approximation
                derivative = self._activation_derivative(pre_activation, layer_config["activation"])
                error *= derivative

                current_errors.append(error)

            layer_errors.insert(0, current_errors)

        # Update weights and biases
        for layer_idx in range(len(self.weights)):
            errors = layer_errors[layer_idx + 1]
            inputs = activations[layer_idx]

            # Update weights
            for i in range(len(inputs)):
                for j in range(len(errors)):
                    self.weights[layer_idx][i][j] += self.learning_rate * errors[j] * inputs[i]

            # Update biases
            for j in range(len(errors)):
                self.biases[layer_idx][j] += self.learning_rate * errors[j]

    def train_batch(self, training_data: List[Tuple[List[float], List[float]]]) -> float:
        """Train on a batch of data."""
        total_loss = 0.0

        for input_vector, target in training_data:
            output, activations = self.forward_pass(input_vector)
            self.backward_pass(activations, target)

            # Compute loss (MSE)
            loss = sum((target[i] - output[i]) ** 2 for i in range(len(target))) / len(target)
            total_loss += loss

        return total_loss / len(training_data)

    def predict(self, input_vector: List[float]) -> Dict[str, float]:
        """Make a prediction and return emotion scores."""
        output, _ = self.forward_pass(input_vector)

        # Map output to emotion names
        emotion_names = [
            "joy", "sadness", "anger", "fear", "surprise", "disgust", "curiosity", "trust",
            "excitement", "frustration", "satisfaction", "confusion", "anticipation", "pride", "empathy", "flow_state",
            "confidence"
        ]

        # Apply softmax to normalize probabilities
        max_val = max(output)
        exp_values = [math.exp(x - max_val) for x in output]
        sum_exp = sum(exp_values)
        probabilities = [x / sum_exp for x in exp_values]

        return {emotion_names[i]: probabilities[i] for i in range(min(len(emotion_names), len(probabilities)))}

    def save_model(self, file_path: str) -> None:
        """Save model to JSON file."""
        model_data = {
            "config": self.config,
            "weights": self.weights,
            "biases": self.biases,
            "training_history": self.training_history[-100:],  # Keep last 100 training records
            "timestamp": datetime.now().isoformat()
        }

        try:
            with open(file_path, 'w') as f:
                json.dump(model_data, f, indent=2)
        except Exception as e:
            print(f"Error saving model: {e}")

    def load_model(self, file_path: str) -> bool:
        """Load model from JSON file."""
        try:
            with open(file_path, 'r') as f:
                model_data = json.load(f)

            self.config = model_data["config"]
            self.weights = model_data["weights"]
            self.biases = model_data["biases"]
            self.training_history = model_data.get("training_history", [])

            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False


class EmotionalFeatureExtractor:
    """Extract features from text and context for neural network input."""

    def __init__(self):
        self.feature_size = 140

    def extract_features(self, text: str, context: Dict, sentiment_analysis: Dict, history: List[Dict]) -> List[float]:
        """Extract feature vector for neural network."""
        features = []

        # Sentiment features (50 dimensions)
        features.extend(self._extract_sentiment_features(sentiment_analysis))

        # Context features (30 dimensions)
        features.extend(self._extract_context_features(text, context))

        # Behavioral features (20 dimensions)
        features.extend(self._extract_behavioral_features(text, history))

        # Historical features (40 dimensions)
        features.extend(self._extract_historical_features(history))

        # Pad or truncate to exact size
        while len(features) < self.feature_size:
            features.append(0.0)

        return features[:self.feature_size]

    def _extract_sentiment_features(self, sentiment_analysis: Dict) -> List[float]:
        """Extract sentiment-related features."""
        features = []

        # Overall sentiment
        features.append(sentiment_analysis.get("overall_sentiment", 0.0))

        # Individual emotion scores
        emotions = sentiment_analysis.get("emotions", {})
        emotion_names = ["joy", "sadness", "anger", "fear", "surprise", "disgust", "curiosity", "trust",
                        "excitement", "frustration", "satisfaction", "confusion", "anticipation", "pride", "empathy"]

        for emotion in emotion_names:
            features.append(emotions.get(emotion, 0.0))

        # Confidence and intensity
        features.append(sentiment_analysis.get("confidence", 0.0))

        # Linguistic features
        linguistic = sentiment_analysis.get("analysis_components", {}).get("linguistic", {})
        features.append(linguistic.get("complexity", 0.0))
        features.append(linguistic.get("intensity", 0.0))
        features.append(linguistic.get("word_count", 0.0) / 100.0)  # Normalize
        features.append(linguistic.get("sentence_count", 0.0) / 10.0)  # Normalize

        # Pad to 50
        while len(features) < 50:
            features.append(0.0)

        return features[:50]

    def _extract_context_features(self, text: str, context: Dict) -> List[float]:
        """Extract context-related features."""
        features = []

        # Context type indicators
        context_types = ["technical_discussion", "problem_solving", "learning", "creative_work", "urgent_request"]
        detected_context = context.get("context_type", "general")

        for ctx_type in context_types:
            features.append(1.0 if detected_context == ctx_type else 0.0)

        # Complexity and urgency
        features.append(context.get("topic_complexity", 0.0))
        features.append(context.get("urgency", 0.0))

        # Text characteristics
        text_lower = text.lower()
        features.append(1.0 if "?" in text else 0.0)  # Question
        features.append(1.0 if "!" in text else 0.0)  # Exclamation
        features.append(len(text) / 1000.0)  # Normalized length

        # Common word patterns
        technical_words = ["code", "algorithm", "function", "api", "system"]
        emotional_words = ["feel", "think", "like", "love", "hate", "enjoy"]

        tech_count = sum(1 for word in technical_words if word in text_lower)
        emotional_count = sum(1 for word in emotional_words if word in text_lower)

        features.append(tech_count / 5.0)  # Normalized
        features.append(emotional_count / 6.0)  # Normalized

        # Pad to 30
        while len(features) < 30:
            features.append(0.0)

        return features[:30]

    def _extract_behavioral_features(self, text: str, history: List[Dict]) -> List[float]:
        """Extract behavioral pattern features."""
        features = []

        # Engagement indicators
        text_lower = text.lower()
        engagement_words = ["more", "explain", "tell", "show", "how", "why", "what", "continue"]
        disengagement_words = ["ok", "fine", "stop", "enough", "skip", "never mind"]

        engagement_score = sum(1 for word in engagement_words if word in text_lower) / len(engagement_words)
        disengagement_score = sum(1 for word in disengagement_words if word in text_lower) / len(disengagement_words)

        features.extend([engagement_score, disengagement_score])

        # Conversation patterns
        if history:
            recent_history = history[-5:] if len(history) >= 5 else history
            avg_length = sum(len(interaction.get("text", "")) for interaction in recent_history) / len(recent_history)
            features.append(avg_length / 200.0)  # Normalized

            # Response time patterns (placeholder)
            features.append(0.5)  # Would need actual timing data
        else:
            features.extend([0.0, 0.0])

        # Interaction frequency
        features.append(len(history) / 100.0)  # Normalized interaction count

        # Pad to 20
        while len(features) < 20:
            features.append(0.0)

        return features[:20]

    def _extract_historical_features(self, history: List[Dict]) -> List[float]:
        """Extract features from interaction history."""
        features = []

        if not history:
            return [0.0] * 40

        recent_history = history[-10:] if len(history) >= 10 else history

        # Average emotions from recent history
        emotion_names = ["joy", "sadness", "anger", "fear", "surprise", "disgust", "curiosity", "trust"]
        for emotion in emotion_names:
            scores = []
            for interaction in recent_history:
                sentiment = interaction.get("sentiment", {})
                emotions = sentiment.get("emotions", {})
                if emotion in emotions:
                    scores.append(emotions[emotion])

            avg_score = sum(scores) / len(scores) if scores else 0.0
            features.append(avg_score)

        # Emotional volatility
        if len(recent_history) >= 3:
            sentiment_scores = []
            for interaction in recent_history:
                sentiment = interaction.get("sentiment", {})
                sentiment_scores.append(sentiment.get("overall_sentiment", 0.0))

            # Calculate variance as volatility measure
            mean_sentiment = sum(sentiment_scores) / len(sentiment_scores)
            variance = sum((x - mean_sentiment) ** 2 for x in sentiment_scores) / len(sentiment_scores)
            features.append(min(1.0, variance))  # Cap at 1.0
        else:
            features.append(0.0)

        # Trend analysis (simplified)
        if len(recent_history) >= 3:
            # Simple trend: compare first half vs second half
            mid = len(recent_history) // 2
            first_half_sentiment = sum(interaction.get("sentiment", {}).get("overall_sentiment", 0.0)
                                     for interaction in recent_history[:mid]) / mid
            second_half_sentiment = sum(interaction.get("sentiment", {}).get("overall_sentiment", 0.0)
                                      for interaction in recent_history[mid:]) / (len(recent_history) - mid)

            trend = second_half_sentiment - first_half_sentiment
            features.append(trend)
        else:
            features.append(0.0)

        # Session characteristics
        features.append(len(history) / 100.0)  # Normalized total interactions
        features.append(len(recent_history) / 10.0)  # Normalized recent activity

        # Pad to 40
        while len(features) < 40:
            features.append(0.0)

        return features[:40]


class EmotionalPatternRecognizer:
    """Recognize and learn emotional patterns using the neural network."""

    def __init__(self, neural_network: SimpleNeuralNetwork):
        self.nn = neural_network
        self.feature_extractor = EmotionalFeatureExtractor()
        self.training_data = []
        self.pattern_cache = {}

    def recognize_patterns(self, text: str, context: Dict, sentiment_analysis: Dict, history: List[Dict]) -> Dict:
        """Recognize emotional patterns and predict future states."""
        # Extract features
        features = self.feature_extractor.extract_features(text, context, sentiment_analysis, history)

        # Get prediction from neural network
        prediction = self.nn.predict(features)

        # Store for future training
        self._store_training_data(features, sentiment_analysis.get("emotions", {}))

        return {
            "predicted_emotions": prediction,
            "pattern_confidence": prediction.get("confidence", 0.5),
            "features_used": len(features)
        }

    def _store_training_data(self, features: List[float], actual_emotions: Dict[str, float]):
        """Store data for future training."""
        # Convert emotions dict to target vector
        emotion_names = [
            "joy", "sadness", "anger", "fear", "surprise", "disgust", "curiosity", "trust",
            "excitement", "frustration", "satisfaction", "confusion", "anticipation", "pride", "empathy", "flow_state",
            "confidence"
        ]

        target_vector = []
        for emotion in emotion_names:
            target_vector.append(actual_emotions.get(emotion, 0.0))

        self.training_data.append((features, target_vector))

        # Keep only recent training data
        if len(self.training_data) > 1000:
            self.training_data = self.training_data[-500:]

    def update_learning(self, feedback_score: float = None):
        """Update the neural network with accumulated training data."""
        if len(self.training_data) < 10:
            return False

        # Train on recent data
        batch_size = min(32, len(self.training_data))
        training_batch = self.training_data[-batch_size:]

        try:
            loss = self.nn.train_batch(training_batch)
            self.nn.training_history.append({
                "timestamp": datetime.now().isoformat(),
                "loss": loss,
                "batch_size": batch_size,
                "feedback_score": feedback_score
            })
            return True
        except Exception as e:
            print(f"Error updating neural network: {e}")
            return False

    def get_learning_stats(self) -> Dict:
        """Get learning statistics."""
        if not self.nn.training_history:
            return {"training_episodes": 0, "average_loss": 0.0, "last_update": None}

        recent_history = self.nn.training_history[-10:]
        avg_loss = sum(episode.get("loss", 0.0) for episode in recent_history) / len(recent_history)

        return {
            "training_episodes": len(self.nn.training_history),
            "average_loss": avg_loss,
            "last_update": recent_history[-1].get("timestamp") if recent_history else None,
            "training_data_size": len(self.training_data)
        }