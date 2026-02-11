# Build stage
FROM node:22-alpine AS builder

WORKDIR /app/dashboard

# Copy package.json only first
COPY dashboard/package.json ./

# Install pnpm globally
RUN npm install -g pnpm

# Install dependencies (will generate pnpm-lock.yaml)
RUN pnpm install

# Copy patches
COPY dashboard/patches ../patches

# Copy source code
COPY dashboard/ .

# Build application
RUN pnpm build

# Runtime stage
FROM node:22-alpine

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy package.json
COPY dashboard/package.json ./

# Install production dependencies only
RUN pnpm install --prod

# Copy built application from builder
COPY --from=builder /app/dashboard/dist ./dist
COPY --from=builder /app/dashboard/client/dist ./client/dist

# Expose port (Railway uses PORT env var)
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})" || exit 1

# Start application
CMD ["node", "dist/index.js"]
