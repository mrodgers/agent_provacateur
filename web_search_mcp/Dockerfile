FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./
COPY tsconfig.json ./

# Copy source files before install
COPY src/ ./src/

# Install dependencies and build
RUN npm ci && npm run build

# Runtime image
FROM node:20-alpine AS runtime

WORKDIR /app

# Copy built files and production dependencies
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./

# Environment variables
ENV NODE_ENV=production
ENV DEFAULT_SEARCH_PROVIDER=brave
ENV ENABLE_CACHE=true
ENV CACHE_TTL_SECONDS=3600
ENV RATE_LIMIT_PER_SECOND=1
ENV RATE_LIMIT_PER_DAY=1000

# Make output directory executable
RUN chmod +x ./dist/index.js

# Run the server
ENTRYPOINT ["node", "dist/index.js"]