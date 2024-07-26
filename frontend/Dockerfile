FROM node:22

RUN npm install -g http-server

WORKDIR /app

COPY package*.json ./

RUN npm install

# Bundle app source
COPY . .

RUN npm run build

EXPOSE 8080

CMD [ "http-server", "dist" ]