/* The map maker: a town laid with the fair's tiles, for a story's world.
   Deal one from seed words (the same words deal the same town), or lay it by
   hand: pick a tile, tap a spot, tap it to turn, Place; every edge it touches
   must match. Lift takes a tile back up. Name puts a name on a square, a well,
   a crossing, a basin, a bridge, a stall or a landing: each named one is a
   place in the world, and the Table lights it when a scene is there, and
   write.py offers it when a story asks where. Save gives the map as a file
   for box/maps/; nothing here is kept on its own. */
const MAPS = GAME.maps || [], WORLDS = GAME.worlds || [];
let M, mode = "lay", pick = "lane", rot = 0, spot = null, naming = null, board = null;

function blank(world, set = SET_OF_WORLD[world] || "fair") { return { world, set, seed: "", tiles: new Map([[key(0, 0), { x: 0, y: 0, id: "start", rot: 0, set, stalls: stallsOf("start").map((s) => ({ ...s, good: null })) }]]), places: [] }; }
function fromMap(m) { return { world: m.world, set: m.set || "fair", seed: m.seed || "", tiles: mapTiles(m), places: m.places.map((p) => ({ ...p })) }; }
/* the world being mapped: its map from box/maps if it has one, else a town dealt for it */
function openWorld(world) {
  const m = MAPS.find((x) => x.world === world);
  M = m ? fromMap(m) : blank(world);
  spot = null; naming = null;
  if (m) { board.fit(M.tiles.values()); render(); } else deal(seedWords(), 24);
}
const tileOf = (x, y, id, r) => ({ x, y, id, rot: r, set: M ? M.set : "fair", stalls: stallsOf(id).map((s) => ({ ...s, good: null })) });

function fitsHere(x, y, id, r) {
  if (M.tiles.has(key(x, y))) return false;
  let touches = false;
  for (let d = 0; d < 4; d++) {
    const nb = M.tiles.get(key(x + DIRS[d][0], y + DIRS[d][1]));
    if (!nb) continue;
    touches = true;
    if (edgeOf(id, r, d) !== edgeOf(nb.id, nb.rot, (d + 2) % 4)) return false;
  }
  return touches || M.tiles.size === 0;
}
function openSpots() {
  const out = new Map();
  for (const t of M.tiles.values()) for (const [dx, dy] of DIRS) { const k = key(t.x + dx, t.y + dy); if (!M.tiles.has(k)) out.set(k, [t.x + dx, t.y + dy]); }
  return [...out.values()];
}

/* a town dealt from seed words: the fair's tiles shuffled by the words, each
   set at a spot the words pick among those it fits */
function deal(words, size) {
  const rng = Stream.fromText(`lantern-map:${words}`);
  M = blank(M ? M.world : "lantern-fair", M ? M.set : "fair");
  M.seed = words;
  const pool = rng.shuffled(TILES.filter((t) => t.id !== "start").flatMap((t) => Array(t.n).fill(t.id)));
  for (const id of pool) {
    if (M.tiles.size >= size) break;
    const ok = [];
    for (const [x, y] of openSpots()) for (let r = 0; r < 4; r++) if (fitsHere(x, y, id, r)) ok.push([x, y, r]);
    if (!ok.length) continue;
    const [x, y, r] = rng.pick(ok);
    M.tiles.set(key(x, y), tileOf(x, y, id, r));
  }
  spot = null; naming = null;
  board.fit(M.tiles.values());
  render();
}

