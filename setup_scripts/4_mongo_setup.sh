#!/bin/bash
MONGO_USER=copo_user
MONGO_PASSWORD=password
mongosh localhost/admin --eval "db.createUser({user: '$MONGO_USER', pwd: '$MONGO_PASSWORD', roles:[{ role:'readWrite', db: 'copo_mongo' }]})"

MONGO_USER=admin
MONGO_PASSWORD=password
mongosh localhost/admin --eval "db.createUser({user: '$MONGO_USER', pwd: '$MONGO_PASSWORD', roles:[{ role:'userAdminAnyDatabase', db: 'admin' }]})"

