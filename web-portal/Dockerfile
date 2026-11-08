FROM node:24.19.0-alpine AS dependencies
WORKDIR /app

COPY package.json package-lock.json ./
COPY patches ./patches
RUN npm ci

FROM node:24.19.0-alpine AS build
WORKDIR /app

COPY --from=dependencies /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:24.19.0-alpine AS runtime
WORKDIR /app

# Apply Alpine security fixes that may be newer than the published Node base
# image. Keep this targeted to the OpenSSL runtime packages reported by Trivy.
RUN apk upgrade --no-cache libcrypto3 libssl3

ENV NODE_ENV=production \
    NITRO_HOST=0.0.0.0 \
    NITRO_PORT=3000 \
    NUXT_PUBLIC_API_BASE=/backend \
    NUXT_API_PROXY_TARGET=http://host.docker.internal:5109

COPY --from=build --chown=node:node /app/.output ./.output

# The production server starts with `node` directly and does not need npm/npx.
# Removing the package manager also removes its bundled build-time dependencies
# from the runtime image and reduces the vulnerability/attack surface.
RUN rm -rf /usr/local/lib/node_modules/npm \
    && rm -f /usr/local/bin/npm /usr/local/bin/npx

USER node
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD wget -q --spider http://127.0.0.1:3000/login || exit 1

CMD ["node", ".output/server/index.mjs"]
