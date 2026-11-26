/* Lantern Fair: build the night market on the river, you against North.
   Draw a tile, turn it, and set it against the fair so every edge it touches
   matches: canal to canal, lane to lane, quay to quay. Then you may hang one
   of your seven lanterns on a lane or a canal of that tile, if no lantern is
   on it yet. A lane or canal closed at every end scores for whoever has more
   lanterns on it (both, when tied), and the lanterns come home: a lane 1 a
   tile, 2 a lit stall, 4 a dark stall (lit at last); a canal 1 a tile and 2 a
   bridge over it. When the tiles run out, whatever is still open scores 1 a
   tile. A page of its own: nothing here is kept. */
const N = 0, E = 1, So = 2, W = 3;
const DIRS = [[0, -1], [1, 0], [0, 1], [-1, 0]];
const MID = [[50, 0], [100, 50], [50, 100], [0, 50]];
const NORTH = 0, ME = 1, WHO = ["North", "You"];
const LANTERNS = 7;

/* the tiles, edges N E S W; a segment joins the edges it names, and one with an
   end stops there (at a stall, a well, a crossing, a basin or a landing) */
const TILES = [
  { id: "lane", n: 6, segs: [{ k: "L", e: [N, So] }] },
  { id: "lane-bend", n: 6, segs: [{ k: "L", e: [N, E] }] },
  { id: "lane-stall", n: 4, segs: [{ k: "L", e: [N, So], stalls: ["lit"] }] },
  { id: "lane-dark", n: 2, segs: [{ k: "L", e: [N, So], stalls: ["dark"] }] },
  { id: "stall-end", n: 3, segs: [{ k: "L", e: [So], end: "stall", stalls: ["lit"] }] },
  { id: "dark-end", n: 1, segs: [{ k: "L", e: [So], end: "stall", stalls: ["dark"] }] },
  { id: "well", n: 3, segs: [{ k: "L", e: [E], end: "well" }, { k: "L", e: [So], end: "well" }, { k: "L", e: [W], end: "well" }] },
  { id: "crossing", n: 2, segs: [N, E, So, W].map((e) => ({ k: "L", e: [e], end: "cross" })) },
  { id: "canal", n: 5, segs: [{ k: "C", e: [N, So] }] },
  { id: "canal-bend", n: 5, segs: [{ k: "C", e: [N, E] }] },
  { id: "basin", n: 3, segs: [{ k: "C", e: [So], end: "basin" }] },
  { id: "fork", n: 2, segs: [{ k: "C", e: [E, So, W] }] },
  { id: "bridge", n: 5, bridge: true, segs: [{ k: "C", e: [N, So] }, { k: "L", e: [E, W] }] },
  { id: "landing", n: 4, segs: [{ k: "C", e: [E, W] }, { k: "L", e: [So], end: "landing" }] },
  { id: "start", n: 0, bridge: true, segs: [{ k: "C", e: [N, So] }, { k: "L", e: [E, W], stalls: ["lit"] }] },
];
const T = Object.fromEntries(TILES.map((t) => [t.id, t]));
const edgeOf = (def, rot, dir) => { const e = (dir - rot + 4) % 4; const s = def.segs.find((g) => g.e.includes(e)); return s ? s.k : "Q"; };
const key = (x, y) => `${x},${y}`;

/* ── the board ── */
let G, chosenSpot = null;

function newGame() {
  const deck = shuffle(TILES.flatMap((t) => Array(t.n).fill(t.id)));
  G = { board: new Map(), deck, scores: [0, 0], left: [LANTERNS, LANTERNS], lanterns: new Map(), done: new Set(), rows: [], turn: rnd(2), phase: "place", held: null, rot: 0, last: null, over: false, flash: "" };
  G.board.set(key(0, 0), { x: 0, y: 0, id: "start", rot: 0 });
  frame.clearLog();
  frame.log(`<b>The fair opens.</b> One bridge over the canal, one stall lit. ${WHO[G.turn]} ${G.turn === ME ? "go" : "goes"} first.`);
  view = null; chosenSpot = null;
  nextTurn(true);
}

