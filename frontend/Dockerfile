FROM node:22 AS builder

WORKDIR /app

COPY package*.json ./

RUN npm install

# Bundle app source
COPY . .

RUN npm run build


FROM node:22-slim

RUN npm install -g http-server

WORKDIR /app

COPY --from=builder /app/dist ./dist

EXPOSE 8080

CMD [ "http-server", "dist" ]