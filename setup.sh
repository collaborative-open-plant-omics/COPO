#!/bin/bash


# function to set environmental vars
set_envs(){
export ENVIRONMENT_TYPE="dev"
export COPO_VM_NAME="copo_env"
# django secret key.....this must be changed before any public deployment
export SECRET_KEY=f9834op2ji0ikaiowdu9hgcg-9iojla

# admin user and password for mongo and postgres
export MONGO_ADMIN_USER=admin
export MONGO_ADMIN_PASSWORD=password
export POSTGRES_ADMIN_USER=postgres
export POSTGRES_ADMIN_PASSWORD=

# settings for mongo service
export MONGO_DB=copo_mongo
export MONGO_HOST=127.0.0.1
export MONGO_PORT=27017
export MONGO_MAX_POOL_SIZE=10
export MONGO_USER=mongo_user
export MONGO_PASSWORD=mongo_user

# settings for postgres
export POSTGRES_DB=copo
export POSTGRES_USER=postgres_user
export POSTGRES_PASSWORD=postgres_user
export POSTGRES_SERVICE=127.0.0.1
export POSTGRES_PORT=5432

# settings for redis service; visible to the web container; matches docker-compose.yml
export REDIS_HOST=127.0.0.1
export REDIS_PORT=6379

# settings for orcid
export ORCID_REDIRECT=http://127.0.0.1/accounts/orcid/login/callback/
export MEDIA_PATH=media/

# settings for ENA
export WEBIN_USER=
export WEBIN_USER_PASSWORD=
# note this is the test service....url for live service can be found at
# https://www.ebi.ac.uk/ena/submit/programmatic-submission....USE WITH CAUTION!
export ENA_SERVICE=https://www-test.ebi.ac.uk
# settings for aspera
# choose from 'aspera_mac_plugin' or 'aspera_linux_plugin'
# TODO - this can be infered from user questions
export ASPERA_PLUGIN_DIRECTORY=aspera_linux_plugin
}


divider() {
      s=$(printf "%-30s" "-")
      echo "${s// /-}"
      printf "\n"
    }
div=divider

get_user_envs(){
# set other environment variables which may vary or need to be kept secret
if [ $1 == "install" ]
then
printf "In order to proceed you need to have created an App for ORCiD (https://orcid.org/developer-tools).
You will need the 'Client Key' and 'Secret Key'. Additionally, if you have set an administrator account for PostgreSQL
different from the defaults, you will need to enter these as well. Press return to proceed or Ctrl-C to exit.
If you already have these details exported in existing environment variables jus press enter at the prompt.\n"
elif [[ $1 == "env" ]]
then
printf "Enter details at prompt...\n"
fi

# check if postgres admin user account supplied
printf "Enter PostgreSQL admin user if different from default: ($POSTGRES_ADMIN_USER)\n"
read input
if [[ $input != "" ]]
then
	export POSTGRES_ADMIN_USER=$input
    printf "Using $input \n"
else
	printf "Using Default ($POSTGRES_ADMIN_USER)\n"
fi
divider
# check if postgres admin password supplied
printf "Enter PostgreSQL admin password (if set):\n"
read input
if [[ $input != "" ]]
then
	export POSTGRES_ADMIN_PASSWORD=$input
    printf "Using $input \n"
else
	printf "Using Default ($POSTGRES_ADMIN_PASSWORD)\n"
fi
divider
# check if MongoDB account supplied
printf "Enter MongoDB admin user if different from default: ($MONGO_ADMIN_USER):\n"
read input
if [[ $input != "" ]]
then
	export MONGO_ADMIN_USER=$input
    printf "Using $input \n"
else
	printf "Using Default ($MONGO_ADMIN_USER)\n"
fi
divider
# check if MongoDB password supplied
printf "Enter MongoDB admin password if different from default: ($MONGO_ADMIN_PASSWORD):\n"
read input
if [[ $input != "" ]]
then
	export MONGO_ADMIN_PASSWORD=$input
    printf "Using $input \n"
else
	printf "Using Default ($MONGO_ADMIN_USER)\n"
fi


divider
# get ORCiD Client ID
if [[ $ORCID_CLIENT_ID == "" ]]
then
    printf "Enter Orcid Client Key:\n"
    read input
    while [[ $input == "" ]]
    do
        printf "Enter Orcid Client Key:\n"
        read input
    done
    export ORCID_CLIENT_ID=$input
    printf "Using $input \n"

    divider
fi
if [[ $ORCID_SECRET == "" ]]
then
    # get ORCiD secret key
    printf "Enter Orcid Secret Key:\n"
    read input
    while [[ $input == "" ]]
    do
        printf "Enter Orcid Secret Key:\n"
        read input
    done
    export ORCID_SECRET=$input
    printf "Using $input \n"fi
fi
}



