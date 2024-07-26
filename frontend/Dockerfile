ARG NODE_VERSION=22

FROM node:${NODE_VERSION} AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM node:${NODE_VERSION}-slim
RUN npm install -g http-server
WORKDIR /app
COPY --from=builder /app/dist ./dist
EXPOSE 8080
CMD [ "http-server", "dist" ]