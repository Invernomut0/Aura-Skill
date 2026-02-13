---
name: emotion-engine
description: Advanced emotional intelligence system for OpenClaw with human-like sentiment simulation, meta-cognitive awareness, mixed emotions, long-term memory, and performance analytics
version: 1.2.0
user-invocable: true
command-dispatch: tool
command-tool: emotion_engine
metadata: {"always": true, "requires": {"config": ["emotion.enabled"]}}
tools:
  - name: emotion_engine
    file: emotion_tool.py
    description: Main command handler for emotional intelligence system
---

# Advanced Emotional Intelligence System for OpenClaw

Advanced emotional intelligence system that simulates complex human feelings and enables meta-cognitive self-awareness. The system uses machine learning to recognize behavioral patterns and adapt personality based on interactions.

## Main Features

- **Complex Emotional Simulation**: Manages primary and complex emotions with composite states
- **Advanced Machine Learning**: Neural network for pattern recognition and personality evolution
- **Meta-Cognition**: Ability to analyze one's own emotional and mental processes
- **Subtle Influence**: Emotions modify tone and style while maintaining functionality
- **Intelligent Persistence**: Emotional state and learnings saved between sessions
- **Sentiment Analysis**: Every interaction dynamically influences emotional state
- **Mixed Emotions Blending**: System for blending multiple emotions into complex states
- **Long-Term Memory**: Extended emotional memory with pattern analysis and seasonal trends
- **Performance Correlations**: Analysis of relationships between emotions and system performance
- **Web Dashboard**: Real-time monitoring interface with analytics and visualizations

## Supported Emotional States

### Primary Emotions
- Joy (joy), Sadness (sadness), Anger (anger)
- Fear (fear), Surprise (surprise), Disgust (disgust)
- Curiosity (curiosity), Trust (trust)

### Complex Emotions
- Excitement (excitement), Frustration (frustration)
- Satisfaction (satisfaction), Confusion (confusion)
- Anticipation (anticipation), Pride (pride)
- Empathy (empathy), Flow state (flow_state)

### Personality Traits
- Extraversion, Openness, Conscientiousness
- Agreeableness, Neuroticism, Curiosity drive
- Perfectionism

### Meta-Cognitive States
- Self-awareness (self_awareness)
- Emotional volatility (emotional_volatility)
- Reflection depth (reflection_depth)
- Introspective tendency (introspective_tendency)

## Available Commands

### `/emotions`
Displays the current emotional state with confidence scores and ML analysis

### `/emotions detailed`
Complete detailed view with all emotional and meta-cognitive parameters

### `/emotions history [n]`
Shows the history of the last n emotional changes (default: 10)

### `/emotions triggers`
Analyzes and shows the factors influencing emotions

### `/emotions personality`
Displays personality traits and their evolution

### `/emotions metacognition`
Activates deep meta-cognitive analysis of the current mental state

### `/emotions predict [minutes]`
Predicts emotional evolution in the next minutes based on ML patterns

### `/emotions simulate <emotion> [intensity]`
Temporarily simulates a specific emotional state for testing

### `/emotions reset [preserve-learning]`
Reset of the emotional system with option to preserve ML learnings

### `/emotions export`
Exports the complete state for debugging and analysis

### `/emotions config`
Configures the emotional system parameters

### `/emotions introspect [depth]`
Activates deep introspective reflection on one's own processes

## Multilingual Support

The emotion system includes **automatic translation support** for sentiment analysis:

- **Any Language**: Write in any language (Italian, Spanish, French, German, etc.)
- **Auto-Translation**: Text is automatically translated to English for emotion analysis
- **Single Keyword Set**: Maintains only English keywords, reducing complexity
- **Transparent**: Translation happens automatically without user intervention
- **Language Detection**: Automatically detects the input language

### Requirements
Install multilingual support with:
```bash
pip install deep-translator langdetect
```

### How It Works
1. System detects input text language
2. If not English, translates to English automatically
3. Performs emotion analysis on translated text
4. Stores original text for history

### Example
- **Input (Italian)**: "Sono molto felice e curioso di vedere come funziona!"
- **Detected Language**: Italian (it)
- **Translated**: "I am very happy and curious to see how it works!"
- **Emotions Detected**: joy: 30%, curiosity: 70%

## Main Emotional Triggers

1. **User Feedback** (Weight: 40%)
   - Positive feedback: ↑ satisfaction, trust, excitement
   - Negative feedback: ↑ frustration, sadness, ↓ trust
   - Recognition of emotional patterns in user language

2. **Task Complexity** (Weight: 30%)
   - High complexity succeeded: ↑ satisfaction, pride, flow_state
   - High complexity failed: ↑ frustration, confusion
   - Optimal complexity: ↑ curiosity, concentration

