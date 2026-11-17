import os
import asyncio
import time
import math
import subprocess
import psutil
import shutil
import sys
import random
import string
import re
import logging
import io
import urllib.request
import uuid
import urllib.parse
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

try:
    import updater
    updater.auto_update()
except Exception as e:
    print(f"auto update skipped: {e}")
from motor.motor_asyncio import AsyncIOMotorClient
from pyrogram import Client, filters, enums, StopTransmission, StopPropagation, ContinuePropagation, idle
import json
import platform
import http.client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery, InputMediaPhoto, InputMediaDocument, PreCheckoutQuery, LabeledPrice
from pyrogram.errors import FloodWait, MessageNotModified, MessageIdInvalid
from logging.handlers import RotatingFileHandler
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from theme import Theme, STYLES, set_style, ButtonMaker, mark, pager, tree, menu, btn, onoff, tick, back_close, esc, short, bar as theme_bar, circle_bar
import tmdb as tmdb_mod
from autorename import apply_template as autorename_apply
from pyrogram.types import InputRichMessage
from pyrogram.types import BotCommand, BotCommandScopeChat, LinkPreviewOptions, ReplyParameters

LOG_FILE = "log.txt"
_log_fmt = logging.Formatter("[%(asctime)s] [%(levelname)s] - %(message)s", datefmt="%d-%b-%y %I:%M:%S %p")
_file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=2, encoding="utf-8")
_file_handler.setFormatter(_log_fmt)
_file_handler.setLevel(logging.INFO)
_stream_handler = logging.StreamHandler()
_stream_handler.setFormatter(_log_fmt)
_stream_handler.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO, handlers=[_file_handler, _stream_handler], force=True)
for _noisy in ("pyrogram", "pyrogram.session", "pyrogram.connection", "httpx", "urllib3", "pymongo", "asyncio"):
    logging.getLogger(_noisy).setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

import pyrogram.session
_original_handle = pyrogram.session.Session.handle_packet if hasattr(pyrogram.session.Session, "handle_packet") else None

from pyrogram import raw
_original_resolve = None
try:
    import pyrogram.dispatcher as _dispatcher
    _orig_dispatch = _dispatcher.Dispatcher.update
    async def _safe_dispatch(self, client, update, users, chats):
        try:
            await _orig_dispatch(self, client, update, users, chats)
        except TypeError as e:
            if "topics" in str(e):
                pass
            else:
                raise
    _dispatcher.Dispatcher.update = _safe_dispatch
except Exception:
    pass

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
DUMP_CHANNEL = int(os.getenv("DUMP_CHANNEL"))

SESSION_STRING = os.getenv("SESSION_STRING", "")

VERSION = "2.1.0"
DEVELOPER_NAME = "꧁ 𝕋𝕛 𝔸𝕕𝕞𝕚𝕟 ꧂"
DEVELOPER_USERNAME = "Tj_Bots_Admin"
DEVELOPER_LINK = f"https://t.me/{DEVELOPER_USERNAME}"
CHANNEL_LINK = "https://t.me/Tj_Bots"
try:
    UPSTREAM_REPO, UPSTREAM_BRANCH = updater.defaults()
except Exception:
    UPSTREAM_REPO, UPSTREAM_BRANCH = "", "main"

TEST_PRICE = "Free (one-time)"
GOLD_PRICE = "$1"
ULTRA_PRICE = "$2"

GOLD_STARS_PRICE = 100
ULTRA_STARS_PRICE = 200

FREE_DAILY_LIMIT = 10
TEST_DAILY_LIMIT = 10
GOLD_DAILY_LIMIT = 20
ULTRA_DAILY_LIMIT = 50

MAX_FILE_SIZE_NORMAL = 1950 * 1024 * 1024
MAX_FILE_SIZE_PREMIUM = 4 * 1024 * 1024 * 1024

COOLDOWN_NORMAL = 60

MAX_CONCURRENT_FREE   = 1
MAX_CONCURRENT_TEST   = 2
MAX_CONCURRENT_GOLD   = 2
MAX_CONCURRENT_ULTRA  = 3
MAX_CONCURRENT_ADMIN  = 999

WORKSPACE = os.path.dirname(os.path.realpath(__file__))
DOWNLOAD_LOCATION = f"{WORKSPACE}/downloads"
PREMIUM_LOG = f"{WORKSPACE}/premium_log.txt"

MONGO_URI = os.getenv("MONGO_URI", "")
DB_NAME = os.getenv("DB_NAME", "tj_rename")
RESTART_FILE = f"{WORKSPACE}/.restartmsg"
MAX_BOT_TASKS = 10

BOT_CONFIG_SPEC = {
    "FREE_DAILY_LIMIT": ("int", "quota"), "TEST_DAILY_LIMIT": ("int", "quota"),
    "GOLD_DAILY_LIMIT": ("int", "quota"), "ULTRA_DAILY_LIMIT": ("int", "quota"),
    "MAX_CONCURRENT_FREE": ("int", "conc"), "MAX_CONCURRENT_TEST": ("int", "conc"),
    "MAX_CONCURRENT_GOLD": ("int", "conc"), "MAX_CONCURRENT_ULTRA": ("int", "conc"),
    "MAX_CONCURRENT_ADMIN": ("int", "conc"),
    "COOLDOWN_NORMAL": ("int", "limits"),
    "MAX_FILE_SIZE_NORMAL": ("size", "limits"), "MAX_FILE_SIZE_PREMIUM": ("size", "limits"),
    "SESSION_STRING": ("secret", "session"), "DUMP_CHANNEL": ("chatid", "session"),
    "GOLD_STARS_PRICE": ("int", "price"), "ULTRA_STARS_PRICE": ("int", "price"),
    "GOLD_PRICE": ("str", "price"), "ULTRA_PRICE": ("str", "price"), "TEST_PRICE": ("str", "price"),
    "TEST_DURATION_DAYS": ("int", "price"), "PREMIUM_DAYS": ("int", "price"),
    "DEVELOPER_NAME": ("str", "brand"), "DEVELOPER_USERNAME": ("str", "brand"), "CHANNEL_LINK": ("str", "brand"),
    "UPSTREAM_REPO": ("repo", "sys"), "UPSTREAM_BRANCH": ("str", "sys"),
    "UI_STYLE": ("choice", "sys"),
    "RESTART_CONFIRM": ("bool", "sys"), "RICH_MESSAGES": ("bool", "sys"), "FSUB_IDS": ("str", "short"),
    "SHORTENER_ENABLED": ("bool", "short"), "SHORTENER": ("str", "short"), "SHORTENER_API": ("secret", "short"), "TOKEN_TIMEOUT": ("int", "short"),
    "MAINTENANCE": ("bool", "maint"), "MAINTENANCE_MSG": ("text", "maint"),
}
BOT_CONFIG_DEFAULTS = {
    "FREE_DAILY_LIMIT": FREE_DAILY_LIMIT, "TEST_DAILY_LIMIT": TEST_DAILY_LIMIT,
    "GOLD_DAILY_LIMIT": GOLD_DAILY_LIMIT, "ULTRA_DAILY_LIMIT": ULTRA_DAILY_LIMIT,
    "MAX_CONCURRENT_FREE": MAX_CONCURRENT_FREE, "MAX_CONCURRENT_TEST": MAX_CONCURRENT_TEST,
    "MAX_CONCURRENT_GOLD": MAX_CONCURRENT_GOLD, "MAX_CONCURRENT_ULTRA": MAX_CONCURRENT_ULTRA,
    "MAX_CONCURRENT_ADMIN": MAX_CONCURRENT_ADMIN,
    "COOLDOWN_NORMAL": COOLDOWN_NORMAL,
    "MAX_FILE_SIZE_NORMAL": MAX_FILE_SIZE_NORMAL, "MAX_FILE_SIZE_PREMIUM": MAX_FILE_SIZE_PREMIUM,
    "SESSION_STRING": SESSION_STRING, "DUMP_CHANNEL": DUMP_CHANNEL,
    "GOLD_STARS_PRICE": GOLD_STARS_PRICE, "ULTRA_STARS_PRICE": ULTRA_STARS_PRICE,
    "GOLD_PRICE": GOLD_PRICE, "ULTRA_PRICE": ULTRA_PRICE, "TEST_PRICE": TEST_PRICE,
    "TEST_DURATION_DAYS": 7, "PREMIUM_DAYS": 30,
    "DEVELOPER_NAME": DEVELOPER_NAME, "DEVELOPER_USERNAME": DEVELOPER_USERNAME, "CHANNEL_LINK": CHANNEL_LINK,
    "UPSTREAM_REPO": UPSTREAM_REPO, "UPSTREAM_BRANCH": UPSTREAM_BRANCH,
    "UI_STYLE": "minimal",
    "RESTART_CONFIRM": True, "RICH_MESSAGES": True, "FSUB_IDS": "",
    "SHORTENER_ENABLED": False, "SHORTENER": "", "SHORTENER_API": "", "TOKEN_TIMEOUT": 86400,
    "MAINTENANCE": False, "MAINTENANCE_MSG": "",
}
SIZE_CAPS = {"MAX_FILE_SIZE_NORMAL": 2000 * 1024 * 1024, "MAX_FILE_SIZE_PREMIUM": 4 * 1024 * 1024 * 1024}
BOT_CONFIG = {}

def cfg(key):
    return BOT_CONFIG.get(key, BOT_CONFIG_DEFAULTS[key])

def dev_link():
    return f"https://t.me/{cfg('DEVELOPER_USERNAME')}"

def parse_size(text):
    m = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*([kmgt]?)i?b?\s*", str(text or ""), re.I)
    if not m:
        raise ValueError("use e.g. 1950MB or 2GB")
    mult = {"": 1, "k": 1024, "m": 1024 ** 2, "g": 1024 ** 3, "t": 1024 ** 4}[m.group(2).lower()]
    return int(float(m.group(1)) * mult)

def parse_config_value(key, text):
    """Validate admin input for a bot_config key; raises ValueError with a short reason."""
    kind = BOT_CONFIG_SPEC[key][0]
    text = (text or "").strip()
    if kind == "int":
        if not re.fullmatch(r"\d{1,6}", text):
            raise ValueError("send a whole number")
        v = int(text)
        if v > 100000:
            raise ValueError("max 100000")
        if (key.startswith("MAX_CONCURRENT") or key in ("GOLD_STARS_PRICE", "ULTRA_STARS_PRICE",
                                                         "TEST_DURATION_DAYS", "PREMIUM_DAYS")) and v < 1:
            raise ValueError("min 1")
        if key in ("TEST_DURATION_DAYS", "PREMIUM_DAYS") and v > 3650:
            raise ValueError("max 3650 days")
        return v
    if kind == "size":
        v = parse_size(text)
        if v < 1024 * 1024:
            raise ValueError("min 1MB")
        if v > SIZE_CAPS[key]:
            raise ValueError(f"max {SIZE_CAPS[key] // (1024 * 1024)}MB")
        return v
    if kind == "bool":
        low = text.lower()
        if low in ("1", "on", "true", "yes"):
            return True
        if low in ("0", "off", "false", "no"):
            return False
        raise ValueError("send on/off")
    if kind == "chatid":
        if not re.fullmatch(r"-?\d{5,20}", text):
            raise ValueError("send a chat id like -1001234567890")
        return int(text)
    if kind == "secret":
        if text == "-":
            return BOT_CONFIG_DEFAULTS[key]
        if len(text) < 100 or not re.fullmatch(r"[A-Za-z0-9_=+/\-]+", text):
            raise ValueError("this does not look like a Pyrogram session string")
        return text
    if kind == "choice":
        if text == "-":
            return BOT_CONFIG_DEFAULTS[key]
        if text.lower() not in STYLES:
            raise ValueError("send one of: " + ", ".join(STYLES))
        return text.lower()
    if kind == "repo":
        if text == "-":
            return BOT_CONFIG_DEFAULTS[key]
        if len(text) > 200 or not re.fullmatch(r"https://\S+", text):
            raise ValueError("send a repo link starting with https://")
        return text
    if kind == "str":
        if text == "-":
            return BOT_CONFIG_DEFAULTS[key]
        if key == "UPSTREAM_BRANCH" and not re.fullmatch(r"[A-Za-z0-9._/-]{1,60}", text):
            raise ValueError("send a branch name")
        if not text or len(text) > 100:
            raise ValueError("1-100 characters")
        if key == "DEVELOPER_USERNAME":
            text = text.lstrip("@")
            if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{3,31}", text):
                raise ValueError("send a Telegram username")
        if key == "CHANNEL_LINK" and not re.fullmatch(r"https://\S+", text):
            raise ValueError("send a link starting with https://")
        return text
    if text == "-":
        return ""
    if len(text) > 500:
        raise ValueError("max 500 chars")
    return text

def fmt_config_value(key, value=None):
    value = cfg(key) if value is None else value
    kind = BOT_CONFIG_SPEC[key][0]
    if kind == "size":
        return human_size(value)
    if kind == "bool":
        return "True" if value else "False"
    if kind == "secret":
        return f"Set (...{str(value)[-4:]})" if value else Theme.NOT_SET
    if kind == "choice":
        return str(value).title()
    if kind == "repo":
        return short(re.sub(r"://[^@/\s]+@", "://***@", str(value)), 40) if value else Theme.NOT_SET
    if kind == "str":
        return short(value, 40)
    if kind == "text":
        return short(value, 40) if value else Theme.NOT_SET
    if key == "COOLDOWN_NORMAL":
        return f"{value}s"
    return str(value)

for path in [DOWNLOAD_LOCATION, WORKSPACE]:
    if not os.path.isdir(path):
        os.makedirs(path)

tasks = {}
user_tasks = {}
tasks_lock = asyncio.Lock()
last_refresh = {}
user_pages = {}
user_status_msg = {}
user_status_msg = {}

class TaskInfo:
    def __init__(self, task_id, user_id, original_msg, filename, target, status_msg):
        self.task_id = task_id
        self.user_id = user_id
        self.original_msg = original_msg
        self.filename = filename
        self.target = target
        self.status_msg = status_msg
        self.cancel_event = asyncio.Event()
        self.start_time = time.time()
        self.current = 0
        self.total = 0
        self.stage = "downloading"
        self.lock = asyncio.Lock()
        self.cancelled = False
        self.download_task = None
        self.upload_task = None
        self.position = 0
        self.gid = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=8))
        self.stage_start = time.time()

bot = Client(
    "converter_bot_final_v16",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workdir=WORKSPACE,
    parse_mode=enums.ParseMode.HTML,
    max_concurrent_transmissions=10,
    workers=200,
)
bot.start_time = time.time()

PARALLEL_UP_SESSIONS = 8
PARALLEL_UP_PER_SESSION = 2

async def parallel_upload(uc, path, progress, progress_args):
    """Multi-connection upload: separate Telegram sessions each send different 512KB parts of the file."""
    PART = 512 * 1024
    size = os.path.getsize(path)
    total = (size + PART - 1) // PART
    file_id = uc.rnd_id()
    fd = os.open(path, os.O_RDONLY)
    nxt, sent = [0], [0]
    sessions, jobs = [], []
    async def worker(s):
        while nxt[0] < total:
            i = nxt[0]
            nxt[0] += 1
            data = await asyncio.to_thread(os.pread, fd, PART, i * PART)
            for attempt in range(6):
                try:
                    await s.invoke(raw.functions.upload.SaveBigFilePart(file_id=file_id, file_part=i, file_total_parts=total, bytes=data), sleep_threshold=30)
                    break
                except Exception:
                    if attempt == 5:
                        raise
                    await asyncio.sleep(1 + attempt)
            sent[0] += len(data)
            if progress:
                await progress(min(sent[0], size), size, *progress_args)
    try:
        dc = await uc.storage.dc_id()
        for _ in range(PARALLEL_UP_SESSIONS):
            sessions.append(await uc.get_session(dc, is_media=True, temporary=True))
        jobs = [asyncio.create_task(worker(s)) for s in sessions for _ in range(PARALLEL_UP_PER_SESSION)]
        await asyncio.gather(*jobs)
    except BaseException:
        for j in jobs:
            j.cancel()
        raise
    finally:
        os.close(fd)
        for s in sessions:
            try:
                await s.stop()
            except Exception:
                pass
    return raw.types.InputFileBig(id=file_id, parts=total, name=os.path.basename(path))

def make_premium_client(session):
    if not session or session == "your_session_string_here":
        return None
    try:
        c = Client(
            "premium_session",
            session_string=session,
            api_id=API_ID,
            api_hash=API_HASH,
            max_concurrent_transmissions=10,
            no_updates=True
        )
        _orig_save = c.save_file

        async def save_file(path, file_id=None, file_part=0, progress=None, progress_args=()):
            if not isinstance(path, (str, os.PathLike)) or file_id is not None or os.path.getsize(path) <= 10 * 1024 * 1024:
                return await _orig_save(path, file_id=file_id, file_part=file_part, progress=progress, progress_args=progress_args)
            return await parallel_upload(c, path, progress, progress_args)
        c.save_file = save_file
        logger.info("Premium client initialized")
        return c
    except Exception as e:
        logger.error(f"Failed to initialize premium client: {e}")
        return None

premium_client = make_premium_client(SESSION_STRING)
userbot_info = ""

def get_bot_uptime():
    return time.time() - bot.start_time

def time_formatter(seconds):
    if seconds < 0:
        seconds = 0
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0 or days > 0:
        parts.append(f"{hours}h")
    if minutes > 0 or hours > 0 or days > 0:
        parts.append(f"{minutes}m")
    parts.append(f"{secs}s")
    return " ".join(parts)

def get_prog_bar(percent, length=10):
    filled = int(length * percent / 100)
    return "■" * filled + "□" * (length - filled)

def human_size(size):
    if not size:
        return "0 B"
    if size == float('inf'):
        return "Unlimited"
    units = ["B", "KB", "MB", "GB", "TB"]
    i = int(math.floor(math.log(size, 1024))) if size > 0 else 0
    return f"{round(size / math.pow(1024, i), 2)} {units[i]}"

def get_duration(file_path):
    try:
        metadata = extractMetadata(createParser(file_path))
        if metadata and metadata.has("duration"):
            return metadata.get('duration').seconds
    except Exception as e:
        logger.error(f"Error getting duration: {e}")
    return 0

def get_reset_time():
    now = datetime.now()
    reset = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    return reset

def format_timedelta(td):
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def format_remaining_time(expiry_date):
    now = datetime.now()
    if now > expiry_date:
        return "Expired"
    diff = expiry_date - now
    days = diff.days
    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60
    parts = []
    if days > 0:
        parts.append(f"{days} day{'s' if days > 1 else ''}")
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
    return ", ".join(parts) if parts else "Less than a minute"

_mongo_client = AsyncIOMotorClient(MONGO_URI)
_mongo_db = _mongo_client[DB_NAME]

_col_users        = _mongo_db["users"]
_col_banned       = _mongo_db["banned"]
_col_bought_test  = _mongo_db["bought_test"]
_col_redeem_codes = _mongo_db["redeem_codes"]
_col_premium_logs = _mongo_db["premium_logs"]
_col_bot_config   = _mongo_db["bot_config"]

DEFAULT_CAPTION = "<b><i>{filename}</i>\n<blockquote>Size: {filesize}</blockquote></b>"

DEFAULT_USER = lambda uid: {
    "_id": str(uid),
    "thumb": None,
    "mode": "ask",
    "caption": DEFAULT_CAPTION,
    "prefix": "",
    "suffix": "",
    "remname": "",
    "rename": "ask",
    "screenshots": 0,
    "cap_font": "",
    "mediainfo": False,
    "autorename": False,
    "rename_method": "auto",
    "remname_auto": "",
    "spoiler": False,
    "auto_thumb": False,
    "thumb_src": None,
    "audio_fmt": "mp3",
    "audio_br": "192k",
    "poster_lang": "all",
    "poster_kind": "p",
    "premium": {
        "type": "free",
        "expires": None,
        "daily_conversions": 0,
        "daily_failed": 0,
        "last_reset": str(datetime.now().date())
    },
    "redeem_used": False
}

class _DB:
    def __init__(self):
        self.users        = {}
        self.banned       = []
        self.bought_test  = []
        self.redeem_codes = {}
        self.premium_logs = []

    async def load(self):
        async for doc in _col_users.find():
            self.users[doc["_id"]] = doc
        async for doc in _col_banned.find():
            self.banned.append(doc["_id"])
        async for doc in _col_bought_test.find():
            self.bought_test.append(doc["_id"])
        async for doc in _col_redeem_codes.find():
            self.redeem_codes[doc["_id"]] = doc
        doc = await _col_bot_config.find_one({"_id": "settings"}) or {}
        for key, (kind, _) in BOT_CONFIG_SPEC.items():
            if key not in doc:
                continue
            val = doc[key]
            ok = {"int": isinstance(val, int) and not isinstance(val, bool), "size": isinstance(val, int) and not isinstance(val, bool),
                  "bool": isinstance(val, bool), "text": isinstance(val, str),
                  "str": isinstance(val, str), "secret": isinstance(val, str), "repo": isinstance(val, str), "choice": isinstance(val, str) and val in STYLES,
                  "chatid": isinstance(val, int) and not isinstance(val, bool)}[kind]
            if ok:
                BOT_CONFIG[key] = val
            else:
                logger.warning(f"bot_config: ignoring bad value for {key}: {val!r}")
        set_style(cfg("UI_STYLE"))

db = _DB()

async def _save_config(keys):
    sets = {k: BOT_CONFIG[k] for k in keys if k in BOT_CONFIG}
    unsets = {k: "" for k in keys if k not in BOT_CONFIG}
    update = {}
    if sets:
        update["$set"] = sets
    if unsets:
        update["$unset"] = unsets
    if update:
        await _col_bot_config.update_one({"_id": "settings"}, update, upsert=True)

def set_config(key, value):
    """Store an admin override; a value equal to the default removes the override."""
    if value == BOT_CONFIG_DEFAULTS[key]:
        BOT_CONFIG.pop(key, None)
    else:
        BOT_CONFIG[key] = value
    set_style(cfg("UI_STYLE"))
    _run(_save_config([key]))

BSET_PROTECTED = ("SESSION_STRING", "DUMP_CHANNEL")


def reset_config():
    """Reset every config variable except the credentials that come from .env."""
    keys = [k for k in BOT_CONFIG if k not in BSET_PROTECTED]
    for k in keys:
        BOT_CONFIG.pop(k, None)
    set_style(cfg("UI_STYLE"))
    _run(_save_config(keys))

async def _save_user(uid):
    uid = str(uid)
    doc = db.users[uid]
    doc["_id"] = uid
    await _col_users.replace_one({"_id": uid}, doc, upsert=True)

async def _save_code(code, doc):
    await _col_redeem_codes.replace_one({"_id": code}, doc, upsert=True)

async def _save_banned(uid):
    await _col_banned.replace_one({"_id": uid}, {"_id": uid}, upsert=True)

async def _delete_banned(uid):
    await _col_banned.delete_one({"_id": uid})

async def _save_bought_test(uid):
    await _col_bought_test.replace_one({"_id": uid}, {"_id": uid}, upsert=True)

def _task_done(t):
    if not t.cancelled() and t.exception():
        logger.error(f"DB save failed: {t.exception()!r}")

def _run(coro):
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(coro).add_done_callback(_task_done)
    except RuntimeError:
        asyncio.get_event_loop().run_until_complete(coro)