function landmarkNear(bx, by) {
  let best = null;
  for (const t of M.tiles.values()) for (const lm of landmarks(t.id, M.set)) {
    const [px, py] = onBoard(t, ...lm.at), d = Math.hypot(px - bx, py - by);
    if (d < 34 && (!best || d < best.d)) best = { d, at: `${key(t.x, t.y)}:${lm.k}`, kind: lm.kind };
  }
  return best;
}
function tapBoard(bx, by) {
  const x = Math.floor(bx / 100), y = Math.floor(by / 100);
  if (mode === "lay") {
    if (M.tiles.has(key(x, y)) || !openSpots().some(([a, b]) => a === x && b === y)) return;
    spot = [x, y];
    if (!fitsHere(x, y, pick, rot)) for (let r = 1; r < 4; r++) if (fitsHere(x, y, pick, (rot + r) % 4)) { rot = (rot + r) % 4; break; }
  } else if (mode === "lift") {
    if (!M.tiles.has(key(x, y)) || M.tiles.size === 1) return;
    M.tiles.delete(key(x, y));
    M.places = M.places.filter((p) => !p.at.startsWith(key(x, y) + ":"));
  } else {
    const lm = landmarkNear(bx, by);
    naming = lm ? { at: lm.at, kind: lm.kind } : null;
  }
  render();
}
function placeTile() {
  if (!spot) return frame.refuse("tap a spot beside the town first");
  if (!fitsHere(spot[0], spot[1], pick, rot)) return frame.refuse("every edge it touches has to match: canal to canal, lane to lane, square to square, quay to quay");
  M.tiles.set(key(...spot), tileOf(spot[0], spot[1], pick, rot));
  spot = null;
  render();
}
function nameIt(name) {
  name = name.trim();
  if (!naming) return;
  M.places = M.places.filter((p) => p.at !== naming.at);
  if (name) {
    if (M.places.some((p) => p.name.toLowerCase() === name.toLowerCase())) return frame.refuse(`${name} is already a place on this map`);
    M.places.push({ name, at: naming.at });
  }
  naming = null;
  render();
}
function saved() {
  const tiles = [...M.tiles.values()].sort((a, b) => a.y - b.y || a.x - b.x).map((t) => [t.x, t.y, t.id, t.rot]);
  return { world: M.world, ...(M.set !== "fair" ? { set: M.set } : {}), seed: M.seed, tiles, places: M.places.slice().sort((a, b) => a.name.localeCompare(b.name)) };
}
/* written the way box/maps keeps it: one tile a line, so a change reads in a diff */
function savedText() {
  const m = saved();
  return `{\n "world": ${JSON.stringify(m.world)},\n${m.set ? ` "set": ${JSON.stringify(m.set)},\n` : ""} "seed": ${JSON.stringify(m.seed)},\n "tiles": [\n${m.tiles.map((t) => `  ${JSON.stringify(t)}`).join(",\n")}\n ],\n "places": [\n${m.places.map((p) => `  ${JSON.stringify(p)}`).join(",\n")}\n ]\n}\n`;
}

function boardSVG() {
  let s = FAIR_DEFS;
  if (mode === "lay") for (const [x, y] of openSpots()) s += `<rect x="${x * 100 + 4}" y="${y * 100 + 4}" width="92" height="92" rx="8" class="lf-spot"/>`;
  for (const t of M.tiles.values()) s += tileG(t.x, t.y, t.id, t.rot, t.stalls, "", M.set);
  if (mode === "lift") for (const t of M.tiles.values()) if (M.tiles.size > 1) s += `<rect x="${t.x * 100 + 3}" y="${t.y * 100 + 3}" width="94" height="94" class="mm-lift"/>`;
  if (mode === "name") for (const t of M.tiles.values()) for (const lm of landmarks(t.id, M.set)) {
    const at = `${key(t.x, t.y)}:${lm.k}`;
    if (M.places.some((p) => p.at === at)) continue;
    const [px, py] = onBoard(t, ...lm.at);
    s += `<circle cx="${px}" cy="${py}" r="14" class="mm-spot ${naming && naming.at === at ? "on" : ""}"/>`;
  }
  s += labelsSVG(M.places.map((p) => [p, placeAt(M.tiles, p.at)]).filter(([, w]) => w).map(([p, w]) => ({ x: w.pt[0], y: w.pt[1], text: p.name, cls: naming && naming.at === p.at ? "here" : "" })));
  if (mode === "lay" && spot) {
    const ok = fitsHere(spot[0], spot[1], pick, rot);
    s += tileG(spot[0], spot[1], pick, rot, null, `opacity="0.9"`, M.set) + `<rect x="${spot[0] * 100 + 1.5}" y="${spot[1] * 100 + 1.5}" width="97" height="97" class="lf-held ${ok ? "ok" : "no"}"/>`;
  }
  return s;
}