function fits(x, y, id, rot) {
  if (G.board.has(key(x, y))) return false;
  let touches = false;
  for (let d = 0; d < 4; d++) {
    const nb = G.board.get(key(x + DIRS[d][0], y + DIRS[d][1]));
    if (!nb) continue;
    touches = true;
    if (edgeOf(T[id], rot, d) !== edgeOf(T[nb.id], nb.rot, (d + 2) % 4)) return false;
  }
  return touches;
}
function frontier() {
  const out = new Map();
  for (const t of G.board.values()) for (const [dx, dy] of DIRS) { const k = key(t.x + dx, t.y + dy); if (!G.board.has(k)) out.set(k, [t.x + dx, t.y + dy]); }
  return [...out.values()];
}
function placements(id) {
  const out = [];
  for (const [x, y] of frontier()) for (let r = 0; r < 4; r++) if (fits(x, y, id, r)) out.push([x, y, r]);
  return out;
}

/* the lanes and canals as they stand: every segment of every tile, joined across
   the edges where tiles meet; a feature is closed when no edge of it is open */
function features() {
  const parent = new Map();
  const find = (a) => { while (parent.get(a) !== a) { parent.set(a, parent.get(parent.get(a))); a = parent.get(a); } return a; };
  const join = (a, b) => { const ra = find(a), rb = find(b); if (ra !== rb) parent.set(ra, rb); };
  for (const t of G.board.values()) T[t.id].segs.forEach((_, i) => parent.set(`${key(t.x, t.y)}:${i}`, `${key(t.x, t.y)}:${i}`));
  const open = new Map();
  for (const t of G.board.values()) {
    T[t.id].segs.forEach((s, i) => {
      const me = `${key(t.x, t.y)}:${i}`;
      for (const e of s.e) {
        const d = (e + t.rot) % 4, nb = G.board.get(key(t.x + DIRS[d][0], t.y + DIRS[d][1]));
        if (!nb) { open.set(me, (open.get(me) || 0) + 1); continue; }
        const back = ((d + 2) % 4 - nb.rot + 4) % 4;
        const j = T[nb.id].segs.findIndex((g) => g.e.includes(back));
        if (j >= 0) join(me, `${key(nb.x, nb.y)}:${j}`);
      }
    });
  }
  const groups = new Map();
  for (const node of parent.keys()) {
    const r = find(node);
    if (!groups.has(r)) groups.set(r, { nodes: [], kind: null, tiles: new Set(), open: 0, lit: 0, dark: 0, bridges: 0, lanterns: [0, 0] });
    const f = groups.get(r), [tk, si] = node.split(":"), t = G.board.get(tk), s = T[t.id].segs[+si];
    f.nodes.push(node); f.kind = s.k; f.tiles.add(tk); f.open += open.get(node) || 0;
    for (const st of s.stalls || []) st === "lit" ? f.lit++ : f.dark++;
    if (s.k === "C" && T[t.id].bridge) f.bridges++;
    if (G.lanterns.has(node)) f.lanterns[G.lanterns.get(node)]++;
  }
  return [...groups.values()];
}
const worth = (f, closed) => (!closed ? f.tiles.size : f.kind === "L" ? f.tiles.size + 2 * f.lit + 4 * f.dark : f.tiles.size + 2 * f.bridges);
const featSaid = (f) => `${f.kind === "L" ? "lane" : "canal"} of ${f.tiles.size} tile${f.tiles.size > 1 ? "s" : ""}${f.kind === "L" && f.lit + f.dark ? `, ${f.lit + f.dark} stall${f.lit + f.dark > 1 ? "s" : ""}${f.dark ? ` (${f.dark} dark)` : ""}` : ""}${f.kind === "C" && f.bridges ? `, ${f.bridges} bridge${f.bridges > 1 ? "s" : ""}` : ""}`;
const winners = (f) => { const [a, b] = f.lanterns; return a + b === 0 ? [] : a === b ? [0, 1] : [a > b ? 0 : 1]; };

/* what closes now scores, and its lanterns come home */
function settle(final = false) {
  for (const f of features()) {
    const id = f.nodes.slice().sort()[0];
    if (G.done.has(id)) continue;
    const closed = f.open === 0;
    if (!closed && !final) continue;
    G.done.add(id);
    const who = winners(f);
    if (!who.length) continue;
    const pts = worth(f, closed);
    for (const w of who) G.scores[w] += pts;
    for (const n of f.nodes) if (G.lanterns.has(n)) { G.left[G.lanterns.get(n)]++; G.lanterns.delete(n); }
    G.rows.push({ label: `${closed ? "" : "open "}${f.kind === "L" ? "lane" : "canal"} ${f.tiles.size}`, cells: [0, 1].map((i) => (who.includes(i) ? `+${pts}` : "")) });
    const names = who.map((w) => WHO[w]).join(" and ");
    frame.log(`${closed ? "Closed" : "Still open"}: a ${featSaid(f)}. <b>${names} score${who.length === 1 && who[0] === ME ? "" : who.length > 1 ? "" : "s"} ${pts}</b>.`);
    if (!final) G.flash = `<b>${names} score${who.length === 1 && who[0] === ME ? "" : who.length > 1 ? "" : "s"} ${pts}</b> for the ${f.kind === "L" ? "lane" : "canal"}.`;
  }
}

