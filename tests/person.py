"""A person at the keyboard, for the tests: reads what play.py asks, and
answers it, the way someone at the table would.

`at_table(argv, env, answer)` runs a box script and, each time it waits for
a line (what it printed ends without a newline, and it has gone quiet: a
printed line ends in one, a question doesn't), hands everything it has
printed so far, and what it printed since the last answer (the question
itself), to ANSWER(text, asked), which returns the line to type, or None
to walk away (stdin is closed). It returns (exit code, everything printed). A fixed list of keystrokes can't follow a night whose
rolls and branches the dice decide; this reads the prompt instead."""

from __future__ import annotations

import os
import re
import select
import subprocess
import sys
import time


def at_table(argv: list, env: dict, answer, limit: float = 120.0) -> tuple[int, str]:
    child = subprocess.Popen(
        [sys.executable, "-u", *map(str, argv)],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        env={**os.environ, **env, "PYTHONUNBUFFERED": "1"},
    )  # fmt: skip
    out, seen, until = b"", 0, time.monotonic() + limit
    fd = child.stdout.fileno()
    while time.monotonic() < until:
        ready, _, _ = select.select([fd], [], [], 0.05)
        if ready:
            got = os.read(fd, 4096)
            if not got:
                break
            out += got
            continue
        text = out.decode("utf-8", "replace")
        if (
            child.poll() is None
            and len(out) > seen
            and text
            and not text.endswith("\n")
        ):
            asked = out[seen:].decode("utf-8", "replace").rsplit("\n", 1)[-1].strip()
            seen = len(out)
            line = answer(text, asked)
            if line is None:
                child.stdin.close()
            else:
                child.stdin.write(f"{line}\n".encode())
                child.stdin.flush()
        elif child.poll() is not None:
            break
    else:
        child.kill()
        raise TimeoutError(out.decode("utf-8", "replace")[-2000:])
    rest = child.stdout.read()
    child.wait()
    return child.returncode, (out + rest).decode("utf-8", "replace")


def answering(steps: list[tuple[str, str]], every: dict | None = None):
    """An ANSWER for at_table from STEPS, (words in the question, what to
    type), each used once, in order; EVERY says what to type at a question
    asked again and again, by words in it (">", exactly, for a roll: Enter). A question neither names
    is walked away from."""
    left, every = list(steps), {">": ""} if every is None else every

    def answer(_text: str, asked: str):
        if left and left[0][0] in asked:
            return left.pop(0)[1]
        if asked == ">":
            return every.get(">")
        return next((v for k, v in every.items() if k != ">" and k in asked), None)

    answer.left = left
    return answer


def in_order(typed: list[str]):
    """An ANSWER for at_table that types TYPED in order, one line a question,
    and Enter at every roll (">"), which a person presses to throw the dice;
    walks away when TYPED runs out."""
    left = list(typed)

    def answer(_text: str, asked: str):
        if asked == ">":
            return ""
        return left.pop(0) if left else None

    return answer


def typed_run(argv: list, env: dict, typed: list[str]):
    """(argv run with TYPED answered in order) as a CompletedProcess, its
    stderr folded into stdout, as a person sees one screen."""
    code, out = at_table(argv, env, in_order(typed))
    return subprocess.CompletedProcess(argv, code, out, out)


def fights_could_start(out: str) -> None:
    """A fight the table asked for that couldn't start is this machine, not the
    night: say why (a missing library, most often), not the question the story
    went on to ask instead."""
    import pytest

    m = re.search(r"The fight couldn't start: (.+)", out)
    if m:
        pytest.fail(f"a fight couldn't start here: {m.group(1).strip()}", pytrace=False)
