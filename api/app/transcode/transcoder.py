import concurrent.futures
import os
import ffmpeg
from subprocess import run, PIPE

from config.BaseConfig import config
from util.logger import logger

executor = concurrent.futures.ThreadPoolExecutor()

class ABRCommand:
	def __init__(self, **kwargs):
		if not kwargs['input']:
			raise Exception('Input must be provided.')
		elif not kwargs['app']:
			raise Exception('App Name must be provided.')
		elif not kwargs['stream']:
			raise Exception('Stream Name must be provided.')

		logger.debug(kwargs)

		self.input = kwargs['input']
		self.app = kwargs['app']
		self.stream = kwargs['stream']
		self.retries = int(kwargs.get('retries', 5))
		self.retry_delay = int(kwargs.get('retry_delay', 2))

		self.base_path = f'{config.content_folder}/{self.app}/{self.stream}'

		if not os.path.exists(self.base_path):
			os.makedirs(self.base_path)

	def start(self):
		info = ffmpeg.probe(self.input, cmd="ffprobe")

		command_list = [
			'ffmpeg',
			'-rw_timeout', config.read_timeout,
			# '-loglevel quiet -stats',
			'-i',
			self.input,
			'-g', info['format']['tags']['fps'],
			'-sc_threshold', '0',
			'-preset', 'veryfast',
			"-c:v", 'libx264',
			'-filter:v:0 scale=w=-2:h=1080', '-maxrate:v:0', '5000k', 
			# '-filter:v:1 scale=w=-2:h=720', '-maxrate:v:1', '2500k', 
			# '-filter:v:2 scale=w=-2:h=480', '-maxrate:v:2', '1200k', 
			'-c:a', 'aac', '-b:a', '128k', '-ac', '2',
			'-map', 'v:0', # '-map', 'v:0', '-map', 'v:0', 
			'-map', 'a:0', #'-map', 'a:0', '-map', 'a:0',
			# '-var_stream_map', '"v:0,a:0,name:1080p v:1,a:1,name:720p v:2,a:2,name:480p"',
			'-var_stream_map', '"v:0,a:0,name:1080p"',
			'-f', 'hls',
			'-hls_time', '4',
			# '-hls_playlist_type', 'event',
			'-hls_flags', 'delete_segments+program_date_time+independent_segments',
			# '-max_muxing_queue_size', '9999',
			'-master_pl_name', 'playlist.m3u8',
			f'{self.base_path}/stream_%v.m3u8'
		]

		cmd_string = " ".join(command_list)

		with open(f'{self.base_path}/stats.txt', 'w') as f:
			process = run(cmd_string, shell=True, stdout=f, stderr=PIPE)

			f.close()

			if process.returncode != 0:
				logger.debug(stderr)
