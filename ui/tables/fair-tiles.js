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
function squareSVG(s, pave = COL.pave, pave2 = COL.pave2) {
  let out = s.e.length === 4 ? `<rect width="100" height="100" fill="${pave}"/>` : s.e.map((e) => `<polygon points="${PAVE[e]}" fill="${pave}"/>`).join("");
  if (s.e.length >= 2 && s.e.length < 4) out += `<rect x="30" y="30" width="40" height="40" fill="${pave}"/>`;
  out += `<g stroke="${pave2}" stroke-width="1" opacity="0.6">${s.e.map((e) => { const [x, y] = MID[e]; return e % 2 ? `<path d="M${x === 0 ? 8 : 92} 20 V80 M${x === 0 ? 18 : 82} 28 V72"/>` : `<path d="M20 ${y === 0 ? 8 : 92} H80 M28 ${y === 0 ? 18 : 82} H72"/>`; }).join("")}</g>`;
  return out;
}
function stallSVG(x, y, st) {
  const c = GOOD_COL[st.good] || "#c9553f";
  return `${st.lit ? `<circle cx="${x + 13}" cy="${y + 6}" r="24" fill="url(#glow)"/>` : ""}<rect x="${x}" y="${y}" width="26" height="19" rx="2" fill="${st.lit ? "#a8483a" : "#4a4552"}"/><path d="M${x - 3} ${y + 2} h32 l-4 -8 h-24 z" fill="${c}" opacity="${st.lit ? 1 : 0.55}"/><path d="M${x + 5} ${y - 6} v8 M${x + 13} ${y - 6} v8 M${x + 21} ${y - 6} v8" stroke="#fff8" stroke-width="2"/><circle cx="${x + 13}" cy="${y + 8}" r="3.6" fill="${st.lit ? "#fff2b0" : "#1f1c26"}"/>`;
}
/* Each world lays the same tiles in its own look, and calls their places by its
   own names: the fair's lanes, canals and squares are the cellar's corridors,
   brass pipes and workshop rooms, and the ironworks' rails, molten channels and
   plated yards. A map names its set ("set"); the fair's is the one with none. */
const SETS = {
  fair: { name: "the Lantern Fair", kinds: { L: "lane", C: "canal", P: "square" },
    places: { square: "square", well: "well", crossing: "crossing", basin: "basin", stall: "stall", bridge: "bridge", landing: "landing" } },
  cellar: { name: "the Clockwork Cellar", kinds: { L: "corridor", C: "pipe", P: "room" },
    places: { square: "room", well: "gear pit", crossing: "turntable", basin: "boiler", stall: "workbench", bridge: "catwalk", landing: "hatch" } },
  ironworks: { name: "the Ironworks", kinds: { L: "rail", C: "channel", P: "yard" },
    places: { square: "yard", well: "crane", crossing: "switch", basin: "furnace", stall: "shed", bridge: "gantry", landing: "loading dock" } },
};
const SET_OF_WORLD = { "lantern-fair": "fair", "clockwork-cellar": "cellar", "ironworks-last-pour": "ironworks" };
const skinOf = (set) => SETS[set] || SETS.fair;

