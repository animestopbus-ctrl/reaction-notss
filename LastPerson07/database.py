"""LastPerson07 MongoDB Database Manager"""
import pymongo
import motor.motor_asyncio
import time
from typing import Dict, List, Optional, Any
from LastPerson07.config import config

# ✅ FIXED: Global instance after class definition
class LastPerson07DB:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            config.MONGO_URL, 
            serverSelectionTimeoutMS=5000  # ✅ NEW: Connection timeout
        )
        self.db = self.client.lastperson07_db
        self.chats = self.db.chats
        self.logs = self.db.logs
        self.stats = self.db.stats
        
    async def ensure_indexes(self):
        """Create necessary indexes for performance"""
        await self.chats.create_index("chat_id", unique=True)
        # ✅ FIXED: Proper TTL syntax for Motor
        await self.logs.create_index(
            "timestamp", 
            expireAfterSeconds=2592000,  # 30 days TTL ✅ PERFECT
            background=True
        )
        await self.stats.create_index("chat_id")

    async def get_chat_settings(self, chat_id: int) -> Dict[str, Any]:
        """Get chat settings or default"""
        chat = await self.chats.find_one({"chat_id": chat_id})
        if not chat:
            return {
                "chat_id": chat_id,
                "emojis": ["👍", "❤️"],
                "delay": 2,
                "random": True,
                "enabled": True,
                "blacklisted": False
            }
        return chat

    async def update_chat_settings(self, chat_id: int, settings: Dict[str, Any]):
        """Update or create chat settings"""
        await self.chats.update_one(
            {"chat_id": chat_id},
            {"$set": {**settings, "chat_id": chat_id}},
            upsert=True
        )

    async def add_emoji(self, chat_id: int, emoji: str) -> bool:
        """Add emoji to chat (validate first)"""
        if self.is_valid_emoji(emoji):  # ✅ FIXED: Now works (static method)
            chat = await self.get_chat_settings(chat_id)
            if emoji not in chat["emojis"]:
                chat["emojis"].append(emoji)
                await self.update_chat_settings(chat_id, chat)
                return True
        return False

    async def remove_emoji(self, chat_id: int, emoji: str) -> bool:
        """Remove emoji from chat"""
        chat = await self.get_chat_settings(chat_id)
        if emoji in chat["emojis"]:
            chat["emojis"].remove(emoji)
            await self.update_chat_settings(chat_id, chat)
            return True
        return False

    async def get_emojis(self, chat_id: int) -> List[str]:
        """Get emojis for chat"""
        chat = await self.get_chat_settings(chat_id)
        return chat["emojis"]

    async def set_delay(self, chat_id: int, delay: int):
        """Set reaction delay"""
        await self.update_chat_settings(chat_id, {"delay": max(0, min(60, delay))})

    async def set_random(self, chat_id: int, random_mode: bool):
        """Set random mode"""
        await self.update_chat_settings(chat_id, {"random": random_mode})

    async def blacklist_chat(self, chat_id: int):
        """Blacklist chat"""
        await self.update_chat_settings(chat_id, {"blacklisted": True})

    async def unblacklist_chat(self, chat_id: int):
        """Unblacklist chat"""
        await self.update_chat_settings(chat_id, {"blacklisted": False})

    async def log_reaction(self, chat_id: int, message_id: int, emojis: List[str]):
        """Log successful reaction"""
        await self.logs.insert_one({
            "type": "reaction",
            "chat_id": chat_id,
            "message_id": message_id,
            "emojis": emojis,
            "timestamp": self.get_timestamp()
        })

    async def log_error(self, error: str, chat_id: Optional[int] = None):
        """Log error"""
        await self.logs.insert_one({
            "type": "error",
            "chat_id": chat_id,
            "error": error,
            "timestamp": self.get_timestamp()
        })

    async def get_stats(self, chat_id: Optional[int] = None) -> List[Dict]:
        """Get reaction stats"""
        if chat_id:
            return await self.stats.find({"chat_id": chat_id}).to_list(100)
        return await self.stats.find().to_list(100)

    @staticmethod
    def get_timestamp() -> float:
        """Get current timestamp"""
        return time.time()

    @staticmethod
    def is_valid_emoji(emoji: str) -> bool:
        """Validate Telegram emoji (simplified check)"""
        valid_emojis = ["👍", "❤️", "🔥", "😂", "😍", "👏", "🎉", "⭐", "🙏", "💯"]
        return emoji in valid_emojis or len(emoji) == 1

# ✅ FIXED: Global instance at BOTTOM (after all methods defined)
db = LastPerson07DB()
