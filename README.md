<div align="center">

# TJ Rename Bot

**Rename, convert and manage Telegram files - with TMDB posters, MediaInfo and a full admin panel.**

[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Pyrofork](https://img.shields.io/badge/Pyrofork-MTProto-2CA5E0?logo=telegram&logoColor=white)](https://github.com/Mayuri-Chan/pyrofork)
[![Demo](https://img.shields.io/badge/Demo-@TJRenameBot-2CA5E0?logo=telegram&logoColor=white)](https://t.me/TJRenameBot)

</div>

---

## Features

- **Rename and convert** - any video or document, Video <-> File, audio extraction (MP3 / M4A / OPUS / FLAC).
- **Thumbnails** - custom thumbnail, or an automatic TMDB poster / video frame.
- **Captions and names** - HTML captions with variables, prefix, suffix and regex *remname* rules.
- **Screenshots and spoiler** - up to 10 screenshots per video, optional spoiler.
- **`/poster`** - browse TMDB posters and backdrops by language, send the original or set it as thumbnail.
- **`/mediainfo`** - full MediaInfo of any file or direct link.
- **`/cover`** - add a cover to a video without re-uploading it.
- **Plans** - Free / Test / Gold / Ultra with daily limits, size limits, cooldowns and Stars payments.
- **Redeem codes**, broadcast, bans, user stats, speedtest and live server stats.
- **Premium userbot** - uploads up to 4 GB through a user session, which can be added from the bot itself.
- **Auto update** - on every start the bot pulls the latest code from this repository.

## Settings

| Command | Who | What |
|---|---|---|
| `/settings` | everyone | Personal settings: upload type, thumbnail, caption, prefix / suffix / remname, screenshots, audio, poster defaults |
| `/bsetting` | admin | Bot settings stored in MongoDB and applied instantly - limits, sizes, prices, plan days, channels, maintenance mode and the premium `SESSION_STRING` |

## Commands

| Command | Aliases | Admin | Description |
|---|---|:---:|---|
| `/start` | | | Start the bot |
| `/help` | `/h` | | Help menu |
| `/settings` | `/us` `/usetting` | | Your settings |
| `/status` | `/s` | | Active tasks and server load |
| `/cancel <id>` | `/cn` | | Cancel a task |
| `/plans` | `/pl` | | Premium plans |
| `/redeem <code>` | | | Activate a code |
| `/poster <title>` | `/p` | | TMDB posters and backdrops |
| `/mediainfo` | `/mi` | | MediaInfo of a replied file or link |
| `/cover` | `/c` | | Add a cover to a replied video |
| `/set_cap` `/see_caption` `/del_cap` | | | Caption |
| `/viewthumb` `/delthumb` | | | Thumbnail |
| `/ping` | | | Latency |
| `/bsetting` | `/bs` | yes | Bot settings |
| `/admin` | `/ad` | yes | Admin panel |
| `/stats` | `/st` | yes | Bot statistics |
| `/speedtest` | `/sp` | yes | Server speedtest |
| `/broadcast` | `/bc` | yes | Message all users |
| `/gencodes` `/redeem_stats` | | yes | Redeem codes |
| `/add_plan` `/remove_plan` `/plan_list` | | yes | Manage premium users |
| `/users` `/ban` `/unban` `/allban` | | yes | Users and bans |
| `/cancelall` | `/ca` | yes | Cancel every task |
| `/restart` | `/r` | yes | Restart the bot |

## Setup

### Requirements

- Python 3.13+, `ffmpeg` and `mediainfo`
- A MongoDB database (Atlas free tier is enough)
- Telegram `API_ID` / `API_HASH` from [my.telegram.org](https://my.telegram.org) and a bot token from [@BotFather](https://t.me/BotFather)

### Run on a VPS

```bash
sudo apt update && sudo apt install -y python3-pip python3-venv ffmpeg mediainfo git
git clone https://github.com/Tj-Bots/TJ-Rename-Bot.git
cd TJ-Rename-Bot
python3 -m venv venv && venv/bin/pip install -r requirements.txt
cp .env.example .env        # fill in your values
venv/bin/python main.py
```

Keep it running with `pm2` or `screen`. `/restart` re-executes the process, so no external restart is needed.

### Run with Docker

```bash
cp .env.example .env        # fill in your values
docker compose up -d --build
docker compose logs -f
```

## Configuration (`.env`)

| Variable | Description | Required |
|---|---|:---:|
| `API_ID` | Telegram API ID | yes |
| `API_HASH` | Telegram API hash | yes |
| `BOT_TOKEN` | Bot token from @BotFather | yes |
| `ADMIN_ID` | Numeric Telegram ID of the admin | yes |
| `MONGO_URI` | MongoDB connection string | yes |
| `DUMP_CHANNEL` | Channel ID (`-100...`) used to store uploads | yes |
| `DB_NAME` | Database name, default `tj_rename` | no |
| `SESSION_STRING` | Pyrogram session of a premium account, enables 4 GB uploads (can also be set in `/bsetting`) | no |
| `TMDB_API_KEY` | Enables `/poster`, auto thumbnail and auto cover | no |
| `TMDB_IMAGE_LANGS` | Extra TMDB image languages, e.g. `en,he` | no |
| `AUTO_UPDATE` | `false` disables the update on start, default `true` | no |
| `UPSTREAM_BRANCH` | Branch to update from, default `main` | no |

## Auto update

On every start `updater.py` fetches this repository and fast-forwards to the latest commit.

- Only files tracked by git are changed. `.env`, sessions, downloads and every other local file are never touched.
- Nothing happens when there are local edits to tracked files, local commits that are not on GitHub, or no connection.
- New code is compiled before it is used. If it does not compile, the update is rolled back.
- `requirements.txt` changes are installed automatically.

Set `AUTO_UPDATE=false` to turn it off.

## Links

- Demo bot: [@TJRenameBot](https://t.me/TJRenameBot)
- Updates: [@Tj_Bots](https://t.me/Tj_Bots)
- Group: [@TJ_Bots_Chat](https://t.me/TJ_Bots_Chat)
- Developer: [The Joker](https://t.me/The_Joker121_bot)
