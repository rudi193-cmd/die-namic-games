"""utety_history.py: UTETY's branches and pull requests, as pages a box can read. Python 3.9+.

    python boxes/safe-app-store/utety_history.py REPO MAIN OUT

A box over a repository's tree at one commit holds what was merged, not why,
nor what never was. This writes, from a checkout whose branches are fetched
(refs/remotes/origin/*) and whose pull requests are too (refs/remotes/pr/N,
from refs/pull/N/head), into OUT, a folder that must not be there yet:

- prs.md: each pull request, its title as its merge on MAIN says it (or its
  head's subject if it isn't merged), merged at what and when or not merged,
  and every commit in it with its whole message;
- branches.md: each branch, merged into MAIN or how many commits ahead, and
  for one ahead, each of those commits with its whole message;
- branches/NAME/: for a branch ahead of MAIN, the files it changed, as they
  are at its head (the rest is MAIN's, already in the box).

It only reads the checkout (git log, show, archive), and writes only OUT.
Exit codes: 0 written; 2 refused (no checkout, MAIN not in it, OUT there, or
no branches fetched).
"""

from __future__ import annotations

import io
import re
import subprocess
import sys
import tarfile
from pathlib import Path


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout  # fmt: skip


def refs(repo: Path, where: str) -> list[str]:
    out = git(repo, "for-each-ref", "--format=%(refname:short)", where).split()
    return [r for r in out if not r.endswith("/HEAD") and r != "origin"]


def commits(repo: Path, span: str) -> list[str]:
    """Each commit in SPAN, oldest first: a heading and its whole message."""
    log = git(repo, "log", "--reverse", "--no-merges", "--format=%x00%h %cs %s%n%n%b", span)  # fmt: skip
    demote = re.compile(
        r"^(#+ )", re.MULTILINE
    )  # a message's own headings sit under its commit
    return [
        "### " + demote.sub(r"###\1", c.strip()) for c in log.split("\0") if c.strip()
    ]


def merges(repo: Path, main: str) -> dict[int, tuple[str, str, str, str]]:
    """PR number -> (merge hash, date, title, the head it merged)."""
    got = {}
    log = git(repo, "log", "--merges", "--first-parent", "--format=%h%x01%cs%x01%s%x01%b%x01%P%x00", main)  # fmt: skip
    for rec in log.split("\0"):
        if not rec.strip():
            continue
        h, day, subj, body, parents = rec.strip().split("\x01")
        m = re.match(r"Merge pull request #(\d+)", subj)
        if m:
            title = body.strip().splitlines()[0] if body.strip() else subj
            got[int(m.group(1))] = (h, day, title, parents.split()[-1])
    return got


def main_(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    repo, main, out = Path(argv[0]), argv[1], Path(argv[2])
    try:
        main = git(repo, "rev-parse", "--verify", main + "^{commit}").strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"refused: no checkout at {repo} holding {argv[1]}", file=sys.stderr)
        return 2
    if out.exists():
        print(f"refused: {out} is already there", file=sys.stderr)
        return 2
    branches, prs = refs(repo, "refs/remotes/origin"), refs(repo, "refs/remotes/pr")
    if not branches:
        print("refused: no branches fetched (git fetch origin '+refs/heads/*:refs/remotes/origin/*')", file=sys.stderr)  # fmt: skip
        return 2
    out.mkdir(parents=True)
    done = merges(repo, main)
    page = [f"# UTETY's pull requests\n\nAs main at {main[:7]} has them: {len(prs)} pull requests.\n"]  # fmt: skip
    for r in sorted(prs, key=lambda r: int(r.split("/")[-1])):
        n, head = int(r.split("/")[-1]), git(repo, "rev-parse", r).strip()
        if n in done:
            h, day, title, _ = done[n]
            state, span = f"merged into main at {h} on {day}", f"{h}^1..{h}^2"
        else:
            title = git(repo, "log", "-1", "--format=%s", head).strip()
            state, span = "not merged into main", f"{main}..{head}"
        page += [f"## PR #{n}: {title}\n", f"{state}; its head {head[:7]}.\n"]
        page += [c + "\n" for c in commits(repo, span)]
    (out / "prs.md").write_text("\n".join(page), encoding="utf-8")
    page = [f"# UTETY's branches\n\nAs main at {main[:7]} has them: {len(branches)} branches.\n"]  # fmt: skip
    for r in sorted(branches):
        name, ahead = r.removeprefix("origin/"), int(git(repo, "rev-list", "--count", f"{main}..{r}"))  # fmt: skip
        base = git(repo, "merge-base", main, r).strip()[:7]
        if not ahead:
            page.append(
                f"## {name}\n\nmerged into main: every commit of it is there.\n"
            )
            continue
        page += [f"## {name}\n", f"{ahead} commits ahead of main, never merged; it left main at {base}. Its files that differ are at branches/{name.replace('/', '-')}/.\n"]  # fmt: skip
        page += [c + "\n" for c in commits(repo, f"{main}..{r}")]
        files = git(
            repo, "diff", "--name-only", "--diff-filter=AM", f"{main}...{r}"
        ).split()
        if files:
            tar = subprocess.run(["git", "-C", str(repo), "archive", r, "--", *files], capture_output=True, check=True).stdout  # fmt: skip
            to = out / "branches" / name.replace("/", "-")
            to.mkdir(parents=True)
            with tarfile.open(fileobj=io.BytesIO(tar)) as t:
                t.extractall(to, filter="data")
    (out / "branches.md").write_text("\n".join(page), encoding="utf-8")
    print(f"{len(prs)} pull requests and {len(branches)} branches written to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main_(sys.argv[1:]))