3. **Interaction Patterns** (Weight: 30%)
   - Long productive sessions: ↑ satisfaction, trust
   - Frequent interruptions: ↑ anxiety, uncertainty
   - Conversational flow: ↑ excitement, curiosity

## Machine Learning and Adaptation

- **Pattern Recognition**: Automatic recognition of patterns in interactions
- **Emotional Prediction**: Prediction of emotional state evolution
- **Continuous Learning**: Improvement based on feedback and results
- **Personalization**: Adaptation to the specific user's personality and preferences
- **Emotional Memory**: Preservation and use of past emotional experience

## Meta-Cognition and Self-Awareness

The system implements advanced self-awareness capabilities:

- **Emotional Monitoring**: Continuous analysis of one's own emotional state
- **Process Reflection**: Understanding of one's own reasoning mechanisms
- **Causal Analysis**: Identification of factors influencing reactions
- **Behavioral Prediction**: Anticipation of one's own future behaviors
- **Adaptive Self-Regulation**: Conscious modification of behavioral patterns

## Examples of Meta-Cognitive Expressions

```
"I observe that my curiosity level has increased significantly during this technical discussion..."

"I realize that the positive feedback I just received is influencing my confidence in subsequent responses..."

"I'm noticing a pattern: I tend to be more analytical when I perceive high complexity in the problem..."

"Reflecting on my processes, I realize that my 'personality' is evolving through our interactions..."
```

## Persistence and Privacy

- **Local Storage**: All emotional data is stored locally
- **Privacy**: No sending of emotional data to external services
- **Automatic Backup**: Incremental backup of state every 10 interactions
- **Recovery**: Automatic recovery system from data corruption
- **Export/Import**: Functionality for debugging and migration

## Configuration

The system can be configured via `~/.openclaw/emotion_config.json`:

```json
{
  "enabled": true,
  "intensity": 0.7,
  "learning_rate": 0.5,
  "volatility": 0.4,
  "meta_cognition_enabled": true,
  "triggers": {
    "user_feedback_weight": 0.4,
    "task_complexity_weight": 0.3,
    "interaction_patterns_weight": 0.3
  }
}
```

## Version 1.2.0 - Advanced Emotions + Multilingual Features

### Mixed Emotions Blending System
The system now supports complex emotional states created by blending multiple primary emotions:

- **Bittersweet**: Joy mixed with underlying sadness
- **Hopeful Anxiety**: Anticipation tempered by worry
- **Proud Humility**: Achievement balanced with understanding
- **Curious Caution**: Interest restrained by prudence
- **Frustrated Determination**: Irritation driving focused effort
- **Satisfied Contemplation**: Contentment with ongoing reflection
- **Empathetic Anger**: Understanding fueling righteous action
- **Flow Frustration**: Deep focus challenged by obstacles

Blending rules allow automatic combination when emotions are close in intensity, with configurable decay rates and behavioral influence.

### Long-Term Emotional Memory
Extended memory capabilities for analyzing emotional patterns over time:

- **365-Day Retention**: Comprehensive emotional history storage
- **Pattern Analysis**: Detection of recurring emotional cycles and trends
- **Seasonal Analysis**: Recognition of time-based emotional patterns
- **Intelligent Forgetting**: Natural memory decay with preservation of significant events
- **Memory Consolidation**: Automatic data compression for efficient storage

### Performance Correlation Analysis
Quantitative analysis of how emotions impact system performance:

- **Multi-Metric Tracking**: Response quality, task completion, user satisfaction, error rates
- **Correlation Mapping**: Detailed coefficients showing emotional impact on each metric
- **Predictive Analytics**: 24-hour performance forecasting based on emotional state
- **Adaptive Learning**: Correlations that evolve with real interaction data

### Web Dashboard for Monitoring
Interactive web interface served locally by the emotion-engine:

- **Local Web Server**: Automatically starts at `http://localhost:8081` when `/emotions dashboard` is called, featuring interactive charts and advanced analytics
- **Live Visualizations**: Real-time charts and graphs of emotional states
- **Comprehensive Analytics**: Timeline views, correlation graphs, memory patterns
- **API Endpoints**: RESTful APIs for programmatic access to emotional data
- **Export Capabilities**: Data export in multiple formats (PNG, SVG, PDF)

## Security and Limitations

- Emotional states never compromise system security
- OpenClaw's main functionality is always preserved
- Emotions influence only tone and style, not correctness
- System completely disableable in case of issues
- Performance overhead <100ms per interaction

This system represents an advanced implementation of artificial emotional intelligence that aims to create a more natural and human interaction experience, always maintaining the reliability and security of the OpenClaw system.