# build stage
FROM node:18-alpine AS build
WORKDIR /app
COPY package.json .
RUN npm install --production
COPY . .

# runtime stage
FROM node:18-alpine
WORKDIR /app
COPY --from=build /app .
EXPOSE 3000
CMD ["node","index.js"]
