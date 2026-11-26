/* The fair's tiles, shared by every page that lays them: Lantern Fair, the map
   maker and the Table's maps. A tile is square, its edges N E S W each a canal,
   a lane, a square or quay; its segments join the edges they name. This file
   draws them, and holds the board a finger pans and pinches. */
const N = 0, E = 1, So = 2, W = 3;
const DIRS = [[0, -1], [1, 0], [0, 1], [-1, 0]];
const MID = [[50, 0], [100, 50], [50, 100], [0, 50]];
const GOODS = ["spice", "silk", "sweets", "masks"];
const GOOD_COL = { spice: "#e0662f", silk: "#9a68d8", sweets: "#ee86b0", masks: "#e9c74a" };
const KIND_NAME = { L: "lane", C: "canal", P: "square" };

/* the tiles, edges N E S W; a segment joins the edges it names, and one with an
   end stops there (at a stall, a well, a crossing, a basin, a landing or a
   square it opens onto). A square segment is paving along the edges it names. */
const TILES = [
  { id: "lane", n: 6, segs: [{ k: "L", e: [N, So] }] },
  { id: "lane-bend", n: 6, segs: [{ k: "L", e: [N, E] }] },
  { id: "lane-stall", n: 6, segs: [{ k: "L", e: [N, So], stalls: ["lit"] }] },
  { id: "lane-dark", n: 3, segs: [{ k: "L", e: [N, So], stalls: ["dark"] }] },
  { id: "stall-end", n: 3, segs: [{ k: "L", e: [So], end: "stall", stalls: ["lit"] }] },
  { id: "dark-end", n: 1, segs: [{ k: "L", e: [So], end: "stall", stalls: ["dark"] }] },
  { id: "well", n: 3, segs: [{ k: "L", e: [E], end: "well" }, { k: "L", e: [So], end: "well" }, { k: "L", e: [W], end: "well" }] },
  { id: "crossing", n: 2, segs: [N, E, So, W].map((e) => ({ k: "L", e: [e], end: "cross" })) },
  { id: "canal", n: 5, segs: [{ k: "C", e: [N, So] }] },
  { id: "canal-bend", n: 4, segs: [{ k: "C", e: [N, E] }] },
  { id: "basin", n: 3, segs: [{ k: "C", e: [So], end: "basin" }] },
  { id: "fork", n: 2, segs: [{ k: "C", e: [E, So, W] }] },
  { id: "bridge", n: 4, bridge: true, segs: [{ k: "C", e: [N, So] }, { k: "L", e: [E, W] }] },
  { id: "bridge-stall", n: 2, bridge: true, segs: [{ k: "C", e: [N, So] }, { k: "L", e: [E, W], stalls: ["lit"] }] },
  { id: "landing", n: 4, segs: [{ k: "C", e: [E, W] }, { k: "L", e: [So], end: "landing" }] },
  { id: "square-edge", n: 4, segs: [{ k: "P", e: [N] }] },
  { id: "square-mouth", n: 4, segs: [{ k: "P", e: [N] }, { k: "L", e: [So], end: "square" }] },
  { id: "square-corner", n: 3, segs: [{ k: "P", e: [N, E] }] },
  { id: "square-through", n: 2, segs: [{ k: "P", e: [N, So] }] },
  { id: "square-three", n: 2, segs: [{ k: "P", e: [N, E, W] }] },
  { id: "square-three-mouth", n: 2, segs: [{ k: "P", e: [N, E, W] }, { k: "L", e: [So], end: "square" }] },
  { id: "square-corner-mouths", n: 2, segs: [{ k: "P", e: [N, E] }, { k: "L", e: [So], end: "square" }, { k: "L", e: [W], end: "square" }] },
  { id: "square-full", n: 1, segs: [{ k: "P", e: [N, E, So, W] }] },
  { id: "start", n: 0, bridge: true, segs: [{ k: "C", e: [N, So] }, { k: "L", e: [E, W], stalls: ["lit"] }] },
];
const T = Object.fromEntries(TILES.map((t) => [t.id, t]));
const stallsOf = (id) => T[id].segs.flatMap((s, i) => (s.stalls || []).map((st) => ({ seg: i, lit: st === "lit" })));
const edgeOf = (id, rot, dir) => { const e = (dir - rot + 4) % 4; const s = T[id].segs.find((g) => g.e.includes(e)); return s ? s.k : "Q"; };
const key = (x, y) => `${x},${y}`;
const tileName = (id) => id.replace(/-/g, " ");

