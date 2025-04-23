import winston from 'winston';
import config from './config';

const logger = winston.createLogger({
  level: config.logLevel,
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  defaultMeta: { service: 'entity-detector-mcp' },
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.timestamp(),
        winston.format.printf(info => {
          return `${info.timestamp} ${info.level}: ${info.message}`;
        })
      )
    })
  ]
});

export default logger;