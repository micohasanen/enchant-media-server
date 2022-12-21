from fastapi import APIRouter, Form, Body
import ffmpeg
from threading import Timer
from datetime import datetime
import subprocess

from util.logger import logger
from util.cluster import get_current_ip
from config.BaseConfig import config
from transcode import transcoder

from database.models import Stream
from beanie.odm.operators.update.general import Set

router = APIRouter()

def handle_stream(url, app_name, stream_name):
	command = transcoder.ABRCommand(input=url, app=app_name, stream=stream_name)
	command.start()

@router.post('/')
async def process_stream(name: str = Form(), app: str = Form(), addr: str = Form()): # name: str = Form(), app: str = Form()
	if name == None or app == None:
		return False

	stream_url = f'rtmp://{addr}:1935/{app}/{name}'
	logger.info(f'incoming {stream_url}')

	stream = await Stream.find_one(Stream.name == name, Stream.app == app).upsert(
		Set({ 
			Stream.status: 'online',
			Stream.origin: get_current_ip(), 
			Stream.method: 'rtmp',
			Stream.source_url: stream_url,
			Stream.recordPid: ''
		}),
		on_insert=Stream(
			app=app, 
			name=name, 
			status='online', 
			origin=stream_url, 
			method='rtmp',
			source_url=stream_url
		)
	)

	# Start Transcode on a thread, 1 sec timer for safety
	Timer(1.0, handle_stream, [stream_url, app, name]).start()

	return True

@router.post('/end')
async def handle_stream_end(app: str = Form(), name: str = Form()):
	stream = await Stream.find_one(Stream.app == app, Stream.name == name)
	if stream != None:
		await stream.update(Set({
			Stream.status: 'offline', 
			Stream.origin: '', 
			Stream.source_url: '',
			Stream.last_seen: datetime.utcnow(),
			Stream.recording: False,
			Stream.recordPid: ''
		}))

	return True

@router.post('/test')
def test_video(url: str = Form()):
	info = ffmpeg.probe(url, cmd="ffprobe")
	return info