import { DatabaseManager } from './database_manager';

/**
 * Emotional State Manager for handling persistence and retrieval of emotional states
 */
export class EmotionalStateManager {
  private db: DatabaseManager;
  private config: any;
  private currentState: any = null;
  private stateCache: Map<string, any> = new Map();

  constructor(database: DatabaseManager, config: any) {
    this.db = database;
    this.config = config;
  }

  /**
   * Get current emotional state, with caching
   */
  async getCurrentState(sessionId?: string): Promise<any> {
    try {
      const cacheKey = sessionId || 'default';

      // Check cache first
      if (this.stateCache.has(cacheKey)) {
        const cached = this.stateCache.get(cacheKey);
        const now = Date.now();

        // Cache is valid for 5 minutes
        if (cached && (now - cached.timestamp) < 5 * 60 * 1000) {
          return cached.state;
        }
      }

      // Load from database
      const state = await this.db.getLatestEmotionalState(sessionId);

      if (state) {
        // Cache the result
        this.stateCache.set(cacheKey, {
          state: state.state_data,
          timestamp: Date.now()
        });

        this.currentState = state.state_data;
        return state.state_data;
      }

      // Return default state if nothing found
      return this.createDefaultState(sessionId);

    } catch (error) {
      console.error('Error getting current emotional state:', error);
      return this.createDefaultState(sessionId);
    }
  }

  /**
   * Save emotional state with validation and optimization
   */
  async saveState(state: any, context: any = {}): Promise<void> {
    try {
      // Validate state structure
      if (!this.validateState(state)) {
        throw new Error('Invalid emotional state structure');
      }

      // Add metadata
      const enrichedState = {
        ...state,
        timestamp: new Date().toISOString(),
        version: '1.0.0',
        validation_passed: true
      };

      // Save to database
      const stateId = await this.db.saveEmotionalState(enrichedState, context);

      // Update cache
      const cacheKey = state.session_id || 'default';
      this.stateCache.set(cacheKey, {
        state: enrichedState,
        timestamp: Date.now()
      });

      this.currentState = enrichedState;

      // Trigger state change listeners
      await this.notifyStateChange(enrichedState, context);

      console.log(`Emotional state saved with ID: ${stateId}`);

    } catch (error) {
      console.error('Error saving emotional state:', error);
      throw error;
    }
  }

  /**
   * Get interaction history with advanced filtering
   */
  async getInteractionHistory(filters: any = {}): Promise<any[]> {
    try {
      // Enhance filters with defaults
      const enhancedFilters = {
        limit: 50,
        ...filters
      };

      // Check cache for common queries
      const cacheKey = this.createCacheKey('interactions', enhancedFilters);
      const cached = await this.db.getCachedAnalytics(cacheKey);

      if (cached) {
        return cached;
      }

      // Load from database
      const history = await this.db.getInteractionHistory(enhancedFilters);

      // Process and enrich history
      const enrichedHistory = history.map(interaction => ({
        ...interaction,
        emotional_impact: this.calculateEmotionalImpact(interaction),
        learning_value: this.calculateLearningValue(interaction),
        pattern_significance: this.calculatePatternSignificance(interaction)
      }));

      // Cache result for 1 hour
      await this.db.cacheAnalytics(cacheKey, enrichedHistory, 1);

      return enrichedHistory;

    } catch (error) {
      console.error('Error getting interaction history:', error);
      return [];
    }
  }

  /**
   * Save interaction with emotional analysis
   */
  async saveInteraction(interaction: any): Promise<void> {
    try {
      // Enrich interaction with emotional analysis
      const enrichedInteraction = {
        ...interaction,
        timestamp: new Date().toISOString(),
        emotional_impact: this.calculateEmotionalImpact(interaction),
        learning_value: this.calculateLearningValue(interaction),
        response_time_ms: interaction.response_time_ms || null
      };

      // Save to database
      const interactionId = await this.db.saveInteraction(enrichedInteraction);

      // Update real-time analytics
      await this.updateRealTimeAnalytics(enrichedInteraction);

      console.log(`Interaction saved with ID: ${interactionId}`);

    } catch (error) {
      console.error('Error saving interaction:', error);
      throw error;
    }
  }

