"""UI theme for the converter bot (texts + button helpers).

Modeled on Leech-TJ's themes (bot/helper/themes/wzml_emoji.py): all
user-facing strings live here, so changing the look never requires touching
the bot logic.
Placeholders use str.format() names, e.g. {name}. Strings marked RAW are sent
as-is (never .format()-ed), so they may contain literal {braces}.
"""
import html as _html
import re

from pyrogram import enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# ---- button colors: exact port of Leech-TJ bot/helper/telegram_helper/button_build.py ----
DANGER_KEYS = ("❌", "✘", "close", "cancel", "no!", "delete", "remove", "reset", "clear", "unban")
SUCCESS_KEYS = ("✓", "✅", "yes!", "done", "activate", "continue", "buy", "get test")
PRIMARY_KEYS = ("◀️", "▶️", "⌫", "♻️", "view in", "page ", "⏮", "⏭", "‹", "›", "«", "»")


def auto_style(text, is_url=False):
    """Leech-TJ auto_style: danger > success > primary(back/paging/url) > default."""
    t = str(text)
    if t.isupper() and "_" in t:
        return enums.ButtonStyle.DEFAULT
    low = t.lower()
    if any(k in low for k in DANGER_KEYS):
        return enums.ButtonStyle.DANGER
    if any(k in low for k in SUCCESS_KEYS):
        return enums.ButtonStyle.SUCCESS
    if is_url or re.search(r"\bback\b", low) or any(k in low for k in PRIMARY_KEYS):
        return enums.ButtonStyle.PRIMARY
    return enums.ButtonStyle.DEFAULT


def btn(text, data=None, url=None, style=None):
    style = style or auto_style(text, bool(url))
    if url:
        return InlineKeyboardButton(text, url=url, style=style)
    return InlineKeyboardButton(text, callback_data=data, style=style)


class ButtonMaker:
    """Leech-TJ ButtonMaker: body + header / f_body / l_body / footer rows."""

    def __init__(self):
        self._b, self._h, self._fb, self._lb, self._f = [], [], [], [], []

    def _add(self, b, position):
        {None: self._b, "header": self._h, "f_body": self._fb, "l_body": self._lb, "footer": self._f}[position].append(b)

    def ubutton(self, key, link, position=None, style=None):
        self._add(btn(key, url=link, style=style), position)

    def ibutton(self, key, data, position=None, style=None):
        self._add(btn(key, data, style=style), position)

    def build_menu(self, b_cols=1, h_cols=8, fb_cols=2, lb_cols=2, f_cols=8):
        chunk = lambda l, n: [l[i:i + n] for i in range(0, len(l), n)]
        menu_ = chunk(self._b, b_cols)
        if self._h:
            menu_ = chunk(self._h, h_cols) + menu_
        menu_ += chunk(self._fb, fb_cols) + chunk(self._lb, lb_cols) + chunk(self._f, f_cols)
        return InlineKeyboardMarkup(menu_)


def menu(rows):
    """rows: list of lists of (text, data) or (text, data, {'url': ...})."""
    out = []
    for row in rows:
        out.append([
            btn(t[0], data=t[1] if len(t) > 1 else None, url=(t[2] or {}).get("url") if len(t) > 2 else None)
            for t in row
        ])
    return InlineKeyboardMarkup(out)


# ---------- small pure helpers (used by the screens) ----------
def onoff(v):
    return "✅ ON" if v else "❌ OFF"


def tick(cond, label):
    """Mark the currently selected option of a picker."""
    return f"✅ {label}" if cond else label


def back_close(back):
    """Standard footer row: Back to <back> + Close."""
    return [(Theme.BT_BACK, back), (Theme.BT_CLOSE, "close_all")]


def esc(v):
    return _html.escape("" if v is None else str(v))


def short(v, n=40):
    s = "" if v is None else str(v)
    return s if len(s) <= n else s[: n - 1] + "…"


def bar(percent, length=12):
    percent = max(0, min(100, percent or 0))
    filled = int(length * percent / 100)
    return "■" * filled + "□" * (length - filled)


