import { EmotionalStateManager } from './ml_state_manager';
import { PatternRecognizer } from './pattern_recognizer';
import { NeuralNetworkManager } from './neural_network';
import { DatabaseManager } from './database_manager';
import { AnalyticsEngine } from './analytics_engine';

/**
 * Main entry point for the emotion-persistence plugin
 */
export class EmotionPersistencePlugin {
  private stateManager: EmotionalStateManager;
  private patternRecognizer: PatternRecognizer;
  private neuralNetworkManager: NeuralNetworkManager;
  private databaseManager: DatabaseManager;
  private analyticsEngine: AnalyticsEngine;
  private config: any;

  constructor(config: any = {}) {
    this.config = {
      database_path: config.database_path || '~/.openclaw/emotional_state.db',
      backup_enabled: config.backup_enabled ?? true,
      backup_interval_hours: config.backup_interval_hours || 24,
      data_retention_days: config.data_retention_days || 365,
      compression_enabled: config.compression_enabled ?? true,
      encryption_enabled: config.encryption_enabled ?? false,
      ...config
    };

    this.initializeComponents();
  }

  /**
   * Initialize all plugin components
   */
  private async initializeComponents(): Promise<void> {
    try {
      // Initialize database first
      this.databaseManager = new DatabaseManager(this.config);
      await this.databaseManager.initialize();

      // Initialize other components
      this.stateManager = new EmotionalStateManager(this.databaseManager, this.config);
      this.patternRecognizer = new PatternRecognizer(this.databaseManager, this.config);
      this.neuralNetworkManager = new NeuralNetworkManager(this.databaseManager, this.config);
      this.analyticsEngine = new AnalyticsEngine(this.databaseManager, this.config);

      console.log('Emotion persistence plugin initialized successfully');

    } catch (error) {
      console.error('Failed to initialize emotion persistence plugin:', error);
      throw error;
    }
  }

  /**
   * Plugin API: Get current emotional state
   */
  async getEmotionalState(sessionId?: string): Promise<any> {
    return await this.stateManager.getCurrentState(sessionId);
  }

  /**
   * Plugin API: Save emotional state
   */
  async saveEmotionalState(state: any, context: any = {}): Promise<void> {
    await this.stateManager.saveState(state, context);
  }

  /**
   * Plugin API: Get interaction history
   */
  async getInteractionHistory(filters: any = {}): Promise<any[]> {
    return await this.stateManager.getInteractionHistory(filters);
  }

  /**
   * Plugin API: Save ML training data
   */
  async saveMlTrainingData(features: number[], targets: number[], metadata: any = {}): Promise<void> {
    await this.neuralNetworkManager.saveTrainingData(features, targets, metadata);
  }

  /**
   * Plugin API: Get emotional analytics
   */
  async getEmotionalAnalytics(timeRange: any = {}): Promise<any> {
    return await this.analyticsEngine.generateAnalytics(timeRange);
  }

  /**
   * Plugin API: Train neural network
   */
  async trainNeuralNetwork(options: any = {}): Promise<any> {
    return await this.neuralNetworkManager.trainNetwork(options);
  }

  /**
   * Plugin API: Recognize patterns
   */
  async recognizePatterns(data: any): Promise<any> {
    return await this.patternRecognizer.recognizePatterns(data);
  }

  /**
   * Plugin API: Get learning insights
   */
  async getLearningInsights(): Promise<any> {
    return await this.analyticsEngine.generateLearningInsights();
  }

  /**
   * Plugin API: Backup data
   */
  async backupData(options: any = {}): Promise<string> {
    return await this.databaseManager.createBackup(options);
  }

  /**
   * Plugin API: Restore data
   */
  async restoreData(backupPath: string): Promise<void> {
    await this.databaseManager.restoreFromBackup(backupPath);
  }

  /**
   * Plugin API: Clean up old data
   */
  async cleanupOldData(retentionDays?: number): Promise<void> {
    const days = retentionDays || this.config.data_retention_days;
    await this.databaseManager.cleanupOldData(days);
  }

  /**
   * Plugin API: Export data for analysis
   */
  async exportData(format: 'json' | 'csv' = 'json', options: any = {}): Promise<string> {
    return await this.analyticsEngine.exportData(format, options);
  }

