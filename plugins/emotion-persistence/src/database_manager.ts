import Database from 'better-sqlite3';
import { join } from 'path';
import { homedir } from 'os';
import { existsSync, mkdirSync, copyFileSync, writeFileSync } from 'fs';
import { createHash } from 'crypto';

/**
 * Database manager for emotional intelligence persistence
 */
export class DatabaseManager {
  private db: Database.Database | null = null;
  private config: any;
  private dbPath: string;

  constructor(config: any) {
    this.config = config;
    this.dbPath = this.resolveDatabasePath(config.database_path);
  }

  /**
   * Initialize database with schema
   */
  async initialize(): Promise<void> {
    try {
      // Ensure directory exists
      const dbDir = join(this.dbPath, '..');
      if (!existsSync(dbDir)) {
        mkdirSync(dbDir, { recursive: true });
      }

      // Open database
      this.db = new Database(this.dbPath);
      this.db.pragma('journal_mode = WAL'); // Write-Ahead Logging for better performance
      this.db.pragma('foreign_keys = ON');

      // Create schema
      await this.createSchema();

      console.log(`Emotional intelligence database initialized at: ${this.dbPath}`);

    } catch (error) {
      console.error('Failed to initialize database:', error);
      throw error;
    }
  }

  /**
   * Create database schema
   */
  private async createSchema(): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    // Emotional states table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS emotional_states (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        session_id TEXT NOT NULL,
        state_data TEXT NOT NULL,
        meta_cognitive_state TEXT NOT NULL,
        confidence_score REAL NOT NULL,
        trigger_context TEXT,
        hash TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // Interactions table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        session_id TEXT NOT NULL,
        user_input TEXT NOT NULL,
        user_input_hash TEXT NOT NULL,
        context_data TEXT,
        sentiment_analysis TEXT NOT NULL,
        emotional_response TEXT NOT NULL,
        success_score REAL,
        feedback_score REAL,
        response_time_ms INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // ML training data table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS ml_training_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        session_id TEXT NOT NULL,
        features TEXT NOT NULL,
        targets TEXT NOT NULL,
        metadata TEXT,
        feedback_score REAL,
        used_for_training BOOLEAN DEFAULT 0,
        training_epoch INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // Pattern recognition table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS recognized_patterns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        session_id TEXT NOT NULL,
        pattern_type TEXT NOT NULL,
        pattern_data TEXT NOT NULL,
        confidence_score REAL NOT NULL,
        occurrence_count INTEGER DEFAULT 1,
        last_seen TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // Neural network states table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS neural_network_states (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        network_type TEXT NOT NULL,
        weights_data TEXT NOT NULL,
        biases_data TEXT NOT NULL,
        training_history TEXT,
        performance_metrics TEXT,
        version TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // Analytics cache table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS analytics_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cache_key TEXT UNIQUE NOT NULL,
        cache_data TEXT NOT NULL,
        expiry_timestamp TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // Configuration table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS system_config (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // Create indexes for better performance
    this.createIndexes();

