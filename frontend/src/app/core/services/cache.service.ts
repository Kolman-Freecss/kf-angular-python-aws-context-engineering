import { Injectable, signal } from '@angular/core';

export interface CacheItem<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

@Injectable({
  providedIn: 'root'
})
export class CacheService {
  private cache = new Map<string, CacheItem<any>>();
  private cacheStats = signal({
    hits: 0,
    misses: 0,
    size: 0
  });

  /**
   * Set a value in the cache with TTL (Time To Live)
   */
  set<T>(key: string, data: T, ttlMinutes: number = 5): void {
    const item: CacheItem<T> = {
      data,
      timestamp: Date.now(),
      ttl: ttlMinutes * 60 * 1000 // Convert minutes to milliseconds
    };
    
    this.cache.set(key, item);
    this.updateStats();
  }

  /**
   * Get a value from the cache
   */
  get<T>(key: string): T | null {
    const item = this.cache.get(key);
    
    if (!item) {
      this.cacheStats.update(stats => ({ ...stats, misses: stats.misses + 1 }));
      return null;
    }

    // Check if item has expired
    if (this.isExpired(item)) {
      this.cache.delete(key);
      this.cacheStats.update(stats => ({ ...stats, misses: stats.misses + 1 }));
      return null;
    }

    this.cacheStats.update(stats => ({ ...stats, hits: stats.hits + 1 }));
    return item.data;
  }

  /**
   * Check if cache item has expired
   */
  private isExpired(item: CacheItem<any>): boolean {
    return Date.now() - item.timestamp > item.ttl;
  }

  /**
   * Remove a specific key from cache
   */
  delete(key: string): boolean {
    const deleted = this.cache.delete(key);
    this.updateStats();
    return deleted;
  }

  /**
   * Clear all cache entries
   */
  clear(): void {
    this.cache.clear();
    this.updateStats();
  }

  /**
   * Clear expired entries
   */
  clearExpired(): void {
    const now = Date.now();
    for (const [key, item] of this.cache.entries()) {
      if (now - item.timestamp > item.ttl) {
        this.cache.delete(key);
      }
    }
    this.updateStats();
  }

  /**
   * Get cache statistics
   */
  getStats() {
    return this.cacheStats();
  }

  /**
   * Update cache statistics
   */
  private updateStats(): void {
    this.cacheStats.update(stats => ({ ...stats, size: this.cache.size }));
  }

  /**
   * Check if key exists in cache
   */
  has(key: string): boolean {
    const item = this.cache.get(key);
    if (!item) return false;
    
    if (this.isExpired(item)) {
      this.cache.delete(key);
      this.updateStats();
      return false;
    }
    
    return true;
  }

  /**
   * Get cache size
   */
  size(): number {
    return this.cache.size;
  }
}