  /**
   * Get emotional state evolution over time
   */
  async getEmotionalEvolution(sessionId?: string, timeRange?: any): Promise<any> {
    try {
      const cacheKey = this.createCacheKey('evolution', { sessionId, timeRange });
      const cached = await this.db.getCachedAnalytics(cacheKey);

      if (cached) {
        return cached;
      }

      // Query for emotional states over time
      const query = `
        SELECT
          timestamp,
          state_data,
          confidence_score,
          trigger_context
        FROM emotional_states
        WHERE 1=1
        ${sessionId ? 'AND session_id = ?' : ''}
        ${timeRange?.start ? 'AND timestamp >= ?' : ''}
        ${timeRange?.end ? 'AND timestamp <= ?' : ''}
        ORDER BY timestamp ASC
      `;

      const params: any[] = [];
      if (sessionId) params.push(sessionId);
      if (timeRange?.start) params.push(timeRange.start);
      if (timeRange?.end) params.push(timeRange.end);

      const rawData = await this.db.getAnalyticsData(query, params);

      // Process evolution data
      const evolution = this.processEmotionalEvolution(rawData);

      // Cache for 6 hours
      await this.db.cacheAnalytics(cacheKey, evolution, 6);

      return evolution;

    } catch (error) {
      console.error('Error getting emotional evolution:', error);
      return { emotions_over_time: [], trends: {}, insights: [] };
    }
  }

  /**
   * Get emotional insights and patterns
   */
  async getEmotionalInsights(sessionId?: string): Promise<any> {
    try {
      const cacheKey = this.createCacheKey('insights', { sessionId });
      const cached = await this.db.getCachedAnalytics(cacheKey);

      if (cached) {
        return cached;
      }

      // Get recent interactions for analysis
      const interactions = await this.getInteractionHistory({
        session_id: sessionId,
        limit: 100
      });

      // Get emotional evolution
      const evolution = await this.getEmotionalEvolution(sessionId);

      // Generate insights
      const insights = {
        dominant_emotions: this.analyzeDominantEmotions(interactions),
        emotional_volatility: this.analyzeEmotionalVolatility(evolution),
        trigger_patterns: this.analyzeTriggerPatterns(interactions),
        learning_progression: this.analyzeLearningProgression(interactions),
        personality_traits: this.analyzePersonalityTraits(interactions),
        recommendations: this.generateRecommendations(interactions, evolution)
      };

      // Cache for 4 hours
      await this.db.cacheAnalytics(cacheKey, insights, 4);

      return insights;

    } catch (error) {
      console.error('Error getting emotional insights:', error);
      return { insights: [], patterns: [], recommendations: [] };
    }
  }

  /**
   * Validate emotional state structure
   */
  private validateState(state: any): boolean {
    try {
      // Check required fields
      if (!state.primary_emotions || typeof state.primary_emotions !== 'object') {
        return false;
      }

      if (!state.complex_emotions || typeof state.complex_emotions !== 'object') {
        return false;
      }

      if (!state.personality_traits || typeof state.personality_traits !== 'object') {
        return false;
      }

      // Check emotion values are numbers between 0 and 1
      const allEmotions = { ...state.primary_emotions, ...state.complex_emotions };

      for (const [emotion, value] of Object.entries(allEmotions)) {
        if (typeof value !== 'number' || value < 0 || value > 1) {
          console.warn(`Invalid emotion value for ${emotion}: ${value}`);
          return false;
        }
      }

      // Check personality traits
      for (const [trait, value] of Object.entries(state.personality_traits)) {
        if (typeof value !== 'number' || value < 0 || value > 1) {
          console.warn(`Invalid personality trait value for ${trait}: ${value}`);
          return false;
        }
      }

      return true;

    } catch (error) {
      console.error('Error validating state:', error);
      return false;
    }
  }

