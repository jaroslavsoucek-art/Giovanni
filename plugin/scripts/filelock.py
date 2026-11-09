#!/usr/bin/env python3
"""scripts/filelock.py — one exclusive file lock for macOS, Linux and Windows.

The inbox and the autocommit hook serialise through a lock file: a headless
morning run and an interactive session can write the same inbox at the same
moment. `fcntl.flock` exists only on POSIX; on Windows the same job is
`msvcrt.locking` on the first byte of the lock file. Same contract on both:

  lock(fh)                  block until held (Windows: up to `timeout` seconds, then OSError)
  lock(fh, blocking=False)  True if held, False if someone else holds it
  unlock(fh)

Open the lock file with mode "a+" (never "w": on Windows truncating a file
another process has locked is an error).
"""
from __future__ import annotations

import os
import time

if os.name == "nt":  # pragma: no cover — exercised by the Windows CI job
    import msvcrt

    def lock(fh, blocking: bool = True, timeout: float = 30.0) -> bool:
        deadline = time.monotonic() + timeout
        while True:
            try:
                fh.seek(0)
                msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
                return True
            except OSError:
                if not blocking:
                    return False
                if time.monotonic() > deadline:
                    raise
                time.sleep(0.05)

    def unlock(fh) -> None:
        try:
            fh.seek(0)
            msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
        except OSError:
            pass
else:
    import fcntl

    def lock(fh, blocking: bool = True, timeout: float | None = None) -> bool:
        try:
            fcntl.flock(fh, fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB))
            return True
        except OSError:
            if blocking:
                raise
            return False

    def unlock(fh) -> None:
        fcntl.flock(fh, fcntl.LOCK_UN)