    // Insert initial configuration
    this.insertInitialConfig();
  }

  /**
   * Create indexes for better query performance
   */
  private createIndexes(): void {
    if (!this.db) return;

    // Indexes for emotional_states
    this.db.exec(`CREATE INDEX IF NOT EXISTS idx_emotional_states_timestamp ON emotional_states(timestamp)`);
    this.db.exec(`CREATE INDEX IF NOT EXISTS idx_emotional_states_session ON emotional_states(session_id)`);
    this.db.exec(`CREATE INDEX IF NOT EXISTS idx_emotional_states_confidence ON emotional_states(confidence_score)`);

    // Indexes for interactions
    this.db.exec(`CREATE INDEX IF NOT EXISTS idx_interactions_timestamp ON interactions(timestamp)`);
    this.db.exec(`CREATE INDEX IF NOT EXISTS idx_interactions_session ON interactions(session_id)`);
    this.db.exec(`CREATE INDEX IF NOT EXISTS idx_interactions_success ON interactions(success_score)`);
    this.db.exec(`CREATE INDEX IF NOT EXISTS idx_interactions_hash ON interactions(user_input_hash)`);

    // Indexes for ML training data
    this.db.exec(`CREATE INDEX IF NOT EXISTS idx_ml_training_timestamp ON ml_training_data(timestamp)`);
    this.db.exec(`CREATE INDEX IF NOT EXISTS idx_ml_training_session ON ml_training_data(session_id)`);
    this.db.exec(`CREATE INDEX IF NOT EXISTS idx_ml_training_used ON ml_training_data(used_for_training)`);

    // Indexes for patterns
    this.db.exec(`CREATE INDEX IF NOT EXISTS idx_patterns_type ON recognized_patterns(pattern_type)`);
    this.db.exec(`CREATE INDEX IF NOT EXISTS idx_patterns_confidence ON recognized_patterns(confidence_score)`);
    this.db.exec(`CREATE INDEX IF NOT EXISTS idx_patterns_last_seen ON recognized_patterns(last_seen)`);

    // Indexes for analytics cache
    this.db.exec(`CREATE INDEX IF NOT EXISTS idx_analytics_cache_expiry ON analytics_cache(expiry_timestamp)`);
  }

  /**
   * Insert initial system configuration
   */
  private insertInitialConfig(): void {
    if (!this.db) return;

    const insert = this.db.prepare('INSERT OR REPLACE INTO system_config (key, value) VALUES (?, ?)');

    insert.run('schema_version', '1.0.0');
    insert.run('initialization_date', new Date().toISOString());
    insert.run('plugin_version', '1.0.0');
  }

  /**
   * Save emotional state
   */
  async saveEmotionalState(state: any, context: any = {}): Promise<number> {
    if (!this.db) throw new Error('Database not initialized');

    const timestamp = new Date().toISOString();
    const stateJson = JSON.stringify(state);
    const metaCognitiveJson = JSON.stringify(state.meta_cognitive_state || {});
    const contextJson = JSON.stringify(context);
    const hash = this.createHash(stateJson);

    const insert = this.db.prepare(`
      INSERT INTO emotional_states
      (timestamp, session_id, state_data, meta_cognitive_state, confidence_score, trigger_context, hash)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `);

    const result = insert.run(
      timestamp,
      state.session_id || 'unknown',
      stateJson,
      metaCognitiveJson,
      state.confidence_score || 0.5,
      contextJson,
      hash
    );

    return result.lastInsertRowid as number;
  }

  /**
   * Get latest emotional state
   */
  async getLatestEmotionalState(sessionId?: string): Promise<any> {
    if (!this.db) throw new Error('Database not initialized');

    let query = 'SELECT * FROM emotional_states';
    let params: any[] = [];

    if (sessionId) {
      query += ' WHERE session_id = ?';
      params.push(sessionId);
    }

    query += ' ORDER BY timestamp DESC LIMIT 1';

    const select = this.db.prepare(query);
    const result = select.get(...params);

    if (result) {
      return {
        ...result,
        state_data: JSON.parse(result.state_data as string),
        meta_cognitive_state: JSON.parse(result.meta_cognitive_state as string),
        trigger_context: result.trigger_context ? JSON.parse(result.trigger_context as string) : null
      };
    }

    return null;
  }

  /**
   * Save interaction
   */
  async saveInteraction(interaction: any): Promise<number> {
    if (!this.db) throw new Error('Database not initialized');

    const timestamp = new Date().toISOString();
    const userInputHash = this.createHash(interaction.user_input || '');

    const insert = this.db.prepare(`
      INSERT INTO interactions
      (timestamp, session_id, user_input, user_input_hash, context_data,
       sentiment_analysis, emotional_response, success_score, feedback_score, response_time_ms)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    const result = insert.run(
      timestamp,
      interaction.session_id || 'unknown',
      interaction.user_input || '',
      userInputHash,
      JSON.stringify(interaction.context || {}),
      JSON.stringify(interaction.sentiment_analysis || {}),
      JSON.stringify(interaction.emotional_response || {}),
      interaction.success_score || null,
      interaction.feedback_score || null,
      interaction.response_time_ms || null
    );

    return result.lastInsertRowid as number;
  }

  /**
   * Get interaction history
   */
  async getInteractionHistory(filters: any = {}): Promise<any[]> {
    if (!this.db) throw new Error('Database not initialized');

    let query = 'SELECT * FROM interactions WHERE 1=1';
    let params: any[] = [];

    if (filters.session_id) {
      query += ' AND session_id = ?';
      params.push(filters.session_id);
    }

    if (filters.since_timestamp) {
      query += ' AND timestamp >= ?';
      params.push(filters.since_timestamp);
    }

    if (filters.min_success_score) {
      query += ' AND success_score >= ?';
      params.push(filters.min_success_score);
    }

    query += ' ORDER BY timestamp DESC';

    if (filters.limit) {
      query += ' LIMIT ?';
      params.push(filters.limit);
    }

    const select = this.db.prepare(query);
    const results = select.all(...params);

    return results.map((row: any) => ({
      ...row,
      context_data: JSON.parse(row.context_data || '{}'),
      sentiment_analysis: JSON.parse(row.sentiment_analysis || '{}'),
      emotional_response: JSON.parse(row.emotional_response || '{}')
    }));
  }

  /**
   * Save ML training data
   */
  async saveMlTrainingData(features: number[], targets: number[], metadata: any = {}): Promise<number> {
    if (!this.db) throw new Error('Database not initialized');

    const timestamp = new Date().toISOString();

    const insert = this.db.prepare(`
      INSERT INTO ml_training_data
      (timestamp, session_id, features, targets, metadata, feedback_score)
      VALUES (?, ?, ?, ?, ?, ?)
    `);

    const result = insert.run(
      timestamp,
      metadata.session_id || 'unknown',
      JSON.stringify(features),
      JSON.stringify(targets),
      JSON.stringify(metadata),
      metadata.feedback_score || null
    );

    return result.lastInsertRowid as number;
  }

  /**
   * Get ML training data
   */
  async getMlTrainingData(filters: any = {}): Promise<any[]> {
    if (!this.db) throw new Error('Database not initialized');

    let query = 'SELECT * FROM ml_training_data WHERE 1=1';
    let params: any[] = [];

    if (filters.unused_only) {
      query += ' AND used_for_training = 0';
    }

    if (filters.min_feedback_score) {
      query += ' AND feedback_score >= ?';
      params.push(filters.min_feedback_score);
    }

    if (filters.limit) {
      query += ' ORDER BY timestamp DESC LIMIT ?';
      params.push(filters.limit);
    }

    const select = this.db.prepare(query);
    const results = select.all(...params);

    return results.map((row: any) => ({
      ...row,
      features: JSON.parse(row.features),
      targets: JSON.parse(row.targets),
      metadata: JSON.parse(row.metadata || '{}')
    }));
  }

  /**
   * Mark training data as used
   */
  async markTrainingDataAsUsed(ids: number[], epoch: number): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    const update = this.db.prepare(`
      UPDATE ml_training_data
      SET used_for_training = 1, training_epoch = ?
      WHERE id IN (${ids.map(() => '?').join(',')})
    `);

    update.run(epoch, ...ids);
  }

  /**
   * Save neural network state
   */
  async saveNeuralNetworkState(networkType: string, weights: any, biases: any, metadata: any = {}): Promise<number> {
    if (!this.db) throw new Error('Database not initialized');

    const timestamp = new Date().toISOString();

    const insert = this.db.prepare(`
      INSERT INTO neural_network_states
      (timestamp, network_type, weights_data, biases_data, training_history, performance_metrics, version)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `);

    const result = insert.run(
      timestamp,
      networkType,
      JSON.stringify(weights),
      JSON.stringify(biases),
      JSON.stringify(metadata.training_history || []),
      JSON.stringify(metadata.performance_metrics || {}),
      metadata.version || '1.0.0'
    );

    return result.lastInsertRowid as number;
  }

  /**
   * Get latest neural network state
   */
  async getLatestNeuralNetworkState(networkType: string): Promise<any> {
    if (!this.db) throw new Error('Database not initialized');

    const select = this.db.prepare(`
      SELECT * FROM neural_network_states
      WHERE network_type = ?
      ORDER BY timestamp DESC
      LIMIT 1
    `);

    const result = select.get(networkType);

    if (result) {
      return {
        ...result,
        weights_data: JSON.parse(result.weights_data as string),
        biases_data: JSON.parse(result.biases_data as string),
        training_history: JSON.parse(result.training_history as string),
        performance_metrics: JSON.parse(result.performance_metrics as string)
      };
    }

    return null;
  }

  /**
   * Save recognized pattern
   */
  async saveRecognizedPattern(pattern: any): Promise<number> {
    if (!this.db) throw new Error('Database not initialized');

    const timestamp = new Date().toISOString();

    // Check if pattern already exists
    const existing = this.db.prepare(`
      SELECT * FROM recognized_patterns
      WHERE pattern_type = ? AND pattern_data = ?
    `).get(pattern.type, JSON.stringify(pattern.data));

    if (existing) {
      // Update existing pattern
      const update = this.db.prepare(`
        UPDATE recognized_patterns
        SET occurrence_count = occurrence_count + 1,
            last_seen = ?,
            confidence_score = ?
        WHERE id = ?
      `);

      update.run(timestamp, pattern.confidence, existing.id);
      return existing.id;
    } else {
      // Insert new pattern
      const insert = this.db.prepare(`
        INSERT INTO recognized_patterns
        (timestamp, session_id, pattern_type, pattern_data, confidence_score, last_seen)
        VALUES (?, ?, ?, ?, ?, ?)
      `);

      const result = insert.run(
        timestamp,
        pattern.session_id || 'unknown',
        pattern.type,
        JSON.stringify(pattern.data),
        pattern.confidence,
        timestamp
      );

      return result.lastInsertRowid as number;
    }
  }

  /**
   * Get analytics data
   */
  async getAnalyticsData(query: string, params: any[] = []): Promise<any[]> {
    if (!this.db) throw new Error('Database not initialized');

    const select = this.db.prepare(query);
    return select.all(...params);
  }

  /**
   * Cache analytics result
   */
  async cacheAnalytics(key: string, data: any, expiryHours: number = 24): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    const expiryTimestamp = new Date(Date.now() + expiryHours * 60 * 60 * 1000).toISOString();

    const insert = this.db.prepare(`
      INSERT OR REPLACE INTO analytics_cache
      (cache_key, cache_data, expiry_timestamp)
      VALUES (?, ?, ?)
    `);

    insert.run(key, JSON.stringify(data), expiryTimestamp);
  }

  /**
   * Get cached analytics
   */
  async getCachedAnalytics(key: string): Promise<any> {
    if (!this.db) throw new Error('Database not initialized');

    const select = this.db.prepare(`
      SELECT cache_data FROM analytics_cache
      WHERE cache_key = ? AND expiry_timestamp > ?
    `);

    const result = select.get(key, new Date().toISOString());

    if (result) {
      return JSON.parse(result.cache_data);
    }

    return null;
  }

  /**
   * Create backup
   */
  async createBackup(options: any = {}): Promise<string> {
    if (!this.db) throw new Error('Database not initialized');

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const backupDir = join(homedir(), '.openclaw', 'emotion_backups');
    const backupPath = join(backupDir, `emotional_state_backup_${timestamp}.db`);

    // Ensure backup directory exists
    if (!existsSync(backupDir)) {
      mkdirSync(backupDir, { recursive: true });
    }

    // Create backup using SQLite backup API
    this.db.backup(backupPath);

    // Create metadata file
    const metadataPath = backupPath.replace('.db', '_metadata.json');
    const metadata = {
      backup_timestamp: new Date().toISOString(),
      original_db_path: this.dbPath,
      backup_reason: options.reason || 'manual',
      schema_version: '1.0.0',
      plugin_version: '1.0.0',
      record_counts: await this.getRecordCounts()
    };

    writeFileSync(metadataPath, JSON.stringify(metadata, null, 2));

    console.log(`Database backup created: ${backupPath}`);
    return backupPath;
  }

  /**
   * Restore from backup
   */
  async restoreFromBackup(backupPath: string): Promise<void> {
    if (!existsSync(backupPath)) {
      throw new Error(`Backup file not found: ${backupPath}`);
    }

    // Close current database
    if (this.db) {
      this.db.close();
    }

    // Copy backup to current location
    copyFileSync(backupPath, this.dbPath);

    // Reinitialize
    await this.initialize();

    console.log(`Database restored from backup: ${backupPath}`);
  }

  /**
   * Clean up old data
   */
  async cleanupOldData(retentionDays: number): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    const cutoffDate = new Date(Date.now() - retentionDays * 24 * 60 * 60 * 1000).toISOString();

    // Clean old interactions
    const deleteInteractions = this.db.prepare('DELETE FROM interactions WHERE timestamp < ?');
    const interactionsDeleted = deleteInteractions.run(cutoffDate);

    // Clean old emotional states (keep recent ones)
    const deleteStates = this.db.prepare(`
      DELETE FROM emotional_states
      WHERE timestamp < ? AND id NOT IN (
        SELECT id FROM emotional_states ORDER BY timestamp DESC LIMIT 100
      )
    `);
    const statesDeleted = deleteStates.run(cutoffDate);

    // Clean expired analytics cache
    const deleteCache = this.db.prepare('DELETE FROM analytics_cache WHERE expiry_timestamp < ?');
    const cacheDeleted = deleteCache.run(new Date().toISOString());

    // Vacuum database to reclaim space
    this.db.exec('VACUUM');

    console.log(`Cleanup completed: ${interactionsDeleted.changes} interactions, ${statesDeleted.changes} states, ${cacheDeleted.changes} cache entries deleted`);
  }

  /**
   * Get record counts for all tables
   */
  async getRecordCounts(): Promise<any> {
    if (!this.db) throw new Error('Database not initialized');

    const tables = ['emotional_states', 'interactions', 'ml_training_data', 'recognized_patterns', 'neural_network_states'];
    const counts: any = {};

    for (const table of tables) {
      const result = this.db.prepare(`SELECT COUNT(*) as count FROM ${table}`).get();
      counts[table] = result?.count || 0;
    }

    return counts;
  }

  /**
   * Get health status
   */
  async getHealthStatus(): Promise<any> {
    try {
      const recordCounts = await this.getRecordCounts();
      const dbSize = this.getDbSize();

      return {
        status: 'healthy',
        database_path: this.dbPath,
        database_size_mb: dbSize,
        record_counts: recordCounts,
        last_backup: this.getLastBackupInfo(),
        integrity_check: this.checkIntegrity()
      };
    } catch (error) {
      return {
        status: 'error',
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * Close database connection
   */
  async close(): Promise<void> {
    if (this.db) {
      this.db.close();
      this.db = null;
    }
  }

  // Helper methods
  private resolveDatabasePath(path: string): string {
    return path.replace('~', homedir());
  }

  private createHash(data: string): string {
    return createHash('sha256').update(data).digest('hex').substring(0, 16);
  }

  private getDbSize(): number {
    try {
      const stats = require('fs').statSync(this.dbPath);
      return Math.round(stats.size / 1024 / 1024 * 100) / 100; // MB with 2 decimal places
    } catch {
      return 0;
    }
  }

  private getLastBackupInfo(): any {
    try {
      const backupDir = join(homedir(), '.openclaw', 'emotion_backups');
      if (!existsSync(backupDir)) return null;

      const files = require('fs').readdirSync(backupDir)
        .filter((f: string) => f.endsWith('.db'))
        .sort()
        .reverse();

      if (files.length === 0) return null;

      const lastBackup = files[0];
      const stats = require('fs').statSync(join(backupDir, lastBackup));

      return {
        filename: lastBackup,
        timestamp: stats.mtime.toISOString(),
        size_mb: Math.round(stats.size / 1024 / 1024 * 100) / 100
      };
    } catch {
      return null;
    }
  }

  private checkIntegrity(): boolean {
    if (!this.db) return false;

    try {
      const result = this.db.prepare('PRAGMA integrity_check').get();
      return result && (result as any).integrity_check === 'ok';
    } catch {
      return false;
    }
  }
}