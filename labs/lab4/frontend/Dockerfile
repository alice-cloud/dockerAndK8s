FROM node-base as builder
WORKDIR /app
COPY . /app
RUN yarn build

FROM nginx:1.15.7-alpine
COPY --from=builder /app/build /usr/share/nginx/html/