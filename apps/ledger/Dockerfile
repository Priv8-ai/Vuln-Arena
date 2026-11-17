FROM php:8.2-apache
RUN apt-get update && apt-get install -y --no-install-recommends libsqlite3-dev iputils-ping \
 && docker-php-ext-install pdo pdo_sqlite \
 && a2enmod rewrite headers \
 && sed -i 's/AllowOverride None/AllowOverride All/g' /etc/apache2/apache2.conf \
 && rm -rf /var/lib/apt/lists/*
COPY src/ /var/www/html/
RUN chown -R www-data:www-data /var/www/html && mkdir -p /var/www/html/data /var/www/html/uploads \
 && chown -R www-data:www-data /var/www/html/data /var/www/html/uploads
EXPOSE 80
