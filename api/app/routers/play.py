from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from util.cluster import pull_content

import os
import m3u8
import time
import threading
from util.logger import pp, logger
from config.BaseConfig import config
from database.models import Stream

router = APIRouter()

@router.get('/{app}/{name}/playlist.m3u8')
async def serve_stream(app, name):
	# https://moctobpltc-i.akamaihd.net/hls/live/571329/eight/playlist.m3u8
	# https://cph-p2p-msl.akamaized.net/hls/live/2000341/test/master.m3u8

	base_path = f'{config.content_folder}/{app}/{name}'
	master_pl_path = f'{base_path}/playlist.m3u8'

	if not os.path.exists(base_path):
		os.makedirs(base_path)

	# If playlist does not exist, start pulling
	if not os.path.exists(master_pl_path):
		pull_list = []

		stream = await Stream.find_one(Stream.app == app, Stream.name == name)
		
		if not stream or not stream.origin:
			raise HTTPException(status_code=404, detail="Not found")

		# Craft a master playlist from the loaded HLS
		master_pl = m3u8.M3U8()
		origin_stream = f'http://{stream.origin}/{master_pl_path}'
		test_stream = 'https://cph-p2p-msl.akamaized.net/hls/live/2000341/test/master.m3u8'
		logger.debug(origin_stream)

		try:
			manifest = m3u8.load(origin_stream)
		except Exception:
			logger.error('Failed to load manifest')
			raise HTTPException(detail='Failed to load manifest', status_code=500)

		for i, playlist in enumerate(manifest.playlists):
			uri_components = playlist.uri.split('/')
			variant_name = uri_components[-1]

			uri = f'{playlist.base_uri}{variant_name}'

			stream_path = f'stream_{i}.m3u8'

			# Convert resolution tuple to desired format
			res_tuple = playlist.stream_info.resolution
			resolution = 'x'.join(map(str, res_tuple))

			# Create playlist from stream info
			pl = m3u8.Playlist(stream_path, stream_info={
				**vars(playlist.stream_info), 
				'resolution': resolution 
			}, media=[], base_uri=None)
			master_pl.add_playlist(pl)

			pull_list.append({ 
				'uri': uri,
				'dest': f'{base_path}/{stream_path}'
			})

		# Create master playlist
		f = open(master_pl_path, 'w')
		f.write(master_pl.dumps())
		f.close()
		
		for stream in pull_list:
			threading.Thread(target=pull_content, kwargs=stream).start()
		
		# It's horrible, but to prevent first load to not fail
		time.sleep(1)

	return RedirectResponse(f'/{master_pl_path}')
