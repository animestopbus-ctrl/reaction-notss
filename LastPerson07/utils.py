"""LastPerson07 Utility Functions"""
import logging
import asyncio
from pyrogram.errors import FloodWait
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton  # ✅ FIXED: Missing imports
from LastPerson07.config import config
from LastPerson07.logger import logger  # ✅ NEW: Use global logger

class LastPerson07Utils:
    @staticmethod
    def setup_logger():
        """Legacy method - use LastPerson07.logger instead"""
        logger.info("⚠️ Use LastPerson07.logger directly (logger.py)")
        return logger

    @staticmethod
    async def safe_send(app: Client, *args, **kwargs):
        """Flood-safe message sending"""
        max_retries = 5
        for attempt in range(max_retries):
            try:
                return await app.send_message(*args, **kwargs)
            except FloodWait as e:
                logger.warning(f"FloodWait {e.value}s, retrying...")  # ✅ FIXED: Proper logger
                await asyncio.sleep(e.value)
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"❌ Safe send failed after {max_retries} retries: {e}")  # ✅ FIXED
                else:
                    logger.debug(f"Send attempt {attempt+1} failed: {e}")
                await asyncio.sleep(2 ** attempt)
        return None

    @staticmethod
    def broadcast_keyboard():
        """Broadcast confirmation keyboard"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Confirm", callback_data="broadcast_confirm")],
            [InlineKeyboardButton("❌ Cancel", callback_data="broadcast_cancel")]
        ])

    @staticmethod
    async def safe_react(app: Client, message, emoji: str):
        """Flood-safe reaction"""
        try:
            await message.react(emoji)
            return True
        except FloodWait as e:
            logger.warning(f"Reaction floodwait: {e.value}s")
            await asyncio.sleep(e.value)
            return await app.react(message.chat.id, message.id, emoji)
        except Exception as e:
            logger.error(f"❌ Reaction failed: {e}")
            return False

    @staticmethod
    def validate_chat_id(chat_id: int) -> bool:
        """Validate Telegram chat ID format"""
        return isinstance(chat_id, int) and (
            (chat_id < 0 and chat_id > -1000000000000) or  # Groups/Channels/Supergroups
            (chat_id > 0 and chat_id < 1000000000000)      # Users
        )