# embedded python function to get system info
function check_os {
python - <<END
# check os version
import platform
p = platform.platform()
if "Darwin" in p:
    print("Darwin")
elif "Linux" in p:
    if "Ubuntu" in platform.linux_distribution()[0]:
        print("Ubuntu")
    elif "CentOS" in platform.linux_distribution()[0]:
        print("CentOS")
END
}

# get working location of this script....this is needed later
local_dir=$(dirname $0)
# get os
opsys=$(check_os)
printf '\nDetermining OS: %s\n' "$opsys"
# get current user
me=$(whoami)
printf 'Welcome: %s\n' "$me"

if [ $# -eq 0 ]
then
  printf "\nCOPO Setup: Missing Argument\n"
  printf "Options are:\n"
  printf "run - runs installed COPO instance\n"
  printf "install - installs development instance of COPO on this machine along with all its dependencies\n"
  printf "env <filepath> - export environment variables to <filepath>. Required to run COPO independently of this script.\n\n"
elif [ $1 == "env" ]
then
  # first remove existing file at location
  rm $2
  set_envs
  get_user_envs env
  x=$(env | grep -E 'REDIS|MONGO|POSTGRES|COPO|ORCID|MEDIA|SECRET')
  for line in $x ; do
    echo export $line >> $2
  done
elif [ $1 == "run" ]
then
  set_envs
  printf "Starting COPO...\n"
	  mongod --fork -- logpath "~/mongolog/"
  if [ "$opsys" == "Darwin" ]
  then
    brew services start postgres
  else
    service postgresql start
  fi
  printf "To stop press Ctrl-C...\n"
  source $COPO_VM_NAME/bin/activate
  $local_dir/web/src/manage.py runserver

elif [ $1 == "test" ]

  set_envs
  printf "Testing...\n"
  mongod --fork
  if [ "$opsys" == "Darwin" ]
  then
    brew services start postgres
  else
    service postgresql start
  fi
  printf "To stop press Ctrl-C...\n"
  source $COPO_VM_NAME/bin/activate
  $local_dir/web/src/manage.py test tests
then
    echo test
elif [ $1 == "install" ]
then
    python -c "exit"
    if [ "$?" -eq 127 ]
    then
      echo "Python not found on this system. Please install any version of python and try again"
      exit
    fi

    # START
    printf "This script will install a development ready instance of COPO onto your machine along with all its dependencies. Only OSX and Ubuntu installations are currently supported. \n"
    printf "If you are asked for a password, it will be the password you use for sudo"
    $div
    set_envs
    get_user_envs install


    if [[ $opsys == "Darwin" ]]
    then
      brew info
      if [ "$?" -eq 127 ]
      then
        # brew not installed so install it and update
        printf "installing homebrew\n"
        /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
        brew update
        pac_man='brew'
      else
        # brew is installed now update
        pac_man='brew'
      fi
    elif [[ $opsys == "Ubuntu" ]]
    then

      pac_man='apt-get -q'
    elif [[ $opsys == "CentOS" ]]
    then
      pac_man='yum'
    fi
    printf "updating packages\n"
    $pac_man update


    # first determine the current OS
    os=check

    # now check dependencies are installed
    $pac_man install -y git libpq-dev libbz2-dev liblzma-dev libxml2-dev libxslt1-dev
    easy_install lxml


    if [[ $opsys == "Darwin" ]]
    then
      # install python3
      $pac_man install -y python3
      # install MongoDB
      $pac_man install mongodb
      echo making data/db/
      sudo mkdir -p /data/db
      brew services start mongodb
      # install redis
      $pac_man install redis
      $pac_man services start redis
      # install postgres
      $pac_man install postgresql
      printf "Attempting to allow access to copo database on PostgreSQL. If this doesn't work, add the following line at the top of your pg_hba.conf file:\n
      local     copo    all     trust\n
      then restart PostgreSQL."
      echo -e "local\t\tcopo\t\tall\t\ttrust\n$(cat /usr/local/var/postgres/pg_hba.conf)" > /usr/local/var/postgres/pg_hba.conf
      $pac_man services restart postgresql
      $pac_man install poppler

      printf "Attempting to add required users to PostgreSQL. If this fails, try adding a .pgpass file to your home directory
      which should contain a line like:
      \n *:*:*:<admin_username>:<admin_password>\n
      remember to restart postgres"
      printf "Press any key to continue\n"
      read


      # create psql user and db
      sudo -u $me createuser $POSTGRES_USER
      sudo -u $me createdb $POSRGRES_DB
      psql postgres $me -c "alter user $POSTGRES_USER with encrypted password '$POSTGRES_PASSWORD';"
      psql postgres $me -c "grant all privileges on database $POSTGRES_DB to $POSTGRES_USER ;"
      psql postgres $me -c "ALTER USER $POSTGRES_USER CREATEDB;"

      # install virtual env
      pip3 install virtualenv
      virtualenv -p python3 $COPO_VM_NAME
      source $local_dir/$COPO_VM_NAME/bin/activate
      pip3 install --upgrade setuptools
      pip3 install -r $local_dir/requirements/base.txt
      $local_dir/manage.py makemigrations
      $local_dir/manage.py makemigrations chunked_upload
      $local_dir/manage.py makemigrations allauth
      $local_dir/manage.py migrate
      $local_dir/manage.py setup_groups
      $local_dir/manage.py setup_schemas

      # add social account records
      psql $POSTGRES_DB $POSTGRES_USER -c "DELETE FROM socialaccount_socialapp_sites"
      psql $POSTGRES_DB $POSTGRES_USER -c "DELETE FROM django_site"
      psql $POSTGRES_DB $POSTGRES_USER -c "DELETE FROM socialaccount_socialapp"
      psql $POSTGRES_DB $POSTGRES_USER -c "INSERT INTO django_site (id, domain, name) VALUES (1, 'www.copo-project.org', 'www.copo-project.org')"
      psql $POSTGRES_DB $POSTGRES_USER -c "INSERT INTO socialaccount_socialapp (id, provider, name, client_id, secret, key) VALUES (1, 'orcid', 'Orcid', '$ORCID_CLIENT_ID', '$ORCID_SECRET', '')"
      psql $POSTGRES_DB $POSTGRES_USER -c "INSERT INTO socialaccount_socialapp_sites (id, socialapp_id, site_id) VALUES (1, 1, 1)"
      div
      sudo gem install sass
      printf "Finished Installing....type 'setup run' to run the COPO development server."
    #elif [[ $opsys == "Ubuntu" ]]
    #then
      $pac_man --allow-unauthenticated install -y python3
      # import public key used by apt-get
      $pac_man install -y apt-transport-https
      apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2930ADAE8CAF5059EE73BB4B58712A2291FA4AD5
      # create list file for MongoDB
      echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.6 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-3.6.list
      $pac_man update
      # install and start mongo
      $pac_man install -y mongodb-org
      # need to start mongo without auth, make admin user and copo_user, then
      # restart with auth
      mongod --fork --config /etc/mongod.conf
      mongo localhost/admin --eval "db.createUser({user: '$MONGO_ADMIN_USER', pwd: '$MONGO_ADMIN_PASSWORD', roles:[{ role: 'userAdminAnyDatabase', db: 'admin' } ]});"
      mongo localhost/admin --eval "db.createUser({user: '$MONGO_USER', pwd: '$MONGO_PASSWORD', roles:[{ role:'readWrite', db: 'copo_mongo' }]})"
      #mongo localhost/admin --eval "db.shutdownServer()"
      #mongod --fork --config /etc/mongod.conf
      # install and start redis
      $pac_man install -y curl
      $pac_man install -y redis-server
      service redis-server start
      $pac_man install -y postgresql postgresql-contrib python-psycopg2 libpq-dev
      service postgresql start
      # install sudo for postgres setup
      $pac_man install -y sudo
      # TODO change thse later for user input strings
      # create psql user and db
      # TODO - change authentication in pg_hba.conf to trust for setup and change
      # back to md5 as last thing, this will stop auth errors from occuring if then
      # installation is interupted for some reason.
      echo -e "local\t\tcopo\t\tall\t\ttrust\n$(cat /etc/postgresql/$(ls /etc/postgresql)/main/pg_hba.conf)" > /etc/postgresql/$(ls /etc/postgresql)/main/pg_hba.conf
      service postgresql restart



      printf "Attempting to add required users to PostgreSQL. If this fails, try adding a .pgpass file to your home directory
      which should contain a line like:
      \n *:*:*:<admin_username>:<admin_password>\n
      remember to restart postgres"
      printf "Press any key to continue\n"
      read


      sudo -u postgres createuser $POSTGRES_USER
      sudo -u postgres createdb $POSTGRES_DB
      sudo -u postgres psql -c "alter user $POSTGRES_USER with encrypted password '$POSTGRES_PASSWORD';"
      sudo -u postgres psql -c "grant all privileges on database $POSTGRES_DB to $POSTGRES_USER;"
      sudo -u postgres psql -c "ALTER USER $POSTGRES_USER CREATEDB;"
      # setup pgpass file for later command access
      #echo *:*:copo:postgres_user:postgres_user > ~/.pgpass
      #chmod 0600 ~/.pgpass
      #service postgresql restart
      # install venv
      $pac_man install -y python-setuptools
      easy_install pip
      $pac_man -y install python3-pip
      pip3 install virtualenv
      virtualenv -p python3 $COPO_VM_NAME
      source $COPO_VM_NAME/bin/activate
      pip3 install --upgrade setuptools
      pip3 install -r /$local_dir/web/src/requirements/base.txt
      $local_dir/manage.py makemigrations
      $local_dir/manage.py makemigrations chunked_upload
      $local_dir/manage.py makemigrations allauth
      $local_dir/manage.py migrate
      $local_dir/manage.py setup_groups
      $local_dir/manage.py setup_schemas

      # add social account records
      psql $POSTGRES_DB $POSTGRES_USER -c "DELETE FROM socialaccount_socialapp_sites"
      psql $POSTGRES_DB $POSTGRES_USER -c "DELETE FROM django_site"
      psql $POSTGRES_DB $POSTGRES_USER -c "DELETE FROM socialaccount_socialapp"
      psql $POSTGRES_DB $POSTGRES_USER -c "INSERT INTO django_site (id, domain, name) VALUES (1, 'www.copo-project.org', 'www.copo-project.org')"
      psql $POSTGRES_DB $POSTGRES_USER -c "INSERT INTO socialaccount_socialapp (id, provider, name, client_id, secret, key) VALUES (1, 'orcid', 'Orcid', '$ORCID_CLIENT_ID', '$ORCID_SECRET', '')"
      psql $POSTGRES_DB $POSTGRES_USER -c "INSERT INTO socialaccount_socialapp_sites (id, socialapp_id, site_id) VALUES (1, 1, 1)"
      div
      apt-get install ruby-full rubygems
      gem install sass
      printf "Finished Installing....type 'setup run' to run the COPO development server.\n\n\n"
    fi

fi