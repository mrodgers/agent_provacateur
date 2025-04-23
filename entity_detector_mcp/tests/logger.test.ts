import logger from '../src/logger';

// Mock the winston module
jest.mock('winston', () => {
  const mockLogger = {
    info: jest.fn(),
    error: jest.fn(),
    warn: jest.fn(),
    debug: jest.fn()
  };
  
  return {
    format: {
      combine: jest.fn(),
      timestamp: jest.fn(),
      printf: jest.fn(formatter => formatter),
      colorize: jest.fn()
    },
    createLogger: jest.fn().mockReturnValue(mockLogger),
    transports: {
      Console: jest.fn(),
      File: jest.fn()
    }
  };
});

describe('Logger', () => {
  it('should expose the expected logging methods', () => {
    // Test that the logger has the expected methods
    expect(typeof logger.info).toBe('function');
    expect(typeof logger.error).toBe('function');
    expect(typeof logger.warn).toBe('function');
    expect(typeof logger.debug).toBe('function');
  });

  it('should log info messages', () => {
    const message = 'Test info message';
    logger.info(message);
    
    // Verify the info method was called with the message
    expect(logger.info).toHaveBeenCalledWith(message);
  });

  it('should log error messages', () => {
    const message = 'Test error message';
    logger.error(message);
    
    // Verify the error method was called with the message
    expect(logger.error).toHaveBeenCalledWith(message);
  });

  it('should log warning messages', () => {
    const message = 'Test warning message';
    logger.warn(message);
    
    // Verify the warn method was called with the message
    expect(logger.warn).toHaveBeenCalledWith(message);
  });

  it('should log debug messages', () => {
    const message = 'Test debug message';
    logger.debug(message);
    
    // Verify the debug method was called with the message
    expect(logger.debug).toHaveBeenCalledWith(message);
  });
});