"""LastPerson07 Modern UI"""
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from LastPerson07.config import config
from LastPerson07.database import db
from LastPerson07.logger import logger  # ✅ NEW: Logging

class LastPerson07UI:
    def __init__(self, app: Client):
        self.app = app
        self.register_handlers()
        logger.info("🎨 UI handlers registered")  # ✅ NEW: Logging

    def register_handlers(self):
        """Register UI handlers"""
        self.app.add_handler(filters.command("start"), self.start_cmd)
        self.app.add_handler(filters.regex(r"btn_(.*)"), self.button_callback)

    async def fetch_wallpaper(self) -> str:
        """Fetch anime wallpaper from APIs with fallbacks"""
        apis = [
            "https://nekos.best/api/v2/wallpaper",
            "https://api.waifu.pics/sfw/waifu"
        ]
        
        # ✅ FIXED: Single session (performance + stability)
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            for api in apis:
                try:
                    async with session.get(api) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if api.startswith("nekos"):
                                return data.get("url", "")
                            elif api.startswith("waifu"):
                                return data.get("url", "")
                except Exception:
                    logger.debug(f"Wallpaper API failed: {api}")  # ✅ NEW: Silent fail
                    continue
        
        # Fallback
        return "https://picsum.photos/512/512?random=1"

    async def start_cmd(self, client, message):  # ✅ FIXED: client param
        """Modern /start command"""
        try:
            wallpaper = await self.fetch_wallpaper()
            
            await message.reply_photo(
                photo=wallpaper,
                caption=(
                    "🚀 <b>LastPerson07 Auto Reaction Bot</b>\n\n"
                    "🤖 Automatically reacts to messages with emojis in groups and channels.\n\n"
                    "⚙️ <b>Admin Features:</b>\n"
                    "• /addemoji 👍 ❤️\n"
                    "• /setdelay 3\n"
                    "• /random on/off\n\n"
                    "👇 Tap buttons below to get started!"
                ),
                parse_mode="HTML",
                reply_markup=self.main_keyboard()
            )
            logger.info(f"📱 /start sent to {message.from_user.id}")
        except Exception as e:
            logger.error(f"❌ Start command failed: {e}")
            # Fallback text message
            await message.reply(
                "🚀 LastPerson07 Auto Reaction Bot\n\n"
                "Add bot to groups/channels as admin to start reacting! 👍",
                reply_markup=self.main_keyboard()
            )

    def main_keyboard(self) -> InlineKeyboardMarkup:
        """Main menu keyboard"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("➕ Add to Channel", 
                    url=f"https://t.me/{config.BOT_USERNAME}?startchannel=true&admin=manage_chat+post_messages"),
                InlineKeyboardButton("➕ Add to Group", 
                    url=f"https://t.me/{config.BOT_USERNAME}?startgroup=true&admin=manage_chat+post_messages")
            ],
            [
                InlineKeyboardButton("⚙️ Commands", callback_data="btn_commands"),
                InlineKeyboardButton("💬 Support", callback_data="btn_support")
            ],
            [
                InlineKeyboardButton("👨‍💻 Developer", callback_data="btn_dev"),
                InlineKeyboardButton("🌐 Community", callback_data="btn_community")
            ]
        ])

    def commands_keyboard(self) -> InlineKeyboardMarkup:
        """Commands keyboard"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back", callback_data="btn_back")]
        ])

    async def button_callback(self, client, callback: CallbackQuery):  # ✅ FIXED: client param
        """Handle all button callbacks"""
        try:
            data = callback.data.split("_")[1]

            if data == "commands":
                await callback.message.edit_text(
                    "📋 **Available Commands:**\n\n"
                    "• `/addemoji 👍 ❤️` - Add reaction emojis\n"
                    "• `/removeemoji 👍` - Remove emoji\n"
                    "• `/listemoji` - Show current emojis\n"
                    "• `/setdelay 3` - Set reaction delay\n"
                    "• `/random on/off` - Toggle random mode\n\n"
                    "<b>Owner only:</b>\n"
                    "• `/ban -100123456`\n"
                    "• `/stats` • `/logs`",
                    parse_mode="Markdown",
                    reply_markup=self.commands_keyboard()
                )

            elif data == "support":
                await callback.answer("📞 Support coming soon!", show_alert=True)

            elif data == "dev":
                await callback.message.edit_text(
                    "👨‍💻 **Developer:**\n\n"
                    "👉 https://t.me/MrDhanpalSharma\n\n"
                    "**Channel / Community:**\n"
                    "👉 https://t.me/THEUPDATEDGUYS\n\n"
                    "> Powered by **The Updated Guys**",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("⬅️ Back", callback_data="btn_back")]
                    ])
                )

            elif data == "community":
                await callback.answer("🌐 https://t.me/THEUPDATEDGUYS", show_alert=True)

            elif data == "back":
                await callback.message.edit_text(
                    "🚀 <b>Welcome Back!</b>\n\nChoose an option below:",
                    reply_markup=self.main_keyboard(),
                    parse_mode="HTML"
                )

            await callback.answer()
            logger.debug(f"Button clicked: {data} by {callback.from_user.id}")
            
        except Exception as e:
            logger.error(f"❌ Button callback failed: {e}")
            await callback.answer("Something went wrong! Try /start", show_alert=True)

# ✅ NEW: Global instance (optional)
ui_instance = None
