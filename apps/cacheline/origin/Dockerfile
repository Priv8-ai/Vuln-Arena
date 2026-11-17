FROM node:20-alpine
WORKDIR /app
COPY package.json server.js ./
RUN addgroup -S arena && adduser -S arena -G arena && chown -R arena:arena /app
USER arena
EXPOSE 8080
CMD ["node", "server.js"]