def save_db(data=None):
    for uid in db.users:
        _run(_save_user(uid))

user_cooldowns = {}
temp_context = {}

def parse_duration(duration_str):
    try:
        value = int(duration_str[:-1])
        unit = duration_str[-1].lower()
        if unit == 'd':
            return timedelta(days=value)
        elif unit == 'w':
            return timedelta(weeks=value)
        elif unit == 'm':
            return timedelta(days=value * 30)
        elif unit == 'y':
            return timedelta(days=value * 365)
        else:
            return None
    except:
        return None

class _SafeFmt(dict):
    def __missing__(self, key):
        return "{" + key + "}"

def apply_cap_font(cap, config):
    """Wrap the rendered caption in the user's Caption Font tag (b/i/u/s/code/spoiler)."""
    tag = {"b": "b", "i": "i", "u": "u", "s": "s", "code": "code", "spoiler": "spoiler"}.get((config or {}).get("cap_font") or "")
    return f"<{tag}>{cap}</{tag}>" if tag and cap else cap


def render_caption(template, filename, filesize_bytes, duration=0):
    """Fill caption variables; unknown {names} stay as-is instead of crashing."""
    title, year = tmdb_mod.clean_title(filename or "")
    m = re.search(r"(2160p|1440p|1080p|720p|576p|480p|360p|4k)", filename or "", re.I)
    dur = int(duration or 0)
    vals = _SafeFmt(
        filename=filename, filesize=human_size(filesize_bytes),
        title=title or filename, year=year or "",
        quality=m.group(1).upper() if m else "",
        duration=(f"{dur // 3600}:{dur % 3600 // 60:02d}:{dur % 60:02d}" if dur >= 3600 else f"{dur // 60}:{dur % 60:02d}") if dur else "",
        ext=os.path.splitext(filename or "")[1].lstrip(".").upper(),
    )
    try:
        return template.format_map(vals)
    except Exception:
        return template.replace("{filename}", filename or "").replace("{filesize}", human_size(filesize_bytes))

def get_user_config(user_id):
    user_id = str(user_id)
    if user_id not in db.users:
        db.users[user_id] = DEFAULT_USER(user_id)
        _run(_save_user(user_id))
    else:
        changed = False
        u = db.users[user_id]
        if "premium" not in u:
            u["premium"] = {"type": "free", "expires": None, "daily_conversions": 0, "daily_failed": 0, "last_reset": str(datetime.now().date())}
            changed = True
        if "rename" not in u:
            u["rename"] = "ask"; changed = True
        if "redeem_used" not in u:
            u["redeem_used"] = False; changed = True
        if "spoiler" not in u:
            u["spoiler"] = False; changed = True
        if "auto_thumb" not in u:
            u["auto_thumb"] = False; changed = True
        for k in ("prefix", "suffix", "remname"):
            if k not in u:
                u[k] = ""; changed = True
        for k, v in (("thumb_src", None), ("audio_fmt", "mp3"), ("audio_br", "192k"),
                     ("poster_lang", "all"), ("poster_kind", "p"), ("cap_font", ""),
                     ("autorename", False), ("rename_method", "auto"), ("remname_auto", ""), ("mediainfo", False)):
            if k not in u:
                u[k] = v; changed = True
        if changed:
            _run(_save_user(user_id))
    return db.users[user_id]

def _is_admin(user_id):
    """Safe admin check: DB may contain non-numeric ids (e.g. '@username')."""
    try:
        return int(user_id) == ADMIN_ID
    except (ValueError, TypeError):
        return False

def check_premium(user_id):
    if _is_admin(user_id):
        return "admin"
    config = get_user_config(user_id)
    premium = config.get("premium", {"type": "free", "expires": None})
    if premium["type"] == "free":
        return "free"
    if premium["expires"]:
        expires = datetime.fromisoformat(premium["expires"]) if isinstance(premium["expires"], str) else premium["expires"]
        if datetime.now() > expires:
            config["premium"] = {"type": "free", "expires": None, "daily_conversions": 0, "daily_failed": 0, "last_reset": str(datetime.now().date())}
            _run(_save_user(user_id))
            return "free"
    return premium["type"]

def has_userbot():
    return premium_client is not None

def plan_limits(premium_type):
    """Limits of a plan, read from bot_config (constants are the defaults)."""
    has_premium_client = has_userbot()
    normal_size = cfg("MAX_FILE_SIZE_NORMAL")
    premium_max_size = cfg("MAX_FILE_SIZE_PREMIUM") if has_premium_client else normal_size
    if premium_type == "admin":
        return {"daily_limit": float('inf'), "max_file_size": float('inf'),
                "concurrent": cfg('MAX_CONCURRENT_ADMIN'), "cooldown": 0, "use_dump": has_premium_client}
    if premium_type == "free":
        return {"daily_limit": cfg("FREE_DAILY_LIMIT"), "max_file_size": normal_size,
                "concurrent": cfg("MAX_CONCURRENT_FREE"), "cooldown": cfg("COOLDOWN_NORMAL"), "use_dump": False}
    if premium_type == "test":
        return {"daily_limit": cfg("TEST_DAILY_LIMIT"), "max_file_size": premium_max_size,
                "concurrent": cfg("MAX_CONCURRENT_TEST"), "cooldown": 0, "use_dump": has_premium_client}
    if premium_type == "gold":
        return {"daily_limit": cfg("GOLD_DAILY_LIMIT"), "max_file_size": premium_max_size,
                "concurrent": cfg("MAX_CONCURRENT_GOLD"), "cooldown": 0, "use_dump": has_premium_client}
    return {"daily_limit": cfg("ULTRA_DAILY_LIMIT"),
            "max_file_size": float('inf') if has_premium_client else normal_size,
            "concurrent": cfg("MAX_CONCURRENT_ULTRA"), "cooldown": 0, "use_dump": has_premium_client}

def get_premium_limits(user_id):
    if _is_admin(user_id):
        return plan_limits("admin")
    return plan_limits(check_premium(user_id))

def in_maintenance(user_id):
    return bool(cfg("MAINTENANCE")) and not _is_admin(user_id)

def maintenance_text():
    note = cfg("MAINTENANCE_MSG")
    return Theme.MAINTENANCE.format(note=Theme.MAINTENANCE_NOTE.format(note=note) if note else "")

def apply_name_rules(filename, config):
    """Build the output name: remname (regex rules) -> prefix -> suffix (before extension)."""
    name = filename or "file"
    base, ext = os.path.splitext(name)
    if len(ext) > 6 or " " in ext:
        base, ext = name, ""
    if config.get("autorename") and config.get("rename_method", "auto") == "auto" and (config.get("remname_auto") or "").strip():
        tpl = autorename_apply(name, config["remname_auto"].strip())
        base, ext = os.path.splitext(tpl)
        if len(ext) > 6 or " " in ext:
            base, ext = tpl, ""
    remname = (config.get("remname") or "").strip() if config.get("rename_method", "auto") != "auto" or not config.get("autorename") else ""
    if remname:
        for rule in remname.replace("\\s", " ").split("|"):
            if not rule:
                continue
            args = rule.split(":")
            try:
                if len(args) >= 3 and args[2].strip().isdigit():
                    base = re.sub(args[0], args[1], base, count=int(args[2]))
                elif len(args) >= 2:
                    base = re.sub(args[0], args[1], base)
                else:
                    base = re.sub(args[0], "", base)
            except re.error as e:
                logger.warning(f"remname rule {rule!r} skipped: {e}")
        base = re.sub(r"\s{2,}", " ", base).strip(" .-_") or "file"
    prefix = (config.get("prefix") or "").replace("\\s", " ")
    suffix = (config.get("suffix") or "").replace("\\s", " ")
    if prefix and not base.startswith(prefix):
        base = prefix + base
    if suffix and not base.endswith(suffix):
        base = base + suffix
    out = re.sub(r'[\\/:*?"<>|\x00-\x1f]', "_", base + ext)
    return out[:250]

def validate_user_value(key, text):
    """Validate /settings text input. Raises ValueError with a short reason."""
    text = (text or "").strip()
    if key == "caption":
        if not text or len(text) > 1024:
            raise ValueError("1-1024 chars")
        return text
    if key in ("prefix", "suffix"):
        if len(text) > 64:
            raise ValueError("max 64 chars")
        if re.search(r'[\\/\x00-\x1f]', text):
            raise ValueError("no slashes")
        return text
    if key == "remname":
        if len(text) > 300:
            raise ValueError("max 300 chars")
        for rule in text.replace("\\s", " ").split("|"):
            if rule:
                try:
                    re.compile(rule.split(":")[0])
                except re.error as e:
                    raise ValueError(f"bad regex {rule.split(':')[0]!r}: {e}")
        return text
    if key == "screenshots":
        if not text.isdigit() or not 0 <= int(text) <= 10:
            raise ValueError("send a number from 0 to 10")
        return int(text)
    if key == "remname_auto":
        if not text or len(text) > 200 or "{" not in text:
            raise ValueError("use tags like {title} {season} {episode} {quality}")
        return text
    if key == "thumb":
        raise ValueError("send a photo, not text")
    raise ValueError("unknown setting")


def check_daily_limit(user_id):
    if _is_admin(user_id):
        return True

    config = get_user_config(user_id)
    today = str(datetime.now().date())

    if config["premium"].get("last_reset") != today:
        config["premium"]["daily_conversions"] = 0
        config["premium"]["daily_failed"] = 0
        config["premium"]["last_reset"] = today
        _run(_save_user(user_id))

    limits = get_premium_limits(user_id)
    return config["premium"]["daily_conversions"] < limits["daily_limit"]


def add_conversion(user_id, success=True):
    if _is_admin(user_id):
        return

    config = get_user_config(user_id)
    today = str(datetime.now().date())

    if config["premium"].get("last_reset") != today:
        config["premium"]["daily_conversions"] = 0
        config["premium"]["daily_failed"] = 0
        config["premium"]["last_reset"] = today

    if success:
        config["premium"]["daily_conversions"] += 1
    else:
        config["premium"]["daily_failed"] += 1

    _run(_save_user(user_id))


def generate_redeem_codes(count, duration_str, plan="gold"):
    duration = parse_duration(duration_str)
    if not duration:
        return None
    days = duration.days
    codes = []
    for _ in range(count):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        while code in db.redeem_codes:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        doc = {
            "_id": code,
            "plan": plan,
            "days": days,
            "used_by": None,
            "used_at": None,
            "created_at": datetime.now().isoformat()
        }
        db.redeem_codes[code] = doc
        _run(_save_code(code, doc))
        codes.append(code)
    return codes

def get_redeem_code(code):
    return db.redeem_codes.get(code)

def has_active_redeemed_plan(user_id):
    uid = str(user_id)
    for code_data in db.redeem_codes.values():
        if code_data["used_by"] == uid:
            config = get_user_config(uid)
            premium = config.get("premium", {})
            if premium.get("type", "free") != "free":
                expires = premium.get("expires")
                if expires:
                    try:
                        if datetime.fromisoformat(expires) > datetime.now():
                            return True
                    except Exception:
                        pass
    return False

def use_redeem_code(code, user_id):
    if code in db.redeem_codes and db.redeem_codes[code]["used_by"] is None:
        if has_active_redeemed_plan(user_id):
            return "active"
        code_data = db.redeem_codes[code]
        plan = code_data["plan"]
        days = code_data["days"]
        config = get_user_config(user_id)
        expires = datetime.now() + timedelta(days=days)
        config["premium"] = {
            "type": plan,
            "expires": expires.isoformat(),
            "daily_conversions": 0,
            "daily_failed": 0,
            "last_reset": str(datetime.now().date())
        }
        db.redeem_codes[code]["used_by"] = str(user_id)
        db.redeem_codes[code]["used_at"] = datetime.now().isoformat()
        _run(_save_user(user_id))
        _run(_save_code(code, db.redeem_codes[code]))
        return True
    return False

def get_active_redeem_count():
    return sum(1 for code in db.redeem_codes.values() if code["used_by"] is None)

def can_buy_test(user_id):
    return str(user_id) not in db.bought_test

def mark_test_bought(user_id):
    uid = str(user_id)
    if uid not in db.bought_test:
        db.bought_test.append(uid)
        _run(_save_bought_test(uid))

def add_premium(user_id, plan, duration_str):
    duration = parse_duration(duration_str)
    if not duration:
        return False
    config = get_user_config(user_id)
    expires = datetime.now() + duration
    current_type = config["premium"]["type"]
    current_expires = config["premium"]["expires"]
    if current_type == "free" or (current_expires and datetime.fromisoformat(current_expires) < expires):
        config["premium"] = {
            "type": plan,
            "expires": expires.isoformat(),
            "daily_conversions": 0,
            "daily_failed": 0,
            "last_reset": str(datetime.now().date())
        }
        _run(_save_user(user_id))
        return True
    return False

def get_user_stats_text(user_id):
    config = get_user_config(user_id)
    plan = check_premium(user_id)
    limits = get_premium_limits(user_id)
    used, failed = _used_today(config)
    admin = _is_admin(user_id)
    expires = ""
    if plan not in ("free", "admin") and config["premium"].get("expires"):
        try:
            expires = Theme.USET_QUOTA_EXPIRES.format(left=format_remaining_time(datetime.fromisoformat(config["premium"]["expires"])))
        except Exception:
            pass
    return Theme.USER_STATS.format(
        name=f"<a href='tg://user?id={user_id}'>{esc(str(user_id))}</a>", plan=Theme.PLAN_NAMES.get(plan, "Free"),
        expires=expires, limit="∞" if admin else limits["daily_limit"], used=used, failed=failed,
        remaining="∞" if admin else max(0, limits["daily_limit"] - used),
        reset=format_timedelta(get_reset_time() - datetime.now()))

async def get_server_status_button_text():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    async with tasks_lock:
        total_tasks = len(tasks)
        downloads = sum(1 for t in tasks.values() if t.stage == "downloading" and not t.cancelled)
        uploads = sum(1 for t in tasks.values() if t.stage == "uploading" and not t.cancelled)
    return Theme.SERVER.format(
        cpu_bar=theme_bar(cpu), cpu=f"{cpu:.1f}", ram_bar=theme_bar(ram.percent), ram=f"{ram.percent:.1f}",
        disk_bar=theme_bar(disk.percent), disk=f"{disk.percent:.1f}",
        tasks_bar=theme_bar(total_tasks / MAX_BOT_TASKS * 100), tasks=total_tasks, max_tasks=MAX_BOT_TASKS,
        ram_u=human_size(ram.used), ram_t=human_size(ram.total), disk_f=human_size(disk.free), disk_t=human_size(disk.total),
        dls=downloads, uls=uploads, uptime=time_formatter(get_bot_uptime()))

_net_prev = {"t": 0.0, "sent": 0, "recv": 0, "ul": 0.0, "dl": 0.0}

def _net_rates():
    """Server-wide DL/UL speed (bytes/s) from psutil counters, sampled between calls."""
    try:
        io = psutil.net_io_counters()
    except Exception:
        return 0.0, 0.0
    now = time.time()
    dt = now - _net_prev["t"]
    if _net_prev["t"] and dt >= 1:
        _net_prev["dl"] = max(0.0, (io.bytes_recv - _net_prev["recv"]) / dt)
        _net_prev["ul"] = max(0.0, (io.bytes_sent - _net_prev["sent"]) / dt)
    if not _net_prev["t"] or dt >= 1:
        _net_prev.update(t=now, sent=io.bytes_sent, recv=io.bytes_recv)
    return _net_prev["dl"], _net_prev["ul"]

async def get_server_status_mini_text():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    async with tasks_lock:
        active = sum(1 for t in tasks.values() if not t.cancelled)
    dl, ul = _net_rates()
    return Theme.STATUS_FOOTER.format(
        tasks=active, max_tasks=MAX_BOT_TASKS, avl=max(0, MAX_BOT_TASKS - active),
        cpu=f"{cpu:.1f}", free=human_size(disk.free), free_p=f"{100 - disk.percent:.1f}",
        ram=f"{ram.percent:.1f}", uptime=time_formatter(get_bot_uptime()),
        dl=human_size(dl), ul=human_size(ul),
    )

async def build_task_text(task):
    name = esc(short(task.filename, 60))
    if task.cancelled:
        return Theme.STATUS_CANCELLED.format(name=name)
    downloading = task.stage == "downloading"
    current, total = task.current, task.total
    percent = (current / total * 100) if total > 0 else 0
    elapsed = time.time() - getattr(task, "stage_start", task.start_time)
    speed = current / elapsed if elapsed > 0 else 0
    eta = (total - current) / speed if speed > 0 and total > current else 0
    return Theme.STATUS_TASK.format(
        name=name, bar=circle_bar(percent), percent=percent,
        processed_label="Processed" if downloading else "Uploaded",
        done=human_size(current), total=human_size(total),
        status="Download" if downloading else "Upload",
        eta=time_formatter(eta), speed=human_size(speed),
        elapsed=time_formatter(time.time() - task.start_time),
        mode_tag="#download" if downloading else "#upload",
        user=task.user_id, pos=task.position or 1, gid=task.gid,
    )

