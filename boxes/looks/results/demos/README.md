# willow's share demos, run and screenshotted (2026-11-22)

Two of willow's demos build a page per person from what their scene wrote,
never reading a box, a key or a pile. Both were run here at the pin
(370f74a), with Chromium through Playwright, for want 10.

    # from a willow checkout at the pin; OUT is a scratch folder
    python3 demo/annex/make_life.py
    python3 demo/annex/scene.py run --life demo/annex/life --to OUT/annex --box OUT/annex-study
    python3 demo/annex/annex_os.py build --scene OUT/annex --to OUT/annex-os.html
    python3 demo/blackout/make_life.py
    python3 demo/blackout/scene.py run --life demo/blackout/life --to OUT/blackout --box OUT/blackout-study
    python3 demo/blackout/kiosk.py build --scene OUT/blackout --to OUT/kiosk.html
    node shot.js OUT       # these four pictures, into OUT

Annex's scene took 8 s (8 boxes, 8 doors), blackout's 10 s (8 boxes, 8
users); both exited 0. Everything in them is invented by the demos.

| Picture | What it shows |
|---|---|
| [annex-door.png](annex-door.png) | ANNEX-OS, a green-screen terminal, wearing the Intake badge: its door OPEN ("your badge"), the other seven LOCKED, "not on record for you" |
| [annex-witness.png](annex-witness.png) | the same page after WITNESS RUN |
| [kiosk-papers.png](kiosk-papers.png) | the Brannock kiosk, a 2013 office PC, logged on as Ruth Haldane: "Papers on record for this logon. Nothing here is anyone else's": what she sealed and where it came from, the seven packages she sent and to whom, the one she received and that it was good |
| [kiosk-denied.png](kiosk-denied.png) | the same page after "Open someone else's papers..." |

For Die-Namic: choosing who you are is `[ my tables ▾ ]` and your seat;
your own door is your screen, every other seat's is not on record; sealed,
sent and received are what your table made true, the pages you put on the
table, and what arrived. Both pages are built once from a finished scene;
a table's would have to follow packages arriving during the night.