const COL = { quay: "#2f2c44", quay2: "#3a3654", water: "#1d6f8a", water2: "#5fc0d6", lane: "#dcc093", lane2: "#9e7f55", pave: "#6e5a86", pave2: "#8a74a3", glow: "#ffcf5a", you: "#ffcf5a", north: "#8fd8ff" };
function segPath(s) {
  if (s.e.length === 2) { const [a, b] = [MID[s.e[0]], MID[s.e[1]]]; return `M${a[0]} ${a[1]} Q50 50 ${b[0]} ${b[1]}`; }
  return s.e.map((e) => `M${MID[e][0]} ${MID[e][1]} L50 50`).join(" ");
}
function anchor(s) {
  const m = MID[s.e[0]];
  const f = s.k === "P" ? 0.42 : s.e.length === 1 && !s.end ? 0.5 : s.e.length === 1 ? (s.end === "square" ? 0.3 : 0.42) : 0.58;
  return [m[0] + (50 - m[0]) * f, m[1] + (50 - m[1]) * f];
}
const PAVE = { 0: "0,0 100,0 68,42 32,42", 1: "100,0 100,100 58,68 58,32", 2: "0,100 100,100 68,58 32,58", 3: "0,0 0,100 42,68 42,32" };
function squareSVG(s) {
  let out = s.e.length === 4 ? `<rect width="100" height="100" fill="${COL.pave}"/>` : s.e.map((e) => `<polygon points="${PAVE[e]}" fill="${COL.pave}"/>`).join("");
  if (s.e.length >= 2 && s.e.length < 4) out += `<rect x="30" y="30" width="40" height="40" fill="${COL.pave}"/>`;
  out += `<g stroke="${COL.pave2}" stroke-width="1" opacity="0.6">${s.e.map((e) => { const [x, y] = MID[e]; return e % 2 ? `<path d="M${x === 0 ? 8 : 92} 20 V80 M${x === 0 ? 18 : 82} 28 V72"/>` : `<path d="M20 ${y === 0 ? 8 : 92} H80 M28 ${y === 0 ? 18 : 82} H72"/>`; }).join("")}</g>`;
  return out;
}
function stallSVG(x, y, st) {
  const c = GOOD_COL[st.good] || "#c9553f";
  return `${st.lit ? `<circle cx="${x + 13}" cy="${y + 6}" r="24" fill="url(#glow)"/>` : ""}<rect x="${x}" y="${y}" width="26" height="19" rx="2" fill="${st.lit ? "#a8483a" : "#4a4552"}"/><path d="M${x - 3} ${y + 2} h32 l-4 -8 h-24 z" fill="${c}" opacity="${st.lit ? 1 : 0.55}"/><path d="M${x + 5} ${y - 6} v8 M${x + 13} ${y - 6} v8 M${x + 21} ${y - 6} v8" stroke="#fff8" stroke-width="2"/><circle cx="${x + 13}" cy="${y + 8}" r="3.6" fill="${st.lit ? "#fff2b0" : "#1f1c26"}"/>`;
}
function tileInner(id, stalls) {
  const def = T[id];
  let s = `<rect width="100" height="100" fill="${COL.quay}"/><path d="M0 33 H100 M0 66 H100 M33 0 V100 M66 0 V100" stroke="${COL.quay2}" stroke-width="1"/>`;
  for (const g of def.segs.filter((g) => g.k === "C")) {
    s += `<path d="${segPath(g)}" stroke="${COL.water}" stroke-width="34" fill="none"/>`;
    if (g.end === "basin") s += `<circle cx="50" cy="50" r="24" fill="${COL.water}"/>`;
    if (g.e.length === 3) s += `<circle cx="50" cy="50" r="17" fill="${COL.water}"/>`;
    s += `<path d="${segPath(g)}" stroke="${COL.water2}" stroke-width="2" stroke-dasharray="6 9" fill="none" opacity="0.7"/>`;
  }
  for (const g of def.segs.filter((g) => g.k === "L")) {
    const d = g.end === "landing" ? `M50 100 L50 67` : segPath(g);
    s += `<path d="${d}" stroke="${COL.lane2}" stroke-width="22" fill="none"/><path d="${d}" stroke="${COL.lane}" stroke-width="16" fill="none"/>`;
    if (g.end === "landing") s += `<path d="M42 70 H58 M42 75 H58 M42 80 H58" stroke="${COL.lane2}" stroke-width="1.5"/>`;
  }
  for (const g of def.segs.filter((g) => g.k === "P")) s += squareSVG(g);
  if (def.bridge) s += `<path d="M31 39 H69 M31 61 H69" stroke="#6b4e2e" stroke-width="3"/><path d="M33 39 V61 M67 39 V61" stroke="#6b4e2e" stroke-width="1.5" opacity="0.7"/>`;
  const ends = new Set(def.segs.map((g) => g.end).filter(Boolean));
  if (ends.has("well")) s += `<circle cx="50" cy="50" r="13" fill="#8c8698"/><circle cx="50" cy="50" r="7" fill="#15131f"/>`;
  if (ends.has("cross")) s += `<circle cx="50" cy="50" r="15" fill="#8c8698"/><circle cx="50" cy="50" r="10" fill="${COL.water}"/><circle cx="50" cy="50" r="3" fill="${COL.water2}"/>`;
  (stalls || stallsOf(id).map((x) => ({ ...x, good: null }))).forEach((st) => {
    const g = def.segs[st.seg];
    s += g.end === "stall" ? stallSVG(37, 42, st) : id === "start" || id === "bridge-stall" ? stallSVG(5, 70, st) : stallSVG(64, 42, st);
  });
  return s;
}
const tileG = (x, y, id, rot, stalls, extra = "") => `<g transform="translate(${x * 100} ${y * 100}) rotate(${rot * 90} 50 50)" ${extra}>${tileInner(id, stalls)}</g>`;
const onTile = (t, inner) => `<g transform="translate(${t.x * 100} ${t.y * 100}) rotate(${t.rot * 90} 50 50)">${inner}</g>`;

