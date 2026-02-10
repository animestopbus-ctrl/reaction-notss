"""LastPerson07 Reaction Handler"""
import asyncio
import random
import logging
from typing import List
from pyrogram import Client
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from LastPerson07.database import db
from LastPerson07.utils import LastPerson07Utils
from LastPerson07.logger import logger  # ✅ NEW: Proper logging

class LastPerson07Reactions:
    def __init__(self, app: Client):
        self.app = app
        self.utils = LastPerson07Utils()
        logger.info("🎯 Reaction handler initialized")  # ✅ NEW

    async def handle_message_lastperson07(self, message: Message):
        """Main message handler for reactions"""
        try:
            chat_id = message.chat.id
            
            # Skip if blacklisted or not admin
            settings = await db.get_chat_settings(chat_id)
            if not settings["enabled"] or settings["blacklisted"]:
                return

            # Skip own messages, service messages, and empty messages
            if (message.from_user and message.from_user.is_self) or \
               message.service or \
               not (message.text or message.caption or message.media):
                return

            # Random delay (anti-flood) ✅ PERFECT
            delay = settings["delay"] + random.uniform(0, 2)
            await asyncio.sleep(delay)

            # Get emojis
            emojis = await db.get_emojis(chat_id)
            if not emojis:
                return

            # Select emojis ✅ PERFECT LOGIC
            if settings["random"]:
                selected_emojis = [random.choice(emojis)]
            else:
                selected_emojis = emojis[:2]  # Max 2 emojis

            # React with flood protection ✅ IMPROVED
            for emoji in selected_emojis:
                success = await self.utils.safe_react(self.app, message, emoji)
                if success:
                    await db.log_reaction(chat_id, message.id, [emoji])
                    logger.debug(f"✅ Reacted {emoji} in {chat_id}")
                else:
                    await db.log_error(f"Reaction failed for {emoji}", chat_id)
                    await asyncio.sleep(1)  # Backoff

        except Exception as e:
            logger.error(f"❌ Reaction handler error: {e}")  # ✅ FIXED: Proper logger
            await db.log_error(f"Reaction handler error: {e}")

    async def smart_react_lastperson07(self, message: Message):
        """Smart reaction based on message content (bonus feature)"""
        try:
            from textblob import TextBlob
            text = (message.text or message.caption or "").strip()
            if not text or len(text) < 3:  # ✅ IMPROVED: Min length check
                return

            blob = TextBlob(text)
            sentiment = blob.sentiment.polarity

            settings = await db.get_chat_settings(message.chat.id)
            emojis = await db.get_emojis(message.chat.id)

            if not emojis:
                return

            # Smart emoji selection ✅ IMPROVED: Validate emojis exist
            if sentiment > 0.1:  # Positive
                positive_emojis = ["😍", "👍", "❤️", "🎉"]
                emoji = next((e for e in positive_emojis if e in emojis), emojis[0])
            elif sentiment < -0.1:  # Negative
                emoji = next((e for e in ["😢", "😞"] if e in emojis), emojis[0])
            else:
                emoji = emojis[0]

            await asyncio.sleep(settings["delay"])
            success = await self.utils.safe_react(self.app, message, emoji)
            if success:
                logger.debug(f"🧠 Smart react {emoji} (sentiment: {sentiment:.2f})")
                
        except ImportError:
            logger.debug("TextBlob not available, skipping smart reactions")
        except Exception as e:
            logger.debug(f"Smart reaction skipped: {e}")  # ✅ FIXED: Proper logging
