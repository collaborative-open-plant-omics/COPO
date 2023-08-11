FROM python:3.7.9-buster

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    default-jre \
    rsync \
    git \
	nano \
    libxml2-dev \
    python \
    build-essential \
    make \
    gcc \
    python3-dev \
    locales \
    python3-pip \
    ruby-dev \
    rubygems \
    poppler-utils && \
    gem install sass && \
    pip install --upgrade pip && \
    apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/*

COPY ./requirements/ /tmp/requirements/
RUN pip install --use-deprecated=legacy-resolver -r /tmp/requirements/dev.txt

RUN mkdir /copo
RUN mkdir /code

WORKDIR /copo
COPY . /code/

RUN wget -O webin-cli.jar https://github.com/enasequence/webin-cli/releases/download/6.3.0/webin-cli-6.3.0.jar

# add aspera client to path
COPY ./tools/reposit/.aspera/ /root/.aspera/
ENV PATH /root/.aspera/cli/bin:$PATH

ENTRYPOINT ["bash","-c","rsync -avhW --no-compress --progress /code/ /copo/ &&  rm -rf /code/ && python manage.py migrate && python manage.py social_accounts && python manage.py setup_groups && python manage.py setup_schemas && python manage.py createcachetable && supervisord -c celery.conf && supervisorctl -c celery.conf start all && sleep 10000000"]

# wget -nv -O- https://download.calibre-ebook.com/linux-installer.sh | sh /dev/stdin &&
