FROM tutum/nginx

RUN rm /etc/nginx/sites-enabled/default && \
    mkdir -p /var/www/html
COPY ./services/nginx20/sites-enabled/ /etc/nginx/sites-enabled

COPY ./services/nginx20/custom_pages/ /var/www/html

ENV MAINURL copo-project.cyverseuk.org/

CMD sed -i 's\copodev.cyverseuk.org/\'"${MAINURL}"'\g' /var/www/html/502.html