function nextTurn(first = false) {
  if (!first) G.turn = 1 - G.turn;
  while (G.deck.length) {
    const id = G.deck.pop();
    if (placements(id).length) { G.held = id; G.rot = 0; G.phase = "place"; chosenSpot = null; render(); if (G.turn === NORTH) northTurn(); return; }
    frame.log(`A ${id.replace("-", " ")} tile fits nowhere, and is set aside.`);
  }
  settle(true);
  G.over = true; G.phase = "over"; G.held = null;
  frame.log(`<b>The fair is built.</b> ${G.scores[ME] === G.scores[NORTH] ? "A tie" : G.scores[ME] > G.scores[NORTH] ? "You win" : "North wins"}, ${Math.max(...G.scores)} to ${Math.min(...G.scores)}.`);
  render();
}

function put(seat, x, y, rot) {
  G.board.set(key(x, y), { x, y, id: G.held, rot });
  G.last = key(x, y);
  frame.log(`${WHO[seat]} set${seat === ME ? "" : "s"} a ${G.held.replace("-", " ")} tile.`);
  G.held = null;
}
/* the segments of the tile just set that a lantern may go on */
function hangable(k) {
  const t = G.board.get(k), fs = features();
  return T[t.id].segs.map((_, i) => `${k}:${i}`).filter((n) => { const f = fs.find((g) => g.nodes.includes(n)); return f.lanterns[0] + f.lanterns[1] === 0; });
}
function hang(seat, node) {
  if (node) { G.lanterns.set(node, seat); G.left[seat]--; frame.log(`${WHO[seat]} hang${seat === ME ? "" : "s"} a lantern.`); }
  settle();
  nextTurn();
}

/* ── North: tries every place and turn, and every lantern, and takes the best ── */
async function northTurn() {
  render(); await wait(650);
  const id = G.held;
  let best = null;
  for (const [x, y, r] of placements(id)) {
    G.board.set(key(x, y), { x, y, id, rot: r });
    const fs = features(), k = key(x, y);
    const nodes = T[id].segs.map((_, i) => `${k}:${i}`);
    let base = 0;
    for (const f of fs) {
      const mine = nodes.some((n) => f.nodes.includes(n));
      if (!mine) continue;
      const w = winners(f), v = worth(f, f.open === 0);
      if (f.open === 0 && !G.done.has(f.nodes.slice().sort()[0])) { if (w.includes(NORTH)) base += v; if (w.includes(ME)) base -= v; }
      else if (f.open) { if (w.includes(NORTH) && !w.includes(ME)) base += 0.5 * v / (1 + f.open); if (w.includes(ME) && !w.includes(NORTH)) base -= 0.4 * v / (1 + f.open); }
    }
    const options = [[null, 0]];
    if (G.left[NORTH] > 0) for (const n of nodes) {
      const f = fs.find((g) => g.nodes.includes(n));
      if (f.lanterns[0] + f.lanterns[1]) continue;
      const v = worth(f, f.open === 0), closes = f.open === 0;
      options.push([n, closes ? v : (v * 0.6) / (1 + 0.35 * f.open) - (G.left[NORTH] <= 2 ? 1.5 : 0.4)]);
    }
    G.board.delete(k);
    for (const [n, extra] of options) {
      const s = base + extra + rnd(100) / 1000;
      if (!best || s > best.s) best = { x, y, r, n, s };
    }
  }
  put(NORTH, best.x, best.y, best.r);
  render(); await wait(450);
  hang(NORTH, best.n);
}

