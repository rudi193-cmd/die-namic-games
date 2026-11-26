"""box/maps: the towns laid with the map maker, one a world, each held to the
tiles the pages draw (ui/tables/fair-tiles.js, read by Node as the pages read
it): every tile one the fair has, one a spot, every edge matching the edge it
meets, the whole town in one piece, and every named place on a tile that has
that kind of place, no name twice. A map names its world, which is in
box/worlds/."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MAPS = sorted((ROOT / "box" / "maps").glob("*.json"))
TILES_JS = ROOT / "ui" / "tables" / "fair-tiles.js"

CHECK = r"""
const fs = require("fs"), vm = require("vm");
const ctx = { document: { createElement: () => ({}), head: { append() {} } }, esc: (s) => s, window: {} };
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(process.argv[1], "utf8") + "\nthis.api = { T, edgeOf, key, DIRS, landmarks, mapTiles, placeAt };", ctx);
const { T, edgeOf, key, DIRS, mapTiles, placeAt } = ctx.api;
const out = [];
for (const path of process.argv.slice(2)) {
  const m = JSON.parse(fs.readFileSync(path, "utf8")), why = [];
  const seen = new Set();
  for (const [x, y, id, rot] of m.tiles) {
    if (!T[id]) why.push(`${x},${y}: ${id} isn't one of the fair's tiles`);
    if (![0, 1, 2, 3].includes(rot)) why.push(`${x},${y}: its turn is 0 to 3`);
    if (seen.has(key(x, y))) why.push(`${x},${y}: two tiles on one spot`);
    seen.add(key(x, y));
  }
  const tiles = mapTiles({ ...m, tiles: m.tiles.filter((t) => T[t[2]]) });
  for (const t of tiles.values()) for (let d = 0; d < 4; d++) {
    const nb = tiles.get(key(t.x + DIRS[d][0], t.y + DIRS[d][1]));
    if (nb && T[t.id] && T[nb.id] && edgeOf(t.id, t.rot, d) !== edgeOf(nb.id, nb.rot, (d + 2) % 4)) why.push(`${t.x},${t.y}: its edge toward ${nb.x},${nb.y} doesn't match`);
  }
  const first = tiles.keys().next().value, reach = new Set([first]), todo = [first];
  while (todo.length) { const [x, y] = todo.pop().split(",").map(Number); for (const [dx, dy] of DIRS) { const k = key(x + dx, y + dy); if (tiles.has(k) && !reach.has(k)) { reach.add(k); todo.push(k); } } }
  if (reach.size !== tiles.size) why.push(`${tiles.size - reach.size} tiles aren't joined to the rest`);
  const names = new Set();
  for (const p of m.places) {
    if (!placeAt(tiles, p.at)) why.push(`${p.name}: nothing at ${p.at} can be named`);
    if (names.has(p.name.toLowerCase())) why.push(`${p.name}: named twice`);
    names.add(p.name.toLowerCase());
  }
  out.push({ path, why });
}
console.log(JSON.stringify(out));
"""

pytestmark = pytest.mark.skipif(shutil.which("node") is None, reason="the maps are checked by the pages' own tile code, run in Node")


def checked(*paths: Path) -> list[dict]:
    got = subprocess.run(["node", "-e", CHECK, str(TILES_JS), *map(str, paths)], capture_output=True, text=True, check=False)  # fmt: skip
    assert got.returncode == 0, got.stderr
    return json.loads(got.stdout)


def test_there_is_a_map_and_each_names_a_world_in_the_box():
    assert MAPS, "box/maps holds the Lantern Fair's map at least"
    for p in MAPS:
        m = json.loads(p.read_text())
        assert p.stem == m["world"] and (ROOT / "box" / "worlds" / f"{m['world']}.json").exists(), p.name


@pytest.mark.parametrize("path", MAPS, ids=lambda p: p.stem)
def test_every_map_holds_to_the_tiles(path):
    assert checked(path)[0]["why"] == []


def test_the_lantern_fairs_map_has_the_worlds_places_on_it():
    world = json.loads((ROOT / "box" / "worlds" / "lantern-fair.json").read_text())
    named = {p["name"] for p in json.loads((ROOT / "box" / "maps" / "lantern-fair.json").read_text())["places"]}
    assert {p["name"] for p in world["places"]} <= named


def test_a_map_that_doesnt_hold_is_named_by_what_is_wrong(tmp_path):
    good = json.loads(MAPS[0].read_text())
    bad = {**good, "tiles": [*good["tiles"], [99, 99, "lane", 0], [good["tiles"][0][0], good["tiles"][0][1], "castle", 0]],
           "places": [*good["places"], {"name": good["places"][0]["name"].upper(), "at": "0,0:nowhere"}]}  # fmt: skip
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(bad))
    why = " | ".join(checked(path)[0]["why"])
    assert "castle isn't one of the fair's tiles" in why and "two tiles on one spot" in why
    assert "aren't joined to the rest" in why and "named twice" in why and "can be named" in why
