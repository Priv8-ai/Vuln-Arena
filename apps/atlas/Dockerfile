FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/nginx.conf
COPY www/ /usr/share/nginx/html/
COPY leaks/ /usr/share/nginx/leaks/
EXPOSE 80
