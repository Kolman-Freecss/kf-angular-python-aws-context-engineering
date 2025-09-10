import { Injectable, signal } from '@angular/core';

export interface PerformanceMetric {
  name: string;
  value: number;
  timestamp: number;
  type: 'navigation' | 'resource' | 'measure' | 'custom';
}

export interface NavigationTiming {
  loadTime: number;
  domContentLoaded: number;
  firstPaint?: number;
  firstContentfulPaint?: number;
  largestContentfulPaint?: number;
  firstInputDelay?: number;
  cumulativeLayoutShift?: number;
}

@Injectable({
  providedIn: 'root'
})
export class PerformanceService {
  private metrics = signal<PerformanceMetric[]>([]);
  private observers: PerformanceObserver[] = [];

  constructor() {
    this.initializePerformanceMonitoring();
  }

  /**
   * Initialize performance monitoring
   */
  private initializePerformanceMonitoring(): void {
    if (typeof window !== 'undefined' && 'performance' in window) {
      this.setupNavigationTiming();
      this.setupResourceTiming();
      this.setupPaintTiming();
      this.setupLayoutShift();
      this.setupFirstInputDelay();
    }
  }

  /**
   * Setup navigation timing monitoring
   */
  private setupNavigationTiming(): void {
    window.addEventListener('load', () => {
      setTimeout(() => {
        const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
        
        if (navigation) {
          this.addMetric('loadTime', navigation.loadEventEnd - navigation.loadEventStart, 'navigation');
          this.addMetric('domContentLoaded', navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart, 'navigation');
        }
      }, 0);
    });
  }

  /**
   * Setup resource timing monitoring
   */
  private setupResourceTiming(): void {
    const observer = new PerformanceObserver((list) => {
      list.getEntries().forEach((entry) => {
        if (entry.entryType === 'resource') {
          const resourceEntry = entry as PerformanceResourceTiming;
          this.addMetric(`resource_${resourceEntry.name}`, resourceEntry.duration, 'resource');
        }
      });
    });

    observer.observe({ entryTypes: ['resource'] });
    this.observers.push(observer);
  }

  /**
   * Setup paint timing monitoring
   */
  private setupPaintTiming(): void {
    const observer = new PerformanceObserver((list) => {
      list.getEntries().forEach((entry) => {
        if (entry.entryType === 'paint') {
          this.addMetric(entry.name, entry.startTime, 'measure');
        }
      });
    });

    observer.observe({ entryTypes: ['paint'] });
    this.observers.push(observer);
  }

  /**
   * Setup layout shift monitoring
   */
  private setupLayoutShift(): void {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          if (entry.entryType === 'layout-shift' && !(entry as any).hadRecentInput) {
            this.addMetric('cumulativeLayoutShift', (entry as any).value, 'measure');
          }
        });
      });

      observer.observe({ entryTypes: ['layout-shift'] });
      this.observers.push(observer);
    }
  }

  /**
   * Setup first input delay monitoring
   */
  private setupFirstInputDelay(): void {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          if (entry.entryType === 'first-input') {
            this.addMetric('firstInputDelay', (entry as any).processingStart - entry.startTime, 'measure');
          }
        });
      });

      observer.observe({ entryTypes: ['first-input'] });
      this.observers.push(observer);
    }
  }

  /**
   * Add a custom performance metric
   */
  addMetric(name: string, value: number, type: 'navigation' | 'resource' | 'measure' | 'custom' = 'custom'): void {
    const metric: PerformanceMetric = {
      name,
      value,
      timestamp: Date.now(),
      type
    };

    this.metrics.update(current => [...current, metric]);
  }

  /**
   * Start a performance mark
   */
  mark(name: string): void {
    if (typeof window !== 'undefined' && 'performance' in window) {
      performance.mark(name);
    }
  }

  /**
   * End a performance mark and measure
   */
  measure(name: string, startMark: string, endMark?: string): number {
    if (typeof window !== 'undefined' && 'performance' in window) {
      try {
        if (endMark) {
          performance.measure(name, startMark, endMark);
        } else {
          performance.measure(name, startMark);
        }

        const measure = performance.getEntriesByName(name, 'measure')[0];
        if (measure) {
          this.addMetric(name, measure.duration, 'measure');
          return measure.duration;
        }
      } catch (error) {
        console.warn('Performance measure failed:', error);
      }
    }
    return 0;
  }

  /**
   * Get navigation timing metrics
   */
  getNavigationTiming(): NavigationTiming | null {
    if (typeof window === 'undefined' || !('performance' in window)) {
      return null;
    }

    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    if (!navigation) {
      return null;
    }

    return {
      loadTime: navigation.loadEventEnd - navigation.loadEventStart,
      domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
      firstPaint: this.getMetricValue('first-paint'),
      firstContentfulPaint: this.getMetricValue('first-contentful-paint'),
      largestContentfulPaint: this.getMetricValue('largest-contentful-paint'),
      firstInputDelay: this.getMetricValue('firstInputDelay'),
      cumulativeLayoutShift: this.getMetricValue('cumulativeLayoutShift')
    };
  }

  /**
   * Get all performance metrics
   */
  getMetrics(): PerformanceMetric[] {
    return this.metrics();
  }

  /**
   * Get metrics by type
   */
  getMetricsByType(type: 'navigation' | 'resource' | 'measure' | 'custom'): PerformanceMetric[] {
    return this.metrics().filter(metric => metric.type === type);
  }

  /**
   * Get a specific metric value
   */
  getMetricValue(name: string): number | undefined {
    const metric = this.metrics().find(m => m.name === name);
    return metric?.value;
  }

  /**
   * Get performance score based on Core Web Vitals
   */
  getPerformanceScore(): number {
    const timing = this.getNavigationTiming();
    if (!timing) return 0;

    let score = 100;

    // First Contentful Paint (target: < 1.5s)
    if (timing.firstContentfulPaint) {
      if (timing.firstContentfulPaint > 3000) score -= 30;
      else if (timing.firstContentfulPaint > 1500) score -= 15;
    }

    // Largest Contentful Paint (target: < 2.5s)
    if (timing.largestContentfulPaint) {
      if (timing.largestContentfulPaint > 4000) score -= 30;
      else if (timing.largestContentfulPaint > 2500) score -= 15;
    }

    // First Input Delay (target: < 100ms)
    if (timing.firstInputDelay) {
      if (timing.firstInputDelay > 300) score -= 20;
      else if (timing.firstInputDelay > 100) score -= 10;
    }

    // Cumulative Layout Shift (target: < 0.1)
    if (timing.cumulativeLayoutShift) {
      if (timing.cumulativeLayoutShift > 0.25) score -= 20;
      else if (timing.cumulativeLayoutShift > 0.1) score -= 10;
    }

    return Math.max(0, score);
  }

  /**
   * Clear all metrics
   */
  clearMetrics(): void {
    this.metrics.set([]);
  }

  /**
   * Cleanup observers
   */
  ngOnDestroy(): void {
    this.observers.forEach(observer => observer.disconnect());
    this.observers = [];
  }
}