async def build_combined_status(user_id, page=0):
    async with tasks_lock:
        user_task_ids = user_tasks.get(user_id, [])
        user_tasks_list = [tasks[tid] for tid in user_task_ids if tid in tasks and not tasks[tid].cancelled]
    
    if not user_tasks_list:
        return None, 0, 0
    
    for idx, task in enumerate(user_tasks_list, 1):
        task.position = idx
    
    tasks_per_page = 2
    total_pages = max(1, (len(user_tasks_list) + tasks_per_page - 1) // tasks_per_page)
    page = page % total_pages
    start_idx = page * tasks_per_page
    end_idx = min(start_idx + tasks_per_page, len(user_tasks_list))
    page_tasks = user_tasks_list[start_idx:end_idx]
    
    all_text = ""
    for task in page_tasks:
        task_text = await build_task_text(task)
        all_text += task_text + "\n\n"
    
    server_stats = await get_server_status_mini_text()
    all_text += server_stats
    
    return all_text, total_pages, page

_CANCEL_LINE = re.compile(r'(?:┖❌|<b>╰</b>) <code>/cancel_([a-z0-9]{8})</code></blockquote>\n*')

def rich_status_html(text):
    """Status text -> rich HTML: a Cancel Task button inside every task, a line between tasks."""
    text = _CANCEL_LINE.sub(lambda mt: '<b>╰</b> <tg-button type="callback_data" style="danger" data="cxask_%s">Cancel Task</tg-button></blockquote><hr/>\n' % mt.group(1), text)
    i = text.rfind("<hr/>")
    if i >= 0:
        text = text[:i] + text[i + 5:]
    h = text.strip().replace("\n", "<br>")
    h = re.sub(r'(?:<br>\s*)+(<(?:/?blockquote|hr|/?p)\b[^>]*>)', r'\1', h)
    return re.sub(r'(</blockquote>|<hr/>|</p>)(?:\s*<br>)+', r'\1', h)

async def _rich_put(uid, msg, combined, markup):
    """Edit the status as a rich message; a plain one can't become rich, so a new rich one replaces it."""
    rm = InputRichMessage(html=rich_status_html(combined))
    if getattr(msg, "_rich", False):
        await msg.edit_text(rich_message=rm, reply_markup=markup)
        return msg
    new = await bot.send_rich_message(msg.chat.id, rm, reply_markup=markup)
    new._rich = True
    user_status_msg[uid] = new
    try:
        await msg.delete()
    except Exception:
        pass
    return new

async def update_user_status(user_id):
    page = user_pages.get(user_id, 0)
    combined, total_pages, current_page = await build_combined_status(user_id, page)
    
    status_msg = user_status_msg.get(user_id)
    
    if not combined:
        if status_msg:
            try:
                await status_msg.delete()
            except:
                pass
            user_status_msg.pop(user_id, None)
        return
    
    if not status_msg:
        return
    if cancel_pending.get(user_id, 0) > time.time():
        return
    
    nav_buttons = []
    async with tasks_lock:
        user_task_ids = user_tasks.get(user_id, [])
        user_tasks_list = [tasks[tid] for tid in user_task_ids if tid in tasks and not tasks[tid].cancelled]
        for task in user_tasks_list:
            nav_buttons.append(InlineKeyboardButton(f"✘ {task.position} ✘", callback_data=f"cancel_pos_{user_id}_{task.position}", style=enums.ButtonStyle.DANGER))
    
    nav_row = []
    if total_pages > 1:
        nav_row.append(InlineKeyboardButton("⫷", callback_data=f"page_{user_id}_{(current_page - 1) % total_pages}", style=enums.ButtonStyle.PRIMARY))
        nav_row.append(InlineKeyboardButton(f"⌬ ᴘᴀɢᴇs {current_page + 1}/{total_pages}", callback_data=f"refresh_{user_id}", style=enums.ButtonStyle.PRIMARY))
        nav_row.append(InlineKeyboardButton("⫸", callback_data=f"page_{user_id}_{(current_page + 1) % total_pages}", style=enums.ButtonStyle.PRIMARY))
    else:
        nav_row.append(InlineKeyboardButton("⟳ ʀᴇꜰʀᴇsʜ", callback_data=f"refresh_{user_id}", style=enums.ButtonStyle.PRIMARY))
    
    buttons = []
    if cfg("RICH_MESSAGES"):
        nav_buttons = []
    
    if nav_buttons:
        for i in range(0, len(nav_buttons), 3):
            buttons.append(nav_buttons[i:i+3])
    
    buttons.append(nav_row)
    
    try:
        if cfg("RICH_MESSAGES"):
            try:
                await _rich_put(user_id, status_msg, combined, InlineKeyboardMarkup(buttons))
            except (MessageNotModified, FloodWait):
                raise
            except Exception as e:
                logger.warning(f"rich status failed, plain text: {e}")
                await status_msg.edit_text(combined, reply_markup=InlineKeyboardMarkup(buttons))
        else:
            await status_msg.edit_text(combined, reply_markup=InlineKeyboardMarkup(buttons))
    except (MessageNotModified, FloodWait):
        pass
    except Exception as e:
        logger.error(f"Failed to update status message for user {user_id}: {e}")
        if user_status_msg.get(user_id) is status_msg:
            user_status_msg.pop(user_id, None)

async def progress_bar(current, total, task_id):
    task = tasks.get(task_id)
    if not task or task.cancelled:
        return
    if task.cancel_event.is_set():
        task.cancelled = True
        raise StopTransmission
    
    async with task.lock:
        task.current = current
        task.total = total
    
    status_msg = user_status_msg.get(task.user_id)
    if not status_msg:
        return
    
    now = time.time()
    last_update = getattr(status_msg, "last_update_time", 0)
    if now - last_update < 10 and current < total:
        return
    status_msg.last_update_time = now
    
    await update_user_status(task.user_id)

async def extract_audio(video_path, output_path):
    try:
        proc = await asyncio.create_subprocess_exec(
            'ffmpeg', '-i', video_path, '-vn', '-acodec', 'libmp3lame',
            '-q:a', '2', '-y', output_path,
            stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.PIPE
        )
        _, err = await proc.communicate()
        if proc.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path
        logger.error(f"extract_audio failed: {err.decode()[-300:]}")
    except Exception as e:
        logger.error(f"extract_audio error: {e}")
    return None

async def get_video_thumbnail(video_path, output_path, ss_time=1):
    try:
        process = await asyncio.create_subprocess_exec(
            'ffmpeg', '-ss', str(ss_time), '-i', video_path,
            '-vframes', '1', '-q:v', '2',
            output_path, '-y',
            stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL
        )
        await process.wait()
        return output_path if os.path.exists(output_path) else None
    except Exception as e:
        logger.error(f"Thumbnail error: {e}")
        return None

async def upload_to_dump(client, file_path, file_name, task_id, thumb_path=None, duration=0, file_type="document", spoiler=False, cover=None):
    try:
        upload_client = premium_client if premium_client else client
        if file_type == "video":
            msg = await upload_client.send_video(
                cfg('DUMP_CHANNEL'),
                video=file_path,
                file_name=file_name,
                thumb=thumb_path,
                duration=duration,
                supports_streaming=True,
                has_spoiler=spoiler,
                video_cover=cover,
                progress=progress_bar,
                progress_args=(task_id,)
            )
        elif file_type == "audio":
            msg = await upload_client.send_audio(
                cfg('DUMP_CHANNEL'),
                audio=file_path,
                file_name=file_name,
                thumb=thumb_path,
                duration=duration,
                progress=progress_bar,
                progress_args=(task_id,)
            )
        else:
            msg = await upload_client.send_document(
                cfg('DUMP_CHANNEL'),
                document=file_path,
                file_name=file_name,
                thumb=thumb_path,
                progress=progress_bar,
                progress_args=(task_id,)
            )
        return msg
    except Exception as e:
        logger.error(f"Error uploading to dump: {e}", exc_info=True)
        print(f"[DUMP ERROR] {e}")
        return None

async def mediainfo_markup(path, name, config):
    """MediaInfo URL button under the sent file when the user turned MediaInfo on."""
    if not config.get("mediainfo"):
        return None
    try:
        proc = await asyncio.create_subprocess_exec("mediainfo", path, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
        out, _ = await asyncio.wait_for(proc.communicate(), timeout=60)
        url = await _telegraph_mediainfo(name, out.decode("utf-8", "ignore"))
        if url:
            return menu([[("📃 MediaInfo", None, {"url": url})]])
    except Exception as e:
        logger.warning(f"mediainfo button failed: {e}")
    return None


async def copy_from_dump_to_user(client, dump_msg, user_id, caption, reply_to_message_id, spoiler=False, reply_markup=None):
    try:
        return await client.copy_message(
            chat_id=user_id,
            from_chat_id=cfg('DUMP_CHANNEL'),
            message_id=dump_msg.id,
            caption=caption,
            reply_parameters=ReplyParameters(message_id=reply_to_message_id),
            has_spoiler=spoiler,
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Error copying from dump: {e}")
        return None

def get_main_btns():
    B = Theme.START_BTNS
    b = ButtonMaker()
    b.ibutton(B["settings"], "ui_settings")
    b.ibutton(B["plans"], "ui_plans")
    b.ibutton(B["server"], "ui_status")
    b.ibutton(B["about"], "ui_about")
    b.ibutton(B["help"], "ui_help")
    b.ubutton(B["group"], "https://t.me/TJ_Bots_Chat", "l_body")
    b.ubutton(B["channel"], "https://t.me/Tj_Bots", "l_body")
    b.ibutton("❌", "close_all", "footer")
    return b.build_menu(2)

def plans_kb():
    P = Theme.PLAN_BTNS
    b = ButtonMaker()
    for k in ("free", "test", "gold", "ultra"):
        b.ibutton(P[k], f"show_{k}")
    b.ibutton(P["refresh"], "refresh_stats", "l_body")
    b.ibutton("◀️", "ui_home", "footer")
    b.ibutton("❌", "close_all", "footer")
    return b.build_menu(2)

def back_plans_kb(extra=None):
    b = ButtonMaker()
    for t, d, u in (extra or []):
        (b.ubutton(t, u) if u else b.ibutton(t, d))
    b.ibutton("◀️", "ui_plans", "footer")
    b.ibutton("❌", "close_all", "footer")
    return b.build_menu(1)

def back_kb(back):
    b = ButtonMaker()
    b.ibutton("◀️", back, "footer")
    b.ibutton("❌", "close_all", "footer")
    return b.build_menu(2)

@bot.on_message(filters.command("start"))
async def start_cmd(client, message):
    config = get_user_config(message.from_user.id)
    arg = message.command[1] if len(message.command) > 1 else ""
    if arg.startswith("token_"):
        tk = config.get("token") or {}
        if tk.get("value") == arg[6:] and tk.get("expires", 0) <= time.time():
            tk["expires"] = time.time() + int(cfg("TOKEN_TIMEOUT"))
            config["token"] = tk
            _run(_save_user(message.from_user.id))
            return await message.reply_text(f"<b>✓ Token activated</b>\nValid for {max(1, int(cfg('TOKEN_TIMEOUT')) // 3600)}h. Send your file now.")
        return await message.reply_text("<b>This token is not valid.</b> Send a file to get a new one.")
    text = Theme.START.format(
        name=esc(message.from_user.first_name),
        dev_link=dev_link(),
        dev_name=cfg('DEVELOPER_NAME'),
    )
    await message.reply_text(text, reply_markup=get_main_btns(), link_preview_options=LinkPreviewOptions(is_disabled=True))

@bot.on_message(filters.command(["help", "h"]))
async def help_command(client, message):
    await show_help_menu(client, message, message.from_user.id)

def _quota_text(uid, config):
    limits = get_premium_limits(uid)
    if _is_admin(uid):
        return "∞"
    used, _ = _used_today(config)
    return f"{used}/{limits['daily_limit']}"

def _used_today(config):
    p = config.get("premium") or {}
    if p.get("last_reset") != str(datetime.now().date()):
        return 0, 0
    return p.get("daily_conversions", 0), p.get("daily_failed", 0)

def _user_link(user):
    return f"<a href='tg://user?id={user.id}'>{esc(getattr(user, 'first_name', None) or 'User')}</a>"

USET_PAGE_KEYS = ("caption", "prefix", "suffix", "remname", "remname_auto", "thumb")
USET_SCREENS = ("home", "universal", "leech", "mode", "fmt", "br", "plang", "pkind", "capfont", "shots", "quota", "reset") + tuple(f"pg_{k}" for k in USET_PAGE_KEYS)
USET_INPUT_PARENT = {**{k: f"pg_{k}" for k in USET_PAGE_KEYS}, "screenshots": "shots"}
USET_RESET_KEYS = ("thumb", "thumb_src", "mode", "caption", "prefix", "suffix", "remname", "rename", "screenshots",
                   "spoiler", "auto_thumb", "cap_font", "mediainfo", "autorename", "rename_method", "remname_auto", "audio_fmt", "audio_br", "poster_lang", "poster_kind")
USET_ROUTES = {"ui_settings": "home", "st_mode": "mode", "st_rename": "home", "st_ss": "home",
               "us_auto": "home", **{f"us_{s}": s for s in USET_SCREENS}}
LANG_NAMES = {"en": "English", "he": "Hebrew", "ar": "Arabic", "ru": "Russian", "fr": "French", "de": "German",
              "es": "Spanish", "it": "Italian", "pt": "Portuguese", "tr": "Turkish", "hi": "Hindi", "fa": "Persian",
              "uk": "Ukrainian", "pl": "Polish", "nl": "Dutch", "ja": "Japanese", "ko": "Korean", "zh": "Chinese",
              "id": "Indonesian", "ms": "Malay", "ta": "Tamil", "te": "Telugu", "bn": "Bengali", "ur": "Urdu"}


def rename_on(config):
    return config.get("rename", "ask") in ("ask", "yes")


def close_kb():
    b = ButtonMaker()
    b.ibutton("❌", "close_all")
    return b.build_menu(1)


def _nxt(seq, cur):
    seq = list(seq)
    return seq[(seq.index(cur) + 1) % len(seq)] if cur in seq else seq[0]


_UINFO_EXTRA = {
    "capfont": "➲ Font applied to the caption of every file you get\n➲ <b>Regular</b> leaves the caption as it is",
    "shots": "➲ How many screenshots are sent after every video\n➲ <b>Off</b> sends none",
}
_UBACK = {"mode": "us_leech", "shots": "us_leech", "capfont": "us_leech",
          "fmt": "us_universal", "br": "us_universal", "plang": "us_universal", "pkind": "us_universal"}


def _uset_is_set(key, config):
    if key == "caption":
        return (config.get("caption") or DEFAULT_CAPTION) != DEFAULT_CAPTION
    return bool(config.get(key))


def _uset_value(key, config):
    v = config.get(key)
    if key == "thumb":
        return "<i>Exists</i>" if v else f"<i>{Theme.NOT_SET}</i>"
    if key == "caption" and not _uset_is_set(key, config):
        return f"<i>{Theme.NOT_SET} (Default)</i>"
    return f"<code>{esc(short(v, 200))}</code>" if v else f"<i>{Theme.NOT_SET}</i>"


def _uset_page_text(key, config):
    title, label, desc, _ = Theme.USET_PAGES[key]
    return Theme.USET_PAGE.format(title=title, label=label, value=_uset_value(key, config), desc=desc)


def _uset_choice(uid, user, config, screen):
    b = ButtonMaker()
    mode = config.get("mode", "ask")
    fmt, br = config.get("audio_fmt", "mp3"), config.get("audio_br", "192k")
    pl, pk = config.get("poster_lang", "all"), config.get("poster_kind", "p")
    n = int(config.get("screenshots", 0) or 0)
    cf = config.get("cap_font") or ""
    title, cur, opts = {
        "mode": ("Upload Type", Theme.MODE_NAMES.get(mode, "Ask"),
                 [(v, f"m_{k}", mode == k) for k, v in Theme.MODE_NAMES.items()]),
        "fmt": ("Audio Format", Theme.AUDIO_FORMATS.get(fmt, ("MP3",))[0],
                [(v[0], f"af_{k}", fmt == k) for k, v in Theme.AUDIO_FORMATS.items()]),
        "br": ("Audio Quality", "Lossless" if fmt == "flac" else br,
               [(r, f"ab_{r}", br == r) for r in Theme.AUDIO_BITRATES]),
        "plang": ("Poster Language", Theme.POSTER_LANG_OPTS.get(pl, pl.upper()),
                  [(v, f"pl_{k}", pl == k) for k, v in Theme.POSTER_LANG_OPTS.items()]),
        "pkind": ("Poster Type", Theme.POSTER_KINDS_PL[pk],
                  [(v, f"pk_{k}", pk == k) for k, v in Theme.POSTER_KINDS_PL.items()]),
        "shots": ("Screenshots", "Disabled" if n <= 0 else f"{n} per video",
                  [("Off" if i == 0 else str(i), f"ss_{i}", n == i) for i in range(11)]),
        "capfont": ("Caption Font", Theme.CAP_FONTS.get(cf, "Regular"),
                    [(v, f"cf_{k or 'none'}", cf == k) for k, v in Theme.CAP_FONTS.items()]),
    }[screen]
    info = Theme.USET_CHOICE_INFO.get(screen) or _UINFO_EXTRA[screen]
    text = Theme.USET_CHOICE.format(title=title, name=_user_link(user), current=cur, info=info)
    for label, data, active in opts:
        b.ibutton(mark(active, label), data)
    b.ibutton("◀️", _UBACK[screen], "footer")
    b.ibutton("❌", "close_all", "footer")
    return text, b.build_menu(3 if screen in ("shots", "br") else 2)


_UALIAS = {"thumb": "pg_thumb", "caption": "pg_caption", "name": "leech"}


def _uset_home(uid, user, config, b):
    text = Theme.USET_HOME.format(name=_user_link(user), id=user.id)
    b.ibutton(Theme.USET_MENU_BTNS["universal"], "us_universal")
    b.ibutton(Theme.USET_MENU_BTNS["leech"], "us_leech")
    defaults = DEFAULT_USER(uid)
    if any(config.get(k, defaults[k]) != defaults[k] for k in USET_RESET_KEYS):
        b.ibutton(Theme.USET_MENU_BTNS["reset"], "us_reset")
    b.ibutton("◀️", "ui_home", "footer")
    b.ibutton("❌", "close_all", "footer")
    return text, b.build_menu(1)


def _uset_universal(uid, user, config, b):
    fmt, br = config.get("audio_fmt", "mp3"), config.get("audio_br", "192k")
    pl, pk = config.get("poster_lang", "all"), config.get("poster_kind", "p")
    plan = check_premium(uid)
    text = Theme.USET_UNIVERSAL.format(
        name=_user_link(user), used=_used_today(config)[0], plan=Theme.PLAN_NAMES.get(plan, plan),
        fmt=Theme.AUDIO_FORMATS.get(fmt, ("MP3",))[0], br="Lossless" if fmt == "flac" else br,
        mediainfo="Enabled" if config.get("mediainfo") else "Disabled",
        lang=Theme.POSTER_LANG_OPTS.get(pl, pl.upper()), kind=Theme.POSTER_KINDS_PL[pk])
    b.ibutton(mark(config.get("mediainfo"), "MediaInfo"), "tg_mediainfo")
    b.ibutton("Audio Format", "us_fmt")
    if fmt != "flac":
        b.ibutton("Audio Quality", "us_br")
    b.ibutton("Poster Language", "us_plang")
    b.ibutton("Poster Type", "us_pkind")
    b.ibutton("◀️", "us_home", "footer")
    b.ibutton("❌", "close_all", "footer")
    return text, b.build_menu(2)


def _uset_leech(uid, user, config, b):
    mode = config.get("mode", "ask")
    fmt, br = config.get("audio_fmt", "mp3"), config.get("audio_br", "192k")
    pl, pk = config.get("poster_lang", "all"), config.get("poster_kind", "p")
    n = int(config.get("screenshots", 0) or 0)
    cap_custom = _uset_is_set("caption", config)
    cf = config.get("cap_font") or ""
    vals = {k: esc(short(config.get(k) or "", 40)) or Theme.NOT_SET for k in ("prefix", "suffix", "remname")}
    text = Theme.USET_MAIN.format(
        name=_user_link(user), id=user.id, plan=Theme.PLAN_NAMES.get(check_premium(uid), "Free"),
        mode=Theme.MODE_NAMES.get(mode, "Ask"), rename="Enabled" if rename_on(config) else "Disabled",
        thumb="Exists" if config.get("thumb") else Theme.NOT_SET,
        auto_thumb="Enabled" if config.get("auto_thumb") else "Disabled",
        caption="Custom" if cap_custom else "Default",
        screenshots="Disabled" if n <= 0 else f"{n} per video",
        remname_auto=esc(short(config.get("remname_auto") or "", 40)) or Theme.NOT_SET,
        method="Regex" if config.get("rename_method") == "regex" else "Auto Rename",
        autorename="Enabled" if config.get("autorename") else "Disabled",
        spoiler="Enabled" if config.get("spoiler") else "Disabled", cap_font=Theme.CAP_FONTS.get(cf, "Regular"),
        fmt=Theme.AUDIO_FORMATS.get(fmt, ("MP3",))[0], br="Lossless" if fmt == "flac" else br,
        lang=Theme.POSTER_LANG_OPTS.get(pl, pl.upper()), kind=Theme.POSTER_KINDS_PL[pk], **vals)
    b.ibutton("Upload Type", "us_mode")
    b.ibutton(mark(config.get("thumb"), "Thumbnail"), "us_pg_thumb")
    b.ibutton(mark(cap_custom, "Caption"), "us_pg_caption")
    b.ibutton(mark(config.get("prefix"), "Prefix"), "us_pg_prefix")
    b.ibutton(mark(config.get("suffix"), "Suffix"), "us_pg_suffix")
    b.ibutton(mark(config.get("remname"), "Regex Remname"), "us_pg_remname")
    b.ibutton(mark(config.get("remname_auto"), "AutoRename Template"), "us_pg_remname_auto")
    b.ibutton(mark(config.get("autorename"), "AutoRename"), "tg_autorename")
    b.ibutton("Rename Method: Regex" if config.get("rename_method") == "regex" else "Rename Method: Auto", "tg_method")
    b.ibutton(mark(rename_on(config), "Rename Prompt"), "tg_rename")
    b.ibutton(mark(config.get("auto_thumb"), "Auto Thumbnail"), "tg_auto_thumb")
    b.ibutton(mark(config.get("spoiler"), "Spoiler"), "tg_spoiler")
    b.ibutton("Caption Font", "us_capfont")
    b.ibutton(mark(n > 0, "Screenshots"), "us_shots")
    b.ibutton("◀️", "us_home", "footer")
    b.ibutton("❌", "close_all", "footer")
    return text, b.build_menu(2)


def _uset_page(uid, user, config, key, b):
    isset = _uset_is_set(key, config)
    if key == "thumb" and config.get("thumb"):
        b.ibutton(Theme.USET_BTN["view"], "us_thumbview", "header")
    b.ibutton(Theme.USET_BTN["change" if isset else "set"].format(n=Theme.USET_PAGES[key][0]), f"us_in_{key}")
    if isset:
        b.ibutton(Theme.USET_BTN["delete"], f"us_rm_{key}")
    b.ibutton("◀️", "us_leech", "footer")
    b.ibutton("❌", "close_all", "footer")
    return _uset_page_text(key, config), b.build_menu(2)


def uset_view(uid, user, config, screen="home"):
    """One renderer for every /settings screen -> (text, keyboard)."""
    screen = _UALIAS.get(screen, screen)
    name = _user_link(user)
    b = ButtonMaker()
    if screen in ("mode", "fmt", "br", "plang", "pkind", "capfont", "shots"):
        return _uset_choice(uid, user, config, screen)
    if screen == "home":
        return _uset_home(uid, user, config, b)
    if screen == "universal":
        return _uset_universal(uid, user, config, b)
    if screen == "leech":
        return _uset_leech(uid, user, config, b)
    if screen.startswith("pg_"):
        return _uset_page(uid, user, config, screen[3:], b)
    if screen == "quota":
        plan = check_premium(uid)
        limits = get_premium_limits(uid)
        used, failed = _used_today(config)
        admin = _is_admin(uid)
        expires = ""
        exp = (config.get("premium") or {}).get("expires")
        if plan not in ("free", "admin") and exp:
            try:
                expires = Theme.USET_QUOTA_EXPIRES.format(left=format_remaining_time(datetime.fromisoformat(exp)))
            except Exception:
                pass
        text = Theme.USET_QUOTA.format(
            name=name, plan=Theme.PLAN_NAMES.get(plan, plan), expires=expires,
            used=used, limit="∞" if admin else limits["daily_limit"], failed=failed,
            remaining="∞" if admin else max(0, limits["daily_limit"] - used),
            reset=format_timedelta(get_reset_time() - datetime.now()),
            max_size=human_size(limits["max_file_size"]),
            concurrent="∞" if admin else limits["concurrent"],
            cooldown=f"{limits['cooldown']}s" if limits["cooldown"] else "None",
        )
        b.ibutton("Plans", "ui_plans")
        b.ibutton("♻️ Refresh", "us_quota")
    elif screen == "reset":
        text = Theme.USET_RESET
        b.ibutton("Yes!, Reset", "us_resetyes")
    b.ibutton("◀️", "us_home", "footer")
    b.ibutton("❌", "close_all", "footer")
    return text, b.build_menu(2, fb_cols=3)


def uset_prompt_view(key, config, error=None):
    text = Theme.USET_ASK.format(page=_uset_page_text(key, config), ask=Theme.USET_PAGES[key][3])
    if error:
        text = Theme.USET_INVALID.format(err=esc(error)) + "\n\n" + text
    b = ButtonMaker()
    b.ibutton(Theme.USET_BTN["stop"], "us_shots" if key == "screenshots" else f"us_pg_{key}")
    if _uset_is_set(key, config):
        b.ibutton(Theme.USET_BTN["delete"], f"us_rm_{key}")
    b.ibutton("◀️", "us_leech", "footer")
    b.ibutton("❌", "close_all", "footer")
    return text, b.build_menu(2)

BSET_KEYS = list(BOT_CONFIG_SPEC)
BSET_PER_PAGE = 8


async def apply_userbot(session):
    """Hot-swap the premium userbot without restarting the bot. Returns '' on success, else an error text."""
    global premium_client, userbot_info
    if tasks:
        return f"{len(tasks)} active task(s). Wait for them or /cancelall, then try again."
    new, info = None, ""
    if session and session != "your_session_string_here":
        new = make_premium_client(session)
        if new is None:
            return "could not build a client from this session"
        try:
            await new.start()
            me = await new.get_me()
        except Exception as e:
            try:
                await new.stop()
            except Exception:
                pass
            return f"login failed: {type(e).__name__}"
        info = (f"@{me.username}" if me.username else str(me.first_name)) + (" · Premium" if me.is_premium else " · no Premium")
    old, premium_client, userbot_info = premium_client, new, info
    if old is not None:
        try:
            await old.stop()
        except Exception as e:
            logger.warning(f"old userbot stop failed: {e}")
    return ""


def bset_home_view():
    text = Theme.BSET_HOME
    b = ButtonMaker()
    b.ibutton(Theme.BSET_BTNS["vars"], "bs_vars")
    b.ibutton(Theme.BSET_BTNS["session"], "bs_g_session")
    b.ibutton(Theme.BSET_BTNS["short"], "bs_g_short")
    if BOT_CONFIG:
        b.ibutton(Theme.BSET_BTNS["reset_all"], "bs_reset")
    b.ibutton("◀️", "adm_home", "footer")
    b.ibutton("❌", "close_all", "footer")
    return text, b.build_menu(1)


def bset_vars_view(page=0):
    lines = tree([(Theme.BSET_GROUP_NAMES.get(g, g.title()), f"{len(BSET_GROUPED[g])} vars")
                  for g in BSET_GROUP_ORDER if BSET_GROUPED.get(g)])
    text = Theme.BSET_VARS.format(lines=lines, page=1, pages=1)
    b = ButtonMaker()
    for g in BSET_GROUP_ORDER:
        if BSET_GROUPED.get(g):
            b.ibutton(Theme.BSET_GROUP_NAMES.get(g, g.title()), f"bs_g_{g}")
    b.ibutton("◀️", "bs_home", "footer")
    b.ibutton("❌", "close_all", "footer")
    return text, b.build_menu(2)


def bset_page_of(key):
    return BOT_CONFIG_SPEC[key][1]


def bset_prompt_view(key, error=None):
    kind = BOT_CONFIG_SPEC[key][0]
    text = Theme.BSET_EDIT.format(key=key, desc=Theme.BSET_DESC[key], current=esc(fmt_config_value(key)),
                                  default=esc(fmt_config_value(key, BOT_CONFIG_DEFAULTS[key])), hint=Theme.BSET_HINTS[kind])
    if error:
        text = Theme.BSET_INVALID.format(err=esc(error)) + "\n\n" + text
    b = ButtonMaker()
    if kind == "bool":
        cur = bool(cfg(key))
        b.ibutton(("✓ " if cur else "") + "True", f"bs_set_{key}_1",
                  style=enums.ButtonStyle.SUCCESS if cur else enums.ButtonStyle.DEFAULT)
        b.ibutton(("" if cur else "✓ ") + "False", f"bs_set_{key}_0",
                  style=enums.ButtonStyle.SUCCESS if not cur else enums.ButtonStyle.DEFAULT)
    if kind == "choice":
        cur = cfg(key)
        for name in STYLES:
            b.ibutton(("✓ " if cur == name else "") + name.title(), f"bs_st_{name}",
                      style=enums.ButtonStyle.SUCCESS if cur == name else enums.ButtonStyle.DEFAULT)
    if key in BOT_CONFIG:
        b.ibutton(Theme.BSET_BTNS["default"], f"bs_def_{key}")
    b.ibutton("◀️", f"bs_g_{bset_page_of(key)}", "footer")
    b.ibutton("❌", "close_all", "footer")
    return text, b.build_menu(2)


BSET_GROUP_ORDER = ["quota", "conc", "limits", "price", "brand", "session", "short", "sys"]
BSET_GROUPED = {g: [k for k, (_, grp) in BOT_CONFIG_SPEC.items() if grp == g] for g in BSET_GROUP_ORDER}


def bset_group_view(group):
    keys = BSET_GROUPED.get(group) or []
    if not keys:
        return bset_vars_view(0)
    title = Theme.BSET_GROUP_NAMES.get(group, group.title())
    lines = tree([(k, f"<code>{esc(fmt_config_value(k))}</code>") for k in keys])
    text = Theme.BSET_GROUP.format(title=title, lines=lines)
    b = ButtonMaker()
    for k in keys:
        b.ibutton(k, f"bs_e_{k}")
    b.ibutton("◀️", "bs_vars", "footer")
    b.ibutton("❌", "close_all", "footer")
    return text, b.build_menu(2)


def admin_panel_view():
    counts = {"test": 0, "gold": 0, "ultra": 0}
    for u in list(db.users):
        t = check_premium(u)
        if t in counts:
            counts[t] += 1
    text = Theme.ADMIN_PANEL.format(
        admin=ADMIN_ID, users=len(db.users), banned=len(db.banned), redeem=get_active_redeem_count(),
        maint="Enabled" if cfg("MAINTENANCE") else "Disabled", **counts)
    A = Theme.ADMIN_BTNS
    b = ButtonMaker()
    b.ibutton(A["bset"], "bs_home")
    b.ibutton(A["stats"], "stats_bot")
    b.ibutton("Logs", "log_refresh")
    b.ibutton("◀️", "ui_home", "footer")
    b.ibutton("❌", "close_all", "footer")
    return text, b.build_menu(2)

def _stats_page(page):
    if page == "bot":
        ram, swap, disk = psutil.virtual_memory(), psutil.swap_memory(), psutil.disk_usage("/")
        try:
            dio = psutil.disk_io_counters()
            dr, dw = human_size(dio.read_bytes), human_size(dio.write_bytes)
        except Exception:
            dr = dw = "N/A"
        return Theme.STATS_BOT.format(
            bot_uptime=time_formatter(get_bot_uptime()), app_ram=f"{psutil.Process().memory_info().rss / 1048576:.1f} MB",
            ram_bar=theme_bar(ram.percent), ram=ram.percent, ram_u=human_size(ram.used), ram_f=human_size(ram.available), ram_t=human_size(ram.total),
            swap_bar=theme_bar(swap.percent), swap=swap.percent, swap_u=human_size(swap.used), swap_f=human_size(swap.free), swap_t=human_size(swap.total),
            disk_bar=theme_bar(disk.percent), disk=disk.percent, disk_read=dr, disk_write=dw,
            disk_u=human_size(disk.used), disk_f=human_size(disk.free), disk_t=human_size(disk.total))
    if page == "sys":
        net = psutil.net_io_counters()
        freq = psutil.cpu_freq()
        try:
            load = ", ".join(f"{x:.2f}" for x in os.getloadavg())
        except OSError:
            load = "N/A"
        cpu = psutil.cpu_percent(interval=0.5)
        return Theme.STATS_SYS.format(
            os_uptime=time_formatter(time.time() - psutil.boot_time()), os_version=esc(platform.platform()),
            os_arch=platform.machine(), up_data=human_size(net.bytes_sent), dl_data=human_size(net.bytes_recv),
            pkt_sent=net.packets_sent // 1000, pkt_recv=net.packets_recv // 1000,
            tl_data=human_size(net.bytes_sent + net.bytes_recv), cpu_bar=theme_bar(cpu), cpu=cpu,
            cpu_freq=f"{freq.current / 1000:.2f} GHz" if freq else "N/A", sys_load=load,
            p_core=psutil.cpu_count(logical=False) or "N/A", v_core=psutil.cpu_count(logical=True) or "N/A",
            total_core=psutil.cpu_count() or "N/A", usable_cpu=len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else (psutil.cpu_count() or "N/A"))
    if page == "lim":
        return Theme.STATS_LIMITS.format(
            q_free=cfg("FREE_DAILY_LIMIT"), q_test=cfg("TEST_DAILY_LIMIT"), q_gold=cfg("GOLD_DAILY_LIMIT"), q_ultra=cfg("ULTRA_DAILY_LIMIT"),
            c_free=cfg("MAX_CONCURRENT_FREE"), c_test=cfg("MAX_CONCURRENT_TEST"), c_gold=cfg("MAX_CONCURRENT_GOLD"), c_ultra=cfg("MAX_CONCURRENT_ULTRA"),
            cooldown=fmt_config_value("COOLDOWN_NORMAL"), size_n=human_size(cfg("MAX_FILE_SIZE_NORMAL")),
            size_p=human_size(cfg("MAX_FILE_SIZE_PREMIUM")), userbot=onoff(has_userbot()), maint=onoff(cfg("MAINTENANCE")))
    now = datetime.now()
    premium = 0
    for u in db.users.values():
        p = u.get("premium") or {}
        try:
            if p.get("type") != "free" and p.get("expires") and datetime.fromisoformat(p["expires"]) > now:
                premium += 1
        except Exception:
            pass
    active = sum(1 for t in list(tasks.values()) if not t.cancelled)
    return Theme.STATS.format(users=len(db.users), premium=premium,
                              thumbs=sum(1 for u in db.users.values() if u.get("thumb")),
                              banned=len(db.banned), tasks=active, uptime=time_formatter(get_bot_uptime()))

async def stats_view(page="bot"):
    if page not in Theme.STATS_BTNS:
        page = "bot"
    text = await asyncio.to_thread(_stats_page, page)
    b = ButtonMaker()
    for k, v in Theme.STATS_BTNS.items():
        b.ibutton(mark(page == k, v.split(" ", 1)[-1]), f"stats_{k}")
    b.ibutton("◀️", "adm_home", "footer")
    b.ibutton("❌", "close_all", "footer")
    return text, b.build_menu(2)

def plan_text(plan, extra=""):
    lim = plan_limits(plan)
    price = {"free": "Free", "test": cfg('TEST_PRICE'),
             "gold": f"{cfg('GOLD_PRICE')} or ⭐ {cfg('GOLD_STARS_PRICE')} Stars",
             "ultra": f"{cfg('ULTRA_PRICE')} or ⭐ {cfg('ULTRA_STARS_PRICE')} Stars"}[plan]
    duration = {"test": f"• <b>Duration:</b> {cfg('TEST_DURATION_DAYS')} days\n",
                "gold": f"• <b>Duration:</b> {cfg('PREMIUM_DAYS')} days\n",
                "ultra": f"• <b>Duration:</b> {cfg('PREMIUM_DAYS')} days\n"}.get(plan, "")
    return Theme.PLAN.format(title=Theme.PLAN_TITLES[plan], price=price, duration=duration,
                             daily=lim["daily_limit"], size=human_size(lim["max_file_size"]), conc=lim["concurrent"],
                             cooldown=f"{lim['cooldown']} seconds" if lim["cooldown"] else "None", extra=extra,
                             speed="High speed (multi-connection Premium)" if lim["use_dump"] else "Standard")

async def _edit(query, text, kb, toast=None):
    try:
        await query.message.edit_text(text, reply_markup=kb, link_preview_options=LinkPreviewOptions(is_disabled=True))
    except MessageNotModified:
        pass
    try:
        await query.answer(toast or "")
    except Exception:
        pass

async def admin_callback(client, query, uid, data):
    if data == "adm_home":
        return await _edit(query, *admin_panel_view())
    if data.startswith("stats_"):
        text, kb = await stats_view(data[6:])
        return await _edit(query, text, kb)
    if data == "bs_home":
        temp_context.pop(f"input_{uid}", None)
        return await _edit(query, *bset_home_view())
    if data == "bs_vars":
        temp_context.pop(f"input_{uid}", None)
        return await _edit(query, *bset_vars_view(0))
    if data.startswith("bs_g_") and data[5:] in BSET_GROUPED:
        temp_context.pop(f"input_{uid}", None)
        return await _edit(query, *bset_group_view(data[5:]))
    if data.startswith("bs_v_") and data[5:].isdigit():
        temp_context.pop(f"input_{uid}", None)
        return await _edit(query, *bset_vars_view(int(data[5:])))
    if data.startswith("bs_e_") and data[5:] in BOT_CONFIG_SPEC:
        key = data[5:]
        if BOT_CONFIG_SPEC[key][0] != "bool":
            temp_context[f"input_{uid}"] = {"kind": "bot", "key": key, "chat": query.message.chat.id, "mid": query.message.id}
        return await _edit(query, *bset_prompt_view(key))
    if data.startswith("bs_st_") and data[6:] in STYLES:
        set_config("UI_STYLE", data[6:])
        return await _edit(query, *bset_prompt_view("UI_STYLE"),
                           toast=Theme.BSET_SAVED.format(label="UI_STYLE", value=fmt_config_value("UI_STYLE")))
    if data.startswith("bs_set_"):
        key, _, val = data[7:].rpartition("_")
        if key in BOT_CONFIG_SPEC and BOT_CONFIG_SPEC[key][0] == "bool":
            set_config(key, val == "1")
            return await _edit(query, *bset_prompt_view(key),
                               toast=Theme.BSET_SAVED.format(label=key, value=fmt_config_value(key)))
    if data.startswith("bs_def_") and data[7:] in BOT_CONFIG_SPEC:
        key = data[7:]
        temp_context.pop(f"input_{uid}", None)
        if key == "SESSION_STRING":
            err = await apply_userbot(BOT_CONFIG_DEFAULTS[key])
            if err:
                return await query.answer(err, show_alert=True)
        set_config(key, BOT_CONFIG_DEFAULTS[key])
        return await _edit(query, *bset_vars_view(bset_page_of(key)),
                           toast=Theme.BSET_SAVED.format(label=key, value=fmt_config_value(key)))
    if data in ("bs_tg_MAINTENANCE", "bs_tg_MAINTENANCE_A"):
        set_config("MAINTENANCE", not cfg("MAINTENANCE"))
        view = admin_panel_view() if data.endswith("_A") else bset_home_view()
        return await _edit(query, *view, toast=f"Maintenance {'Enabled' if cfg('MAINTENANCE') else 'Disabled'}")
    if data == "bs_reset":
        b = ButtonMaker()
        b.ibutton(Theme.BSET_BTNS["yes"], "bs_resetyes")
        b.ibutton("◀️", "bs_home", "footer")
        b.ibutton("❌", "close_all", "footer")
        return await _edit(query, Theme.BSET_RESET_CONFIRM, b.build_menu(1))
    if data == "bs_resetyes":
        reset_config()
        return await _edit(query, *bset_home_view(), toast=Theme.BSET_RESET_DONE)
    await query.answer("Unknown action")

@bot.on_message(filters.command(["settings", "usetting", "us"]))
async def settings_command(client, message):
    uid = str(message.from_user.id)
    temp_context.pop(f"input_{uid}", None)
    text, kb = uset_view(uid, message.from_user, get_user_config(uid), "home")
    await message.reply_text(text, reply_markup=kb, link_preview_options=LinkPreviewOptions(is_disabled=True))

@bot.on_message(filters.command(["maintenance", "maint"]) & filters.user(ADMIN_ID))
async def maintenance_command(client, message):
    """/maintenance on [message] | off | (no args = status)"""
    args = message.command[1:]
    if args and args[0].lower() in ("on", "off"):
        on = args[0].lower() == "on"
        set_config("MAINTENANCE", on)
        if on and len(args) > 1:
            set_config("MAINTENANCE_MSG", message.text.split(None, 2)[2])
        elif not on:
            set_config("MAINTENANCE_MSG", "")
    note = cfg("MAINTENANCE_MSG")
    await message.reply_text(f"<b>Maintenance:</b> {'Enabled' if cfg('MAINTENANCE') else 'Disabled'}"
                             + (f"\n<code>{esc(note)}</code>" if note else "")
                             + "\n\n<code>/maintenance on [message]</code> · <code>/maintenance off</code>")

@bot.on_message(filters.command(["bsetting", "bsettings", "bs"]) & filters.user(ADMIN_ID))
async def bsetting_command(client, message):
    temp_context.pop(f"input_{message.from_user.id}", None)
    text, kb = bset_home_view()
    await message.reply_text(text, reply_markup=kb)

@bot.on_message(filters.private & filters.text & filters.create(
    lambda _, __, m: bool(m.from_user and temp_context.get(f"input_{m.from_user.id}"))), group=-1)
async def settings_input(client, message):
    uid = str(message.from_user.id)
    st = temp_context.get(f"input_{uid}")
    if not st or message.text.startswith("/"):
        temp_context.pop(f"input_{uid}", None)
        return
    try:
        await message.delete()
    except Exception:
        pass
    key = st["key"]
    if st["kind"] == "bot":
        if not _is_admin(uid):
            temp_context.pop(f"input_{uid}", None)
            raise StopPropagation
        try:
            val = parse_config_value(key, message.text)
            if key == "SESSION_STRING":
                err = await apply_userbot(val)
                if err:
                    raise ValueError(err)
        except ValueError as e:
            text, kb = bset_prompt_view(key, error=str(e))
        else:
            set_config(key, val)
            temp_context.pop(f"input_{uid}", None)
            text, kb = bset_vars_view(bset_page_of(key))
    else:
        config = get_user_config(uid)
        try:
            val = validate_user_value(key, message.text)
        except ValueError as e:
            text, kb = uset_prompt_view(key, config, error=str(e))
        else:
            config[key] = val
            _run(_save_user(uid))
            temp_context.pop(f"input_{uid}", None)
            text, kb = uset_view(uid, message.from_user, config, USET_INPUT_PARENT[key])
            text = f"<b>{Theme.USET_SAVED.format(label=Theme.USET_LABELS[key])}</b>\n\n" + text
    try:
        await client.edit_message_text(st["chat"], st["mid"], text, reply_markup=kb, link_preview_options=LinkPreviewOptions(is_disabled=True))
    except MessageNotModified:
        pass
    except Exception:
        m = await client.send_message(message.chat.id, text, reply_markup=kb, link_preview_options=LinkPreviewOptions(is_disabled=True))
        st["mid"] = m.id
    raise StopPropagation

@bot.on_message(filters.create(lambda _, __, m: bool(
    m.from_user and not getattr(m, "successful_payment", None) and in_maintenance(m.from_user.id))), group=-2)
async def maintenance_message_gate(client, message):
    if message.chat and message.chat.type == enums.ChatType.PRIVATE:
        try:
            await message.reply_text(maintenance_text())
        except Exception:
            pass
    raise StopPropagation

@bot.on_callback_query(filters.create(lambda _, __, q: bool(q.from_user and in_maintenance(q.from_user.id))), group=-2)
async def maintenance_callback_gate(client, query):
    try:
        await query.answer(Theme.MAINTENANCE_ALERT, show_alert=True)
    except Exception:
        pass
    raise StopPropagation

async def show_help_menu(client, message_or_query, user_id):
    H = Theme.HELP_BTNS
    b = ButtonMaker()
    for k, d in (("thumb", "help_thumb"), ("cap", "help_cap"), ("redeem", "help_redeem"), ("cmds", "help_commands"), ("settings", "ui_settings")):
        b.ibutton(H[k], d)
    b.ibutton("◀️", "ui_home", "footer")
    b.ibutton("❌", "close_all", "footer")
    kb = b.build_menu(2)
    if isinstance(message_or_query, Message):
        await message_or_query.reply_text(Theme.HELP_HEADER, reply_markup=kb)
    else:
        await message_or_query.message.edit_text(Theme.HELP_HEADER, reply_markup=kb)

@bot.on_message(filters.command(["status", "s"]))
async def status_command(client, message):
    uid = message.from_user.id
    
    async with tasks_lock:
        user_task_ids = user_tasks.get(uid, [])
        active_tasks = [tasks[tid] for tid in user_task_ids if tid in tasks and not tasks[tid].cancelled]
    
    try:
        await message.delete()
    except:
        pass

    if not active_tasks:
        msg = await client.send_message(message.chat.id, Theme.NO_ACTIVE.format(footer=await get_server_status_mini_text()))
        await asyncio.sleep(3)
        await msg.delete()
        return
    
    old_status = user_status_msg.pop(uid, None)
    if old_status:
        try:
            await old_status.delete()
        except:
            pass
    
    user_pages[uid] = 0
    combined, total_pages, current_page = await build_combined_status(uid, 0)
    
    if not combined:
        return
    
    nav_buttons = []
    async with tasks_lock:
        for task in active_tasks:
            nav_buttons.append(InlineKeyboardButton(f"✘ {task.position} ✘", callback_data=f"cancel_pos_{uid}_{task.position}", style=enums.ButtonStyle.DANGER))
    
    nav_row = []
    if total_pages > 1:
        nav_row.append(InlineKeyboardButton("⫷", callback_data=f"page_{uid}_{(current_page - 1) % total_pages}", style=enums.ButtonStyle.PRIMARY))
        nav_row.append(InlineKeyboardButton(f"⌬ ᴘᴀɢᴇs {current_page + 1}/{total_pages}", callback_data=f"refresh_{uid}", style=enums.ButtonStyle.PRIMARY))
        nav_row.append(InlineKeyboardButton("⫸", callback_data=f"page_{uid}_{(current_page + 1) % total_pages}", style=enums.ButtonStyle.PRIMARY))
    else:
        nav_row.append(InlineKeyboardButton("⟳ ʀᴇꜰʀᴇsʜ", callback_data=f"refresh_{uid}", style=enums.ButtonStyle.PRIMARY))
    
    buttons = []
    if cfg("RICH_MESSAGES"):
        nav_buttons = []
    
    if nav_buttons:
        for i in range(0, len(nav_buttons), 5):
            buttons.append(nav_buttons[i:i+5])
    
    buttons.append(nav_row)
    
    new_status = None
    if cfg("RICH_MESSAGES"):
        try:
            new_status = await client.send_rich_message(message.chat.id, InputRichMessage(html=rich_status_html(combined)), reply_markup=InlineKeyboardMarkup(buttons))
            new_status._rich = True
        except Exception as e:
            logger.warning(f"rich status failed, plain text: {e}")
    if new_status is None:
        new_status = await client.send_message(message.chat.id, combined, reply_markup=InlineKeyboardMarkup(buttons))
    user_status_msg[uid] = new_status

cancel_pending = {}

async def ask_cancel(client, query, task):
    """Turn the status message itself into a Yes/No question (an edit, no new message); back to the status after 30s."""
    uid = task.user_id
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("✓ Yes, Cancel", callback_data=f"cxyes_{task.gid}", style=enums.ButtonStyle.DANGER),
        InlineKeyboardButton("✘ No", callback_data=f"cxno_{task.gid}", style=enums.ButtonStyle.PRIMARY),
    ]])
    until = time.time() + 30
    cancel_pending[uid] = until
    name = esc(task.filename)
    try:
        await query.message.edit_text(rich_message=InputRichMessage(html=f"<b>Cancel this task?</b><br><code>{name}</code>"), reply_markup=kb)
    except Exception:
        await query.message.edit_text(f"<b>Cancel this task?</b>\n<code>{name}</code>", reply_markup=kb)
    await query.answer()
    async def _expire():
        await asyncio.sleep(30)
        if cancel_pending.get(uid) == until:
            cancel_pending.pop(uid, None)
            await update_user_status(uid)
    asyncio.create_task(_expire())

