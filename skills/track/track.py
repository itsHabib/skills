#!/usr/bin/env python3
"""Anchor state for /track — elapsed-time heartbeat for a waiting agent.

One track per --name (default: a slug of the cwd). State lives in
~/.claude/track/<name>.json so a tick in a fresh turn can still compute the
cumulative total the agent cannot carry across ticks itself.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = Path.home() / ".claude" / "track"
UTC = timezone.utc


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "track"


def default_name():
    """Scope a track to the session, not just the repo.

    Two agent sessions in one repo would otherwise share a track and corrupt
    each other's totals. The session id is the only handle that is both unique
    per session and stable across turns — and stability is what matters, since
    the tick that reads this state runs in a much later turn. Outside Claude
    Code there is no session, so fall back to the cwd and let --name isolate.
    """
    base = Path.cwd().name
    sid = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
    return f"{base}-{sid[:8]}" if sid else base


def state_path(name):
    return STATE_DIR / f"{slug(name)}.json"


def now():
    return datetime.now(UTC)


def parse(ts):
    return datetime.fromisoformat(ts)


def humanize(delta):
    """3820s -> '1h3m'. Minute resolution; a heartbeat never needs seconds."""
    total = int(delta.total_seconds())
    if total < 60:
        return f"{total}s"
    m, h = total // 60 % 60, total // 3600
    d, h = h // 24, h % 24
    if d:
        return f"{d}d{h}h"
    if h:
        return f"{h}h{m}m"
    return f"{m}m"


def load(name):
    p = state_path(name)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def save(st):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    state_path(st["name"]).write_text(
        json.dumps(st, indent=1), encoding="utf-8"
    )


def find_bash():
    """Locate a POSIX bash, or None if the box has none.

    shell=True would hand the check to COMSPEC (cmd.exe) on Windows, which
    silently mangles POSIX syntax: `a; b` runs as the single command `a` with
    the rest as literal arguments. Checks are written for the shell the
    operator lives in, so run them there.

    System32\\bash.exe is WSL — a different filesystem (/mnt/c/...) where a
    path written for this shell would not resolve — so it is not a substitute.
    """
    cand = shutil.which("bash")
    if cand and "system32" not in cand.lower():
        return cand
    git = shutil.which("git")
    if git:  # <git>/{cmd,bin}/git.exe -> <git>/usr/bin/bash.exe
        root = Path(git).parent.parent
        for rel in ("usr/bin/bash.exe", "bin/bash.exe"):
            if (root / rel).exists():
                return str(root / rel)
    return None


def bash_env():
    """Give bash a HOME it can actually use.

    On Windows, Python inherits the drive-letter form of HOME. MSYS bash
    rejects it and falls back to its passwd entry (/home/<user>), which need
    not exist — so `~` inside a check would silently point somewhere you never
    meant. Hand it the POSIX form instead.
    """
    env = dict(os.environ)
    m = re.match(r"^([A-Za-z]):[\\/](.*)$", env.get("HOME", ""))
    if m:
        env["HOME"] = f"/{m.group(1).lower()}/{m.group(2)}".replace("\\", "/")
    return env


def run_check(cmd, max_lines):
    """Run the watch command. Its failure is data, not an error for us."""
    sh = find_bash()
    kw = dict(capture_output=True, text=True, encoding="utf-8",
              errors="replace", timeout=180)
    try:
        # -c, not -lc: a login shell sources the profile, measured here at
        # ~1.9s per spawn against ~0.13s, which defeats a cheap tick.
        r = (subprocess.run([sh, "-c", cmd], env=bash_env(), **kw) if sh
             else subprocess.run(cmd, shell=True, **kw))
    except subprocess.TimeoutExpired:
        return ["  check: TIMED OUT after 180s"]
    except OSError as e:
        return [f"  check: could not run ({e})"]
    out = (r.stdout or "") + (r.stderr or "")
    lines = [l for l in out.splitlines() if l.strip()]
    # Say so when falling back: POSIX syntax in the check will misbehave.
    # Kept ASCII — this line shows up on the degraded path, which is the last
    # place to risk a second failure mode.
    via = "" if sh else ", via cmd.exe - no bash found"
    if not lines:
        return [f"  check (exit {r.returncode}{via}): no output"]
    tail = lines[-max_lines:]
    head = (f"  check (exit {r.returncode}{via}, "
            f"last {len(tail)} of {len(lines)} lines):")
    return [head] + [f"  | {l}" for l in tail]


def cmd_start(a):
    st = {
        "name": slug(a.name),
        "label": a.label,
        "started_at": now().isoformat(),
        "last_tick_at": now().isoformat(),
        "ticks": 0,
        "check": a.check,
        "check_lines": a.check_lines,
    }
    save(st)
    print(f"⏱ tracking '{st['label']}' as [{st['name']}] from {st['started_at'][:16]}Z")
    if st["check"]:
        print(f"   per-tick check: {st['check']}")
    # Hand back the loop line with the name pinned. The default name embeds the
    # cwd, so a tick fired from elsewhere would look for a track that isn't
    # there; naming it explicitly makes the loop immune to that.
    print(f"   /loop 10m Run: python ~/.claude/skills/track/track.py tick "
          f"--name {st['name']}")
    return 0


def cmd_tick(a):
    st = load(a.name)
    if not st:
        print(f"⏱ no active track named [{slug(a.name)}] — nothing to tick.")
        print("   start one with: track.py start --label \"<what you're waiting on>\"")
        return 1
    t = now()
    since = t - parse(st["last_tick_at"])
    total = t - parse(st["started_at"])
    st["ticks"] += 1
    st["last_tick_at"] = t.isoformat()
    save(st)
    print(f"⏱ +{humanize(since)} · {humanize(total)} total "
          f"· tick {st['ticks']} · waiting on: {st['label']}")
    if st.get("check"):
        for line in run_check(st["check"], st.get("check_lines") or 12):
            print(line)
    return 0


def cmd_status(a):
    st = load(a.name)
    if not st:
        print(f"⏱ no active track named [{slug(a.name)}].")
        return 1
    total = now() - parse(st["started_at"])
    print(f"⏱ [{st['name']}] {humanize(total)} total across {st['ticks']} tick(s) "
          f"· since {st['started_at'][:16]}Z · waiting on: {st['label']}")
    return 0


def cmd_stop(a):
    st = load(a.name)
    if not st:
        print(f"⏱ no active track named [{slug(a.name)}].")
        return 1
    total = now() - parse(st["started_at"])
    state_path(st["name"]).unlink()
    print(f"⏱ stopped [{st['name']}] — {humanize(total)} total "
          f"across {st['ticks']} tick(s) waiting on: {st['label']}")
    return 0


def cmd_list(_a):
    if not STATE_DIR.exists():
        print("⏱ no active tracks.")
        return 0
    files = sorted(STATE_DIR.glob("*.json"))
    if not files:
        print("⏱ no active tracks.")
        return 0
    for p in files:
        try:
            st = json.loads(p.read_text(encoding="utf-8"))
            total = now() - parse(st["started_at"])
        except (ValueError, KeyError, OSError):
            # One unreadable file must not hide every other live track.
            print(f"  [{p.stem}] unreadable state file")
            continue
        print(f"  [{st['name']}] {humanize(total)} · {st['ticks']} tick(s) · {st['label']}")
    return 0


def main():
    # Windows consoles default to cp1252, which cannot encode the glyphs below.
    # Reconfigure rather than drop them: the heartbeat is meant to be skimmable.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass

    ap = argparse.ArgumentParser(prog="track.py")
    ap.add_argument("--name", default=None,
                    help="track name; defaults to cwd + session id")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("start")
    s.add_argument("--label", required=True, help="what you are waiting on")
    s.add_argument("--check", default=None, help="shell command to run each tick")
    s.add_argument("--check-lines", type=int, default=8,
                   help="tail N lines of check output (default 8)")
    s.set_defaults(fn=cmd_start)

    for name, fn in (("tick", cmd_tick), ("status", cmd_status),
                     ("stop", cmd_stop), ("list", cmd_list)):
        p = sub.add_parser(name)
        p.set_defaults(fn=fn)

    # `tick --name x` is the order anyone writes by hand, so accept --name on
    # either side of the verb. SUPPRESS keeps an unused subparser copy from
    # clobbering a value already given before the verb.
    for p in (s, *[sub.choices[k] for k in ("tick", "status", "stop", "list")]):
        p.add_argument("--name", default=argparse.SUPPRESS, help=argparse.SUPPRESS)

    a = ap.parse_args()
    if not getattr(a, "name", None):
        a.name = default_name()
    sys.exit(a.fn(a))


if __name__ == "__main__":
    main()