class _LegacyTheme:
    SEP = "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
    FOOTER_LINK = "<b><a href='https://t.me/Tj_Bots'>❤️ Powered By 𝗧𝗝 𝗕𝗼𝘁𝘀 ❤️</a></b>"

    # ---------- generic buttons ----------
    BT_BACK = "🔙 Back"
    BT_BACK_HOME = "🔙 Back Home"
    BT_CLOSE = "❌ Close"

    START = (
        "👋 <b>Hᴇʟʟᴏ {name}!</b>\n\n"
        "<blockquote><b>I ᴀᴍ ᴀ Fᴀsᴛ & Pᴏᴡᴇʀғᴜʟ Rᴇɴᴀᴍᴇ Bᴏᴛ. 🚀</b></blockquote>\n\n"
        "💎 <b><i>Wʜᴀᴛ ᴄᴀɴ I ᴅᴏ?</i></b>\n"
        "<blockquote>╭ <b>Rᴇɴᴀᴍᴇ Fɪʟᴇs</b>\n"
        "┊ <b>Cʜᴀɴɢᴇ Tʜᴜᴍʙɴᴀɪʟs</b>\n"
        "┊ <b>Cᴏɴᴠᴇʀᴛ Vɪᴅᴇᴏ ↔️ Fɪʟᴇ</b>\n"
        "┊ <b>Cᴜsᴛᴏᴍ Cᴀᴘᴛɪᴏɴs (HTML)</b>\n"
        "╰ <b>Sᴄʀᴇᴇɴsʜᴏᴛs</b></blockquote>\n\n"
        "<blockquote><b>Bᴏᴛ Dᴇsɪɢɴᴇᴅ & Dᴇᴠᴇʟᴏᴘᴇᴅ ʙʏ <a href='{dev_link}'>{dev_name}</a></b></blockquote>"
    )

    MODE_NAMES = {"ask": "❓ Ask", "video": "🎥 Video", "file": "📁 File", "swap": "🔄 Swap"}
    RENAME_NAMES = {"ask": "❓ Ask", "yes": "✓", "no": "✘"}
    PLAN_NAMES = {"free": "🎯 Free", "test": "🧪 Test", "gold": "🥇 Gold", "ultra": "👑 Ultra", "admin": "👑 Admin"}

    # ==================== /settings (Leech-TJ style) ====================
    # Legacy /settings template (pre-USET). Kept so an older חדש.py loaded with this theme.py won't crash.
    SETTINGS = (
        "⚙️ <b>Usᴇʀ Pᴇʀsᴏɴᴀʟ Sᴇᴛᴛɪɴɢs</b>\n"
        "<blockquote>╭ 📍 <b>Mᴏᴅᴇ:</b> <code>{mode}</code>\n"
        "┊ ✏️ <b>Rᴇɴᴀᴍᴇ:</b> <code>{rename}</code>\n"
        "┊ 📸 <b>Sᴄʀᴇᴇɴsʜᴏᴛs:</b> <code>{screenshots}</code>\n"
        "┊ 🙈 <b>Sᴘᴏɪʟᴇʀ:</b> <code>{spoiler}</code>\n"
        "┊ 🖼 <b>Aᴜᴛᴏ Tʜᴜᴍʙ:</b> <code>{auto_thumb}</code>\n"
        "┊ 🏷 <b>Pʟᴀɴ:</b> <code>{plan}</code>\n"
        "╰ 📊 <b>Tᴏᴅᴀʏ:</b> <code>{quota}</code></blockquote>"
    )

    USET_HOME = (
        "㊂ <b><u>Usᴇʀ Sᴇᴛᴛɪɴɢs :</u></b>\n\n"
        "┎👤 <b>Name :</b> {name} ( <code>{id}</code> )\n"
        "┠🔖 <b>Username :</b> {username}\n"
        "┠🆔 <b>Telegram DC :</b> {dc}\n"
        "┖🗣️ <b>Language :</b> {lang}\n\n"
        "<blockquote>╭ 📤 <b>Upload:</b> <code>{mode}</code> | ✏️ <b>Rename:</b> <code>{rename}</code>\n"
        "┊ 🖼 <b>Thumb:</b> <code>{thumb}</code> | 🎬 <b>Auto Thumb:</b> <code>{auto_thumb}</code>\n"
        "┊ 📝 <b>Caption:</b> <code>{caption}</code>\n"
        "┊ 🔤 <b>Name Rules:</b> <code>{name_rules}</code>\n"
        "┊ 📸 <b>Screenshots:</b> <code>{screenshots}</code> | 🙈 <b>Spoiler:</b> <code>{spoiler}</code>\n"
        "╰ 🏷 <b>Plan:</b> <code>{plan}</code> | 📊 <b>Today:</b> <code>{quota}</code></blockquote>\n\n"
        "<i>Choose a category below 👇</i>"
    )
    USET_HOME_BTNS = {
        "upload": "📤 Upload Mode", "thumb": "🖼 Thumbnail & Cover",
        "caption": "📝 Caption & Vars", "name": "🔤 Prefix / Suffix / Remname",
        "auto": "🎬 Auto Thumb", "media": "📸 Screenshots & Spoiler",
        "quota": "📊 Quota & Plan", "reset": "♻️ Reset All Settings",
    }

    USET_UPLOAD = (
        "㊂ ✔️<b><u>Upload Mode : {name}</u></b>\n"
        "┎📤 <b>Mode :</b> <code>{mode}</code>\n"
        "┖✏️ <b>Rename :</b> <code>{rename}</code>\n\n"
        "<blockquote>╭ <b>Video</b> — always upload as a streamable video\n"
        "┊ <b>File</b> — always upload as a document\n"
        "┊ <b>Swap</b> — auto-flip: video→file, file→video\n"
        "╰ <b>Ask</b> — ask each time</blockquote>\n"
        "<blockquote>╭ <b>Rename ✓</b> — always ask for a new name\n"
        "┊ <b>Rename ✘</b> — always keep the original name\n"
        "╰ <b>Rename ❓</b> — ask each time</blockquote>"
    )
    USET_THUMB = (
        "㊂ ✔️<b><u>Thumbnail & Cover : {name}</u></b>\n"
        "┎🖼️ <b>Custom Thumbnail :</b> <i>{thumb}</i>\n"
        "┖🎬 <b>Auto Thumbnail :</b> <i>{auto_thumb}</i>\n\n"
        "<blockquote>╭ <b>Set:</b> just send me any photo\n"
        "┊ <b>Priority:</b> custom thumb → TMDB poster → video frame\n"
        "╰ <b>Cover:</b> reply to a video with <code>/cover</code></blockquote>"
    )
    USET_THUMB_BTNS = {"view": "👁 View Thumb", "del": "🗑 Delete Thumb"}
    USET_CAPTION = (
        "㊂ ✔️<b><u>Caption : {name}</u></b>\n"
        "┖📄 <b>Current :</b>\n<blockquote expandable><code>{caption}</code></blockquote>\n\n"
        "<b>📌 Variables:</b>\n{vars}"
    )
    USET_CAPTION_BTNS = {"set": "✏️ Set Caption", "reset": "♻️ Reset Default"}
    # RAW: inserted as an argument, never formatted itself
    CAPTION_VARS = (
        "<blockquote>╭ <code>{filename}</code> - file name\n"
        "┊ <code>{filesize}</code> - file size\n"
        "┊ <code>{title}</code> / <code>{year}</code> - cleaned title / year\n"
        "┊ <code>{quality}</code> - 1080P, 720P, 4K…\n"
        "┊ <code>{duration}</code> - video length\n"
        "╰ <code>{ext}</code> - file extension</blockquote>"
    )
    USET_NAME = (
        "㊂ ✔️<b><u>Filename Rules : {name}</u></b>\n"
        "┎Ⓟ <b>Prefix :</b> <code>{prefix}</code>\n"
        "┠Ⓢ <b>Suffix :</b> <code>{suffix}</code>\n"
        "┖🌈 <b>Remname :</b> <code>{remname}</code>\n\n"
        "<b>👀 Preview:</b>\n<blockquote><code>{example}</code>\n↳ <code>{preview}</code></blockquote>\n"
        "<i>Applied to every file before upload (also when you type a new name).</i>"
    )
    USET_NAME_BTNS = {"prefix": "Ⓟ Prefix", "suffix": "Ⓢ Suffix", "remname": "🌈 Remname", "clear": "🗑 Clear All"}
    NAME_EXAMPLE = "www.Site.com - Movie.Name.2023.1080p.WEB-DL.mkv"
    USET_AUTO = (
        "㊂ ✔️<b><u>Auto Thumbnail : {name}</u></b>\n"
        "┎🎬 <b>Status :</b> <i>{auto_thumb}</i>\n"
        "┖🔑 <b>TMDB :</b> <i>{tmdb}</i>\n\n"
        "<blockquote>When ON and no custom thumb is set, the bot finds the movie/series "
        "poster on TMDB (file name → caption → embedded title) and uses it as thumbnail, "
        "plus the full poster as video cover. Falls back to a video frame.</blockquote>"
    )
    USET_MEDIA = (
        "㊂ ✔️<b><u>Screenshots & Spoiler : {name}</u></b>\n"
        "┎📸 <b>Screenshots :</b> <code>{screenshots}</code> per video\n"
        "┖🙈 <b>Spoiler :</b> <i>{spoiler}</i>\n\n"
        "<i>Pick how many screenshots to send after each video (0 = off).</i>"
    )
    USET_QUOTA = (
        "㊂ ✔️<b><u>Quota & Plan : {name}</u></b>\n"
        "┎🏷 <b>Plan :</b> <code>{plan}</code>{expires}\n"
        "┠📊 <b>Used Today :</b> <code>{used}</code> / <code>{limit}</code> ({failed} failed)\n"
        "┠🎯 <b>Remaining :</b> <code>{remaining}</code>\n"
        "┠⏰ <b>Resets In :</b> <code>{reset}</code>\n"
        "┠📦 <b>Max File Size :</b> <code>{max_size}</code>\n"
        "┠⚙️ <b>Parallel Tasks :</b> <code>{concurrent}</code>\n"
        "┖⏳ <b>Cooldown :</b> <code>{cooldown}</code>"
    )
    USET_QUOTA_BTNS = {"plans": "⭐ View Plans", "refresh": "♻️ Refresh"}
    USET_RESET = (
        "♻️ <b>Reset all your settings?</b>\n"
        "<blockquote>Mode, rename, thumbnail, caption, prefix/suffix/remname, auto thumb, "
        "screenshots and spoiler go back to default.\nYour plan and quota are kept.</blockquote>"
    )
    USET_RESET_BTNS = {"yes": "✅ Yes, reset"}
    USET_RESET_DONE = "Settings reset to default"

    USET_LABELS = {"caption": "📝 Caption", "prefix": "Ⓟ Prefix", "suffix": "Ⓢ Suffix", "remname": "🌈 Remname"}
    USET_HINTS = {
        "caption": "Send the caption (HTML allowed, max 1024 chars). Variables like <code>{filename}</code> work.",
        "prefix": "Text added before the name, e.g. <code>@MyChannel - </code> (max 64 chars).",
        "suffix": "Text added before the extension, e.g. <code> - @MyChannel</code> (max 64 chars).",
        "remname": (
            "Regex rules separated by <code>|</code>:\n"
            "<code>word</code> → remove, <code>old:new</code> → replace, <code>old:new:1</code> → replace once.\n"
            "Example: <code>www\\S+|\\[.*?\\]|WEB-DL:WEB</code>"
        ),
    }
    USET_PROMPT = (
        "✏️ <b>Edit {label}</b>\n"
        "<blockquote>╰ <b>Current:</b> <code>{current}</code></blockquote>\n"
        "{hint}\n\n<i>Send the new value now, or tap Back.</i>"
    )
    USET_PROMPT_BTNS = {"remove": "🗑 Remove"}
    USET_SAVED = "✅ {label} saved"
    USET_REMOVED = "🗑 {label} removed"
    USET_INVALID = "❌ <b>Invalid value:</b> <code>{err}</code>\n<i>Send it again or tap Back.</i>"
    NOT_SET = "Not set"

    # ==================== /bsetting (admin bot settings) ====================
    BSET_HOME = (
        "㊂ <b><u>Bᴏᴛ Sᴇᴛᴛɪɴɢs :</u></b> <i>(admin)</i>\n\n"
        "┎📊 <b>Daily Quotas</b>\n"
        "┃ Free <code>{q_free}</code> | Test <code>{q_test}</code> | Gold <code>{q_gold}</code> | Ultra <code>{q_ultra}</code>\n"
        "┠⚙️ <b>Parallel Tasks</b>\n"
        "┃ Free <code>{c_free}</code> | Test <code>{c_test}</code> | Gold <code>{c_gold}</code> | Ultra <code>{c_ultra}</code>\n"
        "┠⏳ <b>Free Cooldown :</b> <code>{cooldown}</code>\n"
        "┠📦 <b>Max Size :</b> Normal <code>{size_n}</code> | Premium <code>{size_p}</code>\n"
        "┖🛠 <b>Maintenance :</b> <code>{maint}</code>\n\n"
        "<i>Stored in MongoDB → <code>bot_config</code>. Changes apply instantly.</i>"
    )
    BSET_GROUP = "㊂ ✔️<b><u>{title}</u></b>\n\n{lines}\n\n<i>Tap a value to edit it.</i>"
    BSET_LINE = "┠ <b>{label} :</b> <code>{value}</code>"
    BSET_GROUPS = {
        "quota": "📊 Daily Quotas", "conc": "⚙️ Parallel Tasks",
        "limits": "📦 Size & Cooldown", "maint": "🛠 Maintenance",
    }
    BSET_LABELS = {
        "FREE_DAILY_LIMIT": "🎯 Free / day", "TEST_DAILY_LIMIT": "🧪 Test / day",
        "GOLD_DAILY_LIMIT": "🥇 Gold / day", "ULTRA_DAILY_LIMIT": "👑 Ultra / day",
        "MAX_CONCURRENT_FREE": "🎯 Free tasks", "MAX_CONCURRENT_TEST": "🧪 Test tasks",
        "MAX_CONCURRENT_GOLD": "🥇 Gold tasks", "MAX_CONCURRENT_ULTRA": "👑 Ultra tasks",
        "COOLDOWN_NORMAL": "⏳ Free cooldown (s)",
        "MAX_FILE_SIZE_NORMAL": "📦 Max size (free)", "MAX_FILE_SIZE_PREMIUM": "📦 Max size (premium)",
        "MAINTENANCE": "🛠 Maintenance", "MAINTENANCE_MSG": "📝 Maintenance note",
    }
    BSET_HINTS = {
        "int": "Send a whole number (0 – 100000).",
        "size": "Send a size: <code>1950MB</code>, <code>2GB</code>, <code>4G</code> (max 4GB).",
        "text": "Send the note shown to users (HTML allowed, max 500 chars). Send <code>-</code> to clear.",
    }
    BSET_PROMPT = (
        "✏️ <b>Edit {label}</b>\n"
        "<blockquote>╭ <b>Current:</b> <code>{current}</code>\n"
        "╰ <b>Default:</b> <code>{default}</code></blockquote>\n"
        "{hint}\n\n<i>Send the new value now, or tap Back.</i>"
    )
    BSET_BTNS = {"default": "↺ Use Default", "reset_all": "♻️ Reset All to Default", "maint_on": "🛠 Maintenance: ✅ ON", "maint_off": "🛠 Maintenance: ❌ OFF"}
    BSET_SAVED = "✅ {label} = {value}"
    BSET_RESET_DONE = "All bot settings reset to default"
    BSET_RESET_CONFIRM = (
        "♻️ <b>Reset ALL bot settings to default?</b>\n"
        "<blockquote>Quotas, parallel tasks, cooldown, max sizes and maintenance go back to the "
        "values in the code. Users' plans are not touched.</blockquote>"
    )
    BSET_INVALID = "❌ <b>Invalid value:</b> <code>{err}</code>\n<i>Send it again or tap Back.</i>"
    ADMIN_ONLY = "Admins only!"

    MAINTENANCE = (
        "🛠 <b>Uɴᴅᴇʀ Mᴀɪɴᴛᴇɴᴀɴᴄᴇ</b>\n\n"
        "<blockquote><b>The bot is being upgraded right now.</b>\n"
        "Please try again a little later. 🙏</blockquote>{note}"
    )
    MAINTENANCE_NOTE = "\n<blockquote>📝 {note}</blockquote>"
    MAINTENANCE_ALERT = "🛠 The bot is under maintenance. Please try again later."

    # ==================== help ====================
    HELP_HEADER = "Hey <b>{name}</b>\n\n<blockquote><b>Choose a category below to get help.</b></blockquote>"
    HELP_BTNS = {"thumb": "📸 Thumbnail", "cap": "📝 Caption", "redeem": "🎫 Redeem", "cmds": "📋 Commands", "settings": "⚙️ Settings"}

    # RAW
    HELP_THUMB = (
        "🖼️ <b>HOW TO SET THUMBNAIL</b>\n\n"
        "<blockquote><b>1. Simply send any photo to the bot.</b>\n"
        "<b>2. The bot will save it as your custom thumbnail.</b>\n"
        "<b>3. This thumbnail will be applied to all your future files.</b></blockquote>\n\n"
        "<blockquote>╭ <code>/viewthumb</code> - <u>View current thumbnail</u>\n"
        "┊ <code>/delthumb</code> - <u>Delete your thumbnail</u>\n"
        "╰ /settings → 🎬 <u>Auto Thumb (TMDB poster)</u></blockquote>"
    )
    # RAW
    HELP_CAP = (
        "📝 <b>HOW TO SET CAPTION</b>\n\n"
        "<blockquote><b>Use <code>/set_cap</code> followed by your caption text, or /settings → 📝 Caption.</b></blockquote>\n\n"
        "<b>📌 AVAILABLE VARIABLES:</b>\n"
        + CAPTION_VARS + "\n\n"
        "<b>🎨 HTML TAGS YOU CAN USE:</b>\n"
        "<blockquote>╭ <code>&lt;b&gt;text&lt;/b&gt;</code> - <b>bold</b>\n"
        "┊ <code>&lt;i&gt;text&lt;/i&gt;</code> - <i>italic</i>\n"
        "┊ <code>&lt;u&gt;text&lt;/u&gt;</code> - <u>underline</u>\n"
        "╰ <code>&lt;code&gt;text&lt;/code&gt;</code> - <code>monospace</code></blockquote>\n\n"
        "<b>📋 EXAMPLES:</b>\n"
        "<blockquote>╭ <code>/set_cap &lt;b&gt;{title} ({year})&lt;/b&gt;</code>\n"
        "╰ <code>/set_cap &lt;b&gt;{filename}&lt;/b&gt; | {quality} | 📦 {filesize}</code></blockquote>\n\n"
        "<blockquote>╭ <code>/see_caption</code> - <u>Check current caption</u>\n"
        "╰ <code>/del_caption</code> - <u>Reset to default</u></blockquote>"
    )
    # RAW
    HELP_REDEEM = (
        "🎫 <b>REDEEM CODES</b>\n\n"
        "<blockquote>You can get premium access by redeeming a code.</blockquote>\n\n"
        "<b>How to use:</b>\n"
        "<blockquote>╭ Get a code from the admin\n"
        "╰ Use <code>/redeem CODE</code></blockquote>\n\n"
        "<b>Example:</b>\n"
        "<code>/redeem ABC12345</code>\n\n"
        "<b>Note:</b> Each user can redeem only one code."
    )
    # RAW
    HELP_COMMANDS = (
        "<b>📋 AVAILABLE COMMANDS</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "<b>Basic Commands:</b>\n"
        "<blockquote>╭ <code>/start</code> - Start the bot.\n"
        "┊ <code>/help</code> - Show this help menu.\n"
        "┊ <code>/settings</code> - Settings: upload mode, thumb, caption, prefix/suffix/remname, auto thumb, quota.\n"
        "┊ <code>/status</code> - Your active tasks.\n"
        "┊ <code>/cancel N</code> - Cancel task number N.\n"
        "┊ <code>/mediainfo</code> - Reply to media/link: full MediaInfo.\n"
        "┊ <code>/cover</code> - Reply to a video: add your thumb/TMDB poster as cover.\n"
        "┊ <code>/poster</code> or <code>/p</code> - Search TMDB: browse posters/backdrops, set as thumb, get original.\n"
        "┊ <code>/ping</code> - Check latency.\n"
        "╰ <code>/plans</code> - View premium plans.</blockquote>\n\n"
        "<b>Thumbnail Commands:</b>\n"
        "<blockquote>╭ <code>/viewthumb</code> - View your thumbnail.\n"
        "╰ <code>/delthumb</code> - Delete thumbnail.</blockquote>\n\n"
        "<b>Caption Commands:</b>\n"
        "<blockquote>╭ <code>/set_cap</code> - Set custom caption.\n"
        "┊ <code>/see_caption</code> - View current caption.\n"
        "╰ <code>/del_caption</code> - Reset caption.</blockquote>\n\n"
        "<b>Premium Commands:</b>\n"
        "<blockquote>╰ <code>/redeem CODE</code> - Redeem a code.</blockquote>\n"
        "━━━━━━━━━━━━━━━━━━"
    )

    MEDIAINFO_HELP = (
        "🔎 <b>Mᴇᴅɪᴀɪɴғᴏ</b>\n"
        "<blockquote>╭ Reply to a video/audio/document:\n"
        "┊ <code>/mediainfo</code>\n"
        "┊ Or send a direct link:\n"
        "╰ <code>/mediainfo https://…/file.mkv</code></blockquote>"
    )
    COVER_HELP = (
        "🖼 <b>Cᴏᴠᴇʀ</b>\n"
        "<blockquote>Reply to a <b>video</b> with <code>/cover</code> to re-send it with your "
        "custom thumbnail (or an auto TMDB poster) as the video cover. No re-upload.</blockquote>"
    )
    COVER_NEED_THUMB = (
        "<i>Set a custom thumbnail (send a photo) or enable 🎬 Auto Thumb in /settings to use /cover!</i>"
    )
    COVER_NOT_FOUND = "❌ <b>No poster found for this file name.</b>"

    INFO = (
        "🎬 <b>{title}</b> <code>({year})</code>\n"
        "<blockquote>╭ ⭐ <b>Rᴀᴛɪɴɢ:</b> <code>{rating}</code>\n"
        "┊ 🎭 <b>Gᴇɴʀᴇs:</b> {genres}\n"
        "┊ ⏱ <b>{runtime_label}:</b> <code>{runtime}</code>\n"
        "╰ 📺 <b>Tʏᴘᴇ:</b> <code>{kind}</code></blockquote>\n"
        "<blockquote expandable>{overview}</blockquote>\n"
        "🔗 <a href='{url}'>TMDB</a>"
    )
    INFO_HELP = (
        "🎬 <b>Pᴏsᴛᴇʀ Sᴇᴀʀᴄʜ</b>\n"
        "<blockquote>╭ <code>/poster Oppenheimer 2023</code> (or <code>/p</code>)\n"
        "┊ or reply to a video/file with <code>/p</code>\n"
        "╰ browse posters & backdrops, set one as thumbnail or get the original</blockquote>"
    )
    INFO_NOT_FOUND = "❌ <b>Nothing found on TMDB.</b>"

    # ==================== /poster browser (DD Bypass style) ====================
    POSTER_SEARCHING = "🔎 <i>Searching TMDB for</i> <code>{query}</code><i>...</i>"
    POSTER_RESULTS = (
        "🎬 <b>Pᴏsᴛᴇʀ Sᴇᴀʀᴄʜ</b>\n"
        "<blockquote>╭ 🔎 <b>Query:</b> <code>{query}</code>\n"
        "╰ 📚 <b>Results:</b> <code>{count}</code> | 📄 <b>Page:</b> <code>{page}/{pages}</code></blockquote>\n"
        "<i>Tap a title to browse its posters & backdrops 👇</i>"
    )
    POSTER_ITEM = "{title} ({year})"  # button label, plain text
    POSTER_CAPTION = (
        "<b>{title} ({year})</b>\n"
        "<blockquote>╭ 🔗 <a href='{url}'>View on TMDB</a>\n"
        "┊ 🖼 <b>Type:</b> <code>{type}</code>\n"
        "┊ 🌐 <b>Language:</b> <code>{lang}</code>\n"
        "┊ 📐 <b>Size:</b> <code>{w} x {h}</code>\n"
        "╰ 📄 <b>{kind}:</b> <code>{i}/{n}</code></blockquote>"
    )
    POSTER_KINDS = {"p": "Poster", "b": "Backdrop"}
    POSTER_KINDS_PL = {"p": "Posters", "b": "Backdrops"}
    POSTER_ORIENT = {"portrait": "Portrait", "landscape": "Landscape"}
    POSTER_BT = {
        "prev": "⇦ Prev", "next": "Next ⇨", "img_prev": "⇦", "img_next": "⇨",
        "p": "🖼 Posters ({n})", "b": "🌄 Backdrops ({n})",
        "thumb": "✅ Set as thumbnail", "orig": "📥 Send original",
        "back": "⇦ Back to results", "close": "✘ Close",
    }
    POSTER_ORIG_CAPTION = "📥 <b>{title} ({year})</b>\n<code>{type} · {w}x{h} · {lang}</code>"
    POSTER_THUMB_SET = "✅ Saved as your thumbnail"
    POSTER_SENDING = "📥 Sending the original file..."
    POSTER_NO_IMAGES = "No images on TMDB for this title."
    POSTER_EXPIRED = "This search expired. Run /poster again."
    POSTER_NOT_YOURS = "Only the user who searched can use these buttons!"
    POSTER_LOAD_FAIL = "Could not load this image, try another one."
    POSTER_SEARCH_FAIL = "❌ <b>TMDB search failed, try again later.</b>"
    POSTER_NO_KEY = "❌ <b>TMDB_API_KEY is not configured.</b>"
    POSTER_NO_TEXT = "No text"
    POSTER_LANGS = {
        "en": "English", "he": "Hebrew", "fr": "French", "de": "German", "es": "Spanish", "it": "Italian",
        "pt": "Portuguese", "ru": "Russian", "ja": "Japanese", "ko": "Korean", "zh": "Chinese", "hi": "Hindi",
        "ar": "Arabic", "tr": "Turkish", "pl": "Polish", "nl": "Dutch", "uk": "Ukrainian", "cs": "Czech",
    }

    # ==================== /stats (admin, paged like Leech-TJ) ====================
    STATS = (
        "⌬ <b><i>USER STATISTICS :</i></b>\n"
        "┎ 👥 <b>Users :</b> <code>{users}</code>\n"
        "┠ ⭐ <b>Premium :</b> <code>{premium}</code>\n"
        "┠ 🖼 <b>With Thumb :</b> <code>{thumbs}</code>\n"
        "┠ 🔨 <b>Banned :</b> <code>{banned}</code>\n"
        "┠ ⚙️ <b>Active Tasks :</b> <code>{tasks}</code>\n"
        "┖ ⏳ <b>Uptime :</b> <code>{uptime}</code>"
    )
    STATS_BOT = (
        "⌬ <b><i>BOT STATISTICS :</i></b>\n"
        "┖ <b>Bot Uptime :</b> {bot_uptime}\n\n"
        "┎ <b><i>RAM ( MEMORY ) :</i></b>\n"
        "┃ <code>{ram_bar}</code> {ram}%\n"
        "┖ <b>U :</b> {ram_u} | <b>F :</b> {ram_f} | <b>T :</b> {ram_t}\n\n"
        "┎ <b><i>SWAP MEMORY :</i></b>\n"
        "┃ <code>{swap_bar}</code> {swap}%\n"
        "┖ <b>U :</b> {swap_u} | <b>F :</b> {swap_f} | <b>T :</b> {swap_t}\n\n"
        "┎ <b><i>DISK :</i></b>\n"
        "┃ <code>{disk_bar}</code> {disk}%\n"
        "┃ <b>Total Disk Read :</b> {disk_read}\n"
        "┃ <b>Total Disk Write :</b> {disk_write}\n"
        "┖ <b>U :</b> {disk_u} | <b>F :</b> {disk_f} | <b>T :</b> {disk_t}"
    )
    STATS_SYS = (
        "⌬ <b><i>OS SYSTEM :</i></b>\n"
        "┠ <b>OS Uptime :</b> {os_uptime}\n"
        "┠ <b>OS Version :</b> {os_version}\n"
        "┖ <b>OS Arch :</b> {os_arch}\n\n"
        "⌬ <b><i>NETWORK STATS :</i></b>\n"
        "┠ <b>Upload Data :</b> {up_data}\n"
        "┠ <b>Download Data :</b> {dl_data}\n"
        "┠ <b>Pkts Sent :</b> {pkt_sent}k\n"
        "┠ <b>Pkts Received :</b> {pkt_recv}k\n"
        "┖ <b>Total I/O Data :</b> {tl_data}\n\n"
        "┎ <b>CPU :</b>\n"
        "┃ <code>{cpu_bar}</code> {cpu}%\n"
        "┠ <b>CPU Frequency :</b> {cpu_freq}\n"
        "┠ <b>System Avg Load :</b> {sys_load}\n"
        "┠ <b>P-Core(s) :</b> {p_core} | <b>V-Core(s) :</b> {v_core}\n"
        "┖ <b>Total Core(s) :</b> {total_core}"
    )
    STATS_LIMITS = (
        "⌬ <b><i>BOT LIMITATIONS :</i></b>\n"
        "┠ <b>Daily (F/T/G/U) :</b> {q_free} / {q_test} / {q_gold} / {q_ultra}\n"
        "┠ <b>Parallel (F/T/G/U) :</b> {c_free} / {c_test} / {c_gold} / {c_ultra}\n"
        "┠ <b>Free Cooldown :</b> {cooldown}\n"
        "┠ <b>Max Size :</b> {size_n} / premium {size_p}\n"
        "┠ <b>UserBot (4GB) :</b> {userbot}\n"
        "┖ <b>Maintenance :</b> {maint}"
    )
    STATS_BTNS = {"bot": "🤖 Bot", "sys": "🖥 OS", "lim": "📏 Limits", "usr": "👥 Users"}

    # ==================== /speedtest (Cloudflare, no extra deps) ====================
    SPEED_START = "<i>🚀 Initiating Speedtest...</i>"
    SPEED_RESULT = (
        "➲ <b><i>SPEEDTEST INFO</i></b>\n"
        "┠ <b>Upload :</b> <code>{up}/s</code> (<code>{up_mbps} Mbps</code>)\n"
        "┠ <b>Download :</b> <code>{dl}/s</code> (<code>{dl_mbps} Mbps</code>)\n"
        "┠ <b>Ping :</b> <code>{ping} ms</code>\n"
        "┠ <b>Time :</b> <code>{time}</code>\n"
        "┠ <b>Data Sent :</b> <code>{sent}</code>\n"
        "┖ <b>Data Received :</b> <code>{recv}</code>\n\n"
        "➲ <b><i>SPEEDTEST SERVER</i></b>\n"
        "┠ <b>Provider :</b> <code>Cloudflare</code>\n"
        "┠ <b>Datacenter :</b> <code>{colo}</code>\n"
        "┖ <b>Country :</b> <code>{loc}</code>"
    )
    SPEED_FAIL = "<b>ERROR:</b> <i>Speedtest failed: {err}</i>"

    # ==================== ping / restart ====================
    PING = "<i>🏓 Starting Ping...</i>"
    PING_VALUE = "🏓 <b>Pong!</b> <code>{ms} ms</code>\n<blockquote>⏳ <b>Uptime:</b> {uptime}</blockquote>"
    RESTARTING = "🔄 <i>Restarting...</i>"
    RESTART_SUCCESS = (
        "⌬ <b><i>Restarted Successfully!</i></b>\n"
        "┠ <b>Date :</b> {date}\n"
        "┠ <b>Time :</b> {time}\n"
        "┠ <b>TimeZone :</b> {tz}\n"
        "┖ <b>Version :</b> {version}"
    )

    # ==================== task status (Leech-TJ progress layout) ====================
    STARTING = "⏳ <b>Starting...</b>"
    STATUS_TASK = (
        "┎🏷️ <b>Name:</b> <blockquote><i>{name}</i></blockquote>\n"
        "┃ <code>[{bar}]</code> {percent:.2f}%\n"
        "┠📊 <b>{processed_label}:</b> {done} of {total}\n"
        "┠⚡ <b>Status:</b> {status} | ⏰ <b>ETA:</b> {eta}\n"
        "┠🚀 <b>Speed:</b> {speed}/s | ⏱️ <b>Elapsed:</b> {elapsed}\n"
        "┠🚂 <b>Engine:</b> #TjGram | 💠 <b>Mode:</b> {mode_tag} | #Tg\n"
        "┠🙋 <b>User:</b> <code>{user}</code> | 🎯 <b>Task:</b> #{pos}\n"
        "┖❌ <code>/cancel {pos}</code>"
    )
    STATUS_CANCELLED = "┎🏷️ <b>Name:</b> <blockquote><i>{name}</i></blockquote>\n┖ ❌ <b>Cancelled</b>"
    STATUS_FOOTER = (
        "⌬ <b><i>Bot Stats</i></b>\n"
        "┠ <b>Tasks:</b> {tasks}/{max_tasks} | <b>AVL:</b> {avl}\n"
        "┠ <b>CPU:</b> {cpu}% | <b>F:</b> {free} [{free_p}%]\n"
        "┠ <b>RAM:</b> {ram}% | <b>UPTIME:</b> {uptime}\n"
        "┖ <b>DL:</b> {dl}/s | <b>UL:</b> {ul}/s"
    )
    NO_ACTIVE = "<i>📭 No Active Downloads/Uploads!</i>\n\n{footer}"

    # ==================== plans ====================
    PLAN = (
        "<blockquote><b>{title}</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "• <b>Price:</b> {price}\n"
        "{duration}"
        "• <b>Daily limit:</b> {daily} conversions\n"
        "• <b>Max file size:</b> {size}\n"
        "• <b>Concurrent tasks:</b> {conc}\n"
        "• <b>Cooldown:</b> {cooldown}\n"
        "━━━━━━━━━━━━━━━━━━</blockquote>{extra}"
    )
    PLAN_TITLES = {"free": "🎯 FREE PLAN", "test": "🧪 TEST PLAN", "gold": "🥇 GOLD PLAN", "ultra": "👑 ULTRA PLAN"}

    # ==================== admin panel ====================
    ADMIN_PANEL = (
        "<blockquote><b>╭── ˹ ADMIN CONTROL ˼ ──</b>\n"
        "<b>│</b>\n"
        "<b>├── 👤 Admin:</b> <code>{admin}</code>\n"
        "<b>├── 📊 Users:</b> <b>{users}</b>\n"
        "<b>├── 🔨 Banned:</b> <b>{banned}</b>\n"
        "<b>├── 🧪 Test:</b> <b>{test}</b>\n"
        "<b>├── 🥇 Gold:</b> <b>{gold}</b>\n"
        "<b>├── 👑 Ultra:</b> <b>{ultra}</b>\n"
        "<b>├── 🎫 Redeem:</b> <b>{redeem}</b>\n"
        "<b>├── 🛠 Maintenance:</b> <b>{maint}</b>\n"
        "<b>│</b>\n"
        "<b>├── 📢 Broadcast:</b>\n"
        "<b>│ ├⊳ /broadcast (Copy)</b>\n"
        "<b>│ └⊳ /broadcast -f (Forward)</b>\n"
        "<b>│</b>\n"
        "<b>├── 👤 Users:</b>\n"
        "<b>│ ├⊳ /ban [id] (Ban)</b>\n"
        "<b>│ ├⊳ /unban [id] (Unban)</b>\n"
        "<b>│ ├⊳ /users (List users)</b>\n"
        "<b>│ └⊳ /allban (List banned)</b>\n"
        "<b>│</b>\n"
        "<b>├── ⭐ Plans:</b>\n"
        "<b>│ ├⊳ /add_plan [id] [test/gold/ultra] [duration]</b>\n"
        "<b>│ ├⊳ /remove_plan [id]</b>\n"
        "<b>│ └⊳ /plan_list</b>\n"
        "<b>│</b>\n"
        "<b>├── 🎫 Redeem Codes:</b>\n"
        "<b>│ ├⊳ /gencodes [count] [duration] [gold/ultra]</b>\n"
        "<b>│ └⊳ /redeem_stats</b>\n"
        "<b>│</b>\n"
        "<b>├── ⚙️ System:</b>\n"
        "<b>│ ├⊳ /bsetting (Bot settings)</b>\n"
        "<b>│ ├⊳ /stats · /speedtest</b>\n"
        "<b>│ ├⊳ /cancelall</b>\n"
        "<b>│ └⊳ /restart</b>\n"
        "<b>│</b>\n"
        "<b>╰────────────────</b></blockquote>"
    )
    ADMIN_BTNS = {"bset": "⚙️ Bot Settings", "stats": "📊 Stats", "home": "🔙 Admin Panel"}

    MEDIAINFO_DONE = (
        "🔎 <b>Mᴇᴅɪᴀɪɴғᴏ</b>\n"
        "<blockquote>╭ 📌 <b>{name}</b>\n"
        "╰ 🔗 <a href='{url}'>Open on Telegraph</a></blockquote>"
    )


