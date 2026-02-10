"""LastPerson07 Admin Panel"""
import logging
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message
from LastPerson07.database import db
from LastPerson07.utils import LastPerson07Utils
from LastPerson07.config import config
from LastPerson07.logger import logger  # ✅ NEW: Proper logging

class LastPerson07Admin:
    def __init__(self, app: Client):
        self.app = app
        self.utils = LastPerson07Utils()
        self.register_handlers()
        logger.info("⚙️ Admin panel initialized")  # ✅ NEW

    def register_handlers(self):
        """Register all admin handlers"""
        self.app.add_handler(filters.command("addemoji") & filters.group, self.add_emoji_cmd)
        self.app.add_handler(filters.command("removeemoji") & filters.group, self.remove_emoji_cmd)
        self.app.add_handler(filters.command("listemoji") & filters.group, self.list_emoji_cmd)
        self.app.add_handler(filters.command("setdelay") & filters.group, self.set_delay_cmd)
        self.app.add_handler(filters.command("random") & filters.group, self.random_cmd)
        self.app.add_handler(filters.command("ban") & filters.private, self.ban_cmd)  # ✅ FIXED: filters.me → filters.private
        self.app.add_handler(filters.command("unban") & filters.private, self.unban_cmd)  # ✅ FIXED
        self.app.add_handler(filters.command("logs") & filters.private, self.logs_cmd)  # ✅ FIXED
        self.app.add_handler(filters.command("stats") & filters.private, self.stats_cmd)  # ✅ FIXED
        self.app.add_handler(filters.command("broadcast") & filters.private, self.broadcast_cmd)  # ✅ FIXED

    async def is_admin_or_owner(self, user_id: int, chat_id: int) -> bool:
        """Check if user is admin or owner"""
        if user_id == config.OWNER_ID:
            return True
        
        try:
            member = await self.app.get_chat_member(chat_id, user_id)
            return member.status in ["administrator", "creator"]
        except Exception as e:
            logger.debug(f"Admin check failed for {user_id}: {e}")  # ✅ NEW: Silent fail
            return False

    async def add_emoji_cmd(self, client, message: Message):  # ✅ FIXED: client param
        """Add emoji command"""
        try:
            if not await self.is_admin_or_owner(message.from_user.id, message.chat.id):
                return await message.reply("❌ Only admins can use this command.")

            emojis = message.text.split()[1:]
            if not emojis:
                return await message.reply("Usage: /addemoji 👍 ❤️")

            success_count = 0
            for emoji in emojis:
                emoji = emoji.strip()
                if await db.add_emoji(message.chat.id, emoji):
                    success_count += 1

            await message.reply(f"✅ Added {success_count}/{len(emojis)} emojis successfully!")
            logger.info(f"Admin added {success_count} emojis in {message.chat.id}")
            
        except Exception as e:
            logger.error(f"❌ Add emoji failed: {e}")
            await message.reply("❌ Something went wrong!")

    async def remove_emoji_cmd(self, client, message: Message):  # ✅ FIXED: client param
        """Remove emoji command"""
        try:
            if not await self.is_admin_or_owner(message.from_user.id, message.chat.id):
                return await message.reply("❌ Only admins can use this command.")

            emojis = message.text.split()[1:]
            if not emojis:
                return await message.reply("Usage: /removeemoji 👍")

            success_count = 0
            for emoji in emojis:
                if await db.remove_emoji(message.chat.id, emoji.strip()):
                    success_count += 1

            await message.reply(f"✅ Removed {success_count}/{len(emojis)} emojis!")
            logger.info(f"Admin removed {success_count} emojis in {message.chat.id}")
            
        except Exception as e:
            logger.error(f"❌ Remove emoji failed: {e}")
            await message.reply("❌ Something went wrong!")

    async def list_emoji_cmd(self, client, message: Message):  # ✅ FIXED: client param
        """List emojis command"""
        try:
            if not await self.is_admin_or_owner(message.from_user.id, message.chat.id):
                return

            emojis = await db.get_emojis(message.chat.id)
            settings = await db.get_chat_settings(message.chat.id)
            
            text = f"🎯 **Chat Emojis:** {', '.join(emojis) if emojis else 'None'}\n"
            text += f"⏱️ **Delay:** {settings['delay']}s\n"
            text += f"🎲 **Random:** {'ON' if settings['random'] else 'OFF'}\n"
            text += f"✅ **Enabled:** {'Yes' if settings['enabled'] else 'No'}\n"
            text += f"🚫 **Blacklisted:** {'Yes' if settings['blacklisted'] else 'No'}"

            await message.reply(text, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"❌ List emoji failed: {e}")
            await message.reply("❌ Failed to fetch settings!")

    async def set_delay_cmd(self, client, message: Message):  # ✅ FIXED: client param
        """Set delay command"""
        try:
            if not await self.is_admin_or_owner(message.from_user.id, message.chat.id):
                return

            parts = message.text.split()
            if len(parts) < 2:
                return await message.reply("Usage: /setdelay 5 (0-60 seconds)")

            try:
                delay = int(parts[1])
                if delay < 0 or delay > 60:
                    return await message.reply("❌ Delay must be 0-60 seconds!")
                await db.set_delay(message.chat.id, delay)
                await message.reply(f"✅ Delay set to **{delay}** seconds!", parse_mode="Markdown")
                logger.info(f"Delay set to {delay}s in {message.chat.id}")
            except ValueError:
                await message.reply("❌ Please enter a valid number!")
                
        except Exception as e:
            logger.error(f"❌ Set delay failed: {e}")
            await message.reply("❌ Something went wrong!")

    async def random_cmd(self, client, message: Message):  # ✅ FIXED: client param
        """Toggle random mode"""
        try:
            if not await self.is_admin_or_owner(message.from_user.id, message.chat.id):
                return

            parts = message.text.split()
            mode = parts[1].lower() if len(parts) > 1 else "toggle"
            
            settings = await db.get_chat_settings(message.chat.id)
            if mode == "on":
                settings["random"] = True
            elif mode == "off":
                settings["random"] = False
            else:
                settings["random"] = not settings["random"]

            await db.set_random(message.chat.id, settings["random"])
            status = "ON" if settings["random"] else "OFF"
            await message.reply(f"🎲 Random mode: **{status}**", parse_mode="Markdown")
            logger.info(f"Random mode {status.lower()} in {message.chat.id}")
            
        except Exception as e:
            logger.error(f"❌ Random cmd failed: {e}")
            await message.reply("❌ Something went wrong!")

    async def ban_cmd(self, client, message: Message):  # ✅ FIXED: client param
        """Ban chat command (owner only)"""
        try:
            if message.from_user.id != config.OWNER_ID:
                return await message.reply("❌ Owner only command.")

            parts = message.text.split()
            if len(parts) < 2:
                return await message.reply("Usage: /ban -1001234567890")

            chat_id = int(parts[1])
            await db.blacklist_chat(chat_id)
            await message.reply(f"✅ Chat **{chat_id}** blacklisted!", parse_mode="Markdown")
            logger.info(f"Owner banned chat {chat_id}")
            
        except ValueError:
            await message.reply("❌ Invalid chat ID! Use: /ban -1001234567890")
        except Exception as e:
            logger.error(f"❌ Ban cmd failed: {e}")
            await message.reply("❌ Something went wrong!")

    async def unban_cmd(self, client, message: Message):  # ✅ FIXED: client param
        """Unban chat command (owner only)"""
        try:
            if message.from_user.id != config.OWNER_ID:
                return await message.reply("❌ Owner only command.")

            parts = message.text.split()
            if len(parts) < 2:
                return await message.reply("Usage: /unban -1001234567890")

            chat_id = int(parts[1])
            await db.unblacklist_chat(chat_id)
            await message.reply(f"✅ Chat **{chat_id}** unblacklisted!", parse_mode="Markdown")
            logger.info(f"Owner unblacklisted chat {chat_id}")
            
        except ValueError:
            await message.reply("❌ Invalid chat ID! Use: /unban -1001234567890")
        except Exception as e:
            logger.error(f"❌ Unban cmd failed: {e}")
            await message.reply("❌ Something went wrong!")

    async def logs_cmd(self, client, message: Message):  # ✅ FIXED: client param
        """Recent logs (owner only)"""
        try:
            if message.from_user.id != config.OWNER_ID:
                return

            recent = await db.logs.find().sort("timestamp", -1).limit(10).to_list(None)
            if not recent:
                return await message.reply("📋 No recent logs.")

            text = "📋 **Recent Logs:**\n\n"
            for log in recent:
                timestamp = time.strftime('%H:%M:%S', time.localtime(log['timestamp']))
                text += f"`[{timestamp}]` {log['type']}: {log.get('error', 'OK')[:100]}...\n"

            await message.reply(text[:4096], parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"❌ Logs cmd failed: {e}")
            await message.reply("❌ Failed to fetch logs!")

    async def stats_cmd(self, client, message: Message):  # ✅ FIXED: client param
        """Reaction stats"""
        try:
            stats = await db.get_stats()
            if not stats:
                return await message.reply("📊 No stats available.")

            total = len(stats)
            text = f"📊 **Total Reactions:** {total:,}\n\n"
            
            chat_stats = {}
            for stat in stats[-50:]:  # Last 50 for better stats
                chat_id = stat["chat_id"]
                chat_stats[chat_id] = chat_stats.get(chat_id, 0) + 1

            for chat_id, count in sorted(chat_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
                text += f"`{chat_id}`: {count:,} reactions\n"

            await message.reply(text, parse_mode="Markdown")
            logger.info(f"Stats requested by owner: {total} total reactions")
            
        except Exception as e:
            logger.error(f"❌ Stats cmd failed: {e}")
            await message.reply("❌ Failed to fetch stats!")

    async def broadcast_cmd(self, client, message: Message):  # ✅ FIXED: client param
        """Start broadcast (owner only)"""
        try:
            if message.from_user.id != config.OWNER_ID:
                return await message.reply("❌ Owner only!")

            await message.reply(
                "📢 **Broadcast Mode**\n\n"
                "Reply to this message with your broadcast text.\n"
                "Use <b>HTML</b> formatting if needed.",
                parse_mode="HTML",
                reply_markup=self.utils.broadcast_keyboard()
            )
            logger.info("Broadcast mode activated by owner")
            
        except Exception as e:
            logger.error(f"❌ Broadcast cmd failed: {e}")
            await message.reply("❌ Failed to start broadcast!")
