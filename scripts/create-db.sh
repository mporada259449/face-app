#!/bin/bash 
export DATABASE_USER=admin
export DATABASE_PASS=admin
export DATABASE_ADRESS=127.0.0.1
export DATABASE_PORT=5432
export DATABASE_NAME=app-db

if [ $(basename $(pwd)) != 'face-app' ]; then
    cd /tmp/face-app
fi

python3 -m venv venv
. venv/bin/activate
pip3 install -r requirements.txt

docker run -d \
    -p 5432:5432 \
    --name db-init \
    -v flask-app-data:/var/lib/postgresql/data \
    -e POSTGRES_USER="${DATABASE_USER}" \
    -e POSTGRES_PASSWORD="${DATABASE_PASS}" \
    -e POSTGRES_DB="${DATABASE_NAME}" \
    postgres:17-bullseye

sleep 30

flask db init
flask db migrate
flask db upgrade

docker exec db-init \
    psql -U admin -d app-db -c "INSERT INTO users (username, password, is_admin, id) VALUES ('admin', 'admin', true, 1);"

docker stop db-init
docker rm db-init 