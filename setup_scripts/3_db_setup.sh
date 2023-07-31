#!/bin/bash

#run this from COPO folder, not setup_scripts

# create postgres database, user and permissions
POSTGRES_USER=copo_user
POSTGRES_DB=copo
POSTGRES_PASSWORD=password
sudo -u postgres createuser -s $POSTGRES_USER
sudo -u postgres createdb $POSTGRES_DB
#psql postgres -c "alter user $POSTGRES_USER with encrypted password '$POSTGRES_PASSWORD';"
sudo -u postgres psql postgres -c "alter user $POSTGRES_USER with encrypted password '$POSTGRES_PASSWORD';"
#psql postgres -c "grant all privileges on database $POSTGRES_DB to $POSTGRES_USER ;"
sudo -u postgres psql postgres -c "grant all privileges on database $POSTGRES_DB to $POSTGRES_USER ;"
#psql postgres -c "ALTER USER $POSTGRES_USER CREATEDB;"
sudo -u postgres psql postgres -c "ALTER USER $POSTGRES_USER CREATEDB;"

# run django/copo setup functions
python manage.py makemigrations
python manage.py makemigrations chunked_upload
python manage.py makemigrations allauth
python manage.py migrate
python manage.py setup_groups
python manage.py setup_schemas
python manage.py createcachetable
python manage.py social_accounts

# setup allauth social accounts....N.B. you should have environmental variables set for $ORCID_CLIENT_ID and $ORCID_SECRET
export PGPASSWORD=$POSTGRES_PASSWORD; psql -h 'localhost' -U  $POSTGRES_USER -d 'copo' -c 'DELETE FROM socialaccount_socialapp_sites'
export PGPASSWORD=$POSTGRES_PASSWORD; psql -h 'localhost' -U  $POSTGRES_USER -d 'copo' -c 'DELETE FROM django_site'
export PGPASSWORD=$POSTGRES_PASSWORD; psql -h 'localhost' -U  $POSTGRES_USER -d 'copo' -c 'DELETE FROM socialaccount_socialapp'
export PGPASSWORD=$POSTGRES_PASSWORD; psql -h 'localhost' -U  $POSTGRES_USER -d 'copo' -c "INSERT INTO django_site (id, domain, name) VALUES (1, 'www.copo-project.org', 'www.copo-project.org')"
# export PGPASSWORD=$POSTGRES_PASSWORD; psql -h 'localhost' -U  $POSTGRES_USER -d 'copo' -c "INSERT INTO socialaccount_socialapp (id, provider, name, client_id, secret, key) VALUES (1, 'orcid', 'Orcid', '$ORCID_CLIENT_ID', '$ORCID_SECRET', '')"
export PGPASSWORD=$POSTGRES_PASSWORD; psql -h 'localhost' -U  $POSTGRES_USER -d 'copo' -c 'INSERT INTO socialaccount_socialapp_sites (id, socialapp_id, site_id) VALUES (1, 1, 1)'
