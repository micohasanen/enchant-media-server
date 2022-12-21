
import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

from beanie import init_beanie

import os
from database.models import Stream, StreamTarget
from util.logger import logger

async def init_db():
	logger.info('Init Database')
	client = AsyncIOMotorClient(os.environ['DATABASE_URL'])

	await init_beanie(database=client.ems, document_models=[Stream, StreamTarget])