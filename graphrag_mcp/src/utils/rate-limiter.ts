/**
 * Rate Limiter Implementation for GraphRAG MCP Server
 * Provides rate limiting to protect resources.
 */

interface RateLimitConfig {
  requestsPerMinute: number;
  burstSize: number;
}

export class RateLimiter {
  private config: RateLimitConfig;
  private tokens: number;
  private lastRefill: number;
  private readonly refillRate: number; // tokens per millisecond
  
  /**
   * Initialize the rate limiter
   * @param config Rate limit configuration
   */
  constructor(config: RateLimitConfig) {
    this.config = config;
    this.tokens = config.burstSize; // Start with full token bucket
    this.lastRefill = Date.now();
    this.refillRate = config.requestsPerMinute / (60 * 1000); // tokens per millisecond
  }
  
  /**
   * Check if a request is allowed and consume a token if it is
   * @returns True if request is allowed, false if rate limit exceeded
   */
  allowRequest(): boolean {
    this.refillTokens();
    
    if (this.tokens >= 1) {
      // Consume a token
      this.tokens -= 1;
      return true;
    }
    
    return false;
  }
  
  /**
   * Refill tokens based on elapsed time
   */
  private refillTokens(): void {
    const now = Date.now();
    const elapsedMs = now - this.lastRefill;
    
    if (elapsedMs > 0) {
      // Calculate tokens to add based on elapsed time
      const newTokens = elapsedMs * this.refillRate;
      
      // Add tokens up to the burst size limit
      this.tokens = Math.min(this.config.burstSize, this.tokens + newTokens);
      
      // Update last refill time
      this.lastRefill = now;
    }
  }
  
  /**
   * Get the current token count (for testing/debugging)
   * @returns Current number of tokens in the bucket
   */
  getTokens(): number {
    this.refillTokens(); // Ensure token count is current
    return this.tokens;
  }
  
  /**
   * Get remaining time in ms until a request would be allowed
   * @returns Time in ms until next request would be allowed, or 0 if requests are allowed now
   */
  getWaitTime(): number {
    this.refillTokens();
    
    if (this.tokens >= 1) {
      return 0; // Request would be allowed now
    }
    
    // Calculate time until 1 token is available
    const neededTokens = 1 - this.tokens;
    return Math.ceil(neededTokens / this.refillRate);
  }
}