/* ── you ── */
function tapCell(x, y) {
  if (G.turn !== ME || G.over) return;
  if (G.phase === "lantern") return;
  if (G.board.has(key(x, y))) return;
  if (!frontier().some(([a, b]) => a === x && b === y)) return;
  chosenSpot = [x, y];
  if (frame.hints && !fits(x, y, G.held, G.rot)) { for (let r = 1; r < 4; r++) if (fits(x, y, G.held, (G.rot + r) % 4)) { G.rot = (G.rot + r) % 4; break; } }
  render();
}
function turnTile() {
  if (G.turn !== ME || G.phase !== "place") return;
  G.rot = (G.rot + 1) % 4;
  if (frame.hints && chosenSpot && placements(G.held).some(([x, y]) => x === chosenSpot[0] && y === chosenSpot[1])) {
    for (let i = 0; i < 4 && !fits(chosenSpot[0], chosenSpot[1], G.held, G.rot); i++) G.rot = (G.rot + 1) % 4;
  }
  render();
}
function placeIt() {
  if (!chosenSpot) return frame.refuse("tap a spot beside the fair first");
  const [x, y] = chosenSpot;
  if (!fits(x, y, G.held, G.rot)) return frame.refuse("every edge it touches has to match: canal to canal, lane to lane, quay to quay");
  G.flash = "";
  put(ME, x, y, G.rot);
  chosenSpot = null;
  if (G.left[ME] > 0 && hangable(G.last).length) { G.phase = "lantern"; render(); }
  else hang(ME, null);
}
function tapLantern(node) { if (G.phase === "lantern" && G.turn === ME && hangable(G.last).includes(node)) { G.phase = "place"; hang(ME, node); } }

/* ── the picture ── */
const COL = { quay: "#2f2c44", quay2: "#3a3654", water: "#1d6f8a", water2: "#5fc0d6", lane: "#dcc093", lane2: "#9e7f55", glow: "#ffcf5a", you: "#ffcf5a", north: "#8fd8ff" };
function segPath(s) {
  const [a, b] = [MID[s.e[0]], MID[s.e[1]]];
  if (s.e.length === 2) return `M${a[0]} ${a[1]} Q50 50 ${b[0]} ${b[1]}`;
  return s.e.map((e) => `M${MID[e][0]} ${MID[e][1]} L50 50`).join(" ");
}
function anchor(s) {
  const m = MID[s.e[0]], f = s.e.length === 1 && !s.end ? 0.5 : s.e.length === 1 ? 0.42 : 0.58;
  return [m[0] + (50 - m[0]) * f, m[1] + (50 - m[1]) * f];
}
function stallSVG(x, y, lit) {
  return `${lit ? `<circle cx="${x + 13}" cy="${y + 6}" r="24" fill="url(#glow)"/>` : ""}<rect x="${x}" y="${y}" width="26" height="19" rx="2" fill="${lit ? "#b8503c" : "#55505e"}"/><path d="M${x - 3} ${y + 2} h32 l-4 -8 h-24 z" fill="${lit ? "#f2e6c8" : "#8a8494"}"/><path d="M${x + 5} ${y - 6} v8 M${x + 13} ${y - 6} v8 M${x + 21} ${y - 6} v8" stroke="${lit ? "#c9553f" : "#6b6575"}" stroke-width="2.5"/><circle cx="${x + 13}" cy="${y + 7}" r="3.4" fill="${lit ? "#fff2b0" : "#2a2733"}"/>`;
}
function tileInner(id) {
  const def = T[id];
  let s = `<rect width="100" height="100" fill="${COL.quay}"/><path d="M0 33 H100 M0 66 H100 M33 0 V100 M66 0 V100" stroke="${COL.quay2}" stroke-width="1"/>`;
  for (const g of def.segs.filter((g) => g.k === "C")) {
    s += `<path d="${segPath(g)}" stroke="${COL.water}" stroke-width="34" fill="none"/>`;
    if (g.end === "basin") s += `<circle cx="50" cy="50" r="24" fill="${COL.water}"/>`;
    if (g.e.length === 3) s += `<circle cx="50" cy="50" r="17" fill="${COL.water}"/>`;
    s += `<path d="${segPath(g)}" stroke="${COL.water2}" stroke-width="2" stroke-dasharray="6 9" fill="none" opacity="0.7"/>`;
  }
  for (const g of def.segs.filter((g) => g.k === "L")) {
    const end = g.end === "landing" ? `M50 100 L50 67` : null;
    const d = end || segPath(g);
    s += `<path d="${d}" stroke="${COL.lane2}" stroke-width="22" fill="none"/><path d="${d}" stroke="${COL.lane}" stroke-width="16" fill="none"/>`;
    if (g.end === "landing") s += `<path d="M42 70 H58 M42 75 H58 M42 80 H58" stroke="${COL.lane2}" stroke-width="1.5"/>`;
  }
  if (def.bridge) s += `<path d="M31 39 H69 M31 61 H69" stroke="#6b4e2e" stroke-width="3"/><path d="M33 39 V61 M67 39 V61" stroke="#6b4e2e" stroke-width="1.5" opacity="0.7"/>`;
  const ends = new Set(def.segs.map((g) => g.end).filter(Boolean));
  if (ends.has("well")) s += `<circle cx="50" cy="50" r="13" fill="#8c8698"/><circle cx="50" cy="50" r="7" fill="#15131f"/>`;
  if (ends.has("cross")) s += `<circle cx="50" cy="50" r="15" fill="#8c8698"/><circle cx="50" cy="50" r="10" fill="${COL.water}"/><circle cx="50" cy="50" r="3" fill="${COL.water2}"/>`;
  for (const g of def.segs) {
    if (!g.stalls) continue;
    const lit = g.stalls[0] === "lit";
    if (g.end === "stall") s += stallSVG(37, 42, lit);
    else if (id === "start") s += stallSVG(5, 70, lit);
    else s += stallSVG(64, 42, lit);
  }
  return s;
}
const tileG = (x, y, id, rot, extra = "") => `<g transform="translate(${x * 100} ${y * 100}) rotate(${rot * 90} 50 50)" ${extra}>${tileInner(id)}</g>`;

