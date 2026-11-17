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


_NOISE = re.compile(
    r"(?<![A-Za-z])(?:(?:dd|ddp|dd\+|aac|ac3|eac3|dts|flac|opus)[\s._]?\d[\s._]\d)|(?<![A-Za-z])(?:x26[45]|h\.?26[45]|hevc|avc|aac\d?|ac3|eac3|dd\+?|ddp|dts(?:-hd)?|flac|web-?dl|web-?rip|blu-?ray|"
    r"bd-?rip|br-?rip|hd-?rip|dvd-?rip|hdtv|hdr|10bit|multi|dual|subs?|dubbed|\d+\s*[km]bps)(?![A-Za-z])|\b[257]\.[01]\b", re.I)
_SE = re.compile(r"(?<![A-Za-z])S\s*0*(\d{1,2})\s*[.\-_ ]*E\s*0*(\d{1,4})(?!\d)", re.I)
_NXM = re.compile(r"(?<!\d)0*(\d{1,2})x0*(\d{1,3})(?!\d)", re.I)
# season / episode words in many languages (Hebrew, Arabic, Cyrillic, CJK, Latin ...); numbers do the real work
_SEASON_W = re.compile(
    r"(?<!\w)(?:season|saison|staffel|temporada|stagione|sezon|sezona|сезон|עונה|موسم|الموسم|シーズン|시즌|seizoen|s[äa]song)"
    r"[\s.\-_:#]*0*(\d{1,2})(?!\d)|第\s*0*(\d{1,2})\s*[季期]|(?<!\d)0*(\d{1,2})\s*(?:기|期|季)", re.I)
_SEASON_PRE = re.compile(r"(?<!\d)0*(\d{1,2})(?:st|nd|rd|th)?\.?\s*(?:season|saison|staffel|temporada|stagione|sezon|сезон|עונה|موسم)(?!\w)", re.I)
_EP_PRE = re.compile(r"(?<!\d)0*(\d{1,4})(?:st|nd|rd|th)?\.?\s*(?:episode|[eé]pisode|folge|b[öo]l[üu]m|серия|эпизод|פרק|حلقة|odcinek|capitulo|capítulo)(?!\w)", re.I)
_EP_W = re.compile(
    r"(?<![A-Za-z])E(?:p|pisode|pisodio|pisod)?[\s.\-_:#]*0*(\d{1,4})(?!\d)|"
    r"(?<!\w)(?:[eé]pisode|folge|capítulo|capitulo|cap|episodio|bölüm|bolum|odcinek|aflevering|avsnitt|afsnit|jakso|díl|rész|tập|"
    r"серия|серии|эпизод|эп|פרק|חלק|حلقة|الحلقة|حلقه|ตอนที่|ตอน|chapter|ch|part)[\s.\-_:#]*0*(\d{1,4})(?!\d)|"
    r"第\s*0*(\d{1,4})\s*[話话集回章]|(?<!\d)0*(\d{1,4})\s*(?:話|话|集|화|회|話目)", re.I)
_NUM = re.compile(r"(?<![A-Za-z\d])0*(\d{1,4})(?![A-Za-z\d])")


def _first(m):
    return next((g for g in m.groups() if g), None)


def _tidy_title(t):
    t = _YEAR.sub(" ", t.replace("-", " "))
    t = _BRACKET.sub(" ", t)
    return " ".join(t.split())


def extract_meta(filename):
    """Language-independent: season/episode come from the NUMBERS (SxxEyy, 1x04, 'word N', '- N', 第N話 ...)."""
    meta = {"title": "Unknown", "season": "01", "episode": "01", "quality": "1080p", "chapter": "001"}
    name = filename or ""
    qm = _QUAL.search(name)
    if qm:
        meta["quality"] = qm.group(1)
    clean = name
    for rx in _UPLOADER_RX:
        clean = rx.sub("", clean)
    base, ext = os.path.splitext(clean.strip())
    if len(ext) > 5 or " " in ext:
        base = clean.strip()
    base = base.replace("_", " ")
    base = re.sub(r"(?<=\D)\.|\.(?=\D)|(?<=\D)\.(?=\d)", " ", base)
    base = _NOISE.sub(" ", base)
    base = _QUAL.sub(" ", base)
    cut = None
    m = _SE.search(base) or _NXM.search(base)
    if m:
        meta["season"], meta["episode"] = f"{_int(m.group(1)):02d}", f"{_int(m.group(2)):02d}"
        cut = m.start()
    else:
        ps, pe = _SEASON_PRE.search(base), _EP_PRE.search(base)
        ws, we = _SEASON_W.search(base), _EP_W.search(base)
        if ps and pe:      # "2. Sezon 4. Bölüm", "2 сезон 7 серия": numbers come before the words
            sm, em = ps, pe
        elif ws and we:    # "Season 2 Episode 5", "עונה 2 פרק 7": numbers come after the words
            sm, em = ws, we
        else:
            sm, em = ws or ps, we or pe
        if sm:
            meta["season"] = f"{_int(_first(sm)):02d}"
            cut = sm.start()
        if em:
            meta["episode"] = f"{_int(_first(em)):02d}"
            cut = em.start() if cut is None else min(cut, em.start())
    if cut is None:
        plain = _BRACKET.sub(" ", base)
        plain = _YEAR.sub(" ", plain)
        nums = [x for x in _NUM.finditer(plain) if 0 < _int(x.group(1)) < 2000]
        if nums:
            n = nums[-1]
            meta["episode"] = f"{_int(n.group(1)):02d}"
            meta["title"] = _tidy_title(plain[:n.start()]) or "Unknown"
            return meta
        meta["title"] = _tidy_title(_BRACKET.sub(" ", base)) or "Unknown"
        return meta
    meta["title"] = _tidy_title(_BRACKET.sub(" ", base[:cut])) or _tidy_title(base) or "Unknown"
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