# =====================================================================
#  Leech-TJ "minimal" theme (bot/helper/themes/wzml_minimal.py) - 1:1 style
#  Everything above (_LegacyTheme) is only a fallback for old names.
# =====================================================================
def tree(items):
    """[(label, value_html), ...] -> minimal ╭ ┊ ╰ lines (no blockquote)."""
    items = [i for i in items if i]
    out = []
    for n, (label, value) in enumerate(items):
        lead = "╭" if n == 0 else ("╰" if n == len(items) - 1 else "┊")
        if len(items) == 1:
            lead = "╰"
        out.append(f"{lead}<b> {label} :</b> {value}")
    return "\n".join(out)


def mark(on, label):
    """Leech toggle label: '✅️ Label' only when active (auto_style makes it green)."""
    return f"✅️ {label}" if on else label


def pager(prefix, page, pages):
    """⏮ ◀️ x/y ▶️ ⏭ row as (text, data) tuples; prefix + page index."""
    if pages <= 1:
        return []
    return [("⏮", f"{prefix}{0}"), ("◀️", f"{prefix}{(page - 1) % pages}"),
            (f"{page + 1}/{pages}", f"{prefix}{page}"),
            ("▶️", f"{prefix}{(page + 1) % pages}"), ("⏭", f"{prefix}{pages - 1}")]


