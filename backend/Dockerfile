# ── Backend Dockerfile ──────────────────────────────────────────────────────
# Node.js 18 LTS Alpine — small, secure, production-ready
FROM node:18-alpine

# Metadata
LABEL maintainer="FA23-BCS-201"
LABEL description="Quick-Task Hub — Backend API"

# Set working directory
WORKDIR /app

# Copy package manifests first for layer caching
COPY package*.json ./

# Install production dependencies only
RUN npm install --production

# Copy application source
COPY . .

# Expose API port
EXPOSE 3000

# Health check — verifies the server responds
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD wget -qO- http://localhost:3000/api/health || exit 1

# Start the server
CMD ["node", "server.js"]
