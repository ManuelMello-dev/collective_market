# Build stage
FROM node:22-alpine AS builder

WORKDIR /app

# Copy package.json (pnpm-lock.yaml is optional)
COPY dashboard/package.json ./
COPY dashboard/patches ./patches

# Install pnpm globally
RUN npm install -g pnpm

# Install dependencies (will generate pnpm-lock.yaml if not present)
RUN pnpm install || pnpm install --no-frozen-lockfile

# Copy source code
COPY dashboard/ ./

# Build application
RUN pnpm build

# Runtime stage
FROM node:22-alpine

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy package.json and create a production-only version without patches
COPY dashboard/package.json ./package.json.orig
RUN node -e "const pkg = require('./package.json.orig'); delete pkg.pnpm.patchedDependencies; require('fs').writeFileSync('./package.json', JSON.stringify(pkg, null, 2))"

# Install production dependencies only (patches removed from package.json)
RUN pnpm install --prod --frozen-lockfile 2>/dev/null || pnpm install --prod

# Copy built application from builder
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/client/dist ./client/dist

# Expose port (Railway uses PORT env var)
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})" || exit 1

# Start application
CMD ["node", "dist/index.js"]
