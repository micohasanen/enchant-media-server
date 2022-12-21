import subprocess
import threading
import multiprocessing
import os
import ffmpeg
from pathlib import Path
from signal import SIGKILL
from util.logger import logger

class Command:
	def __init__(self, cmd):
		self.cmd = cmd
		self.process = None
	
	def run(self):
		def target ():
			self.process = subprocess.call(self.cmd)
			self.process.communicate()
		
		thread = threading.Thread(target=target).start()
	

def handle_content_pull (url:str, dest:str):
	command_list = [
		'ffmpeg',
		'-i',
		url,
		'-c', 'copy',
		'-hls_flags', 'delete_segments',
		dest
	]

	process = Command(command_list).run()

	return True

class RecordCommand:
	def __init__(self, cmd):
		self.cmd = cmd
		self.process = None
	
	def run(self):
		self.process = subprocess.Popen(self.cmd, stdout=subprocess.DEVNULL)
		logger.debug(self.process)
		return self.process

def handle_record (source: str, destination: str, pid: str):
	if not pid:

		# info = ffmpeg.probe(source, cmd='ffprobe')
		# video_stream = next(stream for stream in info['streams'] if stream['codec_type'] == 'video')
		# logger.debug(video_stream)
		# frame_rate = video_stream['r_frame_rate'].split('/')[0]
		# logger.debug(frame_rate)

		command_list = [
			'ffmpeg',
			'-timeout', '5',
			'-loglevel', 'quiet',
			'-i',
			source,
			'-c:v', 'libx264',
			'-c:a', 'aac',
			'-pix_fmt', 'yuv420p',
			# '-movflags', 'frag_keyframe+separate_moof+omit_tfhd_offset+empty_moov',
			destination
		]

		logger.info(f'Starting record for {source}')

		p = RecordCommand(command_list).run()
		return p.pid

	else:
		try:
			logger.info(f'Stopping recording with process id {pid}')
			os.kill(int(pid), SIGKILL)
			threading.Timer(2.0, convert_recording, [destination]).start()
			return ''
		except Exception:
			logger.error(f'Killing process {pid} failed')
			return ''

def convert_recording(path:str):
	logger.debug('converting started')
	stem = Path(path).stem + '_converted'
	output_path = Path(path).with_name(stem).with_suffix('.mp4').as_posix()
	logger.debug(output_path)

	convert_cmd = [
		'ffmpeg',
		'-i',
		path,
		'-c', 'copy',
		'-map', '0',
		'-movflags', 'faststart',
		output_path
	]

	process = subprocess.run(convert_cmd, stdout=subprocess.DEVNULL)
	logger.debug(process)

	return True
