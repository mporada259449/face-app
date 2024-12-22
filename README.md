## FAST USAGE

### Build fastapi service
`cd src`

`uvicorn main:app --reload --host 0.0.0.0 --port 8001`


### Send requests

`curl -F "image1=@foo1.png" -F "image2=@foo2.webp" http://localhost:8001/faceapp/compare/`

### To generate dependencies
`pip install pipreqs pip-tools`

`pipreqs . --force --savepath==requirements.in`

Change numpy in requirements.in to numpy<2.0.0. & python_magic to python-magic-bin==0.4.14, then

`pip-compile --allow-unsafe --generate-hashes --no-emit-index-url --output-file=requirements.txt requirements.in`