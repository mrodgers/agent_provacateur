/**
 * Rate limiting configuration
 */
export interface RateLimitConfig {
  perSecond: number;
  perDay: number;
}

/**
 * Simple rate limiter implementation for API requests
 */
export class RateLimiter {
  private perSecond: number;
  private perDay: number;
  private secondCount: number = 0;
  private dayCount: number = 0;
  private lastSecondReset: number;
  private lastDayReset: number;
  
  constructor(config: RateLimitConfig) {
    this.perSecond = config.perSecond;
    this.perDay = config.perDay;
    this.lastSecondReset = Date.now();
    this.lastDayReset = Date.now();
  }
  
  /**
   * Check if a request is allowed under the current rate limits
   * @returns True if request is allowed, false if rate limited
   */
  allowRequest(): boolean {
    const now = Date.now();
    
    // Reset second counter if needed
    if (now - this.lastSecondReset > 1000) {
      this.secondCount = 0;
      this.lastSecondReset = now;
    }
    
    // Reset day counter if needed
    if (now - this.lastDayReset > 86400000) { // 24 hours
      this.dayCount = 0;
      this.lastDayReset = now;
    }
    
    // Check if the request exceeds the rate limits
    if (this.secondCount >= this.perSecond || this.dayCount >= this.perDay) {
      return false;
    }
    
    // Increment counters
    this.secondCount++;
    this.dayCount++;
    
    return true;
  }
  
  /**
   * Get the current rate limit status
   */
  getStatus(): { secondCount: number; dayCount: number; perSecond: number; perDay: number } {
    return {
      secondCount: this.secondCount,
      dayCount: this.dayCount,
      perSecond: this.perSecond,
      perDay: this.perDay
    };
  }
  
  /**
   * Reset all rate limit counters
   */
  reset(): void {
    this.secondCount = 0;
    this.dayCount = 0;
    this.lastSecondReset = Date.now();
    this.lastDayReset = Date.now();
  }
}