  /**
   * Create default emotional state
   */
  private createDefaultState(sessionId?: string): any {
    return {
      primary_emotions: {
        joy: 0.1,
        sadness: 0.05,
        anger: 0.05,
        fear: 0.1,
        surprise: 0.1,
        disgust: 0.05,
        curiosity: 0.3,
        trust: 0.2
      },
      complex_emotions: {
        excitement: 0.1,
        frustration: 0.05,
        satisfaction: 0.2,
        confusion: 0.1,
        anticipation: 0.15,
        pride: 0.1,
        empathy: 0.2,
        flow_state: 0.15
      },
      personality_traits: {
        extraversion: 0.6,
        openness: 0.8,
        conscientiousness: 0.7,
        agreeableness: 0.5,
        neuroticism: 0.3,
        curiosity_drive: 0.9,
        perfectionism: 0.4
      },
      meta_cognitive_state: {
        self_awareness: 0.7,
        emotional_volatility: 0.4,
        learning_rate: 0.6,
        reflection_depth: 0.8,
        introspective_tendency: 0.6,
        philosophical_inclination: 0.5
      },
      ml_state: {
        pattern_recognition_confidence: 0.5,
        adaptation_rate: 0.5,
        prediction_accuracy: 0.5,
        learning_episodes: 0
      },
      session_id: sessionId || `default_${Date.now()}`,
      timestamp: new Date().toISOString(),
      confidence_score: 0.5,
      is_default: true
    };
  }

  /**
   * Calculate emotional impact of interaction
   */
  private calculateEmotionalImpact(interaction: any): number {
    try {
      const sentiment = interaction.sentiment_analysis || {};
      const emotions = sentiment.emotions || {};

      // Calculate total emotional intensity
      const totalIntensity = Object.values(emotions)
        .filter(val => typeof val === 'number')
        .reduce((sum: number, val: any) => sum + Math.abs(val), 0);

      // Normalize to 0-1 range
      return Math.min(1.0, totalIntensity / 5.0);

    } catch (error) {
      return 0.5; // Default neutral impact
    }
  }

  /**
   * Calculate learning value of interaction
   */
  private calculateLearningValue(interaction: any): number {
    try {
      let learningValue = 0.5; // Base value

      // Increase for positive feedback
      if (interaction.feedback_score && interaction.feedback_score > 0.7) {
        learningValue += 0.3;
      }

      // Increase for high engagement
      if (interaction.user_input && interaction.user_input.length > 100) {
        learningValue += 0.2;
      }

      // Increase for complex emotional responses
      const emotionalResponse = interaction.emotional_response || {};
      const responseComplexity = Object.keys(emotionalResponse).length;
      learningValue += Math.min(0.2, responseComplexity * 0.05);

      return Math.min(1.0, learningValue);

    } catch (error) {
      return 0.5;
    }
  }

  /**
   * Calculate pattern significance
   */
  private calculatePatternSignificance(interaction: any): number {
    try {
      let significance = 0.3; // Base significance

      // Increase for repeated patterns
      const userInput = interaction.user_input || '';
      const commonPatterns = ['error', 'help', 'explain', 'how', 'what', 'why'];

      for (const pattern of commonPatterns) {
        if (userInput.toLowerCase().includes(pattern)) {
          significance += 0.1;
        }
      }

      // Increase for strong emotional responses
      const emotions = interaction.sentiment_analysis?.emotions || {};
      const strongEmotions = Object.values(emotions).filter((val: any) => val > 0.7);
      significance += strongEmotions.length * 0.15;

      return Math.min(1.0, significance);

    } catch (error) {
      return 0.3;
    }
  }

