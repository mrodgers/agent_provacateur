import { describe, it, expect, beforeEach, vi } from 'vitest';
import { RateLimiter } from '../../src/utils/rate-limiter';

describe('RateLimiter', () => {
  let rateLimiter: RateLimiter;
  
  beforeEach(() => {
    // Create a new rate limiter for each test
    rateLimiter = new RateLimiter({
      perSecond: 2,
      perDay: 5
    });
    
    // Mock timers
    vi.useFakeTimers();
  });
  
  it('should allow requests within the per-second limit', () => {
    // First request should be allowed
    expect(rateLimiter.allowRequest()).toBe(true);
    
    // Second request should be allowed
    expect(rateLimiter.allowRequest()).toBe(true);
    
    // Third request should be denied (exceeds per-second limit)
    expect(rateLimiter.allowRequest()).toBe(false);
  });
  
  it('should reset per-second limit after 1 second', () => {
    // Use up the per-second limit
    expect(rateLimiter.allowRequest()).toBe(true);
    expect(rateLimiter.allowRequest()).toBe(true);
    expect(rateLimiter.allowRequest()).toBe(false);
    
    // Advance time by 1 second
    vi.advanceTimersByTime(1001);
    
    // Should allow requests again
    expect(rateLimiter.allowRequest()).toBe(true);
    expect(rateLimiter.allowRequest()).toBe(true);
    expect(rateLimiter.allowRequest()).toBe(false);
  });
  
  it('should enforce per-day limit', () => {
    // Create a rate limiter with higher per-second but lower per-day limit
    const dayLimiter = new RateLimiter({
      perSecond: 10,
      perDay: 3
    });
    
    // Use up the per-day limit
    expect(dayLimiter.allowRequest()).toBe(true);
    expect(dayLimiter.allowRequest()).toBe(true);
    expect(dayLimiter.allowRequest()).toBe(true);
    
    // Fourth request should be denied (exceeds per-day limit)
    expect(dayLimiter.allowRequest()).toBe(false);
    
    // Advance time by 1 second to reset per-second limit
    vi.advanceTimersByTime(1001);
    
    // Still limited by per-day
    expect(dayLimiter.allowRequest()).toBe(false);
    
    // Advance time by 24 hours to reset per-day limit
    vi.advanceTimersByTime(24 * 60 * 60 * 1000);
    
    // Should allow requests again
    expect(dayLimiter.allowRequest()).toBe(true);
  });
  
  it('should provide accurate status', () => {
    const status = rateLimiter.getStatus();
    expect(status).toEqual({
      secondCount: 0,
      dayCount: 0,
      perSecond: 2,
      perDay: 5
    });
    
    // Make a request
    rateLimiter.allowRequest();
    
    const updatedStatus = rateLimiter.getStatus();
    expect(updatedStatus).toEqual({
      secondCount: 1,
      dayCount: 1,
      perSecond: 2,
      perDay: 5
    });
  });
  
  it('should reset all counters', () => {
    // Make some requests
    rateLimiter.allowRequest();
    rateLimiter.allowRequest();
    
    // Verify counters were incremented
    expect(rateLimiter.getStatus().secondCount).toBe(2);
    expect(rateLimiter.getStatus().dayCount).toBe(2);
    
    // Reset counters
    rateLimiter.reset();
    
    // Verify counters were reset
    expect(rateLimiter.getStatus().secondCount).toBe(0);
    expect(rateLimiter.getStatus().dayCount).toBe(0);
    
    // Should allow requests again
    expect(rateLimiter.allowRequest()).toBe(true);
  });
});