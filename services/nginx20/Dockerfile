FROM tutum/nginx

RUN rm /etc/nginx/sites-enabled/default && \
    mkdir -p /var/www/html
COPY sites-enabled/ /etc/nginx/sites-enabled

COPY custom_pages/ /var/www/html

ENV MAINURL copo-project.cyverseuk.org/

ADD configure.sh configure.sh
RUN chmod +x configure.sh

ENTRYPOINT ./configure.sh