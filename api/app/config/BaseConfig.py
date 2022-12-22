from pydantic import BaseSettings
import os

class BaseConfig(BaseSettings):
    app_name: str = "Enchant Media Server"
    content_folder: str = 'content'
    record_folder: str = 'recordings'
    default_streams = [
        { "-resolution": "1280x720", "-video_bitrate": "3000k" },
        { "-resolution": "640x360", "-video_bitrate": "1200k" }
    ]
    read_timeout = '500000'
    ORIGIN_PORT = os.environ.get('ORIGIN_PORT', '8089')
    USE_LOCALHOST = bool(os.environ.get('USE_LOCALHOST', False))

config = BaseConfig()