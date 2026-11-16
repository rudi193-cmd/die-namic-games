# lock

`requirements.txt` here pins, to one exact version, each dependency the
builds' own `requirements.txt` files declare as a range (`chess>=1.10`,
`dice>=4.0.0`). Those files say what the code needs; this says what CI
installs, as a constraints file (`pip install -r ... -c lock/requirements.txt`).

willow's unpinned add-on fails CI on a range no lockfile pins, advisories
matches these pins to osv.dev's advisories, and ci-cache keys the pip cache on
them, so moving a pin is the one change that re-downloads. To move one: change
its line here, and let CI's run show the builds still pass on it.
