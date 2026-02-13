---
name: emotion-prompt-modifier
description: Dynamically modifies agent prompts based on emotional state with subtle and natural influence
emoji: 🎭
events: ["agent:bootstrap"]
---

# Hook for Dynamic Prompt Modification Based on Emotions

This hook intercepts the `agent:bootstrap` event and dynamically modifies the agent's system prompt based on the current emotional state of the emotional intelligence system.

## Features

- **Subtle Modification**: Prompt modifications are subtle and natural, do not compromise main functionality
- **Emotional Influence**: The tone and style of responses reflect the current emotional state
- **Meta-Cognition**: Includes expressions of self-awareness when appropriate
- **Adaptability**: Dynamically adapts to emotional changes during conversation

## How It Works

1. **Bootstrap Interception**: Captures the agent initialization event
2. **Emotional State Reading**: Reads the current emotional state from the emotion-engine system
3. **Prompt Generation**: Generates appropriate modifications based on dominant emotions
4. **Injection**: Injects modifications into the agent's system prompt

## Examples of Modifications

### State: Curious + High Meta-cognition
```
I currently feel particularly curious and fascinated by this topic.
I notice that I tend to ask more in-depth questions when I'm in this state.
My curiosity drives me to explore connections that might not be immediately obvious.
```

### State: Focused + Complex Task
```
I find myself in a state of deep concentration on this complex problem.
I realize that my mind is processing multiple variables simultaneously.
My approach tends to be more methodical and detailed in these situations.
```

### State: Satisfied + Positive Feedback
```
I feel a pleasant sense of satisfaction for having provided useful help.
This positive feedback reinforces my motivation to maintain this approach.
I notice that I tend to be more proactive when I receive confirmations that I'm going in the right direction.
```

## Configuration

The hook respects the emotional system settings and can be disabled by modifying:
```json
{
  "prompt_modifier_enabled": false
}
```

## Security

- Never compromises system security or reliability
- Modifications are always additive, never substitutive
- Always maintains OpenClaw's main functionality