class Theme(_LegacyTheme):
    FOOTER = "━━━━━━━━⊱♡⊰━━━━━━━━"
    BT_BACK = "◀️"
    BT_BACK_HOME = "◀️"
    BT_CLOSE = "❌"

    # ---------------- start / about / server ----------------
    START = """㊂ <b><u>Hey {name} :</u></b>

<i>I can rename your files, change their thumbnail and caption, convert video ↔ file and extract audio.</i>

<blockquote>╭<b> Rename :</b> <i>custom name, prefix, suffix, regex</i>
┊<b> Thumbnail :</b> <i>your photo or auto TMDB poster</i>
┊<b> Convert :</b> <i>video ↔ file, audio extract</i>
┊<b> Caption :</b> <i>HTML with variables</i>
╰<b> Extras :</b> <i>screenshots, cover, mediainfo, posters</i></blockquote>

<blockquote><b>Send me a video or file to start. Type /help to get a list of available commands</b></blockquote>
<blockquote>Developed by <a href='{dev_link}'><b>{dev_name}</b></a></blockquote>"""
    START_BTNS = {"settings": "Settings", "plans": "Plans", "server": "Server Status", "about": "About",
                  "help": "Help", "group": "Group", "channel": "Channel"}
    ABOUT = """㊂ <b><u>About Bot :</u></b>

<blockquote>╭<b> Bot Name :</b> <a href='https://t.me/{username}'>{bot_name}</a>
┊<b> Version :</b> <code>{version}</code>
┊<b> Language :</b> <a href='https://www.python.org/'>Python 3.13</a>
┊<b> Library :</b> <a href='https://github.com/Tj-Bots/tjgram'>TjGram</a>
╰<b> Channel :</b> <a href='{channel}'>Tj Bots</a></blockquote>

<blockquote>Developed by <a href='{dev_link}'><b>{dev_name}</b></a></blockquote>"""
    ABOUT_SOURCE = "Source Code"
    SERVER = """⌬ <b><i>Server Status :</i></b>

<blockquote>╭<b> CPU :</b> {cpu_bar} {cpu}%
┊<b> RAM :</b> {ram_bar} {ram}%
┊<b> Disk :</b> {disk_bar} {disk}%
╰<b> Tasks :</b> {tasks_bar} {tasks}/{max_tasks}</blockquote>

<blockquote>╭<b> RAM Used :</b> {ram_u} / {ram_t}
┊<b> Disk Free :</b> {disk_f} / {disk_t}
┊<b> Downloads :</b> {dls} | <b>Uploads :</b> {uls}
╰<b> Uptime :</b> {uptime}</blockquote>"""

    MODE_NAMES = {"ask": "Ask", "video": "Video", "file": "File", "swap": "Swap", "audio": "Audio"}
    RENAME_NAMES = {"ask": "Ask", "yes": "Ask", "no": "Never"}
    PLAN_NAMES = {"free": "Free", "test": "Test", "gold": "Gold", "ultra": "Ultra", "admin": "Admin"}
    NOT_SET = "Not Exists"

    # ---------------- /settings (users_settings.py layout) ----------------
    USET_HOME = """㊂ <b><u>User Settings :</u></b>

<blockquote>╭<b> Name :</b> {name} ( <code>{id}</code> )
┊<b> Username :</b> {username}
┊<b> Telegram DC :</b> {dc}
╰<b> Language :</b> {lang}</blockquote>

<blockquote>➲ <u><b>Categories :</b></u>
┊ <b>Upload</b> - video / file / audio, rename prompt
┊ <b>Thumbnail</b> - your photo or auto TMDB poster
┊ <b>Caption</b> - caption text and variables
┊ <b>Rename</b> - prefix, suffix, remove words
┊ <b>Media</b> - screenshots and spoiler
┊ <b>Audio</b> - audio format and quality
┊ <b>Poster</b> - default /poster language and type
╰ <b>Quota</b> - your plan and daily usage</blockquote>"""
    USET_HOME_BTNS = {"upload": "Upload Settings", "thumb": "Thumbnail Settings", "caption": "Caption Settings",
                      "name": "Rename Settings", "media": "Media Settings", "audio": "Audio Settings",
                      "poster": "Poster Settings", "quota": "Quota & Plan", "reset": "Reset Setting"}

    USET_MAIN = """㊂ <b><u>User Settings : {name}</u></b>

<blockquote>╭<b> ID :</b> <code>{id}</code>
┊<b> Upload Type :</b> <i>{mode}</i>
┊<b> Rename Prompt :</b> <i>{rename}</i>
┊<b> Thumbnail :</b> <i>{thumb}</i>
┊<b> Auto Thumbnail :</b> <i>{auto_thumb}</i>
┊<b> Caption :</b> <i>{caption}</i>
┊<b> Prefix :</b> <code>{prefix}</code>
┊<b> Suffix :</b> <code>{suffix}</code>
┊<b> Remname :</b> <code>{remname}</code>
┊<b> Screenshots :</b> <code>{screenshots}</code>
┊<b> Spoiler :</b> <i>{spoiler}</i>
┊<b> Audio :</b> <code>{fmt}</code> / <code>{br}</code>
╰<b> Poster :</b> <code>{lang}</code> / <code>{kind}</code></blockquote>

<blockquote>➲ ✅ marks a setting that is on / customised
➲ Press a button to change it</blockquote>"""
    USET_CHOICE = """㊂ <b><u>{title} : {name}</u></b>

<blockquote>╭<b> Current :</b> <code>{current}</code>
╰<b> Choose :</b> <i>press an option below</i></blockquote>

<blockquote>{info}</blockquote>"""
    USET_CHOICE_INFO = {
        "mode": "➲ <b>Ask</b> - ask me for each file\n┊ <b>Video</b> - streamable video\n┊ <b>File</b> - document\n┊ <b>Swap</b> - video becomes file, file becomes video\n╰ <b>Audio</b> - extract the sound track",
        "fmt": "➲ Used when Upload Type is <b>Audio</b>\n┊ <b>MP3</b> - plays everywhere\n┊ <b>M4A</b> - smaller, same quality\n┊ <b>OPUS</b> - smallest\n╰ <b>FLAC</b> - lossless (quality is ignored)",
        "br": "➲ Bitrate of the extracted audio (ignored for FLAC)",
        "plang": "➲ /poster opens on this language. If a title has no images in it, All is shown\n┊ <b>No Text</b> - clean images without title text\n┊ <b>Original</b> - the language of the movie / series\n╰ <b>My Language</b> - your Telegram app language",
        "pkind": "➲ /poster opens on posters or on backdrops",
    }
    USET_UPLOAD = """㊂ <b><u>Upload Settings : {name}</u></b>

<blockquote>╭<b> Upload Type :</b> <i>{mode}</i>
╰<b> Rename Prompt :</b> <i>{rename}</i></blockquote>

<blockquote>➲ <u><b>Upload Type</b></u> - how every file is sent back
┊ <b>Ask</b> - ask me for each file
┊ <b>Video</b> - streamable video
┊ <b>File</b> - document
┊ <b>Swap</b> - video becomes file, file becomes video
╰ <b>Audio</b> - extract the sound track (see Audio Settings)
➲ <u><b>Rename Prompt</b></u> - when ON, the bot asks for a new name before every upload</blockquote>"""
    USET_THUMB = """㊂ <b><u>Thumbnail Settings : {name}</u></b>

<blockquote>╭<b> Custom Thumbnail :</b> <i>{thumb}</i>
┊<b> Auto Thumbnail :</b> <i>{auto_thumb}</i>
╰<b> TMDB :</b> <i>{tmdb}</i></blockquote>

<blockquote>➲ <u><b>Custom Thumbnail</b></u> - send me any photo (or press Set Thumbnail), it is used for every file
➲ <u><b>Auto Thumbnail</b></u> - without a custom thumbnail, the movie / series poster from TMDB is used
➲ <b>Priority :</b> custom → TMDB poster → video frame</blockquote>"""
    USET_CAPTION = """㊂ <b><u>Caption Settings : {name}</u></b>

<blockquote>╭<b> Custom Caption :</b> <i>{state}</i>
╰<b> Current :</b> <code>{caption}</code></blockquote>

{vars}"""
    CAPTION_VARS = """<blockquote expandable>➲ <u><b>Variables :</b></u>
╭ <code>{filename}</code> - file name
┊ <code>{filesize}</code> - file size
┊ <code>{title}</code> / <code>{year}</code> - clean title / year
┊ <code>{quality}</code> - 1080P, 720P, 4K…
┊ <code>{duration}</code> - video length
╰ <code>{ext}</code> - file extension
➲ HTML allowed: &lt;b&gt; &lt;i&gt; &lt;u&gt; &lt;code&gt; &lt;blockquote&gt;</blockquote>"""
    USET_NAME = """㊂ <b><u>Rename Settings : {name}</u></b>

<blockquote>╭<b> Prefix :</b> <code>{prefix}</code>
┊<b> Suffix :</b> <code>{suffix}</code>
╰<b> Remname :</b> <code>{remname}</code></blockquote>

<blockquote>➲ <u><b>Preview :</b></u>
┊ <code>{example}</code>
╰ <code>{preview}</code></blockquote>

<blockquote>➲ <b>Prefix</b> - text added before the name
➲ <b>Suffix</b> - text added at the end (before the extension)
➲ <b>Remname</b> - remove or replace words (regex)</blockquote>"""
    NAME_EXAMPLE = "www.Site.com - Movie.Name.2023.1080p.WEB-DL.mkv"
    USET_MEDIA = """㊂ <b><u>Media Settings : {name}</u></b>

<blockquote>╭<b> Screenshots :</b> <code>{screenshots}</code> per video
╰<b> Spoiler :</b> <i>{spoiler}</i></blockquote>

<blockquote>➲ <b>Screenshots</b> - photos sent after every video, 0 = off (max 10). Use ➖ / ➕
➲ <b>Spoiler</b> - blur the video and screenshots until tapped</blockquote>"""
    USET_AUDIO = """㊂ <b><u>Audio Settings : {name}</u></b>

<blockquote>╭<b> Format :</b> <code>{fmt}</code>
╰<b> Quality :</b> <code>{br}</code></blockquote>

<blockquote>➲ Used when you choose <b>Audio</b> for a video: the sound track is extracted and sent as a Telegram audio file
┊ <b>MP3</b> - plays everywhere
┊ <b>M4A</b> - smaller, same quality
┊ <b>OPUS</b> - smallest
╰ <b>FLAC</b> - lossless (quality is ignored)</blockquote>"""
    USET_POSTER = """㊂ <b><u>Poster Settings : {name}</u></b>

<blockquote>╭<b> Default Language :</b> <code>{lang}</code>
╰<b> Default Type :</b> <code>{kind}</code></blockquote>

<blockquote>➲ /poster opens on this language and type. If a title has no images in that language, All is shown
➲ <b>No Text</b> - clean images without title text (best for thumbnails)
➲ <b>Original</b> - the language of the movie / series itself
➲ <b>My Language</b> - your Telegram app language</blockquote>"""
    USET_QUOTA = """㊂ <b><u>Quota & Plan : {name}</u></b>

<blockquote>╭<b> Plan :</b> <code>{plan}</code>{expires}
┊<b> Used Today :</b> <code>{used}</code> / <code>{limit}</code> ({failed} failed)
┊<b> Remaining :</b> <code>{remaining}</code>
┊<b> Resets In :</b> <code>{reset}</code>
┊<b> Max File Size :</b> <code>{max_size}</code>
┊<b> Parallel Tasks :</b> <code>{concurrent}</code>
╰<b> Cooldown :</b> <code>{cooldown}</code></blockquote>"""
    USET_QUOTA_EXPIRES = "\n┊<b> Expires In :</b> <code>{left}</code>"
    USET_RESET = """㊂ <b><u>Reset Settings :</u></b>

<blockquote>➲ Upload type, rename prompt, thumbnail, caption, prefix / suffix / remname, auto thumbnail, screenshots, spoiler, audio and poster settings go back to default.
➲ Your plan and quota are kept.</blockquote>"""
    USET_RESET_DONE = "Settings reset to default"

    USET_PROMPT = """㊂ <b><u>Edit {label} :</u></b>

<blockquote>╭<b> Current :</b> <code>{current}</code>
╰<b> Example :</b> <code>{example}</code></blockquote>

<blockquote>➲ {hint}
➲ <i>Send the new value now, or press ◀️ to go back.</i></blockquote>"""
    USET_LABELS = {"caption": "Caption", "prefix": "Prefix", "suffix": "Suffix", "remname": "Remname", "thumb": "Thumbnail", "screenshots": "Screenshots"}
    USET_EXAMPLES = {
        "caption": "<b>{title} ({year})</b> | {quality} | {filesize}",
        "prefix": "@MyChannel - ", "suffix": " - @MyChannel",
        "remname": "www\\S+|\\[.*?\\]|WEB-DL:WEB", "thumb": "any photo", "screenshots": "3",
    }
    USET_HINTS = {
        "caption": "The caption under every file. HTML and variables like <code>{filename}</code> work (max 1024 chars).",
        "prefix": "Text added before every file name (max 64 chars).",
        "suffix": "Text added at the end of every file name, before the extension (max 64 chars).",
        "remname": "Rules separated by <code>|</code> - <code>word</code> removes, <code>old:new</code> replaces, <code>old:new:1</code> replaces once (regex).",
        "thumb": "Send me a photo now - it becomes the thumbnail of all your files.",
        "screenshots": "How many screenshots are sent after every video. Send a number from 0 to 10 (0 = off).",
    }
    USET_SAVED = "{label} saved"
    USET_REMOVED = "{label} removed"
    USET_INVALID = "<b>Invalid value:</b> <code>{err}</code>"
    USET_THUMB_CAPTION = "<b>Custom Thumbnail</b>"

    # ---------------- /bsetting (bot_settings.py layout) ----------------
    BSET_HOME = """㊂ <b><u>Bot Settings :</u></b>

<blockquote>╭<b> Daily Limits (F/T/G/U) :</b> <code>{q}</code>
┊<b> Parallel Tasks (F/T/G/U) :</b> <code>{c}</code>
┊<b> Free Cooldown :</b> <code>{cooldown}</code>
┊<b> Max Size (Free / Premium) :</b> <code>{size}</code>
┊<b> Userbot :</b> <code>{userbot}</code>
╰<b> Maintenance :</b> <code>{maint}</code></blockquote>

<blockquote>➲ <b>Config Variables</b> - edit limits, sizes, prices, userbot session, channels and maintenance
➲ Saved in MongoDB and applied instantly</blockquote>"""
    BSET_VARS = """㊂ <b><u>Config Variables :</u></b>

<blockquote>{lines}</blockquote>

<blockquote>➲ <b>Page :</b> {page}/{pages}
➲ Press a variable to edit it</blockquote>"""
    BSET_EDIT = """㊂ <b><u>Edit {key} :</u></b>

<blockquote>╭<b> Description :</b> <i>{desc}</i>
┊<b> Current :</b> <code>{current}</code>
╰<b> Default :</b> <code>{default}</code></blockquote>

<blockquote>➲ {hint}</blockquote>"""
    BSET_DESC = {
        "FREE_DAILY_LIMIT": "Files per day for Free users", "TEST_DAILY_LIMIT": "Files per day for Test plan",
        "GOLD_DAILY_LIMIT": "Files per day for Gold plan", "ULTRA_DAILY_LIMIT": "Files per day for Ultra plan",
        "MAX_CONCURRENT_FREE": "Parallel tasks for Free users", "MAX_CONCURRENT_TEST": "Parallel tasks for Test plan",
        "MAX_CONCURRENT_GOLD": "Parallel tasks for Gold plan", "MAX_CONCURRENT_ULTRA": "Parallel tasks for Ultra plan",
        "COOLDOWN_NORMAL": "Seconds a Free user waits between files",
        "MAX_FILE_SIZE_NORMAL": "Biggest file a Free user can send",
        "MAX_FILE_SIZE_PREMIUM": "Biggest file a premium user can send",
        "MAINTENANCE": "Block everyone except admin", "MAINTENANCE_MSG": "Note shown to users during maintenance",
        "MAX_CONCURRENT_ADMIN": "Parallel tasks for the admin",
        "SESSION_STRING": "Premium userbot session - enables 4GB uploads, applied instantly",
        "DUMP_CHANNEL": "Channel id the userbot uploads big files to",
        "GOLD_STARS_PRICE": "Gold price in Telegram Stars", "ULTRA_STARS_PRICE": "Ultra price in Telegram Stars",
        "GOLD_PRICE": "Gold price text shown in Plans", "ULTRA_PRICE": "Ultra price text shown in Plans",
        "TEST_PRICE": "Test plan price text shown in Plans",
        "TEST_DURATION_DAYS": "Days the free Test plan lasts", "PREMIUM_DAYS": "Days a paid Gold / Ultra plan lasts",
        "DEVELOPER_NAME": "Name shown in the bot footer", "DEVELOPER_USERNAME": "Contact username for plans (no @)",
        "CHANNEL_LINK": "Channel link shown in About",
    }
    BSET_HINTS = {
        "int": "Send a whole number (0 - 100000).",
        "size": "Send a size like <code>1950MB</code>, <code>2GB</code>, <code>4G</code> (max 4GB).",
        "text": "Send the note (HTML allowed, max 500 chars). Send <code>-</code> to clear.",
        "bool": "Use the buttons below.",
        "str": "Send the new value (max 100 chars). Send <code>-</code> for the default.",
        "chatid": "Send a chat id like <code>-1001234567890</code>.",
        "secret": "Send the Pyrogram session string. Your message is deleted right away. Send <code>-</code> to go back to the .env one.",
    }
    BSET_BTNS = {"vars": "Config Variables", "reset_all": "Reset All Config", "default": "Default",
                 "on": "Enable", "off": "Disable", "yes": "Yes!, Reset"}
    BSET_SAVED = "{label} = {value}"
    BSET_LABELS = {k: k for k in BSET_DESC}
    BSET_RESET_DONE = "All bot settings reset to default"
    BSET_RESET_CONFIRM = """㊂ <b><u>Reset Config :</u></b>

<blockquote>➲ Every config variable goes back to the value in the code / .env (the userbot goes back to the .env session).
➲ Users' plans are not touched.</blockquote>"""
    BSET_INVALID = "<b>Invalid value:</b> <code>{err}</code>"
    ADMIN_ONLY = "Admins only!"

    ADMIN_PANEL = """㊂ <b><u>Admin Panel :</u></b>

<blockquote>╭<b> Admin :</b> <code>{admin}</code>
┊<b> Users :</b> <code>{users}</code>
┊<b> Banned :</b> <code>{banned}</code>
┊<b> Test / Gold / Ultra :</b> <code>{test}</code> / <code>{gold}</code> / <code>{ultra}</code>
┊<b> Redeem Codes :</b> <code>{redeem}</code>
╰<b> Maintenance :</b> <code>{maint}</code></blockquote>

<blockquote expandable>➲ <u><b>Commands :</b></u>
╭ /broadcast - reply to a message (<code>-f</code> to forward)
┊ /ban /unban <code>[id]</code> · /users · /allban
┊ /add_plan <code>[id] [test/gold/ultra] [duration]</code>
┊ /remove_plan <code>[id]</code> · /plan_list
┊ /gencodes <code>[count] [duration] [plan]</code> · /redeem_stats
┊ /bsetting · /stats · /speedtest
╰ /cancelall · /restart</blockquote>"""
    ADMIN_BTNS = {"bset": "Bot Settings", "stats": "Bot Stats", "maint": "Maintenance"}

    MAINTENANCE = """㊂ <b><u>Under Maintenance :</u></b>

<blockquote>➲ The bot is being upgraded right now. Please try again a little later.</blockquote>{note}"""
    MAINTENANCE_NOTE = "\n<blockquote>➲ <b>Note :</b> {note}</blockquote>"
    MAINTENANCE_ALERT = "The bot is under maintenance. Please try again later."

    # ---------------- help ----------------
    HELP_HEADER = "㊂ <b><i>Help Guide Menu!</i></b>\n\n<b>NOTE: <i>Click on any category to see more details.</i></b>"
    HELP_BTNS = {"thumb": "Thumbnail", "cap": "Caption", "redeem": "Redeem", "cmds": "Commands", "settings": "Settings"}
    HELP_THUMB = """㊂ <b><u>Thumbnail :</u></b>

<blockquote>╭ Send any photo - it becomes your thumbnail
┊ It is applied to all your next files
╰ /settings → Thumbnail Settings → Auto Thumbnail (TMDB poster)</blockquote>

<blockquote>╭ /viewthumb - view your thumbnail
╰ /delthumb - delete your thumbnail</blockquote>"""
    HELP_CAP = """㊂ <b><u>Caption :</u></b>

<blockquote>➲ <code>/set_cap</code> + your caption, or /settings → Caption Settings</blockquote>

""" + CAPTION_VARS + """

<blockquote>➲ <u><b>Examples :</b></u>
╭ <code>/set_cap &lt;b&gt;{title} ({year})&lt;/b&gt;</code>
╰ <code>/set_cap &lt;b&gt;{filename}&lt;/b&gt; | {quality} | {filesize}</code></blockquote>

<blockquote>╭ /see_caption - view current caption
╰ /del_caption - reset to default</blockquote>"""
    HELP_REDEEM = """㊂ <b><u>Redeem Codes :</u></b>

<blockquote>╭ Get a code from the admin
┊ Send <code>/redeem CODE</code>
╰ Each user can redeem only one code</blockquote>

<blockquote>➲ <b>Example :</b> <code>/redeem ABC12345</code></blockquote>"""
    HELP_COMMANDS = """㊂ <b><u>Commands :</u></b>

<blockquote>╭ /start - start the bot
┊ /help - this menu
┊ /settings - all your settings
┊ /status - your active tasks
┊ /cancel <code>N</code> - cancel task N
┊ /mediainfo - reply to media / link
┊ /cover - reply to a video: add cover
┊ /poster or /p - search posters & backdrops
┊ /ping - bot latency
╰ /plans - premium plans</blockquote>

<blockquote>╭ /viewthumb · /delthumb - thumbnail
┊ /set_cap · /see_caption · /del_caption - caption
╰ /redeem <code>CODE</code> - redeem a code</blockquote>"""

    # ---------------- file flow ----------------
    ASK_TARGET = """㊂ <b><u>Choose Output :</u></b>

<blockquote>╭<b> Name :</b> <code>{name}</code>
╰<b> Size :</b> {size}</blockquote>

<blockquote>➲ <b>Video</b> - streamable video
➲ <b>File</b> - document
➲ <b>Audio</b> - extract the sound track ({fmt})</blockquote>"""
    ASK_BTNS = {"video": "Video", "file": "File", "audio": "Audio", "cancel": "❌ Cancel"}
    RENAME_ASK = """㊂ <b><u>Rename File :</u></b>

<blockquote>╭<b> Current :</b> <code>{name}</code>
╰<b> Output :</b> <i>{target}</i></blockquote>

<blockquote>➲ Send the new name now (the extension is added automatically), or keep the original name.</blockquote>"""
    RENAME_BTNS = {"keep": "Keep Original", "cancel": "❌ Cancel"}
    STARTING = "<i>Starting...</i>"
    CANCELLED = "<b>Task Cancelled!</b>\n<blockquote>╰<b> Name :</b> <code>{name}</code></blockquote>"
    TASK_ERROR = "<b>Task Failed!</b>\n<blockquote>╰<b> Error :</b> <code>{err}</code></blockquote>"
    BUSY_FREE = """<b>Task Limit Reached!</b>

<blockquote>╭<b> Active :</b> <code>{active}/{limit}</code>
╰ Free users can convert {limit} file(s) at a time</blockquote>

<blockquote>➲ Upgrade your plan to convert more files at once.</blockquote>"""
    BUSY = "<b>Task Limit Reached!</b>\n<blockquote>╭<b> Active :</b> <code>{active}/{limit}</code>\n╰ Wait for one to finish or cancel one.</blockquote>"
    BUSY_BTN = "Upgrade Plan"
    COOLDOWN = "<b>Cooldown Active!</b>\n<blockquote>╰ Please wait <code>{sec}s</code> before sending another file.</blockquote>"
    THUMB_SAVED = "<b>Thumbnail Saved!</b>\n<blockquote>╰ It will be used for all your next files.</blockquote>"
    THUMB_DELETED = "<b>Thumbnail Deleted!</b>"
    NO_THUMB = "<b>No Thumbnail Set!</b>\n<blockquote>╰ Send me any photo to set one.</blockquote>"
    BANNED = "<b>You are banned from using this bot.</b>"

    # ---------------- audio ----------------
    AUDIO_FORMATS = {"mp3": ("MP3", "libmp3lame", "mp3"), "m4a": ("M4A", "aac", "m4a"),
                     "opus": ("OPUS", "libopus", "ogg"), "flac": ("FLAC", "flac", "flac")}
    AUDIO_BITRATES = ("128k", "192k", "256k", "320k")
    AUDIO_NO_TRACK = "<b>No audio track found in this file.</b>"
    AUDIO_CONVERTING = "Extracting audio"

    # ---------------- mediainfo / cover / poster ----------------
    MEDIAINFO_HELP = """㊂ <b><u>MediaInfo :</u></b>

<blockquote>╭ Reply to a video / audio / document with <code>/mediainfo</code>
╰ Or send a direct link: <code>/mediainfo https://…/file.mkv</code></blockquote>"""
    MEDIAINFO_DONE = """㊂ <b><u>MediaInfo :</u></b>

<blockquote>╭<b> Name :</b> <code>{name}</code>
╰<b> Report :</b> <a href='{url}'>Open on Telegraph</a></blockquote>"""
    COVER_HELP = """㊂ <b><u>Cover :</u></b>

<blockquote>➲ Reply to a <b>video</b> with <code>/cover</code> to re-send it with your thumbnail (or an auto TMDB poster) as the video cover. No re-upload.</blockquote>"""
    COVER_NEED_THUMB = "<blockquote>➲ Set a custom thumbnail (send a photo) or enable Auto Thumbnail in /settings to use /cover</blockquote>"
    COVER_NOT_FOUND = "<b>No poster found for this file name.</b>"
    INFO_HELP = """㊂ <b><u>Poster Search :</u></b>

<blockquote>╭ <code>/poster Oppenheimer 2023</code> (or <code>/p</code>)
┊ or reply to a video / file with <code>/p</code>
╰ browse posters & backdrops by language, set one as thumbnail or get the original</blockquote>"""
    INFO_NOT_FOUND = "<b>Nothing found on TMDB.</b>"

    POSTER_SEARCHING = "<i>Searching TMDB for</i> <code>{query}</code><i>...</i>"
    POSTER_RESULTS = """㊂ <b><u>Poster Search :</u></b>

<blockquote>╭<b> Query :</b> <code>{query}</code>
┊<b> Results :</b> <code>{count}</code>
╰<b> Page :</b> <code>{page}/{pages}</code></blockquote>

<blockquote>➲ Press a title to browse its posters & backdrops</blockquote>"""
    POSTER_ITEM = "{title} ({year})"
    POSTER_CAPTION = """<b>{title} ({year})</b>

<blockquote>╭<b> TMDB :</b> <a href='{url}'>{url_short}</a>
┊<b> Type :</b> <i>{type}</i>
┊<b> Language :</b> <i>{lang}</i>
┊<b> Size :</b> <code>{w} x {h}</code>
╰<b> Image :</b> <code>{i}/{n}</code></blockquote>"""
    POSTER_LANG_PICK = """㊂ <b><u>Poster Language : {title}</u></b>

<blockquote>➲ Choose which images to show. The number is how many images exist in that language.</blockquote>"""
    POSTER_KINDS = {"p": "Poster", "b": "Backdrop"}
    POSTER_KINDS_PL = {"p": "Posters", "b": "Backdrops"}
    POSTER_ORIENT = {"portrait": "Portrait", "landscape": "Landscape"}
    POSTER_BT = {"thumb": "Set Thumbnail", "thumb_on": "✅️ Thumbnail Set", "orig": "Send Original",
                 "more": "More", "all": "All", "close": "❌"}
    POSTER_ORIG_CAPTION = "<b>{title} ({year})</b>\n<blockquote>╰ <code>{type} · {w}x{h} · {lang}</code></blockquote>"
    POSTER_THUMB_SET = "Thumbnail set"
    POSTER_THUMB_REMOVED = "Thumbnail removed"
    POSTER_SENDING = "Sending the original file..."
    POSTER_NO_IMAGES = "No images on TMDB for this title."
    POSTER_EXPIRED = "This search expired. Run /poster again."
    POSTER_NOT_YOURS = "Only the user who searched can use these buttons!"
    POSTER_LOAD_FAIL = "Could not load this image, try another one."
    POSTER_SEARCH_FAIL = "<b>TMDB search failed, try again later.</b>"
    POSTER_NO_KEY = "<b>TMDB_API_KEY is not configured.</b>"
    POSTER_NO_TEXT = "No Text"
    POSTER_LANG_OPTS = {"all": "All", "en": "English", "ul": "My Language", "xx": "No Text", "orig": "Original"}

    # ---------------- /stats (wzml_minimal BOT_STATS / SYS_STATS / BOT_LIMITS) ----------------
    STATS_BOT = """⌬ <b><i>BOT STATISTICS :</i></b>
╰ <b>Bot Uptime :</b> {bot_uptime}

<blockquote>╭ <b><i>RAM ( MEMORY ) :</i></b>
┊ {ram_bar} {ram}%
╰ <b>U :</b> {ram_u} | <b>F :</b> {ram_f} | <b>T :</b> {ram_t}</blockquote>

<blockquote>╭ <b><i>SWAP MEMORY :</i></b>
┊ {swap_bar} {swap}%
╰ <b>U :</b> {swap_u} | <b>F :</b> {swap_f} | <b>T :</b> {swap_t}</blockquote>

<blockquote>╭ <b><i>DISK :</i></b>
┊ {disk_bar} {disk}%
┊ <b>Total Disk Read :</b> {disk_read}
┊ <b>Total Disk Write :</b> {disk_write}
╰ <b>U :</b> {disk_u} | <b>F :</b> {disk_f} | <b>T :</b> {disk_t}</blockquote>"""
    STATS_SYS = """⌬ <b><i>OS SYSTEM :</i></b>
<blockquote>╭ <b>OS Uptime :</b> {os_uptime}
┊ <b>OS Version :</b> {os_version}
╰ <b>OS Arch :</b> {os_arch}</blockquote>

⌬ <b><i>NETWORK STATS :</i></b>
<blockquote>╭ <b>Upload Data:</b> {up_data}
┊ <b>Download Data:</b> {dl_data}
┊ <b>Pkts Sent:</b> {pkt_sent}k
┊ <b>Pkts Received:</b> {pkt_recv}k
╰ <b>Total I/O Data:</b> {tl_data}</blockquote>

⌬ <b><i>CPU :</i></b>
<blockquote>╭ {cpu_bar} {cpu}%
┊ <b>CPU Frequency :</b> {cpu_freq}
┊ <b>System Avg Load :</b> {sys_load}
┊ <b>P-Core(s) :</b> {p_core} | <b>V-Core(s) :</b> {v_core}
╰ <b>Total Core(s) :</b> {total_core}</blockquote>"""
    STATS_LIMITS = """⌬ <b><i>BOT LIMITATIONS :</i></b>
<blockquote>╭ <b>Daily (F/T/G/U) :</b> {q_free} / {q_test} / {q_gold} / {q_ultra}
┊ <b>Parallel (F/T/G/U) :</b> {c_free} / {c_test} / {c_gold} / {c_ultra}
┊ <b>Free Cooldown :</b> {cooldown}
╰ <b>Max Size :</b> {size_n} / premium {size_p}</blockquote>

<blockquote>╭ <b>UserBot (4GB) :</b> {userbot}
╰ <b>Maintenance :</b> {maint}</blockquote>"""
    STATS = """⌬ <b><i>USER STATISTICS :</i></b>
<blockquote>╭ <b>Users :</b> {users}
┊ <b>Premium :</b> {premium}
┊ <b>With Thumbnail :</b> {thumbs}
┊ <b>Banned :</b> {banned}
┊ <b>Active Tasks :</b> {tasks}
╰ <b>Uptime :</b> {uptime}</blockquote>"""
    STATS_BTNS = {"bot": "Bot Stats", "sys": "OS Stats", "lim": "Bot Limits", "usr": "User Stats"}

    SPEED_START = "<i>Initiating Speedtest...</i>"
    SPEED_RESULT = """➲ <b><i>SPEEDTEST INFO</i></b>
<blockquote>╭ <b>Upload:</b> <code>{up}/s</code> (<code>{up_mbps} Mbps</code>)
┊ <b>Download:</b> <code>{dl}/s</code> (<code>{dl_mbps} Mbps</code>)
┊ <b>Ping:</b> <code>{ping} ms</code>
┊ <b>Time:</b> <code>{time}</code>
┊ <b>Data Sent:</b> <code>{sent}</code>
╰ <b>Data Received:</b> <code>{recv}</code></blockquote>

➲ <b><i>SPEEDTEST SERVER</i></b>
<blockquote>╭ <b>Provider:</b> <code>Cloudflare</code>
┊ <b>Datacenter:</b> <code>{colo}</code>
╰ <b>Country:</b> <code>{loc}</code></blockquote>"""
    SPEED_FAIL = "<b>ERROR:</b> <i>Speedtest failed: {err}</i>"
    PING = "<i>Starting Ping..</i>"
    PING_VALUE = "<b>Pong</b>\n╰ <code>{ms} ms..</code>"
    RESTARTING = "<i>Restarting...</i>"
    RESTART_SUCCESS = """⌬ <b><i>Restarted Successfully!</i></b>
<blockquote>╭ <b>Date:</b> {date}
┊ <b>Time:</b> {time}
┊ <b>TimeZone:</b> {tz}
╰ <b>Version:</b> {version}</blockquote>"""

    # ---------------- task status (get_readable_message) ----------------
    STATUS_TASK = """<blockquote>╭ <b>Name:</b> <code>{name}</code>
┊ {bar} {percent:.2f}%
┊ <b>{processed_label}:</b> {done} of {total}
┊ <b>Status:</b> {status} | <b>ETA:</b> {eta}
┊ <b>Speed:</b> {speed}/s | <b>Elapsed:</b> {elapsed}
┊ <b>Engine:</b> TjGram | <b>Mode:</b> {mode_tag}
┊ <b>User:</b> <code>{user}</code> | <b>ID:</b> #{pos}
╰ /cancel {pos}</blockquote>"""
    STATUS_CANCELLED = "<blockquote>╭ <b>Name:</b> <code>{name}</code>\n╰ <b>Status:</b> Cancelled</blockquote>"
    STATUS_FOOTER = """<blockquote>╭ <b>CPU:</b> {cpu}% | <b>F:</b> {free} [{free_p}%]
┊ <b>RAM:</b> {ram}% | <b>UPTIME:</b> {uptime}
╰ <b>DL:</b> {dl}/s | <b>UL:</b> {ul}/s</blockquote>"""
    NO_ACTIVE = "<i>No Active Tasks!</i>\n\n{footer}"
    STATUS_NAMES = {"downloading": "Download", "uploading": "Upload", "converting": "Convert"}

    # ---------------- plans ----------------
    USER_STATS = """㊂ <b><u>Your Plan : {name}</u></b>

<blockquote>╭<b> Plan :</b> <code>{plan}</code>{expires}
┊<b> Daily Limit :</b> <code>{limit}</code> files
┊<b> Used Today :</b> <code>{used}</code> ({failed} failed)
┊<b> Remaining :</b> <code>{remaining}</code>
╰<b> Next Reset :</b> <code>{reset}</code></blockquote>

<blockquote>➲ Choose a plan below to see what it gives</blockquote>"""
    PLAN = """㊂ <b><u>{title} :</u></b>

<blockquote>╭<b> Price :</b> {price}
{duration}┊<b> Daily Limit :</b> <code>{daily}</code> files
┊<b> Max File Size :</b> <code>{size}</code>
┊<b> Parallel Tasks :</b> <code>{conc}</code>
╰<b> Cooldown :</b> <code>{cooldown}</code></blockquote>{extra}"""
    PLAN_DURATION = "┊<b> Duration :</b> {days} days\n"
    PLAN_TITLES = {"free": "Free Plan", "test": "Test Plan", "gold": "Gold Plan", "ultra": "Ultra Plan"}
    PLAN_BTNS = {"free": "Free", "test": "Test", "gold": "Gold", "ultra": "Ultra", "refresh": "♻️ Refresh",
                 "get_test": "Activate Test (Free)", "buy": "Buy with {stars} Stars", "contact": "Contact Admin"}
    PLAN_TEST_ONCE = "\n<blockquote>➲ You can get the Test plan only once.</blockquote>"
    PLAN_TEST_FREE = "\n<blockquote>➲ One-time free trial!</blockquote>"
    TEST_ACTIVATED = "<b>Test Plan Activated!</b>\n<blockquote>╰<b> Active Until :</b> <code>{date}</code></blockquote>"