let view = null; // { x, y, w } in board units: the part of the fair shown
function fitView() {
  const ts = [...G.board.values()];
  const xs = ts.map((t) => t.x), ys = ts.map((t) => t.y);
  const x0 = Math.min(...xs) - 1, x1 = Math.max(...xs) + 2, y0 = Math.min(...ys) - 1, y1 = Math.max(...ys) + 2;
  const el = document.getElementById("lf-wrap"), aspect = el ? el.clientWidth / el.clientHeight : 1.3;
  let w = (x1 - x0) * 100, h = (y1 - y0) * 100;
  if (w / h < aspect) w = h * aspect; else h = w / aspect;
  w = Math.max(w, 560);
  view = { x: ((x0 + x1) / 2) * 100 - w / 2, y: ((y0 + y1) / 2) * 100 - w / aspect / 2, w };
}
/* the tile just set, and the spot chosen, are kept in sight: the view slides
   only as far as it must */
function keepInView(x, y) {
  const el = document.getElementById("lf-wrap"), h = view.w / (el.clientWidth / el.clientHeight), m = 12;
  const [x0, y0, x1, y1] = [x * 100 - m, y * 100 - m, x * 100 + 100 + m, y * 100 + 100 + m];
  if (x1 - x0 > view.w || y1 - y0 > h) return;
  if (x0 < view.x) view.x = x0; else if (x1 > view.x + view.w) view.x = x1 - view.w;
  if (y0 < view.y) view.y = y0; else if (y1 > view.y + h) view.y = y1 - h;
}
function viewBox() { const el = document.getElementById("lf-wrap"); const aspect = el.clientWidth / el.clientHeight; return `${view.x} ${view.y} ${view.w} ${view.w / aspect}`; }

