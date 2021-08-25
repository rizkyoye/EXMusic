from pyrogram import Client
from EXmusic import config
from EXmusic.services.queues.queues import queues

client = Client(config.SESSION_NAME, config.API_ID, config.API_HASH)
run = client.run