  /**
   * Plugin API: Get system health
   */
  async getSystemHealth(): Promise<any> {
    return {
      database: await this.databaseManager.getHealthStatus(),
      neural_network: await this.neuralNetworkManager.getStatus(),
      pattern_recognizer: await this.patternRecognizer.getStatus(),
      analytics: await this.analyticsEngine.getStatus(),
      config: this.config
    };
  }

  /**
   * Plugin hook: Startup
   */
  async startup(): Promise<void> {
    await this.initializeComponents();

    // Start periodic backup if enabled
    if (this.config.backup_enabled) {
      this.startPeriodicBackup();
    }

    // Cleanup old data
    await this.cleanupOldData();
  }

  /**
   * Plugin hook: Shutdown
   */
  async shutdown(): Promise<void> {
    try {
      // Create final backup
      if (this.config.backup_enabled) {
        await this.backupData({ reason: 'shutdown' });
      }

      // Close database connections
      await this.databaseManager.close();

      console.log('Emotion persistence plugin shut down successfully');

    } catch (error) {
      console.error('Error during emotion persistence plugin shutdown:', error);
    }
  }

  /**
   * Start periodic backup process
   */
  private startPeriodicBackup(): void {
    const intervalMs = this.config.backup_interval_hours * 60 * 60 * 1000;

    setInterval(async () => {
      try {
        await this.backupData({ reason: 'periodic' });
      } catch (error) {
        console.error('Periodic backup failed:', error);
      }
    }, intervalMs);
  }
}

// Export main plugin class and other components
export { EmotionalStateManager } from './ml_state_manager';
export { PatternRecognizer } from './pattern_recognizer';
export { NeuralNetworkManager } from './neural_network';
export { DatabaseManager } from './database_manager';
export { AnalyticsEngine } from './analytics_engine';

// OpenClaw plugin entry point - must export function (api) => {}
export default function (api: any) {
  const plugin = {
    id: 'emotion-persistence',
    name: 'Emotion Persistence',

    register(api: any) {
      console.log('Registering emotion-persistence plugin...');

      const pluginInstance = new EmotionPersistencePlugin(api.config || {});

      // Register API methods that other plugins/skills can call
      api.registerMethod('getEmotionalState', async (sessionId?: string) => {
        return await pluginInstance.getEmotionalState(sessionId);
      });

      api.registerMethod('saveEmotionalState', async (state: any, context: any = {}) => {
        await pluginInstance.saveEmotionalState(state, context);
      });

      api.registerMethod('getInteractionHistory', async (filters: any = {}) => {
        return await pluginInstance.getInteractionHistory(filters);
      });

      api.registerMethod('saveMlTrainingData', async (features: number[], targets: number[], metadata: any = {}) => {
        await pluginInstance.saveMlTrainingData(features, targets, metadata);
      });

      api.registerMethod('getEmotionalAnalytics', async (timeRange: any = {}) => {
        return await pluginInstance.getEmotionalAnalytics(timeRange);
      });

      api.registerMethod('trainNeuralNetwork', async (options: any = {}) => {
        return await pluginInstance.trainNeuralNetwork(options);
      });

      api.registerMethod('recognizePatterns', async (data: any) => {
        return await pluginInstance.recognizePatterns(data);
      });

      api.registerMethod('getLearningInsights', async () => {
        return await pluginInstance.getLearningInsights();
      });

      api.registerMethod('backupData', async (options: any = {}) => {
        return await pluginInstance.backupData(options);
      });

      api.registerMethod('restoreData', async (backupPath: string) => {
        await pluginInstance.restoreData(backupPath);
      });

      api.registerMethod('cleanupOldData', async (retentionDays?: number) => {
        await pluginInstance.cleanupOldData(retentionDays);
      });

      api.registerMethod('exportData', async (format: 'json' | 'csv' = 'json', options: any = {}) => {
        return await pluginInstance.exportData(format, options);
      });

      api.registerMethod('getSystemHealth', async () => {
        return await pluginInstance.getSystemHealth();
      });

      // Register lifecycle hooks
      api.on('startup', async () => {
        await pluginInstance.startup();
      });

      api.on('shutdown', async () => {
        await pluginInstance.shutdown();
      });

      console.log('Emotion-persistence plugin registered successfully');
    }
  };

  // Call register immediately
  plugin.register(api);
}