function boardSVG() {
  const mine = G.turn === ME && !G.over;
  let s = `<defs><radialGradient id="glow"><stop offset="0" stop-color="${COL.glow}" stop-opacity="0.55"/><stop offset="1" stop-color="${COL.glow}" stop-opacity="0"/></radialGradient><filter id="lit"><feGaussianBlur stdDeviation="2.5"/></filter></defs>`;
  if (mine && G.phase === "place") {
    const ok = frame.hints ? new Set(placements(G.held).map(([x, y]) => key(x, y))) : null;
    for (const [x, y] of frontier()) {
      if (ok && !ok.has(key(x, y))) continue;
      s += `<rect x="${x * 100 + 4}" y="${y * 100 + 4}" width="92" height="92" rx="8" class="lf-spot"/>`;
    }
  }
  for (const t of G.board.values()) s += tileG(t.x, t.y, t.id, t.rot);
  if (G.last) { const [x, y] = G.last.split(",").map(Number); s += `<rect x="${x * 100 + 1.5}" y="${y * 100 + 1.5}" width="97" height="97" class="lf-last"/>`; }
  for (const [node, who] of G.lanterns) {
    const [k, i] = node.split(":"), t = G.board.get(k), [ax, ay] = anchor(T[t.id].segs[+i]);
    s += `<g transform="translate(${t.x * 100} ${t.y * 100}) rotate(${t.rot * 90} 50 50)"><circle cx="${ax}" cy="${ay}" r="15" fill="${who === ME ? COL.you : COL.north}" opacity="0.4" filter="url(#lit)"/><circle cx="${ax}" cy="${ay}" r="9" fill="${who === ME ? COL.you : COL.north}" stroke="#15131f" stroke-width="2"/></g>`;
  }
  if (mine && G.phase === "place" && chosenSpot) {
    const [x, y] = chosenSpot, ok = fits(x, y, G.held, G.rot);
    s += tileG(x, y, G.held, G.rot, `opacity="0.92"`);
    for (let d = 0; d < 4; d++) {
      const nb = G.board.get(key(x + DIRS[d][0], y + DIRS[d][1]));
      if (nb && edgeOf(T[G.held], G.rot, d) !== edgeOf(T[nb.id], nb.rot, (d + 2) % 4)) {
        const [mx, my] = MID[d];
        s += `<line x1="${x * 100 + (d % 2 ? mx : 8)}" y1="${y * 100 + (d % 2 ? 8 : my)}" x2="${x * 100 + (d % 2 ? mx : 92)}" y2="${y * 100 + (d % 2 ? 92 : my)}" class="lf-bad"/>`;
      }
    }
    s += `<rect x="${x * 100 + 1.5}" y="${y * 100 + 1.5}" width="97" height="97" class="lf-held ${ok ? "ok" : "no"}"/>`;
  }
  if (mine && G.phase === "lantern") {
    const t = G.board.get(G.last);
    for (const node of hangable(G.last)) {
      const [ax, ay] = anchor(T[t.id].segs[+node.split(":")[1]]);
      s += `<g transform="translate(${t.x * 100} ${t.y * 100}) rotate(${t.rot * 90} 50 50)"><circle cx="${ax}" cy="${ay}" r="18" class="lf-hang"/></g>`;
    }
  }
  return s;
}

function render() {
  const mine = G.turn === ME && !G.over;
  const scoreLine = `<span class="lf-you">You ${G.scores[ME]}</span> · <span class="lf-north">North ${G.scores[NORTH]}</span>`;
  const lamps = (n, cls) => `<span class="lf-lamps ${cls}" aria-label="${n} lanterns">${"●".repeat(n)}<i>${"●".repeat(LANTERNS - n)}</i></span>`;
  const heldTile = G.held && mine && G.phase === "place"
    ? `<button class="lf-hand" id="lf-turn" aria-label="the tile in hand: tap to turn it"><svg viewBox="0 0 100 100" width="84" height="84">${tileG(0, 0, G.held, G.rot)}</svg><span>tap to turn</span></button>` : "";
  if (!document.getElementById("lf-wrap")) {
    frame.stage(`<div class="lf"><div class="lf-top"><div>${scoreLine}</div><div>${lamps(G.left[ME], "you")} ${lamps(G.left[NORTH], "north")}</div></div><div class="lf-wrap" id="lf-wrap"><svg id="lf-svg" class="lf-svg"></svg><div class="lf-tools"><button id="lf-zin" aria-label="zoom in">+</button><button id="lf-zout" aria-label="zoom out">−</button><button id="lf-fit" aria-label="fit the fair">⤢</button></div></div><div class="lf-bottom" id="lf-bottom"></div></div>`);
    wire();
  }
  document.querySelector(".lf-top").innerHTML = `<div>${scoreLine}</div><div>${lamps(G.left[ME], "you")} ${lamps(G.left[NORTH], "north")}</div>`;
  if (!view) fitView();
  if (G.last) { const [lx, ly] = G.last.split(",").map(Number); keepInView(lx, ly); }
  const svg = document.getElementById("lf-svg");
  svg.setAttribute("viewBox", viewBox());
  svg.innerHTML = boardSVG();
  const left = `<div class="lf-deck">${G.deck.length} tile${G.deck.length === 1 ? "" : "s"} left</div>`;
  let bottom = "";
  if (G.over) bottom = `${left}<button class="btn" id="lf-new">New fair</button>`;
  else if (!mine) bottom = `${left}<div class="lf-wait">North is building…</div>`;
  else if (G.phase === "lantern") bottom = `${left}<div class="lf-ask">Hang a lantern? Tap a ring on the tile.</div><button class="btn ghost" id="lf-none">No lantern</button>`;
  else bottom = `${heldTile}<div class="lf-acts">${left}<button class="btn" id="lf-place" ${chosenSpot ? "" : "disabled"}>Place</button></div>`;
  document.getElementById("lf-bottom").innerHTML = bottom;
  const on = (id, f) => { const b = document.getElementById(id); if (b) b.onclick = f; };
  on("lf-new", newGame); on("lf-none", () => { if (G.phase === "lantern") { G.phase = "place"; hang(ME, null); } }); on("lf-place", placeIt); on("lf-turn", turnTile);
  frame.status(G.over ? `<b>${G.scores[ME] === G.scores[NORTH] ? "A tie" : G.scores[ME] > G.scores[NORTH] ? "You win" : "North wins"}</b>, ${Math.max(...G.scores)} to ${Math.min(...G.scores)}.`
    : (G.flash ? G.flash + " " : "") + (!mine ? "" : G.phase === "lantern" ? "Your lantern." : chosenSpot ? "Turn it till it fits, then <b>Place</b>." : "<b>Your tile.</b> Tap a spot beside the fair."));
  frame.score({ cols: ["North", "You"], rows: G.rows, totals: G.scores, lead: G.scores[0] === G.scores[1] ? [] : [G.scores[0] > G.scores[1] ? 0 : 1], head: "Closed", you: ME, empty: "Nothing closed yet", note: "A lane: 1 a tile, 2 a lit stall, 4 a dark one. A canal: 1 a tile, 2 a bridge. Open at the end: 1 a tile." });
  frame.deck([["Tiles left", String(G.deck.length)], ["Your lanterns", `${G.left[ME]} of ${LANTERNS}`], ["North's lanterns", `${G.left[NORTH]} of ${LANTERNS}`], ["On the fair", String(G.board.size)]], "Edges match canal to canal, lane to lane, quay to quay.");
}