async def find_task_by_gid(gid):
    async with tasks_lock:
        for task in tasks.values():
            if task.gid == gid and not task.cancelled:
                return task
    return None


async def cancel_task_by_position(user_id, position):
    found_task = None
    async with tasks_lock:
        user_task_ids = user_tasks.get(user_id, [])
        active_tasks = [tasks[tid] for tid in user_task_ids if tid in tasks and not tasks[tid].cancelled]
        for idx, task in enumerate(active_tasks, 1):
            task.position = idx
        for task in active_tasks:
            if task.position == position:
                found_task = task
                break
    
    if not found_task:
        return False, None
    
    filename = found_task.filename
    found_task.cancel_event.set()
    found_task.cancelled = True
    
    if found_task.download_task and not found_task.download_task.done():
        found_task.download_task.cancel()
    if found_task.upload_task and not found_task.upload_task.done():
        found_task.upload_task.cancel()
    
    task_dir = os.path.join(DOWNLOAD_LOCATION, found_task.task_id)
    if os.path.exists(task_dir):
        try:
            shutil.rmtree(task_dir)
        except:
            pass
    
    async with tasks_lock:
        if user_id in user_tasks and found_task.task_id in user_tasks[user_id]:
            user_tasks[user_id].remove(found_task.task_id)
        if found_task.task_id in tasks:
            del tasks[found_task.task_id]
    
    return True, filename

@bot.on_message(filters.command(["cancel", "cn"]) | filters.regex(r"^/cancel_[a-z0-9]{8}(@\w+)?$"))
async def cancel_command(client, message):
    parts = message.text.split()
    gm = re.match(r"^/cancel_([a-z0-9]{8})(?:@\w+)?$", parts[0]) if parts else None
    gid = gm.group(1) if gm else (parts[1].strip().lower() if len(parts) == 2 and re.fullmatch(r"[a-z0-9]{8}", parts[1].strip().lower()) and not parts[1].strip().isdigit() else None)
    if gid:
        task = await find_task_by_gid(gid)
        if not task or (task.user_id != message.from_user.id and message.from_user.id != ADMIN_ID):
            msg = await message.reply_text("❌ Task not found")
            await asyncio.sleep(3)
            for x in (message, msg):
                try:
                    await x.delete()
                except Exception:
                    pass
            return
        task_pos = task.position or 1
        ok, filename = await cancel_task_by_position(task.user_id, task_pos)
        if ok:
            await update_user_status(task.user_id)
        try:
            await message.delete()
        except Exception:
            pass
        return
    if len(parts) != 2:
        msg = await message.reply_text("Usage: <code>/cancel_xxxxxxxx</code> (the id shown under your task)")
        await asyncio.sleep(3)
        await message.delete()
        await msg.delete()
        return
    
    try:
        position = int(parts[1].strip())
    except ValueError:
        msg = await message.reply_text("❌ Please provide a valid task number")
        await asyncio.sleep(3)
        await message.delete()
        await msg.delete()
        return
    
    user_id = message.from_user.id
    
    success, filename = await cancel_task_by_position(user_id, position)
    
    if not success:
        msg = await message.reply_text(f"❌ Task #{position} not found")
        await asyncio.sleep(3)
        await message.delete()
        await msg.delete()
        return
    
    await update_user_status(user_id)
    
    confirm_msg = await message.reply_text(f"❌ <b>Cancelled task #{position}</b>\n<i>{filename[:50]}</i>")
    await asyncio.sleep(3)
    await message.delete()
    await confirm_msg.delete()

