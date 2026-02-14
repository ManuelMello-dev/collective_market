# Build stage
FROM node:22-alpine AS builder

WORKDIR /app

# Copy package.json and patches
COPY dashboard/package.json ./
COPY dashboard/patches ./patches

# Install pnpm globally
RUN npm install -g pnpm

# Install dependencies
RUN pnpm install --no-frozen-lockfile

# Copy source code
COPY dashboard/ ./

# Build application
RUN pnpm build

# Runtime stage
FROM node:22-alpine

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy package.json AND patches (needed for pnpm to validate dependencies)
COPY dashboard/package.json ./
COPY dashboard/patches ./patches

# Install production dependencies only
RUN pnpm install --prod --no-optional

# Copy built application from builder
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/client/dist ./client/dist

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})" || exit 1

# Start application
CMD ["node", "dist/index.js"]