function groundSVG(set) {
  if (set === "cellar") return `<rect width="100" height="100" fill="#2b2420"/><path d="M0 22 L30 18 L55 26 L100 20 M0 61 L22 66 L60 58 L100 64 M18 0 L22 18 M70 26 L66 58 M40 66 L44 100 M86 64 L82 100" stroke="#3a312b" stroke-width="1.5" fill="none"/>`;
  if (set === "ironworks") return `<rect width="100" height="100" fill="#1f1c1b"/><g fill="#34302d">${[[12, 14], [37, 8], [71, 19], [88, 47], [9, 58], [27, 83], [58, 76], [84, 90], [46, 41]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="1.6"/>`).join("")}</g>`;
  return `<rect width="100" height="100" fill="${COL.quay}"/><path d="M0 33 H100 M0 66 H100 M33 0 V100 M66 0 V100" stroke="${COL.quay2}" stroke-width="1"/>`;
}
function channelSVG(g, set) {
  const d = segPath(g), pool = g.end === "basin" ? 24 : g.e.length === 3 ? 17 : 0;
  if (set === "cellar") {
    let s = `<path d="${d}" stroke="#4a2d16" stroke-width="22" fill="none"/><path d="${d}" stroke="#c07a3a" stroke-width="16" fill="none"/><path d="${d}" stroke="#7a4a22" stroke-width="22" stroke-dasharray="3 21" fill="none"/><path d="${d}" stroke="#f2b77e" stroke-width="3" fill="none" opacity="0.8"/>`;
    if (g.e.length === 3) s += `<circle cx="50" cy="50" r="15" fill="#c07a3a" stroke="#4a2d16" stroke-width="3"/><circle cx="50" cy="50" r="5" fill="#4a2d16"/>`;
    if (g.end === "basin") s += `<circle cx="50" cy="50" r="24" fill="#a8652d" stroke="#4a2d16" stroke-width="3"/>${[0, 60, 120, 180, 240, 300].map((a) => `<circle cx="${50 + 19 * Math.cos((a * Math.PI) / 180)}" cy="${50 + 19 * Math.sin((a * Math.PI) / 180)}" r="2" fill="#f2b77e"/>`).join("")}<circle cx="50" cy="50" r="8" fill="#5a3518"/>`;
    return s;
  }
  if (set === "ironworks") {
    let s = `<path d="${d}" stroke="#3b1d0f" stroke-width="30" fill="none"/><path d="${d}" stroke="#ff6a1a" stroke-width="20" fill="none"/><path d="${d}" stroke="#ffd27a" stroke-width="5" fill="none" opacity="0.9"/>`;
    if (pool) s += `<circle cx="50" cy="50" r="${pool}" fill="#3b1d0f"/><circle cx="50" cy="50" r="${pool - 6}" fill="#ff6a1a"/><circle cx="50" cy="50" r="${pool - 14}" fill="#ffd27a"/>`;
    return s;
  }
  let s = `<path d="${d}" stroke="${COL.water}" stroke-width="34" fill="none"/>`;
  if (pool) s += `<circle cx="50" cy="50" r="${pool}" fill="${COL.water}"/>`;
  return s + `<path d="${d}" stroke="${COL.water2}" stroke-width="2" stroke-dasharray="6 9" fill="none" opacity="0.7"/>`;
}
function wayPath(g) { return g.end === "landing" ? `M50 100 L50 67` : segPath(g); }
function waySVG(g, set) {
  const d = wayPath(g);
  if (set === "cellar") return `<path d="${d}" stroke="#5c5046" stroke-width="24" fill="none"/><path d="${d}" stroke="#a89a86" stroke-width="18" fill="none"/><path d="${d}" stroke="#8c7f6d" stroke-width="18" stroke-dasharray="1.5 9" fill="none"/>`
    + (g.end === "landing" ? `<path d="M43 70 H57 M43 76 H57 M43 82 H57 M43 68 V86 M57 68 V86" stroke="#3a312b" stroke-width="2"/>` : "");
  if (set === "ironworks") return `<path d="${d}" stroke="#5b4632" stroke-width="24" stroke-dasharray="4 7" fill="none"/><path d="${d}" stroke="#b9c1c8" stroke-width="15" fill="none"/><path d="${d}" stroke="#2c2622" stroke-width="10" fill="none"/>`
    + (g.end === "landing" ? `<rect x="34" y="64" width="32" height="10" fill="#6d7680"/><path d="M36 69 H64" stroke="#9aa3ad" stroke-width="1.5"/>` : "");
  return `<path d="${d}" stroke="${COL.lane2}" stroke-width="22" fill="none"/><path d="${d}" stroke="${COL.lane}" stroke-width="16" fill="none"/>`
    + (g.end === "landing" ? `<path d="M42 70 H58 M42 75 H58 M42 80 H58" stroke="${COL.lane2}" stroke-width="1.5"/>` : "");
}
const PAVES = { fair: [COL.pave, COL.pave2], cellar: ["#6e4b2c", "#56391f"], ironworks: ["#4b5560", "#66727e"] };
function bridgeSVG(set) {
  if (set === "cellar") return `<path d="M30 38 H70 M30 62 H70" stroke="#9aa3ad" stroke-width="3"/><path d="M34 38 V62 M42 38 V62 M50 38 V62 M58 38 V62 M66 38 V62" stroke="#9aa3ad" stroke-width="1.2" opacity="0.8"/>`;
  if (set === "ironworks") return `<path d="M28 36 H72 M28 64 H72" stroke="#8d96a0" stroke-width="5"/><path d="M30 36 L44 64 L58 36 L72 64" stroke="#8d96a0" stroke-width="2" fill="none"/>`;
  return `<path d="M31 39 H69 M31 61 H69" stroke="#6b4e2e" stroke-width="3"/><path d="M33 39 V61 M67 39 V61" stroke="#6b4e2e" stroke-width="1.5" opacity="0.7"/>`;
}
function centreSVG(end, set) {
  if (set === "cellar") {
    const gear = (r, c) => `<circle cx="50" cy="50" r="${r + 3}" fill="none" stroke="${c}" stroke-width="6" stroke-dasharray="4 4"/><circle cx="50" cy="50" r="${r}" fill="${c}"/><circle cx="50" cy="50" r="${r / 2.6}" fill="#2b2420"/>`;
    return end === "well" ? gear(10, "#8c7a5a") : gear(14, "#c9a24a");
  }
  if (set === "ironworks") {
    if (end === "well") return `<rect x="40" y="40" width="20" height="20" fill="#6d7680"/><path d="M50 50 L82 22" stroke="#e2b04f" stroke-width="5"/><path d="M82 22 V36" stroke="#9aa3ad" stroke-width="2"/>`;
    return `<circle cx="50" cy="50" r="16" fill="#4b5560"/><path d="M38 38 L62 62 M62 38 L38 62" stroke="#b9c1c8" stroke-width="3"/><circle cx="50" cy="50" r="4" fill="#e2b04f"/>`;
  }
  if (end === "well") return `<circle cx="50" cy="50" r="13" fill="#8c8698"/><circle cx="50" cy="50" r="7" fill="#15131f"/>`;
  return `<circle cx="50" cy="50" r="15" fill="#8c8698"/><circle cx="50" cy="50" r="10" fill="${COL.water}"/><circle cx="50" cy="50" r="3" fill="${COL.water2}"/>`;
}
function standSVG(x, y, st, set) {
  if (set === "cellar") return `${st.lit ? `<circle cx="${x + 13}" cy="${y + 4}" r="22" fill="url(#glow)"/>` : ""}<rect x="${x}" y="${y + 4}" width="26" height="10" fill="#6e4b2c" stroke="#3a2614"/><path d="M${x + 3} ${y + 14} v6 M${x + 23} ${y + 14} v6" stroke="#3a2614" stroke-width="2.5"/><path d="M${x + 18} ${y + 4} v-8 h5" stroke="#9aa3ad" stroke-width="2" fill="none"/><circle cx="${x + 23}" cy="${y - 3}" r="3.4" fill="${st.lit ? "#fff2b0" : "#1f1c26"}"/>`;
  if (set === "ironworks") return `${st.lit ? `<circle cx="${x + 13}" cy="${y + 8}" r="22" fill="url(#glow)"/>` : ""}<path d="M${x} ${y + 20} V${y + 4} L${x + 13} ${y - 4} L${x + 26} ${y + 4} V${y + 20} Z" fill="#59626c" stroke="#2c2622" stroke-width="1.5"/><rect x="${x + 9}" y="${y + 7}" width="8" height="7" fill="${st.lit ? "#ffd27a" : "#1f1c1b"}"/>`;
  return stallSVG(x, y, st);
}
function tileInner(id, stalls, set = "fair") {
  const def = T[id];
  let s = groundSVG(set);
  for (const g of def.segs.filter((g) => g.k === "C")) s += channelSVG(g, set);
  for (const g of def.segs.filter((g) => g.k === "L")) s += waySVG(g, set);
  const [pave, pave2] = PAVES[set] || PAVES.fair;
  for (const g of def.segs.filter((g) => g.k === "P")) s += squareSVG(g, pave, pave2);
  if (def.bridge) s += bridgeSVG(set);
  const ends = new Set(def.segs.map((g) => g.end).filter(Boolean));
  if (ends.has("well")) s += centreSVG("well", set);
  if (ends.has("cross")) s += centreSVG("cross", set);
  (stalls || stallsOf(id).map((x) => ({ ...x, good: null }))).forEach((st) => {
    const g = def.segs[st.seg];
    s += g.end === "stall" ? standSVG(37, 42, st, set) : id === "start" || id === "bridge-stall" ? standSVG(5, 70, st, set) : standSVG(64, 42, st, set);
  });
  return s;
}
const tileG = (x, y, id, rot, stalls, extra = "", set = "fair") => `<g transform="translate(${x * 100} ${y * 100}) rotate(${rot * 90} 50 50)" ${extra}>${tileInner(id, stalls, set)}</g>`;
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
function landmarks(id, set = "fair") {
  const def = T[id], out = [], named = skinOf(set).places;
  def.segs.forEach((s, i) => { if (s.k === "P") out.push({ k: "sq", kind: "square", at: anchor(s) }); });
  const ends = def.segs.map((s) => s.end).filter(Boolean);
  const centre = ends.find((e) => ["well", "cross", "basin", "stall"].includes(e));
  if (centre) out.push({ k: "c", kind: { well: "well", cross: "crossing", basin: "basin", stall: "stall" }[centre], at: [50, 50] });
  if (def.bridge) out.push({ k: "br", kind: "bridge", at: [50, 50] });
  if (def.segs.some((s) => s.stalls && s.end !== "stall")) out.push({ k: "st", kind: "stall", at: id === "start" || id === "bridge-stall" ? [18, 79] : [77, 51] });
  if (ends.includes("landing")) out.push({ k: "ld", kind: "landing", at: [50, 74] });
  return out.map((l) => ({ ...l, kind: named[l.kind] || l.kind }));
}
/* a map's tiles as the board holds them, and its named places by where they are */
function mapTiles(map) { const set = map.set || "fair"; return new Map(map.tiles.map(([x, y, id, rot]) => [key(x, y), { x, y, id, rot, set, stalls: stallsOf(id).map((s) => ({ ...s, good: null })) }])); }
function placeAt(tiles, at) {
  const [k, lk] = at.split(":"), t = tiles.get(k);
  if (!t) return null;
  const lm = landmarks(t.id, t.set).find((l) => l.k === lk);
  return lm ? { t, lm, pt: onBoard(t, ...lm.at) } : null;
}
/* a label on the board, upright whatever way its tile is turned; dy is where
   its tag sits from its point (above, by default) */
