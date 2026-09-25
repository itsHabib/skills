#!/usr/bin/env python3
"""Record a trusted host command and selected source snapshots. Not a sandbox."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import uuid


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def private_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(content)


def json_write(path, value):
    private_write(path, (json.dumps(value, indent=2) + '\n').encode())


def selected_files(cwd, names):
    selected = {}
    for name in names:
        relative = Path(name)
        if relative.anchor or '..' in relative.parts or str(relative) in selected:
            raise ValueError('source paths must be distinct unanchored relative paths without ..')
        path = (cwd / relative).resolve(strict=True)
        if not path.is_relative_to(cwd) or not path.is_file():
            raise ValueError('selected source must be a file inside the chosen directory')
        selected[str(relative)] = path.read_bytes()
    return selected


def hashes(files):
    return {name: {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
            for name, data in files.items()}


def terminate(process):
    """Best-effort group cleanup on POSIX; direct child only on Windows."""
    if os.name == 'posix':
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            return
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            pass
        # Children may still hold files after the original process exits.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()
        return
    process.kill()
    process.wait()


def wait_for_command(process, began, timeout, received_signal):
    while True:
        if received_signal() is not None:
            return 'interrupted', None
        remaining = None if timeout is None else timeout - (time.monotonic() - began)
        if remaining is not None and remaining <= 0:
            return 'timeout', None
        try:
            return 'completed', process.wait(timeout=.1 if remaining is None else min(.1, remaining))
        except subprocess.TimeoutExpired:
            pass


def finish_command(process, status, code, previous_handlers):
    try:
        if process is not None and status != 'completed':
            terminate(process)
            code = process.returncode
    finally:
        for sig, handler in previous_handlers.items():
            signal.signal(sig, handler)
    return code


def execute_command(cwd, command, timeout, stdout, stderr):
    began = time.monotonic()
    status = 'completed'
    error = None
    code = None
    process = None
    received_signal = None
    def interrupted(signum, _frame):
        # Do not raise between Popen spawning the child and returning its handle.
        nonlocal received_signal
        received_signal = signum
    previous_handlers = {sig: signal.getsignal(sig) for sig in (signal.SIGINT, signal.SIGTERM)}
    for sig in previous_handlers:
        signal.signal(sig, interrupted)
    try:
        process = subprocess.Popen(command, cwd=cwd, stdout=stdout, stderr=stderr,
                                   stdin=subprocess.DEVNULL, start_new_session=os.name == 'posix')
        status, code = wait_for_command(process, began, timeout, lambda: received_signal)
        if received_signal is not None:
            status = 'interrupted'
    except KeyboardInterrupt:
        status = 'interrupted'
        received_signal = signal.SIGINT
    except OSError as exc:
        status = 'launch_error'
        error = str(exc)
    finally:
        code = finish_command(process, status, code, previous_handlers)
    return status, code, received_signal, error, time.monotonic() - began


def run(cwd, names, command, directory, timeout=None):
    cwd = Path(cwd).expanduser().resolve(strict=True)
    if not cwd.is_dir() or not command:
        raise ValueError('an existing working directory and command are required')
    files = selected_files(cwd, names)
    root = Path(directory).expanduser()
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    out = root / uuid.uuid4().hex
    out.mkdir(mode=0o700)
    for name, content in files.items():
        private_write(out / 'source' / name, content)
    before = hashes(files)
    json_write(out / 'started.json', {
        'schema': 'agent-boost-check.v1', 'started_at': timestamp(),
        'cwd': str(cwd), 'command': command, 'timeout_seconds': timeout,
        'execution': 'host command, inherited environment, no sandbox',
        'sources_before': before,
    })
    stdout_fd = os.open(out / 'stdout.log', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    stderr_fd = os.open(out / 'stderr.log', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(stdout_fd, 'wb') as stdout, os.fdopen(stderr_fd, 'wb') as stderr:
        status, code, received_signal, error, elapsed = execute_command(
            cwd, command, timeout, stdout, stderr)
    after = {}
    for name in files:
        try:
            after.update(hashes(selected_files(cwd, [name])))
        except (ValueError, OSError) as exc:
            after[name] = {'error': str(exc)}
    result = {'schema': 'agent-boost-check.v1', 'finished_at': timestamp(),
              'status': status, 'exit_code': code, 'elapsed_seconds': elapsed,
              'interruption_signal': received_signal,
              'error': error, 'sources_after': after,
              'sources_changed': before != after}
    json_write(out / 'result.json', result)
    return out, result


def positive_seconds(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError('timeout must be positive and finite')
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cwd', required=True, type=Path)
    parser.add_argument('--file', action='append', required=True, dest='files')
    parser.add_argument('--directory', type=Path,
                        default=Path.home() / '.local/state/agent-boost/checks')
    parser.add_argument('--timeout', type=positive_seconds)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    try:
        out, result = run(args.cwd, args.files, command, args.directory, args.timeout)
    except (ValueError, OSError) as exc:
        parser.exit(2, f'check not started: {exc}\n')
    print(out)
    if result['status'] == 'timeout':
        return 124
    if result['status'] == 'interrupted':
        return 128 + (result['interruption_signal'] or signal.SIGINT)
    if result['status'] == 'launch_error':
        return 127
    code = result['exit_code']
    return code if code >= 0 else 128 - code


if __name__ == '__main__':
    raise SystemExit(main())
