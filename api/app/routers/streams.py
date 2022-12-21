from fastapi import APIRouter, HTTPException, Query
from typing import Union
from pydantic import BaseModel

from database.models import Stream
from util.logger import logger
from config.BaseConfig import config
from util.cluster import get_current_ip
from util.stream_handler import handle_record

import os
import uuid
import requests

router = APIRouter()

class RecordBody(BaseModel):
	source: str
	destination: str
	pid: Union[str, None] = None

@router.patch('/record/cluster')
async def start_record(body: RecordBody):
	logger.debug('got cluster record')
	os.makedirs(f'{config.content_folder}/{config.record_folder}')

	pid = handle_record(body.source, body.destination, body.pid)
	return pid

@router.patch('/{app}/{name}/record')
async def handle_record_req (app, name):
	stream = await Stream.find_one(Stream.app == app, Stream.name == name)
	logger.debug(f'stream: {stream}')

	if stream == None:
		raise HTTPException(status_code=404, detail="Stream not found")
	#elif stream.status == 'offline':
		# raise HTTPException(status_code=400, detail="Stream offline")

	filepath = f'{config.content_folder}/{config.record_folder}'
	if not os.path.exists(filepath):
		os.makedirs(filepath)

	filenumber = stream.times_recorded if stream.recordPid else int(stream.times_recorded) + 1
	filename = f"{app}_{name}_{filenumber}.ts"
	source = 'https://moctobpltc-i.akamaihd.net/hls/live/571329/eight/playlist.m3u8'
	destination = f'{filepath}/{filename}'
	pid = stream.recordPid

	logger.info(f'Recording dest {destination}')

	# Send record call to origin if not the current server
	if False:
	# if stream.origin != get_current_ip():
		res = requests.patch(
			f'http://{stream.origin}/streams/record/cluster',
			data={ "source": source, "destination": destination, 'pid': pid },
			timeout=5
		)
		logger.debug(res.status_code)
	else:
		logger.debug('same origin')
		pid = handle_record(source, destination, pid)

	if not stream.recordPid:
		stream.times_recorded = int(filenumber)
		stream.recordingName = filename

	stream.recordPid = pid or ''
	stream.recording = not stream.recording
	stream = await stream.save()

	return stream