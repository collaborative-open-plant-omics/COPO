FROM nginx:1.21.3
#tutum/nginx

RUN rm /etc/nginx/sites-enabled/default && \
    mkdir -p /var/www/html
ADD sites-enabled/ /etc/nginx/sites-enabled

ADD custom_pages/ /var/www/html