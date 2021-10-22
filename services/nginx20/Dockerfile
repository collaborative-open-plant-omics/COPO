FROM tutum/nginx

RUN rm /etc/nginx/sites-enabled/default && \
    mkdir -p /var/www/html
COPY ./services/nginx20/sites-enabled/ /etc/nginx/sites-enabled

COPY ./services/nginx20/custom_pages/ /var/www/html

ENV MAINURL copo-project.cyverseuk.org/

ADD ./services/nginx20/configure.sh configure.sh
RUN chmod +x configure.sh

ENTRYPOINT ./configure.sh