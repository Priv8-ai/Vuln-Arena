FROM php:8.2-apache
COPY src/ /var/www/html/
RUN mkdir -p /var/www/html/vault /var/www/html/data && chown -R www-data:www-data /var/www/html \
 && echo 'ARENA{vault_secret_object}' > /var/www/html/vault/object-7.txt
EXPOSE 80