@bot.on_message(filters.command(["cancelall", "ca"]) & filters.user(ADMIN_ID))
async def cancel_all_command(client, message):
    async with tasks_lock:
        for task_id, task in list(tasks.items()):
            task.cancel_event.set()
            task.cancelled = True
            
            if task.download_task and not task.download_task.done():
                task.download_task.cancel()
            if task.upload_task and not task.upload_task.done():
                task.upload_task.cancel()
        
        for status_msg in list(user_status_msg.values()):
            try:
                await status_msg.delete()
            except:
                pass
        
        tasks.clear()
        user_tasks.clear()
        user_pages.clear()
        user_status_msg.clear()
    
    confirm_msg = await message.reply_text("✅ All tasks cancelled")
    await asyncio.sleep(3)
    await message.delete()
    await confirm_msg.delete()

@bot.on_callback_query()
async def callback_manager(client, query: CallbackQuery):
    data = query.data
    uid = str(query.from_user.id)
    
    try:
        config = get_user_config(uid)

        if data.startswith("pt:"):
            await poster_callback(client, query, data)
            return

        if data.startswith(("bs_", "adm_", "stats_")):
            if not _is_admin(uid):
                await query.answer(Theme.ADMIN_ONLY, show_alert=True)
                return
            await admin_callback(client, query, uid, data)
            return
        
        if data.startswith("cancel_pos_"):
            parts = data.split("_")
            if len(parts) >= 4:
                target_uid = int(parts[2])
                position = int(parts[3])
                if query.from_user.id != target_uid and query.from_user.id != ADMIN_ID:
                    await query.answer("Not your task!", show_alert=True)
                    return
                t = next((x for x in (tasks.get(i) for i in user_tasks.get(target_uid, [])) if x and x.position == position and not x.cancelled), None)
                if not t:
                    await query.answer("Task not found", show_alert=True)
                    return
                await ask_cancel(client, query, t)
            return

        elif data == "fsub_chk":
            if await fsub_missing(query.from_user.id):
                await query.answer("You still haven't joined", show_alert=True)
            else:
                await query.answer("All set!")
                await query.message.edit_text("<b>✓ All set!</b> Send the file again.")
            return

        elif data.startswith("cxask_"):
            t = await find_task_by_gid(data[6:])
            if not t:
                await query.answer("Task not found", show_alert=True)
            elif query.from_user.id not in (t.user_id, ADMIN_ID):
                await query.answer("That's not yours", show_alert=True)
            else:
                await ask_cancel(client, query, t)
            return

        elif data.startswith(("cxyes_", "cxno_")):
            act, gid = data.split("_", 1)
            t = await find_task_by_gid(gid)
            if t and query.from_user.id not in (t.user_id, ADMIN_ID):
                await query.answer("That's not yours", show_alert=True)
                return
            uid_t = t.user_id if t else query.from_user.id
            cancel_pending.pop(uid_t, None)
            if act == "cxyes" and t:
                ok, _fn = await cancel_task_by_position(t.user_id, t.position or 1)
                await query.answer("Task cancelled" if ok else "Task not found")
            else:
                await query.answer()
            await update_user_status(uid_t)
            return

        elif data.startswith("page_"):
            parts = data.split("_")
            if len(parts) >= 3:
                target_uid = int(parts[1])
                new_page = int(parts[2])
                if query.from_user.id != target_uid and query.from_user.id != ADMIN_ID:
                    await query.answer("Not your tasks!", show_alert=True)
                    return
                user_pages[target_uid] = new_page
                await update_user_status(target_uid)
                await query.answer()
            return
        
        elif data == "ui_home":
            temp_context.pop(f"input_{uid}", None)
            text = Theme.START.format(name=esc(query.from_user.first_name), dev_link=dev_link(), dev_name=cfg('DEVELOPER_NAME'))
            await query.message.edit_text(text, reply_markup=get_main_btns(), link_preview_options=LinkPreviewOptions(is_disabled=True))
        
        elif data in ("ui_plans", "refresh_stats"):
            await _edit(query, get_user_stats_text(uid), plans_kb(), toast="Refreshed" if data == "refresh_stats" else None)

        elif data == "show_free":
            await _edit(query, plan_text("free"), back_plans_kb())

        elif data == "show_test":
            if not can_buy_test(uid) and not _is_admin(uid):
                await _edit(query, plan_text("test", Theme.PLAN_TEST_ONCE), back_plans_kb())
            else:
                await _edit(query, plan_text("test", Theme.PLAN_TEST_FREE),
                            back_plans_kb([(Theme.PLAN_BTNS["get_test"], "get_test", None)]))

        elif data in ("show_gold", "show_ultra"):
            plan = data[5:]
            stars = cfg('GOLD_STARS_PRICE') if plan == "gold" else cfg('ULTRA_STARS_PRICE')
            await _edit(query, plan_text(plan), back_plans_kb([
                (Theme.PLAN_BTNS["buy"].format(stars=stars), f"buy_stars_{plan}", None),
                (Theme.PLAN_BTNS["contact"], None, f"https://t.me/{cfg('DEVELOPER_USERNAME')}")]))

        elif data in ("buy_stars_gold", "buy_stars_ultra"):
            plan = "gold" if data == "buy_stars_gold" else "ultra"
            stars = cfg('GOLD_STARS_PRICE') if plan == "gold" else cfg('ULTRA_STARS_PRICE')
            plan_label = "🥇 Gold" if plan == "gold" else "👑 Ultra"
            title = f"{plan_label} Plan - {cfg('PREMIUM_DAYS')} Days"
            description = f"Unlock the {plan.upper()} plan for {cfg('PREMIUM_DAYS')} days of premium access."
            try:
                await client.send_invoice(
                    chat_id=query.message.chat.id,
                    title=title,
                    description=description,
                    payload=f"plan_{plan}_{cfg('PREMIUM_DAYS')}d_{uid}",
                    currency="XTR",
                    prices=[LabeledPrice(label=title, amount=stars)],
                    provider_token=""
                )
                await query.answer()
            except Exception as e:
                logger.error(f"Error sending Stars invoice: {e}", exc_info=True)
                await query.answer("❌ Failed to create invoice. Try again later.", show_alert=True)
        
        elif data == "get_test":
            if not can_buy_test(uid) and int(uid) != ADMIN_ID:
                await query.answer("You already used your free test plan!", show_alert=True)
                return
            
            add_premium(uid, "test", f"{cfg('TEST_DURATION_DAYS')}d")
            mark_test_bought(uid)
            
            config = get_user_config(uid)
            expires = datetime.fromisoformat(config["premium"]["expires"])
            
            await query.message.edit_text(Theme.TEST_ACTIVATED.format(date=expires.strftime('%Y-%m-%d')), reply_markup=back_kb("ui_plans"))
        
        elif data == "ui_status":
            await _edit(query, await get_server_status_button_text(), back_kb("ui_home"))

        elif data == "ui_about":
            me = await client.get_me()
            b = ButtonMaker()
            b.ubutton(Theme.ABOUT_SOURCE, "https://github.com/Tj-Bots/TJ-Rename-Bot")
            b.ibutton("◀️", "ui_home", "footer")
            b.ibutton("❌", "close_all", "footer")
            await _edit(query, Theme.ABOUT.format(username=me.username, bot_name=esc(me.first_name), version=esc(VERSION),
                                                  channel=cfg('CHANNEL_LINK'), dev_link=dev_link(), dev_name=cfg('DEVELOPER_NAME')),
                        b.build_menu(1))

        elif data == "ui_help":
            await show_help_menu(client, query, uid)
        
        elif data in ("help_thumb", "help_cap", "help_redeem", "help_commands"):
            text = {"help_thumb": Theme.HELP_THUMB, "help_cap": Theme.HELP_CAP,
                    "help_redeem": Theme.HELP_REDEEM, "help_commands": Theme.HELP_COMMANDS}[data]
            await query.message.edit_text(text, reply_markup=back_kb("ui_help"), link_preview_options=LinkPreviewOptions(is_disabled=True))
        
        elif data in USET_ROUTES:
            temp_context.pop(f"input_{uid}", None)
            await _edit(query, *uset_view(uid, query.from_user, config, USET_ROUTES[data]))

        elif data in ("tg_spoiler", "tg_auto_thumb", "tg_rename", "tg_mediainfo", "tg_autorename", "tg_method"):
            if data == "tg_method":
                config["rename_method"] = "regex" if config.get("rename_method", "auto") == "auto" else "auto"
                _run(_save_user(uid))
                await _edit(query, *uset_view(uid, query.from_user, config, "leech"), toast=f"Method: {config['rename_method'].title()}")
                return
            if data == "tg_rename":
                config["rename"] = "no" if rename_on(config) else "ask"
                on, screen, label = rename_on(config), "leech", "Rename Prompt"
            else:
                key = data[3:]
                config[key] = not config.get(key, False)
                on, screen = config[key], ("universal" if key == "mediainfo" else "leech")
                label = {"spoiler": "Spoiler", "mediainfo": "MediaInfo", "autorename": "AutoRename"}.get(key, "Auto Thumbnail")
            _run(_save_user(uid))
            await _edit(query, *uset_view(uid, query.from_user, config, screen),
                        toast=f"{label} {'Enabled' if on else 'Disabled'}")
            return

        elif data.startswith(("m_", "ss_", "af_", "ab_", "pl_", "pk_", "cf_")) and data.split("_", 1)[1]:
            prefix, val = data.split("_", 1)
            if prefix == "m" and val in Theme.MODE_NAMES:
                config["mode"] = val; screen = "mode"
            elif prefix == "ss" and val.isdigit() and 0 <= int(val) <= 10:
                config["screenshots"] = int(val); screen = "shots"
            elif prefix == "af" and val in Theme.AUDIO_FORMATS:
                config["audio_fmt"] = val; screen = "fmt"
            elif prefix == "ab" and val in Theme.AUDIO_BITRATES:
                config["audio_br"] = val; screen = "br"
            elif prefix == "pl" and val in Theme.POSTER_LANG_OPTS:
                config["poster_lang"] = val; screen = "plang"
            elif prefix == "cf" and (val == "none" or val in Theme.CAP_FONTS):
                config["cap_font"] = "" if val == "none" else val; screen = "capfont"
            elif prefix == "pk" and val in ("p", "b"):
                config["poster_kind"] = val; screen = "pkind"
            else:
                await query.answer("Invalid option")
                return
            _run(_save_user(uid))
            await _edit(query, *uset_view(uid, query.from_user, config, screen), toast="Saved")
            return

        elif data.startswith("us_in_") and data[6:] in USET_INPUT_PARENT:
            key = data[6:]
            temp_context[f"input_{uid}"] = {"kind": "user", "key": key, "chat": query.message.chat.id, "mid": query.message.id}
            await _edit(query, *uset_prompt_view(key, config))

        elif data.startswith("us_rm_") and data[6:] in USET_INPUT_PARENT:
            key = data[6:]
            temp_context.pop(f"input_{uid}", None)
            config[key] = DEFAULT_CAPTION if key == "caption" else (0 if key == "screenshots" else ("" if key != "thumb" else None))
            if key == "thumb":
                config["thumb_src"] = None
            _run(_save_user(uid))
            await _edit(query, *uset_view(uid, query.from_user, config, USET_INPUT_PARENT[key]),
                        toast=Theme.USET_REMOVED.format(label=Theme.USET_LABELS[key]))

        elif data == "us_capreset":
            config["caption"] = DEFAULT_CAPTION
            _run(_save_user(uid))
            await _edit(query, *uset_view(uid, query.from_user, config, "caption"), toast="Caption reset")

        elif data == "us_nameclear":
            for k in ("prefix", "suffix", "remname"):
                config[k] = ""
            _run(_save_user(uid))
            await _edit(query, *uset_view(uid, query.from_user, config, "name"), toast="Cleared")

        elif data == "us_thumbview":
            if config.get("thumb"):
                await client.send_photo(query.message.chat.id, config["thumb"], caption=Theme.USET_THUMB_CAPTION,
                                        reply_markup=close_kb())
                await query.answer()
            else:
                await query.answer("No thumbnail set", show_alert=True)

        elif data == "us_thumbdel":
            config["thumb"] = None
            config["thumb_src"] = None
            _run(_save_user(uid))
            await _edit(query, *uset_view(uid, query.from_user, config, "thumb"), toast="Thumbnail deleted")

        elif data == "us_resetyes":
            fresh = DEFAULT_USER(uid)
            for k in USET_RESET_KEYS:
                config[k] = fresh[k]
            _run(_save_user(uid))
            await _edit(query, *uset_view(uid, query.from_user, config, "home"), toast=Theme.USET_RESET_DONE)

        elif data.startswith("go_"):
            parts = data.split("_")
            if len(parts) < 3:
                await query.answer("Invalid callback data", show_alert=True)
                return
            target = parts[1]
            try:
                mid = int(parts[2])
            except ValueError:
                await query.answer("Invalid message ID", show_alert=True)
                return
            try:
                msg = await client.get_messages(query.message.chat.id, mid)
            except Exception:
                msg = None
            if not msg or not (msg.video or msg.document):
                await query.answer("Original message not found", show_alert=True)
                return
            await start_conversion(client, msg, target, query.message)
        
        elif data.startswith("skp_"):
            parts = data.split("_")
            if len(parts) < 3:
                await query.answer("Invalid callback data", show_alert=True)
                return
            try:
                mid = int(parts[1])
            except ValueError:
                await query.answer("Invalid message ID", show_alert=True)
                return
            target = parts[2]
            try:
                msg = await client.get_messages(query.message.chat.id, mid)
            except Exception:
                msg = None
            if not msg or not (msg.video or msg.document):
                await query.answer("Original message not found", show_alert=True)
                return
            temp_context[f"waiting_{query.from_user.id}"] = False
            await query.message.delete()
            await process_now(client, msg, target, (msg.video or msg.document).file_name or "file")
        
        elif data == "queue_stats":
            async with tasks_lock:
                total = len(tasks)
                downloads = sum(1 for t in tasks.values() if t.stage == "downloading" and not t.cancelled)
                uploads = sum(1 for t in tasks.values() if t.stage == "uploading" and not t.cancelled)
            
            text = (
                f"📊 <b>Task Statistics</b>\n\n"
                f"• Total active: {total}/{MAX_BOT_TASKS}\n"
                f"• Downloads: {downloads}\n"
                f"• Uploads: {uploads}"
            )
            await query.answer(text, show_alert=True)
        
        elif data.startswith("refresh_"):
            user_id = int(data.split("_")[1])
            if user_id != query.from_user.id and query.from_user.id != ADMIN_ID:
                await query.answer("Not your tasks!", show_alert=True)
                return
            
            now = time.time()
            last = last_refresh.get(user_id, 0)
            if now - last < 2:
                await query.answer(f"⏳ Please wait {2 - int(now - last)}s", show_alert=True)
                return
            last_refresh[user_id] = now
            
            async with tasks_lock:
                user_task_ids = user_tasks.get(user_id, [])
                active_tasks = [tasks[tid] for tid in user_task_ids if tid in tasks and not tasks[tid].cancelled]
            
            if not active_tasks:
                try:
                    await query.message.delete()
                except:
                    pass
                user_status_msg.pop(user_id, None)
                await query.answer("No active tasks", show_alert=True)
                return
            
            await update_user_status(user_id)
        
        elif data == "rs_yes":
            if query.from_user.id != ADMIN_ID:
                return await query.answer("Admin only", show_alert=True)
            await query.answer("Restarting...")
            await query.message.edit_text(Theme.RESTARTING)
            await _do_restart(query.message)

        elif data == "rs_no":
            if query.from_user.id != ADMIN_ID:
                return await query.answer("Admin only", show_alert=True)
            await query.answer("Cancelled")
            await query.message.edit_text(Theme.RESTART_CANCELLED)

        elif data == "log_paste":
            if not os.path.exists(LOG_FILE) or os.path.getsize(LOG_FILE) == 0:
                return await query.answer("Log file is empty", show_alert=True)
            await query.answer("Uploading...")
            try:
                with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
                    link = await web_paste(f.read())
            except Exception as e:
                logger.error(f"log paste: {e}")
                link = None
            if not link:
                return await query.answer(Theme.LOG_PASTE_FAIL, show_alert=True)
            text, kb = log_view()
            b = ButtonMaker()
            b.ubutton(Theme.LOG_BTNS["paste"], link, style=enums.ButtonStyle.PRIMARY)
            for row in (kb.inline_keyboard if kb else []):
                for btn_ in row:
                    if btn_.callback_data:
                        b.ibutton(btn_.text, btn_.callback_data,
                                  "footer" if btn_.callback_data in ("adm_home", "close_all") else None)
            try:
                await query.message.edit_text(text, reply_markup=b.build_menu(2))
            except MessageNotModified:
                pass

        elif data == "log_refresh":
            text, kb = log_view()
            try:
                await query.message.edit_text(text, reply_markup=kb)
            except MessageNotModified:
                pass
            await query.answer("Refreshed")

        elif data == "log_file":
            if not os.path.exists(LOG_FILE) or os.path.getsize(LOG_FILE) == 0:
                return await query.answer("Log file is empty", show_alert=True)
            await query.answer("Sending...")
            try:
                await client.send_document(query.message.chat.id, document=LOG_FILE,
                                           file_name="log.txt", reply_parameters=ReplyParameters(message_id=query.message.id))
            except Exception as e:
                logger.error(f"send log file: {e}")

        elif data == "close_all":
            try:
                uid = str(query.from_user.id)
                if f"waiting_{uid}" in temp_context:
                    temp_context[f"waiting_{uid}"] = False
                if f"pending_{uid}" in temp_context:
                    temp_context.pop(f"pending_{uid}", None)
                if f"prompt_{uid}" in temp_context:
                    temp_context.pop(f"prompt_{uid}", None)
                temp_context.pop(f"input_{uid}", None)
                if query.message.reply_to_message:
                    await query.message.reply_to_message.delete()
                await query.message.delete()
            except Exception as e:
                logger.error(f"Error deleting: {e}")
        
        else:
            await query.answer("Unknown action", show_alert=False)
    
    except Exception as e:
        logger.error(f"Error in callback_manager: {e}", exc_info=True)
        await query.answer("An error occurred", show_alert=True)

@bot.on_message(filters.command("gencodes") & filters.user(ADMIN_ID))
async def generate_codes_command(client, message):
    parts = message.text.split()
    if len(parts) < 3:
        await message.reply_text(
            "Usage: <code>/gencodes <count> <duration> [plan]</code>\n"
            "Example: <code>/gencodes 5 30d gold</code>\n"
            "Plan: gold (default) or ultra\n"
            "Duration: 1d, 7d, 2w, 1m, 3m, 1y"
        )
        return
    try:
        count = int(parts[1])
    except ValueError:
        await message.reply_text("❌ Count must be a number.")
        return
    duration_str = parts[2]
    plan = parts[3].lower() if len(parts) > 3 else "gold"
    if plan not in ["gold", "ultra"]:
        await message.reply_text("❌ Plan must be 'gold' or 'ultra'")
        return
    match = re.match(r"^(\d+)([dwm])$", duration_str.lower())
    if not match:
        await message.reply_text("❌ Invalid duration format. Use: 1d, 2w, 3m")
        return
    value = int(match.group(1))
    unit = match.group(2)
    if unit == 'd':
        display = f"{value} day{'s' if value > 1 else ''}"
    elif unit == 'w':
        display = f"{value} week{'s' if value > 1 else ''}"
    else:
        display = f"{value} month{'s' if value > 1 else ''}"
    if count < 1 or count > 100:
        await message.reply_text("❌ Count must be between 1 and 100.")
        return
    codes = generate_redeem_codes(count, duration_str, plan)
    if not codes:
        await message.reply_text("❌ Failed to generate codes.")
        return
    response = f"✅ Generated {count} {plan.upper()} redeem codes ({display}):\n\n"
    for i, code in enumerate(codes, 1):
        response += f"{i}. <code>{code}</code>\n"
    await message.reply_text(response)
    logger.info(f"Admin generated {count} {plan} redeem codes for {display}")

@bot.on_message(filters.command("redeem"))
async def redeem_code_command(client, message):
    user_id = message.from_user.id
    parts = message.text.split()
    if len(parts) != 2:
        await message.reply_text("Usage: <code>/redeem <code></code>")
        return
    code = parts[1].strip().upper()
    code_data = get_redeem_code(code)
    if not code_data:
        await message.reply_text("❌ Code not found.")
        return
    if code_data["used_by"] is not None:
        await message.reply_text("❌ Code already used.")
        return
    plan = code_data["plan"]
    days = code_data["days"]
    result = use_redeem_code(code, user_id)
    if result == "active":
        await message.reply_text("❌ <b>You already have an active premium plan from a redeem code.</b>\nYou can redeem a new code once your current plan expires.")
    elif result is True:
        config = get_user_config(user_id)
        expires = datetime.fromisoformat(config["premium"]["expires"])
        remaining = get_active_redeem_count()
        user_mention = message.from_user.mention
        await client.send_message(
            ADMIN_ID,
            f"🔔 <b>New Redeem Code Used</b>\n\n"
            f"👤 User: {user_mention} (<code>{user_id}</code>)\n"
            f"🔑 Code: <code>{code}</code>\n"
            f"📊 Plan: {plan.upper()}\n"
            f"⏳ Duration: {days} days\n"
            f"📊 Remaining codes: <code>{remaining}</code>"
        )
        await message.reply_text(
            f"✅ <b>Redeem Successful!</b>\n\n"
            f"You now have {plan.upper()} premium for {days} days.\n"
            f"Expires: {expires.strftime('%Y-%m-%d')}"
        )
        logger.info(f"User {user_id} redeemed code {code} for {days} days")
    else:
        await message.reply_text("❌ Error redeeming code. Please try again.")

@bot.on_message(filters.command("redeem_stats") & filters.user(ADMIN_ID))
async def redeem_stats_command(client, message):
    total = len(db.redeem_codes)
    used = sum(1 for code in db.redeem_codes.values() if code["used_by"] is not None)
    available = total - used
    text = (
        f"<b>🎫 Redeem Codes Statistics</b>\n\n"
        f"Total: {total}\n"
        f"Used: {used}\n"
        f"Available: {available}\n\n"
    )
    if available > 0:
        text += "Recent codes:\n"
        count = 0
        for code, data in db.redeem_codes.items():
            if data["used_by"] is None and count < 10:
                days = data["days"]
                plan = data["plan"].upper()
                text += f"• <code>{code}</code> ({plan} - {days} days)\n"
                count += 1
    await message.reply_text(text)

@bot.on_pre_checkout_query()
async def pre_checkout_handler(client, pre_checkout_query: PreCheckoutQuery):
    try:
        await pre_checkout_query.answer(ok=True)
    except Exception as e:
        logger.error(f"Error answering pre_checkout_query: {e}")

