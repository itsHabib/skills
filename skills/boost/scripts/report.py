#!/usr/bin/env python3
"""Summarize local boost use notes so earlier lessons can be reused. Read-only; no network."""
import argparse
from datetime import datetime, timedelta, timezone
import json
import math
from pathlib import Path
import sys

OUTCOMES = ('helped', 'no_change', 'hurt', 'unclear')
MAX_DAYS = 36500


def parse_time(value):
    """Return recorded_at as an aware datetime; a naive time is taken as UTC."""
    if not isinstance(value, str):
        raise ValueError('recorded_at must be a string')
    if value[-1:] in ('Z', 'z'):
        value = value[:-1] + '+00:00'  # Python before 3.11 rejects a trailing Z
    when = datetime.fromisoformat(value)
    if when.tzinfo is None:
        return when.replace(tzinfo=timezone.utc)
    return when


def read_note(path):
    note = json.loads(path.read_text(encoding='utf-8-sig'))  # tolerate a Windows byte-order mark
    if not isinstance(note, dict):
        raise ValueError('a note must be a JSON object')
    return note, parse_time(note.get('recorded_at'))


def load(directory, since_days=None):
    """Return (notes newest first, count of unreadable files)."""
    cutoff = None
    if since_days is not None:
        cutoff = datetime.now(timezone.utc) - timedelta(days=min(since_days, MAX_DAYS))
    dated, unreadable = [], 0
    for path in sorted(Path(directory).glob('*.json')):
        try:
            note, when = read_note(path)
        except (OSError, ValueError, TypeError, RecursionError):
            unreadable += 1
            continue
        if cutoff is None or when >= cutoff:
            dated.append((when, note))
    dated.sort(key=lambda pair: pair[0], reverse=True)
    return [note for _, note in dated], unreadable


def collect(directory, since_days):
    if not directory.is_dir():
        print(f'No use notes yet: {directory} is not a directory.', file=sys.stderr)
        return [], 0
    return load(directory, since_days)


def first_sentence(text, limit=220):
    text = ' '.join(str(text or '').split())
    end = text.find('. ')
    if end != -1:
        text = text[:end + 1]
    if len(text) <= limit:
        return text
    return text[:limit - 3] + '...'


def outcome_of(note):
    """Normalize a recorded outcome; anything unrecognized is counted as 'other', never dropped."""
    value = note.get('outcome')
    if isinstance(value, str) and value.strip().lower() in OUTCOMES:
        return value.strip().lower()
    return 'other'


def counts(notes):
    tally = dict.fromkeys(OUTCOMES + ('other',), 0)
    for note in notes:
        tally[outcome_of(note)] += 1
    return tally


def brief(notes, unreadable):
    tally = counts(notes)
    shown = [f"{tally[o]} {o}" for o in OUTCOMES]
    if tally['other']:
        shown.append(f"{tally['other']} other")
    lines = [f"{len(notes)} use notes, outcomes self-reported: " + ', '.join(shown)]
    if unreadable:
        lines.append(f"({unreadable} unreadable files skipped)")
    for title, wanted in (('What helped', ('helped',)), ('What did not help', ('no_change', 'hurt'))):
        picked = [note for note in notes if outcome_of(note) in wanted][:5]
        if picked:
            lines.append(f"\n{title}:")
            lines += [f"- {first_sentence(note.get('strategy'), 120)} -> {first_sentence(note.get('opinion'))}"
                      for note in picked]
    return '\n'.join(lines)


def markdown(notes, unreadable):
    lines = ['# Boost use notes', '', brief(notes, unreadable), '', '## All notes, newest first', '']
    for note in notes:
        lines += [f"### {note['recorded_at'][:10]} | {note.get('outcome')} | {note.get('model')}",
                  f"- **Task:** {note.get('task')}",
                  f"- **Strategy:** {note.get('strategy')}",
                  f"- **Evidence:** {note.get('evidence')}",
                  f"- **Opinion:** {note.get('opinion')}", '']
    return '\n'.join(lines)


def render(args, notes, unreadable):
    if args.json:
        return json.dumps({'counts': counts(notes), 'unreadable': unreadable, 'notes': notes},
                          indent=2, ensure_ascii=False)
    if args.brief:
        return brief(notes, unreadable)
    return markdown(notes, unreadable)


def write(text, output):
    if output is not None:
        output.expanduser().write_text(text + '\n', encoding='utf-8')
        return
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(errors='replace')  # a narrow console encoding must not crash the report
    print(text)


def positive_days(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError('DAYS must be a positive number')
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=Path.home() / '.local/state/agent-boost/uses')
    parser.add_argument('--since', type=positive_days, metavar='DAYS', help='only notes from the last DAYS days')
    parser.add_argument('--output', type=Path, metavar='FILE', help='write UTF-8 text to FILE instead of stdout')
    shape = parser.add_mutually_exclusive_group()
    shape.add_argument('--brief', action='store_true', help='counts plus what helped and what did not')
    shape.add_argument('--json', action='store_true', help='machine-readable notes and counts')
    args = parser.parse_args(argv)
    notes, unreadable = collect(args.directory.expanduser(), args.since)
    try:
        write(render(args, notes, unreadable), args.output)
    except OSError as error:
        parser.exit(1, f'report not written: {error}\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
