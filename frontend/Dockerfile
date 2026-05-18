# ── Frontend Dockerfile ─────────────────────────────────────────────────────
# Nginx Alpine — lightweight static file server + reverse proxy for /api/
FROM nginx:alpine

# Metadata
LABEL maintainer="FA23-BCS-201"
LABEL description="Quick-Task Hub — Frontend (Nginx)"

# Remove default nginx page
RUN rm -rf /usr/share/nginx/html/*

# Copy the static frontend application
COPY index.html /usr/share/nginx/html/index.html

# Copy custom nginx configuration (includes API proxy)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose HTTP port
EXPOSE 80

# Nginx runs in foreground
CMD ["nginx", "-g", "daemon off;"]