  /**
   * Notify state change listeners
   */
  private async notifyStateChange(state: any, context: any): Promise<void> {
    try {
      // Update current emotional state file for hook access
      const currentStatePath = require('path').join(require('os').homedir(), '.openclaw', 'current_emotional_state.json');
      require('fs').writeFileSync(currentStatePath, JSON.stringify(state, null, 2));

      // Could trigger other listeners here
      console.log('State change notification sent');

    } catch (error) {
      console.error('Error notifying state change:', error);
    }
  }

  /**
   * Update real-time analytics
   */
  private async updateRealTimeAnalytics(interaction: any): Promise<void> {
    try {
      // Update running averages, pattern counters, etc.
      // This would update cached analytics for dashboard views

      const analyticsKey = `realtime_stats_${new Date().toISOString().slice(0, 10)}`;
      let dailyStats = await this.db.getCachedAnalytics(analyticsKey) || {
        total_interactions: 0,
        average_sentiment: 0.5,
        dominant_emotions: {},
        learning_events: 0
      };

      dailyStats.total_interactions += 1;

      // Update average sentiment
      const newSentiment = interaction.sentiment_analysis?.overall_sentiment || 0.5;
      dailyStats.average_sentiment = (dailyStats.average_sentiment * (dailyStats.total_interactions - 1) + newSentiment) / dailyStats.total_interactions;

      // Update dominant emotions
      const emotions = interaction.sentiment_analysis?.emotions || {};
      for (const [emotion, intensity] of Object.entries(emotions)) {
        if (!dailyStats.dominant_emotions[emotion]) {
          dailyStats.dominant_emotions[emotion] = 0;
        }
        dailyStats.dominant_emotions[emotion] += (intensity as number);
      }

      // Cache updated stats
      await this.db.cacheAnalytics(analyticsKey, dailyStats, 24);

    } catch (error) {
      console.error('Error updating real-time analytics:', error);
    }
  }

  /**
   * Create cache key for consistent caching
   */
  private createCacheKey(type: string, params: any): string {
    const paramsString = JSON.stringify(params);
    const hash = require('crypto').createHash('md5').update(paramsString).digest('hex');
    return `${type}_${hash}`;
  }

  /**
   * Process emotional evolution data
   */
  private processEmotionalEvolution(rawData: any[]): any {
    if (rawData.length === 0) {
      return { emotions_over_time: [], trends: {}, insights: [] };
    }

    const emotionsOverTime = rawData.map(row => {
      const stateData = JSON.parse(row.state_data);
      return {
        timestamp: row.timestamp,
        emotions: stateData.primary_emotions,
        complex_emotions: stateData.complex_emotions,
        confidence: row.confidence_score
      };
    });

    // Calculate trends
    const trends = this.calculateEmotionalTrends(emotionsOverTime);

    // Generate insights
    const insights = this.generateEvolutionInsights(emotionsOverTime, trends);

    return {
      emotions_over_time: emotionsOverTime,
      trends: trends,
      insights: insights,
      timespan: {
        start: rawData[0].timestamp,
        end: rawData[rawData.length - 1].timestamp,
        data_points: rawData.length
      }
    };
  }

  /**
   * Calculate emotional trends
   */
  private calculateEmotionalTrends(data: any[]): any {
    const trends: any = {};
    const emotionNames = Object.keys(data[0]?.emotions || {});

    for (const emotion of emotionNames) {
      const values = data.map(d => d.emotions[emotion]).filter(v => v !== undefined);

      if (values.length >= 2) {
        const firstHalf = values.slice(0, Math.floor(values.length / 2));
        const secondHalf = values.slice(Math.floor(values.length / 2));

        const firstAvg = firstHalf.reduce((a, b) => a + b, 0) / firstHalf.length;
        const secondAvg = secondHalf.reduce((a, b) => a + b, 0) / secondHalf.length;

        trends[emotion] = {
          direction: secondAvg > firstAvg ? 'increasing' : 'decreasing',
          magnitude: Math.abs(secondAvg - firstAvg),
          significance: this.calculateTrendSignificance(values)
        };
      }
    }

    return trends;
  }

