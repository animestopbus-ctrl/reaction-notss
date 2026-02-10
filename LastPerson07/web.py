"""LastPerson07 Web Dashboard API"""
from fastapi import APIRouter, HTTPException, FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any
import asyncio
from LastPerson07.database import db  # Assuming this is your DB module
from LastPerson07.config import config  # Assuming this is your config module
from LastPerson07.utils import LastPerson07Utils  # Assuming this is your utils module

app = FastAPI()
router = APIRouter(prefix="/api", tags=["web"])
app.include_router(router)
app.mount("/static", StaticFiles(directory="static"), name="static")  # Serve static files

templates = Jinja2Templates(directory="templates")  # If using templates, else remove
utils = LastPerson07Utils()

class WebAuth(BaseModel):
    owner_id: int

async def verify_owner(owner_id: int) -> bool:
    """Verify owner access"""
    return owner_id == config.OWNER_ID

@router.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve main dashboard"""
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read(), status_code=200)

@router.get("/stats")
async def get_stats(owner_id: int):
    """Get real-time bot statistics"""
    if not await verify_owner(owner_id):
        raise HTTPException(403, "Owner access required")
    
    stats = await db.get_stats()
    chats = await db.chats.find().to_list(50)
    
    return {
        "total_reactions": len(stats),
        "active_chats": len([c for c in chats if c.get("enabled", True)]),
        "blacklisted_chats": len([c for c in chats if c.get("blacklisted", False)]),
        "recent_reactions": len([s for s in stats[-100:]]),
        "top_emojis": await get_top_emojis(stats),
        "chat_stats": await get_chat_breakdown(chats),
        "reactions_over_time": await get_reactions_over_time(stats)  # Improved: Add time-series data for chart
    }

@router.post("/chat/{chat_id}/toggle")
async def toggle_chat(chat_id: int, owner_id: int, enable: bool):
    """Toggle chat enabled status"""
    if not await verify_owner(owner_id):
        raise HTTPException(403)
    await db.update_chat_settings(chat_id, {"enabled": enable})
    return {"success": True}

@router.get("/chats")
async def get_chats(owner_id: int):
    """Get all configured chats"""
    if not await verify_owner(owner_id):
        raise HTTPException(403)
    return await db.chats.find().to_list(100)

@router.get("/recent-logs")
async def get_logs(owner_id: int, limit: int = 50):
    """Get recent logs"""
    if not await verify_owner(owner_id):
        raise HTTPException(403)
    return await db.logs.find().sort("timestamp", -1).limit(limit).to_list(None)

async def get_top_emojis(stats: List[Dict]) -> Dict[str, int]:
    """Calculate top emojis"""
    emoji_count = {}
    for stat in stats:
        for emoji in stat.get("emojis", []):
            emoji_count[emoji] = emoji_count.get(emoji, 0) + 1
    return dict(sorted(emoji_count.items(), key=lambda x: x[1], reverse=True)[:10])

async def get_chat_breakdown(chats: List[Dict]) -> List[Dict]:
    """Chat breakdown stats"""
    return [{"id": c["chat_id"], "title": f"Chat {c['chat_id']}", "enabled": c.get("enabled", True)} for c in chats]

async def get_reactions_over_time(stats: List[Dict]) -> List[Dict]:
    """Aggregate reactions over time (simplified hourly buckets)"""
    from datetime import datetime
    buckets = {}
    for stat in stats:
        time_key = datetime.fromtimestamp(stat['timestamp']).strftime('%Y-%m-%d %H:00')
        buckets[time_key] = buckets.get(time_key, 0) + 1
    return [{"time": k, "count": v} for k, v in sorted(buckets.items())]

# If running directly (for dev)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)