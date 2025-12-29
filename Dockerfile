# Multi-service Dockerfile for German AI Language Learner

# =============================================================================
# Backend Stage
# =============================================================================
FROM python:3.11-slim AS backend

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies for Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy backend source code
COPY backend /app

EXPOSE 8000

# Default environment variables (can be overridden via docker-compose)
ENV MONGODB_URI="mongodb://localhost:27017" \
    MONGODB_DB_NAME="german" \
    JWT_SECRET="change-me" \
    DEV_MODE=false

# Run backend API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# =============================================================================
# Frontend Dependencies Stage
# =============================================================================
FROM node:20-alpine AS frontend-deps

WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# =============================================================================
# Frontend Build Stage
# =============================================================================
FROM node:20-alpine AS frontend-build

WORKDIR /app

# Accept API URL as build argument
ARG NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}

COPY --from=frontend-deps /app/node_modules ./node_modules
COPY frontend ./
RUN npm run build

# =============================================================================
# Frontend Runtime Stage
# =============================================================================
FROM node:20-alpine AS frontend

WORKDIR /app
ENV NODE_ENV=production

# Copy built application
COPY --from=frontend-build /app/.next ./.next
COPY --from=frontend-build /app/public ./public
COPY --from=frontend-build /app/package.json ./package.json
COPY --from=frontend-build /app/next.config.mjs ./next.config.mjs
COPY --from=frontend-build /app/node_modules ./node_modules

EXPOSE 3000

# Run frontend
CMD ["npm", "run", "start"]
