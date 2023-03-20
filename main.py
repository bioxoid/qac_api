from typing import List
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from io import BytesIO
from PIL import Image
import base64
from make_zodiac_sign import make_zodiac_sign

app = FastAPI()

origins = [
	"http://localhost",
	"http://localhost:5173",
	"https://qac.vercel.app/"
]

app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def handler(request:Request, exc:RequestValidationError):
		print(request)
		print(exc)
		return JSONResponse(content={}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

class Star(BaseModel):
	image: str
	angle: List[float]
	max_mag: int
	blur_radius: int
	pixel_rate: int
	class Config:
		orm_mode = True

@app.post("/")
def post_root(star: Star):
	image = Image.open(BytesIO(base64.b64decode(star.image.replace("data:image/png;base64,", ""))))
	connection_list = make_zodiac_sign(image, star.angle, star.max_mag, star.blur_radius, star.pixel_rate)
	return connection_list