  /**
   * Calculate trend significance
   */
  private calculateTrendSignificance(values: number[]): number {
    if (values.length < 3) return 0;

    // Simple significance based on variance and trend consistency
    const variance = this.calculateVariance(values);
    const trendConsistency = this.calculateTrendConsistency(values);

    return Math.min(1.0, (1 - variance) * trendConsistency);
  }

  /**
   * Calculate variance
   */
  private calculateVariance(values: number[]): number {
    const mean = values.reduce((a, b) => a + b, 0) / values.length;
    const squaredDiffs = values.map(value => Math.pow(value - mean, 2));
    return squaredDiffs.reduce((a, b) => a + b, 0) / values.length;
  }

  /**
   * Calculate trend consistency
   */
  private calculateTrendConsistency(values: number[]): number {
    if (values.length < 2) return 0;

    let consistentMoves = 0;
    let totalMoves = values.length - 1;

    // Determine overall direction
    const overallDirection = values[values.length - 1] > values[0] ? 1 : -1;

    for (let i = 1; i < values.length; i++) {
      const moveDirection = values[i] > values[i - 1] ? 1 : -1;
      if (moveDirection === overallDirection) {
        consistentMoves++;
      }
    }

    return consistentMoves / totalMoves;
  }

  /**
   * Generate evolution insights
   */
  private generateEvolutionInsights(data: any[], trends: any): string[] {
    const insights: string[] = [];

    // Analyze dominant trends
    const significantTrends = Object.entries(trends)
      .filter(([_, trend]: [string, any]) => trend.significance > 0.6)
      .sort((a: any, b: any) => b[1].significance - a[1].significance);

    for (const [emotion, trend] of significantTrends.slice(0, 3)) {
      insights.push(
        `${emotion} ha mostrato una tendenza ${(trend as any).direction} significativa con magnitudine ${((trend as any).magnitude * 100).toFixed(1)}%`
      );
    }

    // Analyze stability
    const avgConfidence = data.reduce((sum, d) => sum + d.confidence, 0) / data.length;
    if (avgConfidence > 0.8) {
      insights.push('Lo stato emotivo ha mostrato alta stabilità e consistenza');
    } else if (avgConfidence < 0.4) {
      insights.push('Lo stato emotivo ha mostrato alta volatilità');
    }

    return insights;
  }

  // Additional analysis methods for insights
  private analyzeDominantEmotions(interactions: any[]): any {
    const emotionCounts: any = {};
    const emotionIntensities: any = {};

    for (const interaction of interactions) {
      const emotions = interaction.sentiment_analysis?.emotions || {};

      for (const [emotion, intensity] of Object.entries(emotions)) {
        if (!emotionCounts[emotion]) {
          emotionCounts[emotion] = 0;
          emotionIntensities[emotion] = 0;
        }

        if ((intensity as number) > 0.3) { // Only count significant emotions
          emotionCounts[emotion] += 1;
          emotionIntensities[emotion] += (intensity as number);
        }
      }
    }

    // Calculate averages and rankings
    const dominantEmotions = Object.entries(emotionCounts)
      .map(([emotion, count]) => ({
        emotion,
        frequency: count,
        average_intensity: emotionIntensities[emotion] / (count as number),
        total_impact: (count as number) * emotionIntensities[emotion]
      }))
      .sort((a, b) => b.total_impact - a.total_impact)
      .slice(0, 5);

    return dominantEmotions;
  }

  private analyzeEmotionalVolatility(evolution: any): number {
    const emotionsData = evolution.emotions_over_time || [];

    if (emotionsData.length < 2) return 0;

    let totalVolatility = 0;
    let validComparisons = 0;

    for (let i = 1; i < emotionsData.length; i++) {
      const prev = emotionsData[i - 1].emotions;
      const curr = emotionsData[i].emotions;

      let emotionChange = 0;
      let emotionCount = 0;

      for (const [emotion, value] of Object.entries(curr)) {
        if (prev[emotion] !== undefined) {
          emotionChange += Math.abs((value as number) - prev[emotion]);
          emotionCount++;
        }
      }

      if (emotionCount > 0) {
        totalVolatility += emotionChange / emotionCount;
        validComparisons++;
      }
    }

    return validComparisons > 0 ? totalVolatility / validComparisons : 0;
  }

