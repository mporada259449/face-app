## FAST USAGE

### Build fastapi service
`cd src_models`

`uvicorn main:app --reload --host 0.0.0.0 --port 8001`


### Send requests

`curl -F "image1=@foo1.png" -F "image2=@foo2.webp" http://localhost:8001/faceapp/compare/`

### To generate dependencies
`pip install pipreqs pip-tools`

`pipreqs . --force --savepath==requirements.in`

Change numpy in requirements.in to numpy<2.0.0. & python_magic to python-magic-bin==0.4.14, then

`pip-compile --allow-unsafe --generate-hashes --no-emit-index-url --output-file=requirements.txt requirements.in`

## DATABASE INITALIZATION

`docker run -p 5432:5432 -d --name flask-db -e POSTGRES_PASSWORD=admin -e POSTGRES_USER=admin -e POSTGRES_DB=app-db -v flask-app-data:/var/lib/postgresql/data postgres:17-bullseye`

### Setting variables
`export DATABASE_ADRESS=127.0.0.1`

### DB migration init
`flask db init`

### DB schema revision
`flask db migrate`

### DB upgrade
`flask db upgrade`

### Admin initialization
`docker exec -it containername psql -U admin -d app-db`
`INSERT INTO users (username, password, is_admin, id) VALUES ('admin', 'admin', true, 1);`

