FROM nginx:1.27-alpine
COPY gateway.conf /etc/nginx/nginx.conf
RUN mkdir -p /tmp/nginx && chown -R nginx:nginx /tmp/nginx
USER nginx
EXPOSE 18017-18044
CMD ["nginx", "-g", "daemon off;"]
