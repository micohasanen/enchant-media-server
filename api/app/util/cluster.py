import subprocess
from util.logger import logger
from pathlib import Path

def get_current_ip():
	ip = subprocess.check_output(["hostname", "-i", "awk", "'{print $1}'"]).decode('UTF-8').strip()
	logger.debug(ip)
	return ip

class Command:
	def __init__(self, cmd):
		self.cmd = cmd
		self.process = None
	
	def run(self):
		def target ():
			self.process = subprocess.call(self.cmd)
			
			if self.process.returncode != 0:
				self.process.kill()
				delete_playlist()
		
		thread = threading.Thread(target=target).start()

def pull_content(**kwargs):
	logger.debug(kwargs)
	url = kwargs['uri']
	dest = kwargs['dest']

	command_list = [
		'ffmpeg',
		'-rw_timeout', '1500000', # 15 second timeout
		'-i',
		url,
		'-c', 'copy',
		'-hls_flags', 'delete_segments',
		dest
	]

	process = subprocess.run(command_list, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
	
	# Stream has ended, clean the directory
	basedir = Path(dest).parents[0]
	for child in basedir.iterdir():
		child.unlink()

	if process.returncode != 0:
		process.kill()