function labelSVG(px, py, text, cls = "", dy = -44) {
  const w = Math.max(40, text.length * 9.2 + 18);
  return `<g class="fb-label ${cls}"><circle cx="${px}" cy="${py}" r="9"/><rect x="${px - w / 2}" y="${py + dy}" width="${w}" height="26" rx="13"/><text x="${px}" y="${py + dy + 18}">${esc(text)}</text></g>`;
}
/* several labels laid together: a tag that would cover one already placed
   goes below its point, or further up, and the one lit is drawn last, on top */
function labelsSVG(items) {
  const placed = [], out = [];
  const order = items.slice().sort((a, b) => (a.cls === "here") - (b.cls === "here"));
  for (const it of [...order].sort((a, b) => (b.cls === "here") - (a.cls === "here"))) {
    const w = Math.max(40, it.text.length * 9.2 + 18);
    const box = (dy) => [it.x - w / 2, it.y + dy, it.x + w / 2, it.y + dy + 26];
    const hits = (r) => placed.some((q) => r[0] < q[2] && q[0] < r[2] && r[1] < q[3] && q[1] < r[3]);
    const dy = [-44, 16, -74, 46].find((d) => !hits(box(d))) ?? -44;
    placed.push(box(dy));
    it.dy = dy;
  }
  for (const it of order) out.push(labelSVG(it.x, it.y, it.text, it.cls, it.dy));
  return out.join("");
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
