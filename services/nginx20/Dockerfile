FROM tutum/nginx

RUN rm /etc/nginx/sites-enabled/default && \
    mkdir -p /var/www/html
ADD ./services/nginx20/sites-enabled/ /etc/nginx/sites-enabled

ADD ./services/nginx20/custom_pages/ /var/www/html