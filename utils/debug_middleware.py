from aiogram import BaseMiddleware
from aiogram.types import Update

class DebugMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if isinstance(event, Update):
            print("[DEBUG UPDATE]:")
            print(event.model_dump_json(indent=2))
        return await handler(event, data)
