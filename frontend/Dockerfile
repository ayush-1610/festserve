FROM node:18-alpine
WORKDIR /app
COPY package.json vite.config.js index.html ./
RUN npm install
COPY src/ ./src
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]