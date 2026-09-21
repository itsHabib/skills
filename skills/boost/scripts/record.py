#!/usr/bin/env python3
"""Save one private, local skill-use note. No network or repository writes."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import uuid


def save(note, directory):
    required = ('task', 'model', 'strategy', 'outcome', 'evidence', 'opinion')
    if not isinstance(note, dict):
        raise ValueError('note must be a JSON object')
    for key in required:
        if not isinstance(note.get(key), str) or not note[key].strip():
            raise ValueError(f'{key} must be a nonempty string')
    if note['outcome'] not in ('helped', 'no_change', 'hurt', 'unclear'):
        raise ValueError('outcome must be helped, no_change, hurt, or unclear')
    record = dict(note, schema='agent-boost-use.v1', recorded_at=datetime.now(timezone.utc).isoformat())
    payload = (json.dumps(record, ensure_ascii=False, indent=2) + '\n').encode()
    if len(payload) > 16384:
        raise ValueError('keep the use note below 16 KiB')
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    path = directory / (uuid.uuid4().hex + '.json')
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(payload)
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=Path.home()/'.local/state/agent-boost/uses')
    args = parser.parse_args()
    try:
        raw = sys.stdin.buffer.read(16385)
        if len(raw) > 16384:
            raise ValueError('keep the use note below 16 KiB')
        print(save(json.loads(raw), args.directory.expanduser()))
    except (ValueError, OSError) as error:
        parser.exit(1, f'record not saved: {error}\n')


if __name__ == '__main__':
    main()
