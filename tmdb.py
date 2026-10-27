"""Auto thumbnail from TMDB (ported from Leech-TJ tmdb_utils).

No extra dependencies: HTTP via urllib (run in a thread), image resize via ffmpeg.
Telegram thumbnail limits: JPEG, max 320px on each side, under 200KB.
"""
import asyncio
import json
import logging
import os
import re
import urllib.parse
import urllib.request

logger = logging.getLogger(__name__)

TMDB_KEY = os.getenv("TMDB_API_KEY", "").strip()
SEARCH_URL = "https://api.themoviedb.org/3/search/multi"
IMAGE_URL = "https://image.tmdb.org/t/p/w500"

_QUALITY_TAGS = re.compile(
    r"\b(?:\d{3,4}p|4k|x26[45]|h\.?26[45]|hevc|avc|xvid|divx|aac\d?|ac3|eac3|ddp?\d(?:\.\d)?"
    r"|dts(?:-hd)?|truehd|atmos|hdr\d*|10bit|8bit|web-?dl|web-?rip|blu-?ray|bd-?rip"
    r"|br-?rip|hd-?rip|dvd-?rip|hdts|cam-?rip|hdtv|remux|repack|esubs?|msubs?|subbed"
    r"|dubbed|dsnp|amzn|hmax|hotstar|predvd|hq|mkv|mp4|m4v|avi|webm|mpe?g|rar|zip|7z|part\d+|cd\d+)\b",
    re.IGNORECASE,
)
_SITE_PREFIX = re.compile(
    r"^\W*(?:www\.)?[\w-]+\.(?:com|net|org|xyz|me|in|to|co|cc|info|tv|link|app|online"
    r"|site|club|work|icu|top|vip|pro|party|fun|cam|lol|sbs|ws)"
    r"(?:\s*[-–—]+\s*|\s+)",
    re.IGNORECASE,
)
_cache = {}


def _tidy(t):
    t = re.sub(r"\s-+\s", " ", t)
    return re.sub(r"\s+", " ", t).strip(" -_.")


def _final_clean(t):
    base = re.sub(r"[\[\](){}]", " ", t)
    return _tidy(_QUALITY_TAGS.sub(" ", base)) or _tidy(base)


def clean_title(raw):
    """File name -> (search title, year or None)."""
    t = urllib.parse.unquote(raw)
    t = re.sub(r"https?://\S+", " ", t)
    t = re.sub(r"\b(?:t|telegram)\.me/\S+", " ", t, flags=re.I)
    t = re.sub(r"@\w+", " ", t)
    t = re.sub(r"\[[^\]]*\]", " ", t)
    t = re.sub(r"[\[\](){}]", " ", t)
    t = re.sub(r"\.\w{2,4}$", "", t)
    t = _SITE_PREFIX.sub("", t)
    t = t.replace("_", " ")
    if _QUALITY_TAGS.search(t):
        t = re.sub(r"-\w+$", "", t)
    t = re.sub(r"\s+", " ", t.replace(".", " ")).strip()
    for pat in (
        r"(?<!\w)S0*\d{1,2}\s?E\d{1,3}(?!\w)",
        r"\bSeason\s+\d{1,2}\b",
        r"(?<!\w)S0*\d{1,2}(?!\w)",
        r"(?<!\w)(?:E|EP|EPISODE)\s?\d{1,4}(?!\w)",
    ):
        m = re.search(pat, t, re.I)
        if m:
            head, tail = t[:m.start()].strip(), t[m.end():].strip()
            return _final_clean(head if len(head) > 1 else tail), None
    years = list(re.finditer(r"\b(?:19|20)\d{2}\b", t))
    if years:
        y = years[-1]
        head, tail = t[:y.start()].strip(), t[y.end():].strip()
        return _final_clean(head if len(head) > 1 else tail), y.group(0)
    return _final_clean(t), None


