# ── Stage 1: build the React app ─────────────────────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# Do NOT set VITE_API_URL — the app will default to the /api prefix,
# which nginx proxies to the backend container.
RUN npm run build

# ── Stage 2: serve with nginx ─────────────────────────────────────────────────
FROM nginx:alpine

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