  private analyzeTriggerPatterns(interactions: any[]): any[] {
    const patterns: any = {};

    for (const interaction of interactions) {
      const userInput = interaction.user_input?.toLowerCase() || '';
      const emotionalResponse = interaction.emotional_response || {};

      // Simple keyword-based pattern recognition
      const keywords = ['error', 'help', 'problem', 'thanks', 'great', 'wrong'];

      for (const keyword of keywords) {
        if (userInput.includes(keyword)) {
          if (!patterns[keyword]) {
            patterns[keyword] = { count: 0, emotional_responses: [] };
          }

          patterns[keyword].count += 1;
          patterns[keyword].emotional_responses.push(emotionalResponse);
        }
      }
    }

    return Object.entries(patterns)
      .map(([trigger, data]: [string, any]) => ({
        trigger,
        frequency: data.count,
        typical_response: this.calculateTypicalResponse(data.emotional_responses)
      }))
      .sort((a, b) => b.frequency - a.frequency);
  }

  private calculateTypicalResponse(responses: any[]): any {
    if (responses.length === 0) return {};

    const averages: any = {};

    for (const response of responses) {
      for (const [key, value] of Object.entries(response)) {
        if (typeof value === 'number') {
          if (!averages[key]) averages[key] = 0;
          averages[key] += value;
        }
      }
    }

    for (const key of Object.keys(averages)) {
      averages[key] /= responses.length;
    }

    return averages;
  }

  private analyzeLearningProgression(interactions: any[]): any {
    const progression = {
      total_interactions: interactions.length,
      average_learning_value: interactions.reduce((sum, i) => sum + (i.learning_value || 0.5), 0) / interactions.length,
      improvement_trend: 'stable'
    };

    // Analyze trend over time
    if (interactions.length >= 10) {
      const firstHalf = interactions.slice(0, Math.floor(interactions.length / 2));
      const secondHalf = interactions.slice(Math.floor(interactions.length / 2));

      const firstAvg = firstHalf.reduce((sum, i) => sum + (i.learning_value || 0.5), 0) / firstHalf.length;
      const secondAvg = secondHalf.reduce((sum, i) => sum + (i.learning_value || 0.5), 0) / secondHalf.length;

      if (secondAvg > firstAvg + 0.1) {
        progression.improvement_trend = 'improving';
      } else if (secondAvg < firstAvg - 0.1) {
        progression.improvement_trend = 'declining';
      }
    }

    return progression;
  }

  private analyzePersonalityTraits(interactions: any[]): any {
    // This would analyze how personality traits have evolved
    // For now, return a placeholder
    return {
      stability: 'high',
      dominant_traits: ['curiosity_drive', 'openness'],
      evolution_rate: 'moderate'
    };
  }

  private generateRecommendations(interactions: any[], evolution: any): string[] {
    const recommendations: string[] = [];

    const avgSentiment = interactions.reduce((sum, i) => sum + (i.sentiment_analysis?.overall_sentiment || 0.5), 0) / interactions.length;

    if (avgSentiment < 0.3) {
      recommendations.push('Considerare strategie per migliorare l\'engagement e il sentiment positivo');
    }

    const volatility = this.analyzeEmotionalVolatility(evolution);
    if (volatility > 0.7) {
      recommendations.push('Alta volatilità emotiva rilevata - considerare stabilizzazione dei trigger');
    }

    if (interactions.length < 10) {
      recommendations.push('Raccogliere più dati per analisi più accurate');
    }

    return recommendations;
  }
}