# T059/T060: Frontend Dockerfile - Multi-stage build with Node.js 18 + Nginx

# Stage 1: Builder
ARG NODE_VERSION=18
FROM node:${NODE_VERSION}-alpine AS builder
WORKDIR /app

# Copy package files
COPY package.json ./

# Install dependencies
RUN npm install --ignore-scripts

# Copy application source
COPY . .

# Build the React app
RUN npm run build

# Stage 2: Nginx Runtime
FROM nginx:alpine AS runtime

# Install curl for health checks
RUN apk add --no-cache curl

# Copy custom nginx config for SPA routing
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built static files from builder
COPY --from=builder /app/build /usr/share/nginx/html

# Security: run as non-root user
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chown -R nginx:nginx /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid

USER nginx

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:80/ || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