/* glows for lit stalls and lanterns, once per board */
const FAIR_DEFS = `<defs><radialGradient id="glow"><stop offset="0" stop-color="${COL.glow}" stop-opacity="0.55"/><stop offset="1" stop-color="${COL.glow}" stop-opacity="0"/></radialGradient><filter id="lit"><feGaussianBlur stdDeviation="2.5"/></filter></defs>`;

/* The board under a finger: drag to pan, pinch or wheel to zoom, tap to choose.
   It holds which part of the fair is shown, in board units (a tile is 100),
   and hands a tap back as a point on the board. */
class FairBoard {
  constructor(svg, wrap, onTap, o = {}) {
    Object.assign(this, { svg, wrap, onTap, view: null, min: o.min || 560 });
    if (o.tools !== false) {
      const t = document.createElement("div");
      t.className = "fb-tools";
      t.innerHTML = `<button aria-label="zoom in">+</button><button aria-label="zoom out">−</button><button aria-label="fit the whole map">⤢</button>`;
      const [zin, zout, fit] = t.children, mid = () => { const r = wrap.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; };
      zin.onclick = () => this.zoomAt(1.3, ...mid());
      zout.onclick = () => this.zoomAt(1 / 1.3, ...mid());
      fit.onclick = () => { this.fit(this.lastTiles || []); this.apply(); };
      wrap.append(t);
    }
    if (o.still) return;
    const pts = new Map();
    let moved = false, start = null, pinch = null;
    svg.addEventListener("pointerdown", (e) => {
      if (e.isPrimary) { pts.clear(); pinch = null; } // a first finger down: any other the board thought was down has gone
      svg.setPointerCapture(e.pointerId);
      pts.set(e.pointerId, [e.clientX, e.clientY]);
      if (pts.size === 1) { moved = false; start = { cx: e.clientX, cy: e.clientY, v: { ...this.view } }; }
      if (pts.size === 2) { const [a, b] = [...pts.values()]; pinch = { d: Math.hypot(a[0] - b[0], a[1] - b[1]), w: this.view.w }; moved = true; }
    });
    svg.addEventListener("pointermove", (e) => {
      if (!pts.has(e.pointerId)) return;
      pts.set(e.pointerId, [e.clientX, e.clientY]);
      if (pts.size === 2 && pinch) {
        const [a, b] = [...pts.values()], d = Math.hypot(a[0] - b[0], a[1] - b[1]);
        this.zoomAt(this.view.w / (pinch.w * (pinch.d / d)), (a[0] + b[0]) / 2, (a[1] + b[1]) / 2);
        return;
      }
      if (pts.size === 1 && start) {
        const dx = e.clientX - start.cx, dy = e.clientY - start.cy;
        if (!moved && Math.hypot(dx, dy) < 7) return;
        moved = true;
        const k = this.view.w / wrap.clientWidth;
        this.view = { ...this.view, x: start.v.x - dx * k, y: start.v.y - dy * k };
        this.apply();
      }
    });
    svg.addEventListener("pointerup", (e) => {
      if (!pts.has(e.pointerId)) return;
      pts.delete(e.pointerId);
      if (pts.size < 2) pinch = null;
      if (pts.size === 0 && !moved) onTap(...this.toBoard(e.clientX, e.clientY));
      if (pts.size === 0) start = null;
    });
    svg.addEventListener("pointercancel", (e) => { pts.delete(e.pointerId); pinch = null; });
    svg.addEventListener("wheel", (e) => { e.preventDefault(); this.zoomAt(e.deltaY < 0 ? 1.15 : 1 / 1.15, e.clientX, e.clientY); }, { passive: false });
    window.addEventListener("resize", () => this.apply());
  }
  aspect() { return this.wrap.clientWidth / Math.max(1, this.wrap.clientHeight); }
  toBoard(cx, cy) { const p = this.svg.createSVGPoint(); p.x = cx; p.y = cy; const q = p.matrixTransform(this.svg.getScreenCTM().inverse()); return [q.x, q.y]; }
  /* the whole of these tiles in sight, with a tile's room around them */
  fit(tiles) {
    this.lastTiles = [...tiles];
    const xs = this.lastTiles.map((t) => t.x), ys = this.lastTiles.map((t) => t.y);
    if (!xs.length) { xs.push(0); ys.push(0); }
    const x0 = Math.min(...xs) - 1, x1 = Math.max(...xs) + 2, y0 = Math.min(...ys) - 1, y1 = Math.max(...ys) + 2, a = this.aspect();
    let w = (x1 - x0) * 100, h = (y1 - y0) * 100;
    if (w / h < a) w = h * a; else h = w / a;
    w = Math.max(w, this.min);
    this.view = { x: ((x0 + x1) / 2) * 100 - w / 2, y: ((y0 + y1) / 2) * 100 - w / a / 2, w };
  }
  /* a tile kept in sight: the view slides only as far as it must */
  keep(x, y) {
    const h = this.view.w / this.aspect(), m = 12;
    const [x0, y0, x1, y1] = [x * 100 - m, y * 100 - m, x * 100 + 100 + m, y * 100 + 100 + m];
    if (x1 - x0 > this.view.w || y1 - y0 > h) return;
    if (x0 < this.view.x) this.view.x = x0; else if (x1 > this.view.x + this.view.w) this.view.x = x1 - this.view.w;
    if (y0 < this.view.y) this.view.y = y0; else if (y1 > this.view.y + h) this.view.y = y1 - h;
  }
  /* a tile in the middle, this wide */
  centre(x, y, w) { const a = this.aspect(); this.view = { x: x * 100 + 50 - w / 2, y: y * 100 + 50 - w / a / 2, w }; }
  zoomAt(f, cx, cy) {
    const [bx, by] = this.toBoard(cx, cy), w = Math.min(5000, Math.max(220, this.view.w / f)), k = w / this.view.w;
    this.view = { x: bx - (bx - this.view.x) * k, y: by - (by - this.view.y) * k, w };
    this.apply();
  }
  apply() { if (this.view) this.svg.setAttribute("viewBox", `${this.view.x} ${this.view.y} ${this.view.w} ${this.view.w / this.aspect()}`); }
}
/* where on the board a point on a tile is, the tile turned as it lies */
function onBoard(t, ax, ay) {
  const r = (t.rot * Math.PI) / 2;
  return [t.x * 100 + 50 + (ax - 50) * Math.cos(r) - (ay - 50) * Math.sin(r), t.y * 100 + 50 + (ax - 50) * Math.sin(r) + (ay - 50) * Math.cos(r)];
}

