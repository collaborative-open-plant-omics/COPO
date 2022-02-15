#!/usr/bin/env bash


# usage: file_env VAR [DEFAULT]
#    ie: file_env 'XYZ_DB_PASSWORD' 'example'
# (will allow for "$XYZ_DB_PASSWORD_FILE" to fill in the value of
#  "$XYZ_DB_PASSWORD" from a file, especially for Docker's secrets feature)
file_env() {
	local var="$1"
	local fileVar="${var}_FILE"
	local def="${2:-}"
	if [ "${!var:-}" ] && [ "${!fileVar:-}" ]; then
		echo >&2 "error: both $var and $fileVar are set (but are exclusive)"
		exit 1
	fi
	local val="$def"
	if [ "${!var:-}" ]; then
		val="${!var}"
	elif [ "${!fileVar:-}" ]; then
		val="$(< "${!fileVar}")"
	fi
	export "$var"="$val"
	unset "$fileVar"
}

file_env 'MONGO_USER'
file_env 'MONGO_USER_PASSWORD'
file_env 'MONGO_INITDB_ROOT_USERNAME'
file_env 'MONGO_INITDB_ROOT_PASSWORD'


echo $MONGO_USER $MONGO_USER_PASSWORD $MONGO_INITDB_ROOT_USERNAME $MONGO_INITDB_ROOT_PASSWORD


if [ "$MONGO_USER" -a "$MONGO_USER_PASSWORD" -a "$MONGO_INITDB_ROOT_USERNAME" -a "$MONGO_INITDB_ROOT_PASSWORD" ]; then
    USER=${MONGO_USER}
	PASS=${MONGO_USER_PASSWORD}
	ADMIN_USER=${MONGO_INITDB_ROOT_USERNAME}
	ADMIN_PASS=${MONGO_INITDB_ROOT_PASSWORD}
else
   exit 1
fi

DB=${MONGO_DB:-admin}
ROLE=readWrite

echo "creating Mongo user: \"$USER\"..."
mongo admin -u $ADMIN_USER -p $ADMIN_PASS --eval "db.createUser({ user: '$USER', pwd: '$PASS', roles: [ { role: '$ROLE', db: '$DB' } ] });"

echo "Mongo user created!"




