"""LastPerson07 Auto Reaction Bot + Web Dashboard"""

import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pyrogram import Client, filters

from LastPerson07.config import config
from LastPerson07.database import db
from LastPerson07.reactions import LastPerson07Reactions
from LastPerson07.admin import LastPerson07Admin
from LastPerson07.ui import LastPerson07UI
from LastPerson07.logger import logger


# ---------------- BOT ---------------- #

class LastPerson07Bot:

    def __init__(self):
        self.app = Client(
            "lastperson07",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN
        )

        self.reactions = LastPerson07Reactions(self.app)
        self.admin = LastPerson07Admin(self.app)
        self.ui = LastPerson07UI(self.app)

        self.setup_handlers()

    def setup_handlers(self):

        logger.info("🔧 Setting up handlers...")

        @self.app.on_message(filters.group | filters.channel)
        async def on_message(_, message):
            await self.reactions.handle_message_lastperson07(message)

        @self.app.on_message(filters.private)
        async def on_private(client, message):
            await self.ui.start_cmd(client, message)

    async def start(self):
        logger.info("🚀 Starting bot...")

        await db.ensure_indexes()
        await self.app.start()

        logger.info(f"✅ Bot connected: @{config.BOT_USERNAME}")

    async def stop(self):
        logger.info("🛑 Stopping bot...")
        await self.app.stop()


bot = LastPerson07Bot()


# ---------------- LIFESPAN ---------------- #

@asynccontextmanager
async def lifespan(app: FastAPI):
    await bot.start()
    yield
    await bot.stop()


# ---------------- FASTAPI ---------------- #

app = FastAPI(
    title="LastPerson07 Dashboard",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ✅ Stable health endpoint
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "bot_connected": bot.app.is_connected
    }


# Optional API router
try:
    from LastPerson07.web import router
    app.include_router(router, prefix="/api")
    logger.info("🌐 Web routes loaded")

except ImportError:
    logger.info("ℹ️ No web router found")


# ---------------- RUN ---------------- #

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        log_level="info"
    )
