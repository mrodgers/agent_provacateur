FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY tsconfig.json ./
COPY src/ ./src/

# Build TypeScript code
RUN npm install -g typescript
RUN tsc

# Create logs directory
RUN mkdir -p logs

# Expose API port
EXPOSE 8083

# Set environment variables
ENV NODE_ENV=production
ENV PORT=8083

# Start the server
CMD ["node", "dist/index.js"]