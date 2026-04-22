# Use official Node.js LTS Alpine image (small and secure)
FROM node:18-alpine

# Set working directory inside the container
WORKDIR /app

# Copy package files first (Docker layer caching optimization)
COPY backend/package*.json ./backend/

# Install production dependencies only
RUN cd backend && npm install --production

# Copy all remaining project files
COPY . .

# Expose application port
EXPOSE 3000

# Start the application
CMD ["node", "backend/server.js"]
