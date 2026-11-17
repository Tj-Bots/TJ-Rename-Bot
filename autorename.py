"""AutoRename: build a file name from a template ({title} {season} {episode} {quality} {chapter}).

Python port of azml-go helper/ext/leech_utils.go (ExtractMetadataFromFilename + ApplyTemplateRename).
"""
import os
import re

_UPLOADER_TAGS = [
    "Toonworld4all", "SubsPlease", "EMBER", "Erai-raws", "HorribleSubs", "AnimeRG", "Judas", "ASW",
    "Anime Time", "Virtuality", "SmallSizedAnime", "DKB", "Cleo", "Reaktor", "Commie", "GJM",
    "Underwater", "FFF", "Doki", "gg", "Chihiro", "Coalgirls", "UTW", "Mazui", "Hadena", "Horrible",
    "Mezashite", "Asenshi", "Vivid", "Soldado", "Anime4Life", "Ohys-Raws", "CR", "NanDesuKa", "Plex",
    "Anime-Koi", "AnimeKaizoku", "ReinForce", "BlurayDesuYo", "Beatrice-Raws", "SCY", "Nep_Blanc",
    "Anime-Supreme", "HiSub", "NC-Raws", "nekomoe kissaten",
]
_UPLOADER_RX = [re.compile(r"^\[" + re.escape(t) + r"\]\s*", re.I) for t in _UPLOADER_TAGS]

_TITLE_PATTERNS = [re.compile(p, re.I) for p in (
    r"^\[E(?:p|pisode)?[\s.\-]*0*\d+\][\s.\-]*(.+?)[\s.\-]*(?:\[|@|$)",
    r"^(.+?)[\s.\-]*S0*(\d+)[\s.\-]*E0*(\d+)",
    r"^(.+?)[\s.\-]*Season[\s.\-]*0*(\d+)[\s.\-]*Episode[\s.\-]*0*(\d+)",
    r"^(.+?)[\s.\-]*עונה[\s.\-]*0*(\d+)[\s.\-]*פרק[\s.\-]*0*(\d+)",
    r"^(.+?)[\s.\-]*פרק[\s.\-]*0*\d+",
    r"^\[CH[-\s]?\d+\][\s.\-]*(.+?)[\s.\-]*-",
    r"^\[\d+\][\s.\-]*(.+?)[\s.\-]*(?:@|$)",
    r"^(.+?)[\s.\-]*(?:Ch(?:apter)?|#)[\s.\-]*\d+",
    r"^(.+?)[\s.\-]*\[",
)]
_EP_PATTERNS = [re.compile(p, re.I) for p in (
    r"[\s.\-]+-[\s.\-]*0*(\d{1,4})v\d+",
    r"\[E(?:p|pisode)?[\s.\-]*0*(\d{1,4})\]",
    r"S0*(\d+)E0*(\d+)",
    r"Ep(?:isode)?[\s.\-]*0*(\d{1,4})",
    r"פרק[\s.\-]*0*(\d{1,4})",
    r"E[\s.\-]*0*(\d{1,4})",
    r"[\s.\-]+-[\s.\-]*0*(\d{1,4})",
    r"[\s.\-]+0*(\d{1,4})[\s.\-]+\d{3,4}p",
    r"\[0*(\d{1,4})\]",
)]
_YEAR = re.compile(r"\s*[(\[]?\s*(199[0-9]|20[0-2][0-9]|2030)\s*[)\]]?\s*", re.I)
_SEASON = re.compile(r"S(?:eason[\s.\-]*)?0*(\d+)", re.I)
_SEASON_HE = re.compile(r"עונה[\s.\-]*0*(\d+)")
_QUAL = re.compile(r"(\d{3,4}p|4K|2160p)", re.I)
_OFFSET = re.compile(r"\{(episode|season):([+\-])(\d+)\}")
_BRACKET = re.compile(r"[(\[].*?[)\]]")
_TRAIL = re.compile(r"[\s\-]+0*\d{1,4}\s*$")


def _int(s):
    try:
        return int(s)
    except (TypeError, ValueError):
        return 0


def extract_meta(filename):
    meta = {"title": "Unknown", "season": "01", "episode": "01", "quality": "1080p", "chapter": "001"}
    clean = filename or ""
    for rx in _UPLOADER_RX:
        clean = rx.sub("", clean)
    clean = clean.strip()
    for p in _TITLE_PATTERNS:
        m = p.search(clean)
        if m:
            title = m.group(1).replace(".", " ").replace("-", " ").strip()
            title = _YEAR.sub(" ", title)
            title = _BRACKET.sub(" ", title)
            title = _TRAIL.sub("", title.strip())
            meta["title"] = " ".join(title.split()) or "Unknown"
            if m.lastindex and m.lastindex >= 3:
                meta["season"] = f"{_int(m.group(2)):02d}"
                meta["episode"] = f"{_int(m.group(3)):02d}"
            break
    if meta["title"] == "Unknown":
        base = os.path.splitext(clean)[0].replace(".", " ").replace("_", " ")
        base = _QUAL.sub(" ", _BRACKET.sub(" ", base))
        base = _TRAIL.sub("", base.strip())
        t = " ".join(base.split())
        if t:
            meta["title"] = t
    sm = _SEASON.search(filename or "")
    if sm:
        meta["season"] = f"{_int(sm.group(1)):02d}"
    hm = _SEASON_HE.search(filename or "")
    if hm:
        meta["season"] = f"{_int(hm.group(1)):02d}"
    for p in _EP_PATTERNS:
        m = p.search(clean)
        if m:
            n = _int(m.group(m.lastindex))
            if 0 < n < 2000:
                meta["episode"] = f"{n:02d}"
                break
    qm = _QUAL.search(filename or "")
    if qm:
        meta["quality"] = qm.group(1)
    return meta


def apply_template(filename, tmpl):
    if not tmpl or "{" not in tmpl:
        return filename
    meta = extract_meta(filename)

    def offset(m):
        tag, sign, off = m.group(1), m.group(2), _int(m.group(3))
        orig = _int(meta[tag])
        res = orig + off if sign == "+" else orig - off
        if res <= 0:
            res = orig
        meta[tag] = f"{res:02d}"
        return "{" + tag + "}"

    res = _OFFSET.sub(offset, tmpl)
    ext = os.path.splitext(filename or "")[1]
    for k in ("title", "season", "episode", "quality", "chapter"):
        res = res.replace("{" + k + "}", meta[k])
    if ext and not res.endswith(ext):
        res += ext
    return res