function render() {
  const worldName = (WORLDS.find((w) => w.id === M.world) || {}).title || M.world;
  if (!document.getElementById("mm-wrap")) {
    frame.stage(`<div class="mm"><div class="mm-head"><div class="mm-modes" role="group" aria-label="what a tap does">${[["lay", "Lay"], ["lift", "Lift"], ["name", "Name"]].map(([k, l]) => `<button class="lf-kind" data-mode="${k}">${l}</button>`).join("")}</div>
      <div class="mm-deal"><select id="mm-world" aria-label="which world">${WORLDS.map((w) => `<option value="${esc(w.id)}">${esc(w.title)}</option>`).join("")}</select><select id="mm-set" aria-label="the look">${Object.entries(SETS).map(([k, v]) => `<option value="${k}">looks like ${esc(v.name)}</option>`).join("")}</select></div>
      <div class="mm-deal"><input id="mm-seed" aria-label="seed words" placeholder="seed words"><select id="mm-size" aria-label="how many tiles">${[16, 24, 36, 48].map((n) => `<option ${n === 24 ? "selected" : ""}>${n}</option>`).join("")}</select><button class="btn ghost" id="mm-deal">Deal</button></div></div>
      <div class="lf-wrap fb-wrap" id="mm-wrap"><svg id="mm-svg" class="fb-svg"></svg></div><div class="lf-bottom" id="mm-bottom"></div></div>`);
    board = new FairBoard(document.getElementById("mm-svg"), document.getElementById("mm-wrap"), tapBoard, { min: 640 });
    document.querySelectorAll("[data-mode]").forEach((b) => (b.onclick = () => { mode = b.dataset.mode; spot = null; naming = null; render(); }));
    document.getElementById("mm-world").onchange = (e) => openWorld(e.target.value);
    document.getElementById("mm-set").onchange = (e) => { M.set = e.target.value; for (const t of M.tiles.values()) t.set = M.set; render(); };
    document.getElementById("mm-deal").onclick = () => deal(document.getElementById("mm-seed").value.trim() || seedWords(), +document.getElementById("mm-size").value);
    board.fit(M.tiles.values());
  }
  document.querySelectorAll("[data-mode]").forEach((b) => { b.classList.toggle("on", b.dataset.mode === mode); b.setAttribute("aria-pressed", b.dataset.mode === mode); });
  document.getElementById("mm-seed").value = M.seed;
  document.getElementById("mm-world").value = M.world;
  document.getElementById("mm-set").value = M.set;
  board.lastTiles = [...M.tiles.values()];
  board.apply();
  document.getElementById("mm-svg").innerHTML = boardSVG();
  let bottom = "";
  if (mode === "lay") {
    const palette = TILES.filter((t) => t.id !== "start").map((t) => `<button class="mm-pal ${t.id === pick ? "on" : ""}" data-pick="${t.id}" aria-label="${tileName(t.id)}"><svg viewBox="0 0 100 100" width="52" height="52">${tileG(0, 0, t.id, 0, null, "", M.set)}</svg></button>`).join("");
    bottom = `<div class="mm-palette" role="group" aria-label="tiles">${palette}</div><button class="lf-hand" id="mm-turn" aria-label="the tile: tap to turn it"><svg viewBox="0 0 100 100" width="72" height="72">${tileG(0, 0, pick, rot, null, "", M.set)}</svg><span>tap to turn</span></button><button class="btn" id="mm-place" ${spot ? "" : "disabled"}>Place</button>`;
  } else if (mode === "lift") bottom = `<div class="lf-ask">Tap a tile to lift it.</div>`;
  else if (naming) {
    const free = (WORLDS.find((w) => w.id === M.world) || { places: [] }).places.filter((p) => !M.places.some((q) => q.name.toLowerCase() === p.toLowerCase()));
    const cur = M.places.find((p) => p.at === naming.at);
    bottom = `<div class="mm-name"><label>Name this ${esc(naming.kind)}<input id="mm-name" value="${esc(cur ? cur.name : "")}" placeholder="The lantern bridge"></label>${free.length ? `<div class="mm-chips">${free.map((p) => `<button class="mm-chip" data-name="${esc(p)}">${esc(p)}</button>`).join("")}</div>` : ""}<div class="mm-row"><button class="btn" id="mm-ok">Name it</button>${cur ? `<button class="btn ghost" id="mm-unname">Take the name off</button>` : ""}</div></div>`;
  } else { const pl = Object.values(skinOf(M.set).places); bottom = `<div class="lf-ask">Tap a ring to name a ${pl.slice(0, -1).join(", ")} or ${pl[pl.length - 1]}.</div>`; }
  document.getElementById("mm-bottom").innerHTML = bottom;
  document.querySelectorAll("[data-pick]").forEach((b) => (b.onclick = () => { pick = b.dataset.pick; rot = 0; if (spot && !fitsHere(spot[0], spot[1], pick, rot)) for (let r = 1; r < 4; r++) if (fitsHere(spot[0], spot[1], pick, r)) { rot = r; break; } render(); }));
  const on = (id, f) => { const b = document.getElementById(id); if (b) b.onclick = f; };
  on("mm-turn", () => { rot = (rot + 1) % 4; render(); });
  on("mm-place", placeTile);
  on("mm-ok", () => nameIt(document.getElementById("mm-name").value));
  on("mm-unname", () => nameIt(""));
  document.querySelectorAll("[data-name]").forEach((b) => (b.onclick = () => nameIt(b.dataset.name)));
  const nm = document.getElementById("mm-name");
  if (nm) { nm.onkeydown = (e) => { if (e.key === "Enter") nameIt(nm.value); }; }
  frame.status(`<b>${esc(worldName)}</b>: ${M.tiles.size} tiles, ${M.places.length} place${M.places.length === 1 ? "" : "s"} named${M.seed ? ` · dealt from “${esc(M.seed)}”` : ""}`);
  frame.panel("places", "The places on the map", M.places.length ? `<ul class="lf-rules">${M.places.slice().sort((a, b) => a.name.localeCompare(b.name)).map((p) => `<li><b>${esc(p.name)}</b> · ${esc(placeAt(M.tiles, p.at)?.lm.kind || "")}</li>`).join("")}</ul>` : `<p class="note">None named yet: choose Name and tap a ring.</p>`);
  frame.panel("save", "Save the map", `<p class="note">Kept as <code>box/maps/${esc(M.world)}.json</code>, beside the world. The Table and write.py read it from there.</p><div class="mm-row"><button class="btn" id="mm-copy">Copy</button><button class="btn ghost" id="mm-down">Download</button></div><pre class="mm-json" id="mm-json">${esc(savedText())}</pre>`);
  on("mm-copy", async () => { try { await navigator.clipboard.writeText(savedText()); frame.status("<b>Copied.</b> Paste it into box/maps/" + esc(M.world) + ".json."); } catch (e) { frame.refuse("the browser wouldn't copy; select the text below instead"); } });
  on("mm-down", () => { const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([savedText()], { type: "application/json" })); a.download = `${M.world}.json`; a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 1000); });
}