def _http_json(url, params):
    full = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(full, headers={"accept": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)


def _http_bytes(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read()


def _find_poster_path(title, year):
    data = _http_json(SEARCH_URL, {"api_key": TMDB_KEY, "query": title, "include_adult": "false"})
    results = [r for r in data.get("results", []) if r.get("media_type") != "person"]
    if not results:
        return None
    pick = results[0]
    if year:
        for r in results:
            if (r.get("release_date") or r.get("first_air_date") or "").startswith(year):
                pick = r
                break
    return {"p": pick.get("poster_path") or pick.get("backdrop_path"),
            "b": pick.get("backdrop_path") or pick.get("poster_path")}


async def _resize(src, dst):
    """ffmpeg: fit inside 320x320, JPEG, shrink quality until < 200KB."""
    for q in (3, 6, 10, 15):
        proc = await asyncio.create_subprocess_exec(
            "ffmpeg", "-y", "-loglevel", "error", "-i", src,
            "-vf", "scale=320:320:force_original_aspect_ratio=decrease",
            "-frames:v", "1", "-q:v", str(q), dst,
            stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL,
        )
        await proc.wait()
        if os.path.exists(dst) and os.path.getsize(dst) < 200 * 1024:
            return True
    return os.path.exists(dst)


async def get_auto_thumbnail(filename, out_path, landscape=False):
    """Download a TMDB poster for `filename` and save it as a Telegram-ready
    thumbnail at out_path. Returns out_path, or None when nothing was found."""
    if not TMDB_KEY:
        return None
    title, year = clean_title(filename)
    if len(title) < 2:
        return None
    key = (title.lower(), year)
    try:
        if key not in _cache:
            _cache[key] = await asyncio.to_thread(_find_poster_path, title, year)
            if len(_cache) > 300:
                _cache.clear()
        path = (_cache[key] or {}).get("b" if landscape else "p")
        if not path:
            logger.info(f"TMDB: no result for '{title}' ({year})")
            return None
        raw = await asyncio.to_thread(_http_bytes, f"{IMAGE_URL}{path}")
        tmp = out_path + ".src"
        with open(tmp, "wb") as f:
            f.write(raw)
        ok = await _resize(tmp, out_path)
        try:
            os.remove(tmp)
        except OSError:
            pass
        if ok:
            logger.info(f"TMDB auto thumbnail for '{title}' ({year})")
            return out_path
    except Exception as e:
        logger.warning(f"TMDB auto thumbnail failed for '{title}': {e}")
    return None


async def get_auto_cover(filename, out_path):
    """Landscape TMDB backdrop (w1280) for use as a video cover.
    Returns out_path or None."""
    if not TMDB_KEY:
        return None
    title, year = clean_title(filename or "")
    if len(title) < 2:
        return None
    key = (title.lower(), year)
    try:
        if key not in _cache:
            _cache[key] = await asyncio.to_thread(_find_poster_path, title, year)
            if len(_cache) > 300:
                _cache.clear()
        path = (_cache[key] or {}).get("b")
        if not path:
            return None
        raw = await asyncio.to_thread(_http_bytes, f"{IMG_BASE}w1280{path}")
        with open(out_path, "wb") as f:
            f.write(raw)
        return out_path
    except Exception as e:
        logger.warning(f"TMDB cover failed for '{title}': {e}")
    return None


def _fetch_info(title, year):
    data = _http_json(SEARCH_URL, {"api_key": TMDB_KEY, "query": title, "include_adult": "false"})
    results = [r for r in data.get("results", []) if r.get("media_type") in ("movie", "tv")]
    if not results:
        return None
    pick = results[0]
    if year:
        for r in results:
            if (r.get("release_date") or r.get("first_air_date") or "").startswith(year):
                pick = r
                break
    kind = pick["media_type"]
    d = _http_json(f"https://api.themoviedb.org/3/{kind}/{pick['id']}", {"api_key": TMDB_KEY})
    d["media_type"] = kind
    return d


async def get_info(query):
    """Movie/series details from TMDB for a title or file name (Leech-TJ /imdb style).
    Returns dict or None."""
    if not TMDB_KEY:
        return None
    title, year = clean_title(query)
    if len(title) < 2:
        return None
    try:
        return await asyncio.to_thread(_fetch_info, title, year)
    except Exception as e:
        logger.warning(f"TMDB info failed for '{title}': {e}")
        return None


async def get_poster_bytes(info):
    path = info.get("poster_path") or info.get("backdrop_path")
    if not path:
        return None
    try:
        return await asyncio.to_thread(_http_bytes, f"{IMAGE_URL}{path}")
    except Exception:
        return None


IMG_BASE = "https://image.tmdb.org/t/p/"
SEARCH_PAGES = 2
IMAGE_LANGS = os.getenv("TMDB_IMAGE_LANGS", "").strip()
_LANG_RANK = {"en": 0, None: 1}


def _search_titles(title, year, raw):
    out, seen = [], set()
    for q in dict.fromkeys(x for x in (title, raw) if x and len(x) > 1):
        for page in range(1, SEARCH_PAGES + 1):
            d = _http_json(SEARCH_URL, {"api_key": TMDB_KEY, "query": q, "include_adult": "false", "page": page})
            for r in d.get("results", []):
                kind = r.get("media_type")
                name = r.get("title") or r.get("name")
                if kind not in ("movie", "tv") or not name or (kind, r["id"]) in seen:
                    continue
                seen.add((kind, r["id"]))
                out.append({"id": r["id"], "kind": kind, "title": name,
                            "year": (r.get("release_date") or r.get("first_air_date") or "")[:4],
                            "lang": r.get("original_language")})
            if page >= (d.get("total_pages") or 1):
                break
        if out:
            break
    if year:
        out.sort(key=lambda r: r["year"] != year)
    return out[:40]


async def search_titles(query):
    """Movie/series search -> [{'id','kind','title','year'}] (max 40), [] when nothing, None on error."""
    if not TMDB_KEY:
        return None
    title, year = clean_title(query or "")
    try:
        return await asyncio.to_thread(_search_titles, title, year, (query or "").strip()[:100])
    except Exception as e:
        logger.warning(f"TMDB search failed for '{query}': {e}")
        return None


def _images(kind, tid):
    params = {"api_key": TMDB_KEY}
    if IMAGE_LANGS:
        params["include_image_language"] = IMAGE_LANGS
    d = _http_json(f"https://api.themoviedb.org/3/{kind}/{tid}/images", params)

    def pick(arr):
        arr = sorted(arr, key=lambda im: (_LANG_RANK.get(im.get("iso_639_1"), 3), -(im.get("vote_average") or 0)))
        return [{"path": im["file_path"], "w": im.get("width") or 0, "h": im.get("height") or 0,
                 "lang": im.get("iso_639_1")} for im in arr if im.get("file_path")]
    return {"p": pick(d.get("posters", [])), "b": pick(d.get("backdrops", []))}


async def get_images(kind, tid):
    """All posters ('p') + backdrops ('b') of a title, best first. None on error."""
    try:
        return await asyncio.to_thread(_images, kind, int(tid))
    except Exception as e:
        logger.warning(f"TMDB images failed for {kind}/{tid}: {e}")
        return None


async def fetch_image(path, size="w780"):
    """Image bytes in a TMDB size (w342/w780/w1280/original)."""
    return await asyncio.to_thread(_http_bytes, f"{IMG_BASE}{size}{path}")


async def probe_title(path):
    """Embedded title tag of the media file (ffprobe), or None."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "ffprobe", "-v", "error", "-show_entries", "format_tags=title", "-of", "default=nw=1:nk=1", path,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
        out, _ = await asyncio.wait_for(proc.communicate(), timeout=20)
        t = out.decode("utf-8", "ignore").strip()
        return t if len(t) > 2 else None
    except Exception:
        return None


async def first_hit(names, fetch, out_path):
    """Try several candidate names (file name, caption, embedded title) until one yields an image."""
    seen = set()
    for n in names:
        if not n or n in seen:
            continue
        seen.add(n)
        r = await fetch(n, out_path)
        if r:
            return r
    return None
