FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --omit=dev --no-fund --no-audit
COPY src ./src
EXPOSE 5000
CMD ["node", "src/server.js"]