/* the board under a finger: drag to pan, pinch or wheel to zoom, tap to choose */
function wire() {
  const svg = document.getElementById("lf-svg"), wrap = document.getElementById("lf-wrap");
  const pts = new Map();
  let moved = false, start = null, pinch = null;
  const toBoard = (cx, cy) => { const p = svg.createSVGPoint(); p.x = cx; p.y = cy; const q = p.matrixTransform(svg.getScreenCTM().inverse()); return [q.x, q.y]; };
  const zoomAt = (f, cx, cy) => {
    const [bx, by] = toBoard(cx, cy), w = Math.min(4000, Math.max(220, view.w / f)), k = w / view.w;
    view = { x: bx - (bx - view.x) * k, y: by - (by - view.y) * k, w };
    svg.setAttribute("viewBox", viewBox());
  };
  svg.addEventListener("pointerdown", (e) => {
    svg.setPointerCapture(e.pointerId);
    pts.set(e.pointerId, [e.clientX, e.clientY]);
    if (pts.size === 1) { moved = false; start = { cx: e.clientX, cy: e.clientY, v: { ...view } }; }
    if (pts.size === 2) { const [a, b] = [...pts.values()]; pinch = { d: Math.hypot(a[0] - b[0], a[1] - b[1]), w: view.w }; moved = true; }
  });
  svg.addEventListener("pointermove", (e) => {
    if (!pts.has(e.pointerId)) return;
    pts.set(e.pointerId, [e.clientX, e.clientY]);
    if (pts.size === 2 && pinch) {
      const [a, b] = [...pts.values()], d = Math.hypot(a[0] - b[0], a[1] - b[1]);
      zoomAt(view.w / (pinch.w * (pinch.d / d)), (a[0] + b[0]) / 2, (a[1] + b[1]) / 2);
      return;
    }
    if (pts.size === 1 && start) {
      const dx = e.clientX - start.cx, dy = e.clientY - start.cy;
      if (!moved && Math.hypot(dx, dy) < 7) return;
      moved = true;
      const k = view.w / wrap.clientWidth;
      view = { ...view, x: start.v.x - dx * k, y: start.v.y - dy * k };
      svg.setAttribute("viewBox", viewBox());
    }
  });
  const up = (e) => {
    if (!pts.has(e.pointerId)) return;
    pts.delete(e.pointerId);
    if (pts.size < 2) pinch = null;
    if (pts.size === 0 && !moved) {
      const [bx, by] = toBoard(e.clientX, e.clientY);
      if (G.phase === "lantern" && G.turn === ME) {
        const t = G.board.get(G.last);
        for (const node of hangable(G.last)) {
          const [ax, ay] = anchor(T[t.id].segs[+node.split(":")[1]]), r = t.rot * Math.PI / 2;
          const px = t.x * 100 + 50 + (ax - 50) * Math.cos(r) - (ay - 50) * Math.sin(r), py = t.y * 100 + 50 + (ax - 50) * Math.sin(r) + (ay - 50) * Math.cos(r);
          if (Math.hypot(px - bx, py - by) < 30) return tapLantern(node);
        }
        return;
      }
      tapCell(Math.floor(bx / 100), Math.floor(by / 100));
    }
    if (pts.size === 0) start = null;
  };
  svg.addEventListener("pointerup", up);
  svg.addEventListener("pointercancel", (e) => { pts.delete(e.pointerId); pinch = null; });
  svg.addEventListener("wheel", (e) => { e.preventDefault(); zoomAt(e.deltaY < 0 ? 1.15 : 1 / 1.15, e.clientX, e.clientY); }, { passive: false });
  document.getElementById("lf-zin").onclick = () => { const r = wrap.getBoundingClientRect(); zoomAt(1.3, r.left + r.width / 2, r.top + r.height / 2); };
  document.getElementById("lf-zout").onclick = () => { const r = wrap.getBoundingClientRect(); zoomAt(1 / 1.3, r.left + r.width / 2, r.top + r.height / 2); };
  document.getElementById("lf-fit").onclick = () => { fitView(); svg.setAttribute("viewBox", viewBox()); };
  window.addEventListener("resize", () => { if (view) svg.setAttribute("viewBox", viewBox()); });
}

