FROM node:20-slim AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
# The base image's entrypoint envsubst's every *.template file here into
# /etc/nginx/conf.d/ at container startup, using NGINX_ENVSUBST_FILTER (set
# in docker-compose.yml) to substitute only ${BACKEND_URL} and leave nginx's
# own $uri/$host/$remote_addr variables untouched.
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
EXPOSE 80