const style = document.createElement("style");
style.textContent = `
.mm { display: grid; gap: 10px; width: 100%; min-width: 0; justify-self: stretch; }
.mm > * { min-width: 0; }
.mm-head { display: flex; gap: 10px; flex-wrap: wrap; justify-content: space-between; align-items: center; }
.mm-modes, .mm-deal, .mm-row, .mm-chips { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }
.mm-deal input, .mm-deal select, .mm-name input { font: inherit; color: var(--chalk); background: #0006; border: 1px solid var(--edge); border-radius: 9px; padding: 9px 10px; min-height: 44px; }
.mm-deal input { width: 11em; }
.lf-wrap { height: min(58vh, 560px); min-height: 300px; }
.lf-kind { padding: 10px 14px; min-height: 44px; border-radius: 10px; border: 2px solid var(--edge); font-weight: 800; }
.lf-kind.on { border-color: var(--go); color: var(--go); }
.lf-spot { fill: #ffffff08; stroke: #ffffff40; stroke-width: 2; stroke-dasharray: 8 6; }
.lf-held { fill: none; stroke-width: 4; } .lf-held.ok { stroke: var(--go); } .lf-held.no { stroke: #ff7a66; stroke-dasharray: 10 6; }
.mm-lift { fill: #ff7a6612; stroke: #ff7a6680; stroke-width: 2; stroke-dasharray: 6 6; }
.mm-spot { fill: #ffcf5a22; stroke: var(--go); stroke-width: 3; stroke-dasharray: 5 4; }
.mm-spot.on { fill: var(--go); }
.lf-bottom { display: flex; gap: 12px; align-items: center; justify-content: center; flex-wrap: wrap; min-height: 90px; }
.mm-palette { display: flex; gap: 6px; overflow-x: auto; width: 100%; min-width: 0; padding: 4px 2px 8px; flex: 1 1 100%; }
.mm-pal { flex: none; border-radius: 8px; border: 2px solid transparent; line-height: 0; }
.mm-pal.on { border-color: var(--go); }
.mm-pal svg { border-radius: 5px; }
.lf-hand { display: grid; justify-items: center; gap: 2px; padding: 6px; border-radius: 12px; border: 2px solid var(--go); background: #0006; }
.lf-hand span { font-size: 0.7rem; color: var(--chalk-dim); }
.lf-ask { font-weight: 700; text-align: center; }
.mm-name { display: grid; gap: 10px; width: 100%; max-width: 480px; }
.mm-name label { display: grid; gap: 6px; font-weight: 700; }
.mm-chip { padding: 8px 12px; min-height: 40px; border-radius: 999px; border: 1px solid var(--go); color: var(--go); font-weight: 700; }
.mm-json { margin: 0; max-height: 220px; overflow: auto; background: #00000055; border-radius: 8px; padding: 10px; font: 0.7rem/1.5 var(--mono); white-space: pre; }
.lf-rules { margin: 0; padding-left: 18px; display: grid; gap: 4px; font-size: 0.85rem; color: var(--chalk-dim); }
.lf-rules b { color: var(--chalk); }`;
document.head.append(style);

frame.setup({ seats: false, score: false, deck: false, hints: false, redraw: () => render() });
document.getElementById("p-record").hidden = true;
document.getElementById("p-log").hidden = true;
M = MAPS.length ? fromMap(MAPS.find((m) => m.world === "lantern-fair") || MAPS[0]) : blank("lantern-fair");
render();
if (!MAPS.length) deal(seedWords(), 24);