const style = document.createElement("style");
style.textContent = `
.lf { display: grid; gap: 10px; width: 100%; min-width: 0; }
.lf-top { display: flex; justify-content: space-between; align-items: center; gap: 10px; flex-wrap: wrap; font-weight: 800; font-size: 0.9rem; }
.lf-you { color: ${COL.you}; } .lf-north { color: ${COL.north}; }
.lf-lamps { font-size: 0.7rem; letter-spacing: 1px; } .lf-lamps i { font-style: normal; opacity: 0.2; }
.lf-lamps.you { color: ${COL.you}; } .lf-lamps.north { color: ${COL.north}; }
.lf-wrap { position: relative; height: min(62vh, 560px); min-height: 300px; border-radius: 14px; overflow: hidden; background: radial-gradient(120% 100% at 50% 30%, #1c1a2e, #0d0c16); box-shadow: inset 0 0 30px #000a; }
.lf-svg { width: 100%; height: 100%; display: block; touch-action: none; cursor: grab; user-select: none; -webkit-user-select: none; }
.lf-spot { fill: #ffffff08; stroke: #ffffff40; stroke-width: 2; stroke-dasharray: 8 6; }
.lf-last { fill: none; stroke: #ffffff70; stroke-width: 3; }
.lf-held { fill: none; stroke-width: 4; } .lf-held.ok { stroke: var(--go); } .lf-held.no { stroke: #ff7a66; stroke-dasharray: 10 6; }
.lf-bad { stroke: #ff5a45; stroke-width: 7; stroke-linecap: round; }
.lf-hang { fill: #ffcf5a33; stroke: var(--go); stroke-width: 3; stroke-dasharray: 5 4; }
.lf-tools { position: absolute; right: 8px; top: 8px; display: grid; gap: 6px; }
.lf-tools button { width: 40px; height: 40px; border-radius: 10px; background: #0008; color: var(--chalk); font-size: 1.2rem; font-weight: 800; border: 1px solid #ffffff30; }
.lf-bottom { display: flex; gap: 12px; align-items: center; justify-content: center; flex-wrap: wrap; min-height: 104px; }
.lf-hand { display: grid; justify-items: center; gap: 2px; padding: 6px; border-radius: 12px; border: 2px solid var(--go); background: #0006; }
.lf-hand svg { display: block; border-radius: 6px; }
.lf-hand span { font-size: 0.7rem; color: var(--chalk-dim); }
.lf-acts { display: grid; gap: 8px; justify-items: center; }
.lf-acts .btn { min-width: 120px; min-height: 48px; font-size: 1.05rem; }
.lf-deck { font-family: var(--mono); font-size: 0.75rem; color: var(--chalk-dim); }
.lf-ask, .lf-wait { font-weight: 700; }
.lf-bottom .btn { min-height: 44px; }`;
document.head.append(style);

frame.setup({ seats: false, score: true, deck: true, scoreTitle: "Scoresheet", deckTitle: "The fair", redraw: () => render() });
document.getElementById("p-record").hidden = true;
newGame();
