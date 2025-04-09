#!/bin/bash
echo DATABASE_USER=admin >> .env
echo DATABASE_PASS=admin >> .env
echo DATABASE_NAME=app-db >> .env
echo DATABASE_PORT=5432 >> .env
echo DATABASE_ADRESS=db >> .env
echo FLASK_SECRET_KEY=q5nZ2$m3ASb!6Pp6@F$RG4n >> .env

docker-compose up --build -d