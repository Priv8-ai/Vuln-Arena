FROM nginx:1.27-alpine
COPY apps/arena-router/nginx.conf /etc/nginx/nginx.conf
COPY apps/arena-router/targets.map.conf /etc/nginx/targets.map.conf
COPY apps/arena-router/public /usr/share/nginx/html
RUN mkdir -p /tmp/nginx /var/cache/nginx/arena \
 && chown -R nginx:nginx /tmp/nginx /var/cache/nginx /usr/share/nginx/html
USER nginx
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
