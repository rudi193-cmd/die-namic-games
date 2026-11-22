# ci

What Die-Namic's CI (`.github/workflows/ci.yml`) runs beyond the tests. Each
is one of willow's maintainer add-ons, run from the willow
[willow.pin.json](../willow.pin.json) names, checked out beside this repo (so
none of willow's files is read as Die-Namic's). Locally, with willow beside
die-namic-games or `WILLOW_ROOT` set:

    python ci/known.py --db OSV_DIR          # every report row known
    python ci/mutants.py run [FILE ...]      # the code broken on purpose
    python ci/mutants.py list FILE           # the breaks a file can take

| Job | Add-on | What fails it |
|---|---|---|
| `plan` | ci-cache | nothing it finds: it prints the pip cache's key, keyed on every `requirements.txt` here, [lock/](../lock/) among them, and every job restores `~/.cache/pip` on it |
| `known` | unpinned | a dependency range no lockfile pins |
| | agents-md-check | a path or command an agent instruction file names that the repo doesn't have |
| | secrets-audit | a secret in plain text |
| | ref-check | a link to a file, or a quoted line, that isn't there |
| | advisories | a locked pin a known advisory names, from osv.dev's PyPI database, fetched each run |
| `mutants` | mutants | a break of Die-Namic's code the tests pass on, one job a file |
| `die-namic`, `mutants` | memo.py (willow's ci-memo move, kept small) | nothing: a pull request whose key is one main already passed on stands on main's verdict and skips the job (below) |
| `die-namic` | slow-tests | nothing: the slowest tests and files of the run, in its summary |
| `why` | ci-why | nothing: on a red run only, it puts each failed job's failing block in the run's summary |

## known.py and known.json

The report add-ons find things that are no finding: a variable named for a password that holds a pip
count, a JavaScript template read as a link. [known.json](known.json) lists
each with why, matched by add-on, group, file (never the line, which moves)
and what it says, with how many such rows. A row it doesn't accept fails. An
entry no row matches is stale and fails too, so the list never keeps a reason
for something that has gone. A new entry is a line checked by hand, never a
way to turn a check green; and its reason says what the text is without
quoting it, or the reason itself is found next run.

## mutants.py and mutants.json

willow's mutants add-on is built for willow's own add-ons; mutants.py drives
it for Die-Namic: the add-on's own breaks and ids (a comparison flipped, an
`and` made `or`, a whole number made one larger), over the files
[mutants.json](mutants.json) names, each break run against the whole suite,
fastest file first, in a copy of the repo. The suite must pass unbroken
first. A break the tests pass on fails, unless `accepted` gives the reason no
test could tell it from the code; an accepted id that no longer survives is
stale. The fast files take every break; the box's files, whose suite takes a
minute a break, the first six by id, the same on every machine.

## memo.py: a verdict that stands on the bytes it reached

A mutants job is ten to twenty-five minutes, one per file, and the tests job
is four; most pull requests here change prose, boxes and records that no test
reads. A job's verdict is a function of the bytes it can reach, so
`ci/memo.py key` hashes them, every tracked file but the few nothing reads
([memo.py](memo.py) names them, and `tests/test_memo.py` holds that no string
in the code names one), with the gate's name, the Python, the runner and the
commit of willow-bot (checked out at its head, so the tree can't say). The
workflow keys a cache on it:

- **A pull request** restores `memo-v1-KEY` from main's runs. A hit means every
  byte the job can reach is one main's job already passed on: the job says so
  in its summary and skips its install and its run. A miss runs it.
- **A push to main** never restores: it always runs, and saves the key when
  it passes, so a pull request has a verdict to stand on. Main's run stays the
  merge's evidence, as in willow's CI.
- **A failed run saves nothing** (a cache is saved only after a job passes), so a
  red job is never a standing one.

This is willow's `ci-memo`'s move, not the add-on: ci-memo's gates are willow's
and its pins are ci.py's records, so it can't be run on this repo. It keeps
the two rules that matter: **a key is bytes, never a guess**, and **the reach
is drawn wide, never narrow** (README.md and `.github/` are reached; only
`boxes/`, `open.md`, `open-gaps-from-the-boxes.md` and this file are left
out). To change what is reached, change `EXCLUDED` in memo.py; to change how a
key is made, change `VERSION`, so no old verdict stands.

    python ci/memo.py key --gate tests --extra python=3.12
    python ci/memo.py why open.md

Not done: the other jobs (`known` is fast; `game-lab-sims`, `ai-game-master`
and `the-table` are not memoized), and willow's `test-impact` and `test-shards`
(its plans speak ci.py's gate names, and the tests job is four minutes).

## slow-tests

The tests job writes pytest's junit file and gives it to willow's slow-tests,
from the pin: the slowest tests and files of the run go into the run's summary.
It needs more than one run to say "slower than before" (`--runs` takes a folder
of runs named to sort); with one, it names where the time went.

## local.py: the same moves, for the person working

    python ci/local.py needs     # what this machine can't run, and which tests that costs
    python ci/local.py plan      # the tests a change can reach
    python ci/local.py run       # run those; a full pass is kept for these bytes
    python ci/local.py lists     # test files the mutants jobs never run

The same idea as memo.py, on a laptop: most changes reach a few tests, and a full
pass on bytes that haven't moved needn't be repeated.

- **`needs`** names what is missing (willow beside this repo, willow-bot's
  one-script, dndwright, ruff, tesseract) and what each costs, so a missing tool
  isn't taken for a failure of yours.
- **`plan`** reads what changed since `--base` (default `origin/main`), plus the
  working tree and new files. A test file is itself; a module of `box/`,
  `die_namic/`, `games/` or `ci/` is the tests that name it and those of every
  module that imports it; prose nothing reads is nothing. **Anything it can't
  place runs everything**: wide, never narrow.
- **`run`** runs the plan, stopping at the first failure. A *full* run that
  passes is kept under `.git/`, keyed on memo.py's key (every file a test reads,
  the Python, whether one-script and dndwright are here); the next `run` on the
  same bytes says it stands and runs nothing (`--force` runs anyway, `--all`
  runs everything). A partial pass keeps nothing.
- **`lists`** is how the mutants gap was found: the mutants jobs run only the
  files [mutants.json](mutants.json) names, so a test file it doesn't list can
  never kill a break there. Add a new file to the list when a break only it
  catches.

CI still runs the full suite and every mutants job on main's commit; a stand
here is this machine's own last full pass, not a verdict CI accepts.
