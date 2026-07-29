# ── Stage 1: build the React app ─────────────────────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# VITE_REQUIRE_AUTH is passed from docker-compose build args.
# When true: Microsoft login is enforced. When false/unset: open access (dev/Vercel).
ARG VITE_REQUIRE_AUTH=false
ENV VITE_REQUIRE_AUTH=$VITE_REQUIRE_AUTH

RUN npm run build

# ── Stage 2: serve with nginx ─────────────────────────────────────────────────
FROM nginx:alpine

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
