from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from model import load_model
import os


class Threshold(BaseModel):
    threshold: int

class ImageData(BaseModel):
    img_id: str


face_model = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    #to jast wykonywane przy startupie appki czyli tutaj trzeba załadować modele
    global face_model
    if face_model is None:
        face_model = load_model()
    
    yield

    #tutaj powinno być usuniecie zasobów


app = FastAPI(lifespan=lifespan)



@app.get("/compare")
async def compare_image(img_id: ImageData):
    print(img_id)
    global face_model
    #imgs = img_id
    img_dir = os.listdir(f"/home/dev/face-app/mnt/images/{img_id.img_id}")
    if len(img_dir) != 2:
        print("Wrong number of files")
        json_encoded_res = jsonable_encoder({"error": "Wrong number of files", "file_list": img_dir})
        return JSONResponse(json_encoded_res)
    
    if not all([file.lower().endswith(('.png', '.jpg', '.jpeg')) for file in img_dir]):
        print('File is not an image')
        json_encoded_res = jsonable_encoder({"error": "Files are not an images", "file_list": img_dir})
        return JSONResponse(json_encoded_res)

    print(img_dir)
    #tutaj trzeba zrobić caly processing zdjęć, dobrze by było jakby to zrobić w kilku wątkach
    #wartość zwarcana True albo False, można coś dodać
    return face_model.predict(img_dir[0], img_dir[1])
    
    

@app.post("/set_threshold")
async def set_threshold(new_threshold: Threshold):
    print(f"New threshold will be {new_threshold.threshold}")
    return True