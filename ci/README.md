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
