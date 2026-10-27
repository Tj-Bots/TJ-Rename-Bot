"""Start-up auto update from the GitHub repo.

Safe by design: only tracked files change (fast-forward merge), so .env, sessions,
databases and downloads are never touched. The update is skipped when there is no
.git folder, when tracked files have local edits, when local commits are not on the
remote, or when offline - and it is rolled back if the new code does not compile.
Repo and branch come from /bsetting (UPSTREAM_REPO, UPSTREAM_BRANCH), then .env, then the
git origin. AUTO_UPDATE=false turns the update off.
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.realpath(__file__))
REMOTE = "origin"
_CREDS = re.compile(r"://[^@/\s]+@")


def _log(msg):
    print("[updater] " + _CREDS.sub("://", str(msg)), flush=True)


def _git(*args, timeout=60):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    r = subprocess.run(["git", "-c", "core.quotepath=off", *args], cwd=ROOT, capture_output=True,
                       text=True, timeout=timeout, env=env)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def defaults():
    """Repo URL and branch from .env, falling back to the git origin."""
    repo = os.getenv("UPSTREAM_REPO", "").strip()
    if not repo:
        repo = _git("remote", "get-url", REMOTE)[1]
    return repo, os.getenv("UPSTREAM_BRANCH", "").strip() or "main"


def _saved_settings():
    uri = os.getenv("MONGO_URI", "")
    if not uri:
        return {}
    try:
        from pymongo import MongoClient
        client = MongoClient(uri, serverSelectionTimeoutMS=4000)
        try:
            col = client[os.getenv("DB_NAME", "tj_rename")]["bot_config"]
            return col.find_one({"_id": "settings"}) or {}
        finally:
            client.close()
    except Exception:
        return {}


def check_update():
    """Fast-forward to the remote branch. Returns True when new code was installed."""
    if os.environ.pop("TJ_UPDATED", None):
        return False  # just re-executed after an update
    if os.getenv("AUTO_UPDATE", "true").strip().lower() in ("0", "false", "no", "off"):
        return False
    if not os.path.isdir(os.path.join(ROOT, ".git")):
        return False
    repo, branch = defaults()
    saved = _saved_settings()
    repo = str(saved.get("UPSTREAM_REPO") or repo)
    branch = str(saved.get("UPSTREAM_BRANCH") or branch)
    if not repo:
        return False
    code, _, err = _git("fetch", "--quiet", repo, branch, timeout=45)
    if code != 0:
        _log("fetch failed, running the current code (" + (err.splitlines()[-1] if err else "no details") + ")")
        return False
    old = _git("rev-parse", "HEAD")[1]
    new = _git("rev-parse", "FETCH_HEAD")[1]
    if not new or old == new:
        _log("up to date")
        return False
    if _git("merge-base", "--is-ancestor", "HEAD", "FETCH_HEAD")[0] != 0:
        _log("local code is not part of the history of " + branch + ", skipping update")
        return False
    if _git("status", "--porcelain", "--untracked-files=no")[1]:
        _log("tracked files have local changes, skipping update")
        return False
    changed = _git("diff", "--name-only", "HEAD", "FETCH_HEAD")[1].splitlines()
    if _git("merge", "--ff-only", "--quiet", "FETCH_HEAD")[0] != 0:
        _log("fast-forward failed, skipping update")
        return False
    if "requirements.txt" in changed:
        r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"],
                           cwd=ROOT, capture_output=True, text=True, timeout=900)
        if r.returncode != 0:
            _log("pip install failed, continuing")
    files = [f for f in _git("ls-files", "*.py")[1].splitlines() if f]
    if subprocess.run([sys.executable, "-m", "py_compile", *files], cwd=ROOT, capture_output=True).returncode != 0:
        _git("reset", "--hard", "--quiet", old)
        _log("new code does not compile, rolled back")
        return False
    _log("updated " + old[:7] + " -> " + new[:7])
    for line in _git("log", "--oneline", "--no-decorate", "-5", old + ".." + new)[1].splitlines():
        _log("  " + line)
    return True


def auto_update():
    """Call once at start-up, before the rest of the bot is imported."""
    try:
        updated = check_update()
    except Exception as e:
        _log("skipped (" + str(e) + ")")
        return
    if updated:
        _log("restarting on the new code")
        os.environ["TJ_UPDATED"] = "1"
        os.execv(sys.executable, [sys.executable, *sys.argv])
