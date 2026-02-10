"""LastPerson07 Auto Reaction Bot + Web Dashboard - Main Entry Point"""
import uvicorn
import asyncio
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pyrogram import Client, filters
from LastPerson07.config import config
from LastPerson07.database import db
from LastPerson07.reactions import LastPerson07Reactions
from LastPerson07.admin import LastPerson07Admin
from LastPerson07.ui import LastPerson07UI
from LastPerson07.logger import logger  # Fixed import

# ✅ FIXED: Enhanced FastAPI with static files + CORS
app = FastAPI(title="LastPerson07 Dashboard")

# ✅ NEW: Serve static files (web dashboard)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ NEW: CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ FIXED: Enhanced health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "LastPerson07 Bot + Dashboard",
        "bot_ready": False,  # Will be updated by lifespan
        "timestamp": asyncio.get_event_loop().time()
    }

class LastPerson07Bot:
    def __init__(self):
        self.utils = LastPerson07Utils()
        self.logger = logger  # ✅ FIXED: Use global logger
        self.fastapi_app = app  # ✅ NEW: Reference to FastAPI app
        
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
        """Setup all event handlers"""
        logger.info("🔧 Setting up handlers...")
        
        @self.app.on_message(filters.group | filters.channel)
        async def on_message_lastperson07(client, message):
            await self.reactions.handle_message_lastperson07(message)

        @self.app.on_message(filters.private)
        async def on_private(client, message):
            await self.ui.start_cmd(client, message)

    async def start(self):
        """Start bot and initialize"""
        logger.info("🚀 Starting LastPerson07 Bot...")
        await db.ensure_indexes()
        await self.app.start()
        logger.info("✅ Bot started successfully!")
        logger.info(f"📱 Bot: @{config.BOT_USERNAME}")
        
        # ✅ NEW: Update health check with bot status
        @self.fastapi_app.get("/health")
        async def health_check_updated():
            return {
                "status": "healthy",
                "service": "LastPerson07 Bot + Dashboard",
                "bot_ready": self.app.is_connected,
                "timestamp": asyncio.get_event_loop().time()
            }

    async def stop(self):
        """Graceful shutdown"""
        logger.info("🛑 Stopping bot...")
        await self.app.stop()
        logger.info("✅ Bot stopped.")

# ✅ FIXED: Proper lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    bot = LastPerson07Bot()
    await bot.start()
    yield
    await bot.stop()

# ✅ FIXED: Production FastAPI app
main_app = FastAPI(title="LastPerson07 Ultra Dashboard", lifespan=lifespan)

# ✅ NEW: Include web routes if exist
try:
    from LastPerson07.web import router as web_router
    main_app.include_router(web_router, prefix="/api")
    logger.info("🌐 Web API routes loaded")
except ImportError:
    logger.info("ℹ️ Web API not available")

if __name__ == "__main__":
    # Production uvicorn server
    config = uvicorn.Config(
        "main:main_app", 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", 8000)),
        log_level="info",
        reload=os.getenv("ENV") == "development"
    )
    server = uvicorn.Server(config)
    asyncio.run(server.serve())
