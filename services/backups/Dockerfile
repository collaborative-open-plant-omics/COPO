FROM alpine:3.15

RUN apk update
RUN apk upgrade
RUN apk add bash

RUN apk --update add mongodb mongodb-tools
RUN apk --update add postgresql-client
RUN apk --update add nano

# create backup directories
RUN mkdir -p /backup/mongo
RUN mkdir -p /backup/postgres

# set up cron jobs
ADD crontab.txt /crontab.txt
ADD script.sh /script.sh
ADD restore.sh /restore.sh

COPY entry.sh /entry.sh
RUN chmod 755 /script.sh /entry.sh /restore.sh

RUN /usr/bin/crontab /crontab.txt

CMD ["/entry.sh"]