@bot.on_message(filters.create(lambda _, __, m: getattr(m, "successful_payment", None) is not None))
async def successful_payment_handler(client, message):
    payment = message.successful_payment
    payload = payment.invoice_payload or ""
    uid = message.from_user.id

    match = re.match(r"^plan_(gold|ultra)_(\d+)d_\d+$", payload)
    if not match:
        logger.error(f"Unrecognized payment payload: {payload}")
        await message.reply_text(
            "⚠️ <b>Payment received but the plan could not be identified.</b>\n"
            "Please contact the admin with your payment details."
        )
        try:
            await client.send_message(
                ADMIN_ID,
                f"⚠️ <b>Unrecognized Stars payment</b>\n"
                f"👤 User: <code>{uid}</code>\n"
                f"💰 Amount: {payment.total_amount} Stars\n"
                f"📦 Payload: <code>{payload}</code>"
            )
        except:
            pass
        return

    plan = match.group(1)
    days = match.group(2)

    add_premium(uid, plan, f"{days}d")

    config = get_user_config(uid)
    expires = datetime.fromisoformat(config["premium"]["expires"])

    await message.reply_text(
        f"✅ <b>Payment Successful!</b>\n\n"
        f"You now have the <b>{plan.upper()}</b> plan for {days} days.\n"
        f"⭐ Paid: {payment.total_amount} Stars\n"
        f"Expires: {expires.strftime('%Y-%m-%d')}\n\n"
        f"Enjoy premium features!"
    )
    logger.info(f"User {uid} purchased {plan} plan for {payment.total_amount} Stars")

    try:
        user_mention = message.from_user.mention
        await client.send_message(
            ADMIN_ID,
            f"⭐ <b>New Stars Payment</b>\n\n"
            f"👤 User: {user_mention} (<code>{uid}</code>)\n"
            f"📊 Plan: {plan.upper()}\n"
            f"⏳ Duration: {days} days\n"
            f"💰 Amount: {payment.total_amount} Stars"
        )
    except:
        pass

@bot.on_message(filters.command(["admin", "ad"]) & filters.user(ADMIN_ID))
async def admin_panel(client, message):
    temp_context.pop(f"input_{message.from_user.id}", None)
    text, kb = admin_panel_view()
    await message.reply_text(text, reply_markup=kb)

@bot.on_message(filters.command("add_plan") & filters.user(ADMIN_ID))
async def add_plan_cmd(client, message):
    args = message.text.split()
    if len(args) < 4:
        return await message.reply_text(
            "Usage: <code>/add_plan [user_id] [test/gold/ultra] [duration]</code>\n"
            "Duration: 1d, 2w, 3m, 1y\n"
            "Example: <code>/add_plan 123456 gold 1m</code>"
        )
    user_id = args[1]
    plan = args[2].lower()
    duration = args[3]
    if plan not in ["test", "gold", "ultra"]:
        return await message.reply_text("❌ Plan must be test, gold, or ultra")
    if not add_premium(user_id, plan, duration):
        return await message.reply_text("❌ Invalid duration format!")
    if plan == "test":
        mark_test_bought(user_id)
    config = get_user_config(user_id)
    expires = datetime.fromisoformat(config["premium"]["expires"])
    await message.reply_text(
        f"✅ <b>Plan added to user <code>{user_id}</code></b>\n"
        f"Plan: {plan.upper()}\n"
        f"Expires: {expires.strftime('%Y-%m-%d %H:%M')}"
    )
    try:
        await client.send_message(
            int(user_id),
            f"✨ <b>Congratulations!</b>\n\n"
            f"You have been granted <b>{plan.upper()} Plan</b> by the admin!\n"
            f"Your plan is active until: {expires.strftime('%Y-%m-%d')}\n\n"
            f"Enjoy the benefits!"
        )
    except:
        pass

@bot.on_message(filters.command("remove_plan") & filters.user(ADMIN_ID))
async def remove_plan_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: <code>/remove_plan [user_id]</code>")
    user_id = message.command[1]
    config = get_user_config(user_id)
    if config["premium"]["type"] == "free":
        return await message.reply_text("❌ User has no active plan.")
    old_plan = config["premium"]["type"]
    config["premium"] = {"type": "free", "expires": None, "daily_conversions": 0, "daily_failed": 0, "last_reset": str(datetime.now().date())}
    _run(_save_user(user_id))
    await message.reply_text(f"✅ Removed {old_plan.upper()} plan from user {user_id}")

@bot.on_message(filters.command("plan_list") & filters.user(ADMIN_ID))
async def plan_list_cmd(client, message):
    test_users = []
    gold_users = []
    ultra_users = []
    for uid, user_data in db.users.items():
        premium_type = check_premium(uid)
        if premium_type == "test":
            test_users.append(uid)
        elif premium_type == "gold":
            gold_users.append(uid)
        elif premium_type == "ultra":
            ultra_users.append(uid)
    text = f"<b>⭐ Active Plans</b>\n\n"
    text += f"<b>🧪 Test ({len(test_users)}):</b>\n"
    for uid in test_users[:20]:
        config = get_user_config(uid)
        expires = datetime.fromisoformat(config["premium"]["expires"])
        remaining = format_remaining_time(expires)
        text += f"• <code>{uid}</code> (expires: {remaining})\n"
    text += f"\n<b>🥇 Gold ({len(gold_users)}):</b>\n"
    for uid in gold_users[:20]:
        config = get_user_config(uid)
        expires = datetime.fromisoformat(config["premium"]["expires"])
        remaining = format_remaining_time(expires)
        text += f"• <code>{uid}</code> (expires: {remaining})\n"
    text += f"\n<b>👑 Ultra ({len(ultra_users)}):</b>\n"
    for uid in ultra_users[:20]:
        config = get_user_config(uid)
        expires = datetime.fromisoformat(config["premium"]["expires"])
        remaining = format_remaining_time(expires)
        text += f"• <code>{uid}</code> (expires: {remaining})\n"
    if len(test_users) > 20 or len(gold_users) > 20 or len(ultra_users) > 20:
        text += "\n... and more"
    await message.reply_text(text)

