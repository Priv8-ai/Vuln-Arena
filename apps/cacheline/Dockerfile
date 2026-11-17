FROM nginx:1.27-alpine
COPY apps/cacheline/nginx.conf /etc/nginx/nginx.conf
COPY apps/cacheline/public /usr/share/nginx/html
COPY shared/ui/chrome.css /usr/share/nginx/html/assets/chrome.css
COPY shared/ui/chrome.js /usr/share/nginx/html/assets/chrome.js
RUN mkdir -p /var/cache/nginx/arena /tmp/nginx \
 && chown -R nginx:nginx /var/cache/nginx /tmp/nginx /usr/share/nginx/html
EXPOSE 8080
