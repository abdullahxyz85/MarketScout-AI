FROM node:20-alpine

RUN apk add --no-cache nginx

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

COPY nginx.conf /etc/nginx/http.d/default.conf
COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 5000

CMD ["/start.sh"]
