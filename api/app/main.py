from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routers import rtmp, play, streams
from util.logger import logger
from util.cluster import get_current_ip
from config.BaseConfig import config
from database.client import init_db

import os
import subprocess

app = FastAPI()
app.include_router(rtmp.router, prefix="/rtmp")
app.include_router(play.router, prefix="/play")
app.include_router(streams.router, prefix="/streams")

if not os.path.exists(config.content_folder):
	os.makedirs(config.content_folder)

# Mount stream manifests as a static directory
app.mount('/content', StaticFiles(directory="content"), name="content")

@app.on_event("startup")
async def startup():
	await init_db()
	get_current_ip()

@app.get("/")
def read_root():
	return { "message": "Enchant Media Server" }