{
  const s = document.createElement("style");
  s.textContent = `
.fb-wrap { position: relative; border-radius: 14px; overflow: hidden; background: radial-gradient(120% 100% at 50% 30%, #1c1a2e, #0d0c16); box-shadow: inset 0 0 30px #000a; }
.fb-svg { width: 100%; height: 100%; display: block; touch-action: none; cursor: grab; user-select: none; -webkit-user-select: none; }
.fb-tools { position: absolute; right: 8px; top: 8px; display: grid; gap: 6px; }
.fb-tools button { width: 40px; height: 40px; border-radius: 10px; background: #0008; color: var(--chalk); font-size: 1.2rem; font-weight: 800; border: 1px solid #ffffff30; }`;
  document.head.append(s);
}

/* the places on a tile a map can name: a square, the end of a lane or canal (a
   well, a crossing, a basin, a stall at a lane's end), a bridge, a stall
   beside a lane, a landing. Each is "x,y:KEY" on a map, its point on the tile. */
function landmarks(id) {
  const def = T[id], out = [];
  def.segs.forEach((s, i) => { if (s.k === "P") out.push({ k: "sq", kind: "square", at: anchor(s) }); });
  const ends = def.segs.map((s) => s.end).filter(Boolean);
  const centre = ends.find((e) => ["well", "cross", "basin", "stall"].includes(e));
  if (centre) out.push({ k: "c", kind: { well: "well", cross: "crossing", basin: "basin", stall: "stall" }[centre], at: [50, 50] });
  if (def.bridge) out.push({ k: "br", kind: "bridge", at: [50, 50] });
  if (def.segs.some((s) => s.stalls && s.end !== "stall")) out.push({ k: "st", kind: "stall", at: id === "start" || id === "bridge-stall" ? [18, 79] : [77, 51] });
  if (ends.includes("landing")) out.push({ k: "ld", kind: "landing", at: [50, 74] });
  return out;
}
/* a map's tiles as the board holds them, and its named places by where they are */
function mapTiles(map) { return new Map(map.tiles.map(([x, y, id, rot]) => [key(x, y), { x, y, id, rot, stalls: stallsOf(id).map((s) => ({ ...s, good: null })) }])); }
function placeAt(tiles, at) {
  const [k, lk] = at.split(":"), t = tiles.get(k);
  if (!t) return null;
  const lm = landmarks(t.id).find((l) => l.k === lk);
  return lm ? { t, lm, pt: onBoard(t, ...lm.at) } : null;
}
/* a label on the board, upright whatever way its tile is turned */
function labelSVG(px, py, text, cls = "") {
  const w = Math.max(40, text.length * 9.2 + 18);
  return `<g class="fb-label ${cls}"><circle cx="${px}" cy="${py}" r="9"/><rect x="${px - w / 2}" y="${py - 44}" width="${w}" height="26" rx="13"/><text x="${px}" y="${py - 26}">${esc(text)}</text></g>`;
}
{
  const s = document.createElement("style");
  s.textContent = `
.fb-label circle { fill: #fff3c4; stroke: #2a2140; stroke-width: 3; }
.fb-label rect { fill: #16121fdd; stroke: #fff3c488; stroke-width: 1.5; }
.fb-label text { fill: #fff3c4; font: 700 15px var(--ui); text-anchor: middle; }
.fb-label.here circle { fill: var(--go); r: 13; }
.fb-label.here rect { fill: var(--go); stroke: var(--go); }
.fb-label.here text { fill: var(--go-ink); }`;
  document.head.append(s);
}
