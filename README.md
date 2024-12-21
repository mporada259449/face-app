## FAST USAGE

### Build fastapi service
`cd src`
`uvicorn main:app --reload --host 0.0.0.0 --port 8001`


### Send requests

`curl -F "image1=@foo1.png" -F "image2=@foo2.webp" http://localhost:8001/faceapp/compare/`