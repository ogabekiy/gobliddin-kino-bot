from dotenv import load_dotenv
import os

load_dotenv()
PRIVATE_CHANNEL = os.getenv("PRIVATE_CHANNEL")
CHANNEL_1 = os.getenv("CHANNEL_1")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNELS = [int(os.getenv("CHANNEL_1"))]
CHANNEL_LINKS = [
    "https://t.me/gobliddin_kino"
]