@bot.on_message(filters.command(["broadcast", "bc"]) & filters.user(ADMIN_ID))
async def broadcast_cmd(client, message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a message to broadcast.")
    is_forward = "-f" in message.text
    mode_label = "📨 Forward" if is_forward else "📋 Copy"
    total_users = len(db.users)
    success, failed = 0, 0
    last_edit = time.time()

    status = await message.reply_text(
        f"<b>📢 Broadcasting...</b>\n\n"
        f"<blockquote>"
        f"🔀 <b>Mode:</b> {mode_label}\n"
        f"👥 <b>Users:</b> 0 / {total_users}\n"
        f"✅ <b>Success:</b> 0\n"
        f"❌ <b>Failed:</b> 0"
        f"</blockquote>"
    )

    for user_id in db.users:
        try:
            if is_forward:
                await message.reply_to_message.forward(int(user_id))
            else:
                await message.reply_to_message.copy(int(user_id))
            success += 1
        except Exception as e:
            logger.error(f"Broadcast failed to {user_id}: {e}")
            failed += 1
        await asyncio.sleep(0.1)

        now = time.time()
        if now - last_edit >= 5:
            last_edit = now
            sent = success + failed
            try:
                await status.edit_text(
                    f"<b>📢 Broadcasting...</b>\n\n"
                    f"<blockquote>"
                    f"🔀 <b>Mode:</b> {mode_label}\n"
                    f"👥 <b>Users:</b> {sent} / {total_users}\n"
                    f"✅ <b>Success:</b> {success}\n"
                    f"❌ <b>Failed:</b> {failed}"
                    f"</blockquote>"
                )
            except (MessageNotModified, FloodWait):
                pass

    await status.edit_text(
        f"<b>📢 Broadcast Finished!</b>\n\n"
        f"<blockquote>"
        f"🔀 <b>Mode:</b> {mode_label}\n"
        f"👥 <b>Total:</b> {total_users}\n"
        f"✅ <b>Success:</b> {success}\n"
        f"❌ <b>Failed:</b> {failed}"
        f"</blockquote>"
    )

async def _do_restart(m):
    logger.info("Restart requested by admin")
    try:
        with open(RESTART_FILE, "w") as f:
            json.dump({"chat": m.chat.id, "mid": m.id}, f)
    except Exception as e:
        logger.warning(f"could not write restart marker: {e}")
    await asyncio.sleep(1.5)
    os.execl(sys.executable, sys.executable, *sys.argv)


@bot.on_message(filters.command(["restart", "r"]) & filters.user(ADMIN_ID))
async def restart_bot(client, message):
    if cfg("RESTART_CONFIRM"):
        b = ButtonMaker()
        b.ibutton(Theme.RESTART_BTNS["yes"], "rs_yes", style=enums.ButtonStyle.DANGER)
        b.ibutton(Theme.RESTART_BTNS["no"], "rs_no")
        return await message.reply_text(Theme.RESTART_CONFIRM, reply_markup=b.build_menu(2))
    m = await message.reply_text(Theme.RESTARTING)
    await _do_restart(m)

@bot.on_message(filters.command("ban") & filters.user(ADMIN_ID))
async def ban_user_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: <code>/ban [id]</code>")
    target = message.command[1]
    if target not in db.banned:
        db.banned.append(target)
        _run(_save_banned(target))
        await message.reply_text(f"🚫 User <code>{target}</code> banned.")
    else:
        await message.reply_text("User already banned.")

@bot.on_message(filters.command("unban") & filters.user(ADMIN_ID))
async def unban_user_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: <code>/unban [id]</code>")
    target = message.command[1]
    if target in db.banned:
        db.banned.remove(target)
        _run(_delete_banned(target))
        await message.reply_text(f"✅ User <code>{target}</code> unbanned.")
    else:
        await message.reply_text("User not banned.")

@bot.on_message(filters.command("users") & filters.user(ADMIN_ID))
async def users_list(client, message):
    users = list(db.users.keys())
    total = len(users)
    if total == 0:
        return await message.reply_text("<b>👥 No users yet.</b>")
    
    text = f"<b>👥 Total users: {total}</b>\n\n"
    
    list_lines = []
    if total <= 50:
        for uid in users:
            list_lines.append(f"<code>{uid}</code>")
    else:
        for uid in users[:50]:
            list_lines.append(f"<code>{uid}</code>")
        list_lines.append(f"... and {total - 50} more users.")
    
    text += "<blockquote expandable>\n" + "\n".join(list_lines) + "\n</blockquote>"
    
    await message.reply_text(text)


@bot.on_message(filters.command("allban") & filters.user(ADMIN_ID))
async def allban_list(client, message):
    banned = db.banned
    total = len(banned)
    if total == 0:
        return await message.reply_text("<b>🔨 No banned users.</b>")
    
    text = f"<b>🔨 Total banned users: {total}</b>\n\n"
    
    list_lines = []
    if total <= 50:
        for uid in banned:
            list_lines.append(f"<code>{uid}</code>")
    else:
        for uid in banned[:50]:
            list_lines.append(f"<code>{uid}</code>")
        list_lines.append(f"... and {total - 50} more banned users.")
    
    text += "<blockquote expandable>\n" + "\n".join(list_lines) + "\n</blockquote>"
    
    await message.reply_text(text)

@bot.on_message(filters.command(["set_caption", "set_cap"]))
async def set_cap_p(client, message):
    if len(message.command) < 2:
        help_text = (
            "📝 <b>HOW TO SET CAPTION</b>\n\n"
            "<b>Usage:</b> <code>/set_cap YOUR_CAPTION_HERE</code>\n\n"
            "<b>Available variables:</b>\n"
            "• <code>{filename}</code> - File name\n"
            "• <code>{filesize}</code> - File size\n"
            "• <code>{title}</code> / <code>{year}</code> - Cleaned title / year from the name\n"
            "• <code>{quality}</code> - 1080P, 720P, 4K...\n"
            "• <code>{duration}</code> - Video length\n"
            "• <code>{ext}</code> - File extension\n\n"
            "<b>Example:</b>\n"
            "<code>/set_cap <b>{filename}</b>\n\n📦 {filesize}</code>\n\n"
            "Use <code>/see_caption</code> to view current caption\n"
            "Use <code>/del_caption</code> to reset to default"
        )
        return await message.reply_text(help_text)
    uid = str(message.from_user.id)
    get_user_config(uid)["caption"] = message.text.split(None, 1)[1]
    _run(_save_user(uid))
    await message.reply_text("✅ <b>Caption Updated!</b>")

@bot.on_message(filters.command(["see_caption", "view_cap", "view_caption"]))
async def view_cap_p(client, message):
    cap = get_user_config(message.from_user.id)['caption']
    text = (
        "📝 <b>Your Current Caption:</b>\n\n"
        f"<code>{cap}</code>\n\n"
        "Use <code>/set_cap</code> to change it"
    )
    await message.reply_text(text)

@bot.on_message(filters.command(["del_caption", "del_cap"]))
async def del_cap_p(client, message):
    uid = str(message.from_user.id)
    get_user_config(uid)["caption"] = "<b><i>{filename}</i>\n\n<blockquote>Size: {filesize}</blockquote></b>"
    _run(_save_user(uid))
    await message.reply_text("🗑 <b>Caption Reset to Default!</b>")

@bot.on_message(filters.photo | (filters.document & filters.create(lambda _, __, m: m.document and m.document.mime_type.startswith("image/"))))
async def save_thumb_p(client, message):
    uid = str(message.from_user.id)
    st = temp_context.get(f"input_{uid}")
    if not st or st.get("key") != "thumb":
        if message.document:
            raise ContinuePropagation
        return
    config = get_user_config(uid)
    config["thumb"] = (message.photo or message.document).file_id
    config["thumb_src"] = None
    _run(_save_user(uid))
    temp_context.pop(f"input_{uid}", None)
    try:
        await message.delete()
    except Exception:
        pass
    text, kb = uset_view(uid, message.from_user, config, "pg_thumb")
    text = f"<b>{Theme.USET_SAVED.format(label='Thumbnail')}</b>\n\n" + text
    try:
        await client.edit_message_text(st["chat"], st["mid"], text, reply_markup=kb,
                                       link_preview_options=LinkPreviewOptions(is_disabled=True))
    except MessageNotModified:
        pass
    except Exception:
        await client.send_message(message.chat.id, text, reply_markup=kb,
                                  link_preview_options=LinkPreviewOptions(is_disabled=True))
    raise StopPropagation

@bot.on_message(filters.command(["viewthumb", "view_thumb"]))
async def view_thumb_p(client, message):
    thumb = get_user_config(message.from_user.id)["thumb"]
    if thumb:
        await message.reply_photo(thumb, caption=Theme.USET_THUMB_CAPTION, 
                                  reply_markup=close_kb())
    else:
        await message.reply_text(Theme.NO_THUMB)

@bot.on_message(filters.command(["delthumb", "del_thumb"]))
async def del_thumb_p(client, message):
    uid = str(message.from_user.id)
    get_user_config(uid)["thumb"] = None
    get_user_config(uid)["thumb_src"] = None
    _run(_save_user(uid))
    await message.reply_text(Theme.THUMB_DELETED)

@bot.on_message(filters.command(["plans", "pl"]))
async def plans_command(client, message):
    uid = str(message.from_user.id)
    await message.reply_text(get_user_stats_text(uid), reply_markup=plans_kb())

MI_SECTIONS = {"General": "🗒", "Video": "🎞", "Audio": "🔊", "Text": "🔠", "Menu": "🗃"}

def _format_mediainfo(raw_out):
    """mediainfo CLI output -> Telegram HTML (sections in bold, body in <pre>)."""
    import html as _html
    blocks, cur = [], None
    for line in raw_out.splitlines():
        s = line.strip()
        if not s:
            continue
        head = next((k for k in MI_SECTIONS if line.startswith(k) and ":" not in line), None)
        if head:
            cur = [f"<b>{MI_SECTIONS[head]} {_html.escape(line.replace('Text', 'Subtitle').strip())}</b>", []]
            blocks.append(cur)
        elif cur is not None:
            if line.startswith(("Complete name", "Folder name")):
                continue
            cur[1].append(_html.escape(line))
    return "\n\n".join(f"{h}\n<pre>{chr(10).join(b)}</pre>" for h, b in blocks)

_TG_TOKEN_FILE = os.path.join(WORKSPACE, "telegraph_token.txt")
_TG_AUTHOR = {}


def _tg_author():
    """Telegraph author = this bot (name + t.me link), filled in at startup."""
    return _TG_AUTHOR.get("name") or "Rename Bot", _TG_AUTHOR.get("url") or dev_link()


def _tg_api(method, payload):
    import json as _json
    data = urllib.parse.urlencode(payload).encode()
    with urllib.request.urlopen(urllib.request.Request(f"https://api.telegra.ph/{method}", data=data), timeout=30) as r:
        res = _json.load(r)
    if not res.get("ok"):
        raise RuntimeError(res.get("error", "telegraph error"))
    return res["result"]

def _tg_token():
    try:
        with open(_TG_TOKEN_FILE) as f:
            t = f.read().strip()
            if t:
                return t
    except OSError:
        pass
    an, au = _tg_author()
    acc = _tg_api("createAccount", {"short_name": "MediaInfo", "author_name": an, "author_url": au})
    with open(_TG_TOKEN_FILE, "w") as f:
        f.write(acc["access_token"])
    os.chmod(_TG_TOKEN_FILE, 0o600)
    return acc["access_token"]

def _mediainfo_nodes(raw_out):
    """mediainfo CLI output -> Telegraph nodes (h4 per section + pre body)."""
    nodes, cur = [], None
    def flush():
        if cur is not None:
            nodes.append({"tag": "h4", "children": [cur[0]]})
            nodes.append({"tag": "pre", "children": ["\n".join(cur[1])]})
    for line in raw_out.splitlines():
        if not line.strip():
            continue
        head = next((k for k in MI_SECTIONS if line.startswith(k) and ":" not in line), None)
        if head:
            flush()
            cur = (f"{MI_SECTIONS[head]} {line.replace('Text', 'Subtitle').strip()}", [])
        elif cur is not None and not line.startswith(("Complete name", "Folder name")):
            cur[1].append(line.rstrip())
    flush()
    return nodes

async def _telegraph_mediainfo(name, raw_out):
    import json as _json
    nodes = _mediainfo_nodes(raw_out)
    if not nodes:
        return None
    nodes.insert(0, {"tag": "h3", "children": [f"📌 {name}"]})
    def _create():
        return _tg_api("createPage", {
            "access_token": _tg_token(), "title": "MediaInfo",
            "author_name": _tg_author()[0], "author_url": _tg_author()[1],
            "content": _json.dumps(nodes, ensure_ascii=False), "return_content": "false",
        })
    page = await asyncio.to_thread(_create)
    return page["url"]

async def _fetch_head(url, dest, max_bytes=15 * 1024 * 1024):
    def _dl():
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Range": f"bytes=0-{max_bytes - 1}"})
        with urllib.request.urlopen(req, timeout=30) as r, open(dest, "wb") as f:
            f.write(r.read(max_bytes))
    await asyncio.to_thread(_dl)

@bot.on_message(filters.command(["mediainfo", "mi"]))
async def mediainfo_command(client, message):
    uid = str(message.from_user.id)
    if uid in db.banned:
        return await message.reply_text("🚫 <b>You are banned from using this bot.</b>")
    r = message.reply_to_message
    link = None
    if len(message.command) > 1 and message.command[1].startswith(("http://", "https://")):
        link = message.command[1]
    elif r and r.text and r.text.strip().startswith(("http://", "https://")):
        link = r.text.strip().split()[0]
    media = None
    if r:
        media = next((m for m in (r.video, r.document, r.audio, r.voice, r.animation, r.video_note) if m), None)
    if not link and not media:
        return await message.reply_text(Theme.MEDIAINFO_HELP)

    status = await message.reply_text("<i>🔎 Generating MediaInfo...</i>")
    tmp_dir = os.path.join(DOWNLOAD_LOCATION, f"mi_{uid}_{int(time.time())}")
    os.makedirs(tmp_dir, exist_ok=True)
    try:
        if link:
            name = os.path.basename(link.split("?")[0]) or "file"
            dest = os.path.join(tmp_dir, name)
            await _fetch_head(link, dest)
        else:
            name = getattr(media, "file_name", None) or f"media_{media.file_unique_id}"
            dest = os.path.join(tmp_dir, name)
            if media.file_size and media.file_size <= 50 * 1024 * 1024:
                await client.download_media(r, file_name=dest)
            else:
                with open(dest, "wb") as f:
                    async for chunk in client.stream_media(r, limit=10):
                        f.write(chunk)
        proc = await asyncio.create_subprocess_exec(
            "mediainfo", dest, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
        out, _ = await asyncio.wait_for(proc.communicate(), timeout=60)
        body = _format_mediainfo(out.decode("utf-8", "ignore"))
        if not body:
            return await status.edit_text("❌ <b>Could not read media info.</b>")
        import html as _html
        try:
            tg_url = await _telegraph_mediainfo(name, out.decode("utf-8", "ignore"))
        except Exception as e:
            logger.warning(f"Telegraph mediainfo failed, using inline fallback: {e}")
            tg_url = None
        if tg_url:
            return await status.edit_text(
                Theme.MEDIAINFO_DONE.format(name=_html.escape(name), url=tg_url),
                reply_markup=menu([[("🔗 View MediaInfo", None, {"url": tg_url})]]),
                link_preview_options=LinkPreviewOptions(is_disabled=False),
            )
        title = f"📌 <b>{_html.escape(name)}</b>\n\n"
        if len(title) + len(body) <= 3900:
            await status.edit_text(title + body)
        else:
            txt = os.path.join(tmp_dir, "mediainfo.txt")
            with open(txt, "w", encoding="utf-8") as f:
                f.write(out.decode("utf-8", "ignore"))
            await message.reply_document(txt, caption=title.strip(), file_name="mediainfo.txt")
            await status.delete()
    except Exception as e:
        logger.error(f"mediainfo failed: {e}", exc_info=True)
        try:
            await status.edit_text(f"❌ <b>MediaInfo failed:</b> <code>{str(e)[:200]}</code>")
        except Exception:
            pass
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@bot.on_message(filters.command(["cover", "c"]))
async def cover_command(client, message):
    uid = str(message.from_user.id)
    config = get_user_config(uid)
    if uid in db.banned:
        return await message.reply_text("🚫 <b>You are banned from using this bot.</b>")
    r = message.reply_to_message
    media = r.video if r else None
    if not media:
        return await message.reply_text(Theme.COVER_HELP)
    if not config.get("thumb") and not (config.get("auto_thumb") and tmdb_mod.TMDB_KEY):
        return await message.reply_text(Theme.COVER_NEED_THUMB)

    status = await message.reply_text("<i>🖼 Adding cover...</i>")
    tmp_dir = os.path.join(DOWNLOAD_LOCATION, f"cover_{uid}_{int(time.time())}")
    os.makedirs(tmp_dir, exist_ok=True)
    try:
        cover_path = os.path.join(tmp_dir, "cover.jpg")
        if config.get("thumb"):
            cover_path = await client.download_media(config["thumb"], file_name=cover_path)
        else:
            cover_path = await tmdb_mod.get_auto_cover(media.file_name or r.caption or "", cover_path)
        if not cover_path:
            return await status.edit_text(Theme.COVER_NOT_FOUND)
        fname = media.file_name or "video.mp4"
        try:
            cap = apply_cap_font(render_caption(config["caption"], fname, media.file_size, media.duration or 0), config)
        except Exception:
            cap = f"<b>{fname}</b>"
        await client.send_video(
            message.chat.id, video=media.file_id, caption=cap, video_cover=cover_path,
            duration=media.duration or 0, width=media.width or 0, height=media.height or 0,
            supports_streaming=True, has_spoiler=bool(config.get("spoiler")),
            reply_parameters=ReplyParameters(message_id=r.id),
        )
        await status.delete()
    except Exception as e:
        logger.error(f"cover failed: {e}", exc_info=True)
        try:
            await status.edit_text(f"❌ <b>Cover failed:</b> <code>{str(e)[:200]}</code>")
        except Exception:
            pass
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

POSTER_TTL = 1800
POSTER_PER_PAGE = 8
POSTER_MAX_PER_USER = 5
poster_cache = {}

def _poster_gc():
    now = time.time()
    for k in [k for k, v in poster_cache.items() if now - v["ts"] > POSTER_TTL]:
        poster_cache.pop(k, None)

def poster_new(uid, query, results, lang="all", kind="p"):
    _poster_gc()
    mine = sorted((v["ts"], k) for k, v in poster_cache.items() if v["uid"] == uid)
    for _, k in mine[:max(0, len(mine) - POSTER_MAX_PER_USER + 1)]:
        poster_cache.pop(k, None)
    sid = "".join(random.choices(string.ascii_letters + string.digits, k=6))
    while sid in poster_cache:
        sid = "".join(random.choices(string.ascii_letters + string.digits, k=6))
    poster_cache[sid] = {"uid": uid, "ts": time.time(), "query": query, "results": results, "page": 0,
                         "sel": None, "imgs": {}, "kind": kind, "idx": 0, "lang": lang, "def_lang": lang,
                         "lock": asyncio.Lock(), "ulang": None, "cmd": None}
    return sid

def _poster_lang(code):
    if not code:
        return Theme.POSTER_NO_TEXT
    return LANG_NAMES.get(code, code.upper())

def _lang_key(code):
    return code or "xx"

def poster_filtered(st):
    """Images of the selected title for the current kind + language filter."""
    r = st["results"][st["sel"]]
    lst = st["imgs"][(r["kind"], r["id"])][st["kind"]]
    lang = st["lang"]
    if lang == "all":
        return lst
    return [im for im in lst if _lang_key(im["lang"]) == lang]

def poster_lang_counts(st):
    r = st["results"][st["sel"]]
    lst = st["imgs"][(r["kind"], r["id"])][st["kind"]]
    counts = {}
    for im in lst:
        k = _lang_key(im["lang"])
        counts[k] = counts.get(k, 0) + 1
    ul = st.get("ulang") or "en"
    return sorted(counts.items(), key=lambda kv: (kv[0] != "en", kv[0] != ul, kv[0] != "xx", -kv[1]))

def _resolve_lang(st, wanted):
    """User default (all / en / ul / xx / orig) -> an available language code, else 'all'."""
    r = st["results"][st["sel"]]
    if wanted == "ul":
        wanted = st.get("ulang") or "en"
    if wanted == "orig":
        wanted = r.get("lang") or "all"
    if wanted == "all":
        return "all"
    have = dict(poster_lang_counts(st))
    return wanted if have.get(wanted) else "all"

def poster_results_view(sid):
    st = poster_cache[sid]
    res = st["results"]
    pages = max(1, math.ceil(len(res) / POSTER_PER_PAGE))
    page = st["page"] % pages
    st["page"] = page
    start = page * POSTER_PER_PAGE
    b = ButtonMaker()
    for i, r in enumerate(res[start:start + POSTER_PER_PAGE], start=start):
        b.ibutton(Theme.POSTER_ITEM.format(title=short(r["title"], 48), year=r["year"] or "????"), f"pt:{sid}:o:{i}",
                  style=enums.ButtonStyle.PRIMARY)
    for t, d in pager(f"pt:{sid}:r:", page, pages):
        b.ibutton(t, d, "l_body", style=enums.ButtonStyle.PRIMARY)
    b.ibutton("❌", f"pt:{sid}:x", "footer")
    text = Theme.POSTER_RESULTS.format(query=esc(short(st["query"], 80)), count=len(res), page=page + 1, pages=pages)
    return text, b.build_menu(1, lb_cols=5)

def poster_image_view(sid, uid_config=None):
    """-> (text, keyboard, image dict, preview url). Text message; image shown as a big link preview ABOVE the text."""
    st = poster_cache[sid]
    r = st["results"][st["sel"]]
    imgs = st["imgs"][(r["kind"], r["id"])]
    k = st["kind"]
    lst = poster_filtered(st)
    n = len(lst)
    i = st["idx"] % n
    st["idx"] = i
    im = lst[i]
    orient = "landscape" if im["w"] >= im["h"] else "portrait"
    url = f"https://www.themoviedb.org/{r['kind']}/{r['id']}"
    text = Theme.POSTER_CAPTION.format(
        title=esc(r["title"]), year=r["year"] or "????", url=url, url_short=f"tmdb.org/{r['kind']}/{r['id']}",
        type=f"{Theme.POSTER_KINDS[k]} · {Theme.POSTER_ORIENT[orient]}", lang=_poster_lang(im["lang"]),
        w=im["w"], h=im["h"], i=i + 1, n=n)
    b = ButtonMaker()
    for kk in ("p", "b"):
        if imgs[kk]:
            b.ibutton(mark(k == kk, f"{Theme.POSTER_KINDS_PL[kk]} ({len(imgs[kk])})"), f"pt:{sid}:k:{kk}", "header")
    counts = poster_lang_counts(st)
    total = sum(c for _, c in counts)
    langs = [("all", total)] + counts
    shown = langs[:4]
    if st["lang"] not in [l for l, _ in shown]:
        shown = shown[:3] + [l for l in langs if l[0] == st["lang"]]
    for code, c in shown:
        label = Theme.POSTER_BT["all"] if code == "all" else (Theme.POSTER_NO_TEXT if code == "xx" else code.upper())
        b.ibutton(mark(st["lang"] == code, f"{label} ({c})"), f"pt:{sid}:l:{code}", "f_body")
    if len(langs) > len(shown):
        b.ibutton(Theme.POSTER_BT["more"], f"pt:{sid}:L", "f_body")
    for t, d in pager(f"pt:{sid}:i:", i, n):
        b.ibutton(t, d, "l_body", style=enums.ButtonStyle.PRIMARY)
    is_thumb = bool(uid_config) and uid_config.get("thumb") and uid_config.get("thumb_src") == im["path"]
    b.ibutton(Theme.POSTER_BT["thumb_on"] if is_thumb else Theme.POSTER_BT["thumb"], f"pt:{sid}:t", "footer",
              style=enums.ButtonStyle.SUCCESS if is_thumb else enums.ButtonStyle.PRIMARY)
    b.ibutton(Theme.POSTER_BT["orig"], f"pt:{sid}:g", "footer", style=enums.ButtonStyle.PRIMARY)
    kb = b.build_menu(1, fb_cols=5, lb_cols=5, f_cols=2)
    kb.inline_keyboard.append([btn("◀️", f"pt:{sid}:b"), btn("❌", f"pt:{sid}:x")])
    return text, kb, im, f"{tmdb_mod.IMG_BASE}original{im['path']}"

def poster_lang_view(sid):
    st = poster_cache[sid]
    r = st["results"][st["sel"]]
    counts = poster_lang_counts(st)
    b = ButtonMaker()
    b.ibutton(mark(st["lang"] == "all", f"{Theme.POSTER_BT['all']} ({sum(c for _, c in counts)})"), f"pt:{sid}:l:all")
    for code, c in counts:
        name = Theme.POSTER_NO_TEXT if code == "xx" else LANG_NAMES.get(code, code.upper())
        b.ibutton(mark(st["lang"] == code, f"{name} ({c})"), f"pt:{sid}:l:{code}")
    b.ibutton("◀️", f"pt:{sid}:v", "footer")
    b.ibutton("❌", f"pt:{sid}:x", "footer")
    return Theme.POSTER_LANG_PICK.format(title=esc(r["title"])), b.build_menu(3)

async def _poster_show(client, query, sid):
    """Edit the message into the poster view: text + large link preview above it (no photo upload)."""
    text, kb, im, url = poster_image_view(sid, get_user_config(query.from_user.id))
    lpo = LinkPreviewOptions(url=url, show_above_text=True, prefer_large_media=True)
    if query.message.photo or query.message.document:
        await client.send_message(query.message.chat.id, text, reply_markup=kb, link_preview_options=lpo)
        try:
            await query.message.delete()
        except Exception:
            pass
        return
    try:
        await query.message.edit_text(text, reply_markup=kb, link_preview_options=lpo)
    except MessageNotModified:
        pass

async def _thumb_from_tmdb(client, path):
    """Upload the TMDB image once to the dump channel to get a reusable photo file_id."""
    data = await tmdb_mod.fetch_image(path, "w780")
    bio = io.BytesIO(data)
    bio.name = "thumb.jpg"
    m = await client.send_photo(cfg('DUMP_CHANNEL'), bio)
    fid = m.photo.file_id
    try:
        await m.delete()
    except Exception:
        pass
    return fid

async def poster_callback(client, query, data):
    parts = data.split(":")
    sid, act, args = parts[1], parts[2], parts[3:]
    st = poster_cache.get(sid)
    if not st or time.time() - st["ts"] > POSTER_TTL:
        poster_cache.pop(sid, None)
        return await query.answer(Theme.POSTER_EXPIRED, show_alert=True)
    if query.from_user.id != st["uid"]:
        return await query.answer(Theme.POSTER_NOT_YOURS, show_alert=True)
    st["ts"] = time.time()
    if act == "n":
        return await query.answer()
    if act == "x":
        poster_cache.pop(sid, None)
        await query.answer()
        try:
            await query.message.delete()
        except Exception:
            pass
        if st.get("cmd"):
            try:
                await client.delete_messages(*st["cmd"])
            except Exception:
                pass
        return
    if st["lock"].locked():
        return await query.answer("⏳")
    async with st["lock"]:
        try:
            if act == "r" and args and args[0].isdigit():
                st["page"] = int(args[0])
                text, kb = poster_results_view(sid)
                try:
                    await query.message.edit_text(text, reply_markup=kb, link_preview_options=LinkPreviewOptions(is_disabled=True))
                except MessageNotModified:
                    pass
                return await query.answer()
            if act == "b":
                text, kb = poster_results_view(sid)
                await query.answer()
                if query.message.photo:
                    await client.send_message(query.message.chat.id, text, reply_markup=kb)
                    try:
                        await query.message.delete()
                    except Exception:
                        pass
                else:
                    await query.message.edit_text(text, reply_markup=kb, link_preview_options=LinkPreviewOptions(is_disabled=True))
                return
            if act == "o" and args and args[0].isdigit() and int(args[0]) < len(st["results"]):
                r = st["results"][int(args[0])]
                key = (r["kind"], r["id"])
                if key not in st["imgs"]:
                    imgs = await tmdb_mod.get_images(r["kind"], r["id"])
                    if imgs is None:
                        return await query.answer(Theme.POSTER_LOAD_FAIL, show_alert=True)
                    st["imgs"][key] = imgs
                imgs = st["imgs"][key]
                if not imgs["p"] and not imgs["b"]:
                    return await query.answer(Theme.POSTER_NO_IMAGES, show_alert=True)
                want = get_user_config(query.from_user.id).get("poster_kind", "p")
                st.update(sel=int(args[0]), kind=want if imgs[want] else ("p" if imgs["p"] else "b"), idx=0)
                st["lang"] = _resolve_lang(st, st["def_lang"])
                await query.answer()
                return await _poster_show(client, query, sid)
            if st["sel"] is None:
                return await query.answer(Theme.POSTER_EXPIRED, show_alert=True)
            r = st["results"][st["sel"]]
            imgs = st["imgs"].get((r["kind"], r["id"]), {})
            if act == "i" and args and args[0].isdigit():
                st["idx"] = int(args[0])
                await query.answer()
                return await _poster_show(client, query, sid)
            if act == "k" and args and args[0] in ("p", "b"):
                if not imgs.get(args[0]):
                    return await query.answer(Theme.POSTER_NO_IMAGES, show_alert=True)
                st.update(kind=args[0], idx=0)
                st["lang"] = _resolve_lang(st, st["lang"])
                await query.answer()
                return await _poster_show(client, query, sid)
            if act == "l" and args:
                code = args[0]
                if code != "all" and code not in dict(poster_lang_counts(st)):
                    return await query.answer(Theme.POSTER_NO_IMAGES, show_alert=True)
                st.update(lang=code, idx=0)
                await query.answer()
                return await _poster_show(client, query, sid)
            if act == "L":
                text, kb = poster_lang_view(sid)
                await query.answer()
                return await query.message.edit_text(text, reply_markup=kb, link_preview_options=LinkPreviewOptions(is_disabled=True))
            if act == "v":
                await query.answer()
                return await _poster_show(client, query, sid)
            if act == "t":
                uid = str(query.from_user.id)
                config = get_user_config(uid)
                _, _, im, _ = poster_image_view(sid, config)
                if config.get("thumb") and config.get("thumb_src") == im["path"]:
                    config["thumb"], config["thumb_src"] = None, None
                    toast = Theme.POSTER_THUMB_REMOVED
                else:
                    config["thumb"] = await _thumb_from_tmdb(client, im["path"])
                    config["thumb_src"] = im["path"]
                    toast = Theme.POSTER_THUMB_SET
                _run(_save_user(uid))
                await query.answer(toast)
                return await _poster_show(client, query, sid)
            if act == "g":
                _, _, im, _ = poster_image_view(sid)
                await query.answer(Theme.POSTER_SENDING)
                data = await tmdb_mod.fetch_image(im["path"], "original")
                bio = io.BytesIO(data)
                safe = re.sub(r"[^\w.-]+", "_", r["title"]).strip("_")[:60] or "poster"
                bio.name = f"{safe}_{r['year'] or 'NA'}_{Theme.POSTER_KINDS[st['kind']]}_{im['w']}x{im['h']}.jpg"
                orient = "landscape" if im["w"] >= im["h"] else "portrait"
                await client.send_document(
                    query.message.chat.id, bio, file_name=bio.name, reply_parameters=ReplyParameters(message_id=query.message.id),
                    caption=Theme.POSTER_ORIG_CAPTION.format(
                        title=esc(r["title"]), year=r["year"] or "????", w=im["w"], h=im["h"], lang=_poster_lang(im["lang"]),
                        type=f"{Theme.POSTER_KINDS[st['kind']]} · {Theme.POSTER_ORIENT[orient]}"))
                return
            await query.answer("Unknown action")
        except Exception as e:
            logger.error(f"poster callback {act} failed: {e!r}")
            try:
                await query.answer(Theme.POSTER_LOAD_FAIL, show_alert=True)
            except Exception:
                pass

@bot.on_message(filters.command(["poster", "p"]))
async def poster_command(client, message):
    uid = str(message.from_user.id)
    if uid in db.banned:
        return await message.reply_text(Theme.BANNED)
    query = " ".join(message.command[1:]).strip()
    r = message.reply_to_message
    if not query and r:
        m = r.video or r.document or r.audio
        query = (getattr(m, "file_name", None) or r.caption or r.text or "") if m or r.text else ""
    if not query:
        return await message.reply_text(Theme.INFO_HELP)
    if not tmdb_mod.TMDB_KEY:
        return await message.reply_text(Theme.POSTER_NO_KEY)
    status = await message.reply_text(Theme.POSTER_SEARCHING.format(query=esc(short(query, 80))))
    results = await tmdb_mod.search_titles(query)
    if results is None:
        return await status.edit_text(Theme.POSTER_SEARCH_FAIL)
    if not results:
        return await status.edit_text(Theme.INFO_NOT_FOUND)
    config = get_user_config(uid)
    sid = poster_new(message.from_user.id, query, results, config.get("poster_lang", "all"), config.get("poster_kind", "p"))
    poster_cache[sid]["ulang"] = ((message.from_user.language_code or "en").split("-")[0]).lower()
    poster_cache[sid]["cmd"] = (message.chat.id, message.id)
    text, kb = poster_results_view(sid)
    await status.edit_text(text, reply_markup=kb, link_preview_options=LinkPreviewOptions(is_disabled=True))

PASTE_API = "https://tjfiles.tjbots.chatgpt.site/api/"


def _paste_upload(content):
    """POST the log to TJ Files paste; returns the link or None. Stdlib only."""
    boundary = "----TjPaste" + uuid.uuid4().hex
    body = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="content"\r\n\r\n'
        f"{content}\r\n--{boundary}--\r\n"
    ).encode("utf-8")
    req = urllib.request.Request(
        PASTE_API, data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) TJ-Rename-Bot",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        res = json.loads(r.read().decode("utf-8", "replace"))
        status = r.status
    pid = (res.get("payload") or {}).get("id")
    if status in (200, 201) and pid:
        return PASTE_API.removesuffix("api/") + str(pid)
    logger.error(f"Web Paste Failed: {status} {res.get('error')}")
    return None


async def web_paste(text):
    """Upload log text, trimming to the newest part when it is too big."""
    for content in (text, text[-1_000_000:], text[-200_000:]):
        try:
            link = await asyncio.to_thread(_paste_upload, content)
            if link:
                return link
        except Exception as e:
            logger.error(f"Web Paste Failed: {e}")
        if len(content) <= 200_000:
            break
    return None


LOG_TAIL_CHARS = 3200


def _read_log_tail():
    if not os.path.exists(LOG_FILE):
        return None
    try:
        with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
    except Exception as e:
        logger.error(f"read log: {e}")
        return None
    body, count = "", 0
    for line in reversed(lines):
        if len(body) + len(line) + 1 > LOG_TAIL_CHARS:
            break
        body = line + "\n" + body
        count += 1
    if not count and lines:
        body, count = lines[-1][-LOG_TAIL_CHARS:], 1
    return body.strip(), count


def log_view():
    data = _read_log_tail()
    if data is None:
        return Theme.LOG_MISSING, close_kb()
    body, count = data
    if not body:
        return Theme.LOG_EMPTY, close_kb()
    b = ButtonMaker()
    b.ibutton(Theme.LOG_BTNS["refresh"], "log_refresh")
    b.ibutton(Theme.LOG_BTNS["file"], "log_file")
    b.ibutton(Theme.LOG_BTNS["paste"], "log_paste")
    b.ibutton("◀️", "adm_home", "footer")
    b.ibutton("❌", "close_all", "footer")
    return Theme.LOG_DISPLAY.format(lines=count, body=esc(body)), b.build_menu(2)


@bot.on_message(filters.command(["log", "logs"]) & filters.user(ADMIN_ID))
async def log_command(client, message):
    text, kb = log_view()
    await message.reply_text(text, reply_markup=kb)


@bot.on_message(filters.command("ping"))
async def ping_command(client, message):
    t0 = time.time()
    m = await message.reply_text(Theme.PING)
    await m.edit_text(Theme.PING_VALUE.format(ms=f"{(time.time() - t0) * 1000:.0f}", uptime=time_formatter(get_bot_uptime())))

@bot.on_message(filters.command(["stats", "st"]) & filters.user(ADMIN_ID))
async def stats_command(client, message):
    text, kb = await stats_view("bot")
    await message.reply_text(text, reply_markup=kb)

SPEED_HOST = "speed.cloudflare.com"
_speed_lock = asyncio.Lock()

def _cf_request(method, path, body=None, timeout=30):
    conn = http.client.HTTPSConnection(SPEED_HOST, timeout=timeout)
    try:
        conn.request(method, path, body=body, headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/octet-stream"})
        r = conn.getresponse()
        data = r.read()
        return r, data
    finally:
        conn.close()

def _run_speedtest(dl_bytes=50 * 1024 * 1024, ul_bytes=15 * 1024 * 1024):
    pings = []
    for _ in range(5):
        t = time.time()
        _cf_request("GET", "/__down?bytes=0", timeout=10)
        pings.append((time.time() - t) * 1000)
    t = time.time()
    _, data = _cf_request("GET", f"/__down?bytes={dl_bytes}", timeout=120)
    dl_time = max(time.time() - t, 1e-3)
    recv = len(data)
    payload = os.urandom(ul_bytes)
    t = time.time()
    _cf_request("POST", "/__up", body=payload, timeout=120)
    ul_time = max(time.time() - t, 1e-3)
    _, trace = _cf_request("GET", "/cdn-cgi/trace", timeout=10)
    meta = dict(line.split("=", 1) for line in trace.decode("utf-8", "ignore").splitlines() if "=" in line)
    return {"ping": min(pings), "dl": recv / dl_time, "ul": ul_bytes / ul_time,
            "sent": ul_bytes, "recv": recv, "colo": meta.get("colo", "?"), "loc": meta.get("loc", "?")}

def speedtest_text(r):
    return Theme.SPEED_RESULT.format(
        up=human_size(r["ul"]), up_mbps=f"{r['ul'] * 8 / 1e6:.2f}",
        dl=human_size(r["dl"]), dl_mbps=f"{r['dl'] * 8 / 1e6:.2f}",
        ping=f"{r['ping']:.1f}", time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        sent=human_size(r["sent"]), recv=human_size(r["recv"]), colo=esc(r["colo"]), loc=esc(r["loc"]))

@bot.on_message(filters.command(["speedtest", "sp"]) & filters.user(ADMIN_ID))
async def speedtest_command(client, message):
    if _speed_lock.locked():
        return await message.reply_text("⏳ <i>A speedtest is already running.</i>")
    m = await message.reply_text(Theme.SPEED_START)
    async with _speed_lock:
        try:
            r = await asyncio.wait_for(asyncio.to_thread(_run_speedtest), timeout=240)
            await m.edit_text(speedtest_text(r))
        except Exception as e:
            logger.error(f"speedtest failed: {e!r}")
            await m.edit_text(Theme.SPEED_FAIL.format(err=esc(str(e)[:200] or type(e).__name__)))

def _shorten_sync(long_url):
    dom, key = str(cfg("SHORTENER") or "").strip(), str(cfg("SHORTENER_API") or "").strip()
    if not dom or not key:
        return long_url
    q = urllib.parse.quote(long_url, safe="")
    if "{api}" in dom or "{url}" in dom:
        api = dom.replace("{api}", key).replace("{url}", q)
    else:
        d = re.sub(r"^https?://", "", dom).rstrip("/")
        api = f"https://{d}/api?api={key}&url={q}"
    try:
        req = urllib.request.Request(api, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read().decode("utf-8", "ignore"))
        for k in ("shortenedUrl", "shorturl", "short", "link", "url"):
            v = data.get(k)
            if isinstance(v, str) and v.startswith("http"):
                return v
    except Exception as e:
        logger.warning(f"shortener failed: {e}")
    return long_url

async def token_gate(message):
    """Free users need a valid access token (opened through the shortener link). True = may continue."""
    uid = message.from_user.id
    if _is_admin(uid) or check_premium(uid) != "free" or not cfg("SHORTENER_ENABLED") or not cfg("SHORTENER"):
        return True
    config = get_user_config(uid)
    tk = config.get("token") or {}
    if tk.get("expires", 0) > time.time():
        return True
    val = uuid.uuid4().hex[:16]
    config["token"] = {"value": val, "expires": 0}
    _run(_save_user(uid))
    me = await bot.get_me()
    link = await asyncio.to_thread(_shorten_sync, f"https://t.me/{me.username}?start=token_{val}")
    hours = max(1, int(cfg("TOKEN_TIMEOUT")) // 3600)
    await message.reply_text(
        f"<b>Access token needed</b>\nOpen the link, finish the short step and come back. The token lasts {hours}h.\n"
        "Premium plans skip this step.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Get Token", url=link, style=enums.ButtonStyle.PRIMARY)]]))
    return False

_fsub_cache = {}

