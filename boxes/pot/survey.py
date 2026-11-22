#!/usr/bin/env python3
"""Survey a pot: one box per chunk, the same questions asked of each, one page.

usage: survey.py POT [--questions FILE] [--top N] [--jobs N] [--only NAME,...]

Lays a fresh box over each chunk (POT/survey/box-NAME, a scratch key, nothing
sealed), asks every question in survey-questions.tsv through willow's
all-passages, and writes POT/survey/survey.md:
  1. facts, counted by code, not ranked: licence file, files by kind, build files;
  2. the matrix: for each question and chunk, a hit (a served passage holds the
     question's rule), a miss, or an unreadable box;
  3. for each question, the best passage per chunk that hit, with file:line.
A hit is evidence to read, not proof. A miss means "not in the top N", not
"absent". Raw answers are kept in POT/survey/raw/. Stdlib only.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "box"))
import willow_pin


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, check=False, **kw)


def questions(path):
    qs = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        qid, label, q, rule = line.rstrip("\n").split("\t")
        qs.append((qid, q, re.compile(rule), label))
    return qs


def facts(d):
    exts, build, lic = {}, [], ""
    tests = 0
    for root, _, files in os.walk(d):
        for f in files:
            e = os.path.splitext(f)[1].lower() or f
            exts[e] = exts.get(e, 0) + 1
            if f in (
                "pyproject.toml",
                "requirements.txt",
                "Cargo.toml",
                "mix.exs",
                "package.json",
                "go.mod",
            ) or f.endswith(".csproj"):
                build.append(f)
            if re.match(r"(?i)test_|.*_test\.|.*tests?\.", f):
                tests += 1
    for n in sorted(os.listdir(d)):
        if n.upper().startswith("LICENSE"):
            text = Path(d, n).read_text(encoding="utf-8", errors="replace")
            first = [ln.strip() for ln in text.splitlines() if ln.strip()][:2]
            lic += f"{n}: {' '.join(first)[:70]}; "
    top = ", ".join(
        f"{k} {v}" for k, v in sorted(exts.items(), key=lambda kv: -kv[1])[:5]
    )
    return {
        "licence": lic.rstrip("; ") or "no LICENSE file in the pile",
        "kinds": top,
        "build": ", ".join(sorted(set(build))[:5]) or "-",
        "test files": tests,
    }


def survey_one(name, pile, out, W, words, qs, top):
    box = os.path.join(out, "box-" + name)
    key = os.path.join(out, "key-" + name)
    for p in (box, key):
        shutil.rmtree(p, ignore_errors=True) if os.path.isdir(p) else (
            os.path.exists(p) and os.remove(p)
        )
    r = run(
        [
            sys.executable,
            os.path.join(W, "kernel.py"),
            "init",
            "--box",
            box,
            "--pile",
            pile,
            "--key",
            key,
            "--words",
            words,
        ]
    )
    if r.returncode != 0:
        return name, None, r.stderr.strip()[:200]
    res = {}
    for qid, q, rule, label in qs:
        r = run(
            [
                sys.executable,
                os.path.join(W, "adapters/stdlib/all-passages/all_passages.py"),
                "--box",
                box,
                "--top",
                str(top),
                q,
            ]
        )
        raw = os.path.join(out, "raw", f"{name}-{qid}.json")
        Path(raw).write_text(r.stdout)
        try:
            served = json.loads(r.stdout).get("served", [])
        except (ValueError, KeyError, AttributeError):
            served = []
        hit = next((s for s in served if rule.search(s["text"])), None)
        res[qid] = {
            "served": len(served),
            "hit": hit,
            "first": served[0] if served else None,
        }
    return name, res, ""


def cite(where):
    """`path:12` read as a citation of another repo, not a reference in this one: `path, line 12`."""
    path, _, line = where.rpartition(":")
    return f"{path}, line {line}" if path and line.isdigit() else where


def snip(t, rule, n=230):
    m = rule.search(t)
    a = max(0, (m.start() if m else 0) - 60)
    return re.sub(r"\s+", " ", t[a : a + n]).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pot")
    ap.add_argument("--questions", default=os.path.join(HERE, "survey-questions.tsv"))
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    pot = os.path.abspath(a.pot)
    W = willow_pin.root()
    out = os.path.join(pot, "survey")
    os.makedirs(os.path.join(out, "raw"), exist_ok=True)
    words = os.path.join(pot, "words.txt")
    if not os.path.exists(words):
        shutil.copy(os.path.join(HERE, "words.txt"), words)
        os.chmod(words, 0o600)
    chunks = sorted(
        n
        for n in os.listdir(os.path.join(pot, "pile"))
        if os.path.isdir(os.path.join(pot, "pile", n))
    )
    if a.only:
        chunks = [c for c in chunks if c in a.only.split(",")]
    qs = questions(a.questions)
    with ThreadPoolExecutor(a.jobs) as ex:
        done = list(
            ex.map(
                lambda c: survey_one(
                    c, os.path.join(pot, "pile", c), out, W, words, qs, a.top
                ),
                chunks,
            )
        )
    results = {n: r for n, r, e in done if r}
    errors = {n: e for n, r, e in done if not r}
    L = [
        f"# survey of {len(chunks)} chunks, {len(qs)} questions, top {a.top}\n",
        (
            "A hit: a served passage holds the question's rule (survey-questions.tsv). Evidence to read, not proof. A miss: not in the top "
            f"{a.top}, which is not the same as absent. Nothing here is sealed.\n"
        ),
        "## facts (counted by code)\n",
        "| chunk | licence file | most files | build files | test files |",
        "|---|---|---|---|---|",
    ]
    for c in chunks:
        f = facts(os.path.join(pot, "pile", c))
        L.append(
            f"| {c} | {f['licence']} | {f['kinds']} | {f['build']} | {f['test files']} |"
        )
    L += [
        "",
        "## matrix (● hit, · miss, ! box failed)\n",
        "| | " + " | ".join(chunks) + " |",
        "|---|" + "---|" * len(chunks),
    ]
    for qid, q, rule, label in qs:
        cells = [
            "!" if c in errors else ("●" if results[c][qid]["hit"] else "·")
            for c in chunks
        ]
        L.append(f"| **{qid}** {label} | " + " | ".join(cells) + " |")
    L.append("\n## by question\n")
    for qid, q, rule, label in qs:
        L.append(f'### {qid}: {label} (asked: "{q}")\n')
        for c in chunks:
            if c in errors:
                L.append(f"- **{c}**: box failed ({errors[c]})")
                continue
            r = results[c][qid]
            if r["hit"]:
                h = r["hit"]
                L.append(f"- **{c}** ● `{cite(h['where'])}` — {snip(h['text'], rule)}")
            elif r["first"]:
                L.append(
                    f"- **{c}** · nothing in the top {a.top} holds the rule; best-ranked: `{cite(r['first']['where'])}`"
                )
            else:
                L.append(f"- **{c}** · no passage held the question's words")
        L.append("")
    p = os.path.join(out, "survey.md")
    Path(p).write_text("\n".join(L))
    print(
        f"survey: {len(chunks)} chunks x {len(qs)} questions; hits {sum(1 for c in results for q in results[c] if results[c][q]['hit'])} of {len(results) * len(qs)}; page {p}"
    )
    for n, e in errors.items():
        print("failed:", n, e)


main()
