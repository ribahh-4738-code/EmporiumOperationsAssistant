# Unofficial Admin UI for Chroma (flanker/chromadb-admin), built for Chroma server 1.5+ (JS client v2).
# Hub images (fengzhichao/sanderdw) are stale and call deprecated HTTP /api/v1 → 500 in the browser.

FROM node:20-bookworm-slim AS build
ARG CHROMADB_ADMIN_REF=efe867c86c78683d90b0eb74b88b351fc08f0b5f
RUN apt-get update \
  && apt-get install -y --no-install-recommends git ca-certificates \
  && rm -rf /var/lib/apt/lists/*
WORKDIR /src
RUN git clone --depth 1 https://github.com/flanker/chromadb-admin.git . \
  && git fetch origin "${CHROMADB_ADMIN_REF}" \
  && git checkout "${CHROMADB_ADMIN_REF}"
RUN npm ci && npm run build

FROM node:20-bookworm-slim
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build /src/package*.json ./
COPY --from=build /src/node_modules ./node_modules
COPY --from=build /src/.next ./.next
COPY --from=build /src/public ./public
EXPOSE 3001
CMD ["npm", "start"]