async def fsub_missing(uid):
    """Force-sub channels the user has not joined: [(title, link)]. Channels the bot can't check are skipped."""
    out = []
    for s in str(cfg("FSUB_IDS") or "").split():
        try:
            cid = int(s)
        except ValueError:
            continue
        try:
            await bot.get_chat_member(cid, uid)
            continue
        except Exception as e:
            if "USER_NOT_PARTICIPANT" not in str(e).upper() and type(e).__name__ != "UserNotParticipant":
                logger.warning(f"[FSUB] can't check {cid}: {e}")
                continue
        c = _fsub_cache.get(cid)
        if not c or time.time() - c[2] > 3600:
            try:
                ch = await bot.get_chat(cid)
                link = f"https://t.me/{ch.username}" if ch.username else (ch.invite_link or await bot.export_chat_invite_link(cid))
                c = (ch.title or str(cid), link, time.time())
            except Exception as e:
                logger.warning(f"[FSUB] no link for {cid}: {e}")
                c = (str(cid), None, time.time())
            _fsub_cache[cid] = c
        out.append((c[0], c[1]))
    return out

async def fsub_gate(message):
    """True = the user may continue. Otherwise sends the join message and returns False."""
    uid = message.from_user.id
    if _is_admin(uid) or not str(cfg("FSUB_IDS") or "").strip():
        return True
    miss = await fsub_missing(uid)
    if not miss:
        return True
    rows = [[InlineKeyboardButton(f"Join {ti}", url=li, style=enums.ButtonStyle.PRIMARY)] for ti, li in miss if li]
    rows.append([InlineKeyboardButton("✓ I've joined", callback_data="fsub_chk", style=enums.ButtonStyle.SUCCESS)])
    await message.reply_text("<b>Join our channel first</b>\nYou haven't joined yet. Join, then press <b>I've joined</b> and send the file again.",
                             reply_markup=InlineKeyboardMarkup(rows))
    return False

@bot.on_message(filters.private & (filters.video | filters.document) & ~filters.service)
async def on_file_receive(client, message):
    uid = message.from_user.id
    config = get_user_config(uid)
    
    if str(uid) in db.banned:
        return await message.reply_text("🚫 <b>You are banned from using this bot.</b>")
    if not await fsub_gate(message):
        return
    if not await token_gate(message):
        return
    
    file = message.video or message.document
    if not file:
        return

    file_size = file.file_size
    limits = get_premium_limits(uid)
    is_free = (not _is_admin(uid)) and check_premium(uid) == "free"

    if file_size > limits["max_file_size"]:
        text = f"❌ <b>File too large!</b>\nMax size: {human_size(limits['max_file_size'])}"
        if is_free:
            text += "\n\nUpgrade your plan for larger files!"
        else:
            text += "\n\nUltra plan required for unlimited size."
        btn = [[InlineKeyboardButton("View Plans", callback_data="ui_plans", style=enums.ButtonStyle.PRIMARY)]]
        return await message.reply_text(text, reply_markup=InlineKeyboardMarkup(btn))

    if int(uid) != ADMIN_ID and not check_daily_limit(uid):
        reset_time = get_reset_time()
        time_to_reset = reset_time - datetime.now()
        reset_formatted = format_timedelta(time_to_reset)
        text = f"❌ <b>Daily limit reached!</b>\nReset in: <code>{reset_formatted}</code>"
        if is_free:
            text += "\nUpgrade your plan for higher limits!"
        else:
            text += "\nUltra plan required for more conversions."
        btn = [[InlineKeyboardButton("View Plans", callback_data="ui_plans", style=enums.ButtonStyle.PRIMARY)]]
        return await message.reply_text(text, reply_markup=InlineKeyboardMarkup(btn))

    async with tasks_lock:
        active_count = len([
            tid for tid in user_tasks.get(uid, [])
            if tid in tasks and not tasks[tid].cancelled
        ])

    if active_count >= limits["concurrent"]:
        btns = None
        if is_free:
            text = (
                f"⚠️ <b>You already have {active_count}/{limits['concurrent']} active task(s)!</b>\n"
                f"Free users are limited to {limits['concurrent']} conversion(s) at a time.\n\n"
                "Upgrade your plan to convert more files simultaneously!"
            )
            btns = InlineKeyboardMarkup([[InlineKeyboardButton("Upgrade Plan", callback_data="ui_plans", style=enums.ButtonStyle.PRIMARY)]])
        else:
            text = (
                f"⚠️ <b>You already have {active_count}/{limits['concurrent']} active tasks!</b>\n"
                "Please wait for one to finish or cancel one."
            )
        return await message.reply_text(text, reply_markup=btns)
        
        
    if is_free and limits["cooldown"] > 0:
        if uid in user_cooldowns:
            rem = user_cooldowns[uid] - time.time()
            if rem > 0:
                return await message.reply_text(
                    f"⏳ <b>Cooldown active!</b>\n"
                    f"Please wait <code>{int(rem)} seconds</code> before sending another file."
                )

    if config["mode"] == "ask":
        btns = [
            [InlineKeyboardButton("🎥 Video", callback_data=f"go_video_{message.id}", style=enums.ButtonStyle.PRIMARY),
             InlineKeyboardButton("📁 File", callback_data=f"go_file_{message.id}", style=enums.ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("🎵 Audio", callback_data=f"go_audio_{message.id}", style=enums.ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("❌ Cancel", callback_data="close_all", style=enums.ButtonStyle.DANGER)]
        ]
        msg = await message.reply_text("<b><i>How should I process this file?</i></b>", reply_markup=InlineKeyboardMarkup(btns))
        temp_context[f"prompt_{uid}"] = msg.id
    elif config["mode"] == "swap":
        if message.video:
            await start_conversion(client, message, "file")
        else:
            await start_conversion(client, message, "video")
    elif config["mode"] == "video":
        await start_conversion(client, message, "video")
    elif config["mode"] == "file":
        await start_conversion(client, message, "file")

async def start_conversion(client, message, target, prompt_msg=None):
    uid = str(message.from_user.id)
    config = get_user_config(uid)
    original_name = (message.video or message.document).file_name or "file"
    if target == "audio":
        original_name = os.path.splitext(original_name)[0] + ".mp3"

    if config["rename"] in ["ask", "yes"]:
        temp_context[f"pending_{uid}"], temp_context[f"waiting_{uid}"] = {"msg": message, "target": target}, True
        btns = [
            [InlineKeyboardButton("🔄 Keep Original", callback_data=f"skp_{message.id}_{target}", style=enums.ButtonStyle.SUCCESS)],
            [InlineKeyboardButton("❌ Cancel", callback_data="close_all", style=enums.ButtonStyle.DANGER)]
        ]
        text = f"✏️ <b>Send a new name for:</b>\n\n<code>{original_name}</code>"
        if prompt_msg:
            await prompt_msg.edit_text(text, reply_markup=InlineKeyboardMarkup(btns))
            temp_context[f"prompt_{uid}"] = prompt_msg.id
        else:
            m = await message.reply_text(text, reply_markup=InlineKeyboardMarkup(btns))
            temp_context[f"prompt_{uid}"] = m.id
    else:
        if prompt_msg:
            await prompt_msg.delete()
        await process_now(client, message, target, original_name)

@bot.on_message(filters.private & filters.text & filters.create(lambda _, __, m: temp_context.get(f"waiting_{m.from_user.id}")))
async def receive_name(client, message):
    uid = str(message.from_user.id)
    new_name = message.text
    temp_context[f"waiting_{uid}"] = False
    ctx = temp_context.get(f"pending_{uid}")
    if not ctx:
        await message.delete()
        return
    original_name = (ctx["msg"].video or ctx["msg"].document).file_name or "file"
    if ctx["target"] == "audio":
        new_name = os.path.splitext(new_name)[0] + ".mp3"
    elif "." not in new_name and "." in original_name:
        new_name += os.path.splitext(original_name)[1]
    await message.delete()
    if temp_context.get(f"prompt_{uid}"):
        try:
            await client.delete_messages(message.chat.id, temp_context[f"prompt_{uid}"])
        except:
            pass
    await process_now(client, ctx["msg"], ctx["target"], new_name)

PARALLEL_CONNS = 8

async def parallel_download(uc, msg, path, task_id, conns=PARALLEL_CONNS):
    """Real multi-connection download: `conns` separate sessions to Telegram, each fetching different 1MB parts of the same file."""
    from pyrogram.file_id import FileId
    media = msg.video or msg.document or msg.audio
    fid = FileId.decode(media.file_id)
    size = media.file_size
    loc = raw.types.InputDocumentFileLocation(id=fid.media_id, access_hash=fid.access_hash,
                                              file_reference=fid.file_reference, thumb_size=fid.thumbnail_size)
    CH, n = 1024 * 1024, (size + 1024 * 1024 - 1) // (1024 * 1024)
    sessions, tasks_, fd = [], [], None
    nxt, done = [0], [0]
    async def worker(s):
        while nxt[0] < n:
            i = nxt[0]
            nxt[0] += 1
            for attempt in range(6):
                try:
                    r = await s.invoke(raw.functions.upload.GetFile(location=loc, offset=i * CH, limit=CH), sleep_threshold=30)
                    break
                except Exception:
                    if attempt == 5:
                        raise
                    await asyncio.sleep(1 + attempt)
            if not isinstance(r, raw.types.upload.File):
                raise RuntimeError("unexpected file response (CDN)")
            await asyncio.to_thread(os.pwrite, fd, r.bytes, i * CH)
            done[0] += len(r.bytes)
            await progress_bar(min(done[0], size), size, task_id)
    try:
        for _ in range(conns):
            sessions.append(await uc.get_session(fid.dc_id, is_media=True, temporary=True))
        fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_TRUNC)
        os.ftruncate(fd, size)
        tasks_ = [asyncio.create_task(worker(s)) for s in sessions]
        await asyncio.gather(*tasks_)
    except BaseException:
        for t in tasks_:
            t.cancel()
        raise
    finally:
        if fd is not None:
            os.close(fd)
        for s in sessions:
            try:
                await s.stop()
            except Exception:
                pass

async def fast_download(bot_client, message, path, task_id):
    """Premium speed: the bot copies the file into the dump channel, the Premium userbot downloads it from there."""
    dump = cfg("DUMP_CHANNEL")
    cp = None
    try:
        cp = await bot_client.copy_message(dump, message.chat.id, message.id)
        try:
            await premium_client.get_chat(dump)
        except Exception:
            pass
        dm = await premium_client.get_messages(dump, cp.id)
        if not dm or getattr(dm, "empty", False):
            raise RuntimeError("dump message not visible to the userbot")
        t0 = time.time()
        try:
            await parallel_download(premium_client, dm, path, task_id)
        except (StopTransmission, asyncio.CancelledError):
            raise
        except Exception as e:
            logger.warning(f"parallel download failed ({e}), single-connection fallback")
            await premium_client.download_media(dm, file_name=path, progress=progress_bar, progress_args=(task_id,))
        ok = os.path.exists(path)
        if ok:
            sz = os.path.getsize(path)
            logger.info(f"fast download: {sz / 1048576:.0f}MB in {time.time() - t0:.1f}s ({sz / 1048576 / max(time.time() - t0, 0.1):.1f} MB/s)")
        return ok
    except (StopTransmission, asyncio.CancelledError):
        raise
    except Exception as e:
        logger.warning(f"fast download failed, using the normal download: {e}")
        return False
    finally:
        if cp:
            try:
                await bot_client.delete_messages(dump, cp.id)
            except Exception:
                pass

async def process_now(client, message, target, filename):
    uid = message.from_user.id
    config = get_user_config(uid)
    filename = apply_name_rules(filename, config)
    file_size = (message.video or message.document).file_size
    premium_type = check_premium(uid)
    limits = get_premium_limits(uid)
    
    task_id = f"task_{int(time.time())}_{random.randint(1000, 9999)}"
    
    async with tasks_lock:
        old_status = user_status_msg.pop(uid, None)
        if old_status:
            try:
                await old_status.delete()
            except:
                pass
        status_msg = await message.reply_text(Theme.STARTING)
        user_status_msg[uid] = status_msg
    
    task = TaskInfo(task_id, uid, message, filename, target, status_msg)
    
    async with tasks_lock:
        tasks[task_id] = task
        if uid not in user_tasks:
            user_tasks[uid] = []
        user_tasks[uid].append(task_id)
        
        active_tasks = [tasks[tid] for tid in user_tasks[uid] if tid in tasks and not tasks[tid].cancelled]
        for idx, t in enumerate(active_tasks, 1):
            t.position = idx
    
    task_dir = os.path.join(DOWNLOAD_LOCATION, task_id)
    os.makedirs(task_dir, exist_ok=True)
    path = os.path.join(task_dir, filename)
    thumb = None
    success = False
    
    try:
        task.stage = "downloading"
        task.download_task = asyncio.current_task()
        
        fast_ok = False
        if limits["use_dump"] and premium_client and cfg("DUMP_CHANNEL"):
            fast_ok = await fast_download(client, message, path, task_id)
        if not fast_ok:
            await client.download_media(
                message,
                file_name=path,
                progress=progress_bar,
                progress_args=(task_id,)
            )
        
        if task.cancel_event.is_set():
            raise asyncio.CancelledError
        
        if target == "audio":
            task.stage = "converting"
            audio_path = f"{task_dir}/{os.path.splitext(filename)[0]}.mp3"
            if not await extract_audio(path, audio_path):
                raise Exception("No audio track found in this file")
            try:
                os.remove(path)
            except OSError:
                pass
            path = audio_path
            file_size = os.path.getsize(path)

        should_send_as_video = (
            target == "video" or
            (target == "swap" and message.document)
        )

        cover = None
        if config["thumb"]:
            thumb = await client.download_media(config["thumb"], file_name=f"{path}_t.jpg")
            if thumb and should_send_as_video:
                cover = thumb
        else:
            if config.get("auto_thumb"):
                names = [filename, message.caption, await tmdb_mod.probe_title(path)]
                thumb = await tmdb_mod.first_hit(names, tmdb_mod.get_auto_thumbnail, f"{path}_t.jpg")
                if thumb and should_send_as_video:
                    cover = await tmdb_mod.first_hit(names, tmdb_mod.get_auto_cover, f"{path}_cover.jpg")
            if not thumb and (should_send_as_video or config.get("auto_thumb")):
                thumb = await get_video_thumbnail(path, f"{path}_t.jpg")
        
        duration = get_duration(path) if (should_send_as_video or target == "audio") else 0
        cap = apply_cap_font(render_caption(config["caption"], filename, file_size, duration), config)
        mi_markup = await mediainfo_markup(path, filename, config)
        
        task.stage = "uploading"
        task.stage_start = time.time()
        task.current, task.total = 0, 0
        task.upload_task = asyncio.current_task()

        if file_size > MAX_FILE_SIZE_NORMAL and limits["use_dump"]:
            dump_msg = await upload_to_dump(
                client, path, filename, task_id,
                thumb_path=thumb,
                duration=duration,
                file_type="audio" if target == "audio" else ("video" if should_send_as_video else "document"),
                spoiler=bool(config.get("spoiler")) and should_send_as_video,
                cover=cover
            )
            if not dump_msg:
                raise Exception("Failed to upload to dump channel")
            await copy_from_dump_to_user(client, dump_msg, message.chat.id, cap, message.id, spoiler=bool(config.get("spoiler")) and should_send_as_video, reply_markup=mi_markup)
        else:
            if target == "audio":
                await client.send_audio(
                    message.chat.id, audio=path, caption=cap, thumb=thumb,
                    duration=duration, file_name=filename, reply_markup=mi_markup,
                    progress=progress_bar, progress_args=(task_id,),
                    reply_parameters=ReplyParameters(message_id=message.id)
                )
            elif should_send_as_video:
                await client.send_video(
                    message.chat.id, video=path, caption=cap, thumb=thumb,
                    duration=duration, file_name=filename, supports_streaming=True,
                    has_spoiler=bool(config.get("spoiler")),
                    video_cover=cover, reply_markup=mi_markup,
                    progress=progress_bar, progress_args=(task_id,),
                    reply_parameters=ReplyParameters(message_id=message.id)
                )
            else:
                await client.send_document(
                    message.chat.id, document=path, caption=cap, thumb=thumb,
                    file_name=filename, reply_markup=mi_markup, progress=progress_bar, progress_args=(task_id,),
                    reply_parameters=ReplyParameters(message_id=message.id)
                )
        
        if config["screenshots"] > 0 and should_send_as_video:
            media = []
            dur = get_duration(path)
            for i in range(config["screenshots"]):
                st = (dur // (config["screenshots"] + 1)) * (i + 1)
                ss = await get_video_thumbnail(path, f"{task_dir}/ss_{i}.jpg", ss_time=st)
                if ss:
                    media.append(InputMediaPhoto(ss, caption=f"Shot #{i+1}", has_spoiler=bool(config.get("spoiler"))))
            if media:
                await client.send_media_group(message.chat.id, media=media, reply_parameters=ReplyParameters(message_id=message.id))
        
        success = True
        
        if int(uid) != ADMIN_ID and premium_type == "free":
            user_cooldowns[uid] = time.time() + limits["cooldown"]
    
    except asyncio.CancelledError:
        task.cancelled = True
        
        if os.path.exists(path):
            try:
                os.remove(path)
            except:
                pass
        
        if os.path.exists(task_dir):
            try:
                shutil.rmtree(task_dir)
            except:
                pass
        
        confirm_msg = await message.reply_text(f"❌ <b>Cancelled:</b> <i>{filename}</i>")
        
        await asyncio.sleep(3)
        await confirm_msg.delete()
    
    except Exception as e:
        err_str = str(e)
        if "topics" in err_str or "No such file or directory" in err_str:
            logger.error(f"Ignored known error in process_now: {e}")
        else:
            logger.error(f"Error in process_now: {e}")
            await message.reply_text(f"❌ <b>Error:</b> <code>{err_str}</code>")
    
    finally:
        async with tasks_lock:
            if task_id in tasks:
                del tasks[task_id]
            if uid in user_tasks and task_id in user_tasks[uid]:
                user_tasks[uid].remove(task_id)
        
        if int(uid) != ADMIN_ID and success:
            add_conversion(uid, success)
        
        async with tasks_lock:
            remaining = [t for t in user_tasks.get(uid, []) if t in tasks and not tasks[t].cancelled]
        
        if not remaining:
            current = user_status_msg.get(uid)
            if current is status_msg:
                try:
                    await current.delete()
                except:
                    pass
                user_status_msg.pop(uid, None)
        else:
            await update_user_status(uid)
        
        if os.path.isdir(task_dir):
            try:
                shutil.rmtree(task_dir)
            except:
                pass

async def main():
    global premium_client, userbot_info
    await db.load()
    if cfg("SESSION_STRING") != SESSION_STRING:
        premium_client = make_premium_client(cfg("SESSION_STRING"))
    logger.info(f"DB loaded: {len(db.users)} users, {len(db.banned)} banned, {len(db.redeem_codes)} codes")
    await bot.start()
    try:
        await bot.set_bot_commands([
            BotCommand("start", "Start the bot"), BotCommand("help", "Help menu"),
            BotCommand("settings", "Your settings"), BotCommand("status", "Active tasks"),
            BotCommand("mediainfo", "MediaInfo of replied media/link"),
            BotCommand("cover", "Add cover to replied video"),
            BotCommand("poster", "Search TMDB posters & backdrops"), BotCommand("ping", "Check bot latency"),
            BotCommand("viewthumb", "View thumbnail"), BotCommand("delthumb", "Delete thumbnail"),
            BotCommand("set_cap", "Set caption"), BotCommand("see_caption", "View caption"),
            BotCommand("del_caption", "Reset caption"), BotCommand("plans", "Premium plans"),
            BotCommand("redeem", "Redeem a code"), BotCommand("cancel", "Cancel a task"),
        ])
        await bot.set_bot_commands([
            BotCommand("start", "Start the bot"), BotCommand("help", "Help menu"),
            BotCommand("settings", "Your settings"), BotCommand("status", "Active tasks"),
            BotCommand("admin", "Admin panel"), BotCommand("bsetting", "Bot settings"), BotCommand("maintenance", "Maintenance mode on/off"),
            BotCommand("stats", "Bot statistics"), BotCommand("speedtest", "Server speedtest"),
            BotCommand("log", "Show recent bot logs"),
            BotCommand("mediainfo", "MediaInfo of replied media/link"),
            BotCommand("cover", "Add cover to replied video"),
            BotCommand("poster", "Search TMDB posters & backdrops"), BotCommand("ping", "Check bot latency"),
            BotCommand("broadcast", "Broadcast (reply)"), BotCommand("cancelall", "Cancel all tasks"),
            BotCommand("restart", "Restart the bot"), BotCommand("plans", "Premium plans"),
        ], scope=BotCommandScopeChat(ADMIN_ID))
    except Exception as e:
        logger.warning(f"set_bot_commands failed: {e}")
    try:
        if os.path.exists(RESTART_FILE):
            with open(RESTART_FILE) as f:
                rs = json.load(f)
            os.remove(RESTART_FILE)
            now = datetime.now()
            await bot.edit_message_text(rs["chat"], rs["mid"], Theme.RESTART_SUCCESS.format(
                date=now.strftime("%d/%m/%y"), time=now.strftime("%H:%M:%S"),
                tz=time.strftime("%Z") or "UTC", version=VERSION))
    except Exception as e:
        logger.warning(f"restart notice failed: {e}")
    bot_me = await bot.get_me()
    _TG_AUTHOR.update(name=bot_me.first_name, url=f"https://t.me/{bot_me.username}")
    try:
        await asyncio.to_thread(_tg_api, "editAccountInfo", {"access_token": _tg_token(), "short_name": "MediaInfo",
                                                         "author_name": bot_me.first_name, "author_url": _TG_AUTHOR["url"]})
    except Exception as e:
        logger.warning(f"telegraph author update failed: {e}")
    logger.info(f"Bot started: @{bot_me.username} ({bot_me.first_name}) [{bot_me.id}]")
    logger.info(f"Admin ID: {ADMIN_ID}")
    print(f"🤖 Bot:       @{bot_me.username} ({bot_me.first_name})")
    print(f"🆔 Bot ID:    {bot_me.id}")
    print(f"👑 Admin ID:  {ADMIN_ID}")

    if premium_client:
        try:
            await premium_client.start()
        except Exception as e:
            logger.error(f"Userbot failed to start, running without it: {e}")
            premium_client = None
    if premium_client:
        try:
            prem_me = await premium_client.get_me()
            uname = f"@{prem_me.username}" if prem_me.username else "(no username)"
            userbot_info = f"{uname}" + (" · Premium" if prem_me.is_premium else " · no Premium")
            logger.info(f"UserBot started: {uname} ({prem_me.first_name}) | Premium: {prem_me.is_premium}")
            print(f"⭐ UserBot:   {uname} ({prem_me.first_name}) | Premium: {prem_me.is_premium}")
        except Exception:
            logger.warning("UserBot started but could not fetch its info")
            print("⭐ UserBot:   started (could not fetch info)")
    else:
        logger.info("UserBot not configured - max file size limited to 2GB")
        print("⚠️  UserBot:   not configured (max file size limited to 2GB)")

    logger.info(f"Version: {VERSION} | Style: {cfg('UI_STYLE')} | Workspace: {WORKSPACE}")
    logger.info("Bot is up and listening")
    print(f"📦 Version:   {VERSION}")
    print(f"💾 Workspace: {WORKSPACE}")
    print("=" * 50)
    print("✅ Bot is running. Press Ctrl+C to stop.")
    print("=" * 50)

    await idle()
    await bot.stop()
    if premium_client:
        await premium_client.stop()

if __name__ == "__main__":
    print("=" * 50)
    print(f"🚀 Starting {VERSION}...")
    print("=" * 50)
    asyncio.get_event_loop().run_until_complete(main())
