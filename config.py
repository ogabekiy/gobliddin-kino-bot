from dotenv import load_dotenv
import os

load_dotenv()
PRIVATE_CHANNEL = os.getenv("PRIVATE_CHANNEL")

CHANNEL_1 = os.getenv("CHANNEL_1")

BOT_TOKEN = os.getenv("BOT_TOKEN")

CHANNEL_LINK = os.getenv("CHANNEL_LINK")
CHANNEL_LINKS = [
    "https://t.me/gobliddin_kino"
]

CHANNEL_1 = int(os.getenv("CHANNEL_1"))
CHANNELS = [CHANNEL_1]