from typing import Optional, List
from beanie import Document, Indexed, Link, Update, before_event
from pydantic import root_validator

from datetime import datetime

class StreamTarget(Document):
	source: str
	destination: str
	active: bool = True

	class Settings:
		name = 'stream_targets'

class Stream(Document):
	app: Indexed(str)
	name: Indexed(str)
	method: str = 'rtmp'
	origin: str
	source_url: str = ''
	status: str = 'offline'
	recording: bool = False
	recordingName: Optional[str]
	recordPid: str = ''
	times_recorded: int = 0
	created_at: datetime = datetime.utcnow()
	updated_at: datetime = datetime.utcnow()
	last_seen: Optional[datetime]
	targets: Optional[List[Link[StreamTarget]]]

	@before_event(Update)
	def handle_update(self):
		self.updated_at = datetime.utcnow()

	class Settings:
		name = 'streams'
		# use_cache = True
		# cache_expiration_time = datetime.timedelta(seconds=30)