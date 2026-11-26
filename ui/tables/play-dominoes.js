/* All Fives dominoes, as play-dominoes plays it on the record
   (adapters/stdlib/play-dominoes): two seats on a double-six set, nine tiles
   each, the other ten the boneyard. The first hand, and a hand after a block,
   is led by the highest double dealt; after a seat goes out, it leads any
   tile. The first double played is the spinner: tiles go against its four
   arms in any order. A seat that can play must; one that can't draws until it
   can, and passes when the boneyard is empty. After every play the open ends
   are counted, and a multiple of five scores itself. Out, or fewer pips when
   nobody can play, scores the other's pips to the nearest five; 250 wins the
   game. North plays by play-dominoes' own fixed rule; you sit south. */
const HAND = 9, TARGET = 250;
const ARMS = ["left", "right", "up", "down"];
const NORTH = 0, ME = 1;
const WHO = ["North", "You"];
const tileName = (t) => `${t[0]}|${t[1]}`;
const pipsOf = (h) => h.reduce((n, t) => n + t[0] + t[1], 0);
const toFive = (n) => Math.floor((n + 2) / 5) * 5;
const same = (a, b) => a[0] === b[0] && a[1] === b[1];
const allTiles = () => { const out = []; for (let a = 6; a >= 0; a--) for (let b = a; b >= 0; b--) out.push([a, b]); return out; };

/* ── the layout: a lead, and four arms going out from it, each tile [inner, outer] ── */
function newLayout() { return { lead: null, arms: { left: [], right: [], up: [], down: [] }, spinner: null, seq: [] }; }
function spinnerTile(L) { return L.spinner === "lead" ? L.lead : L.spinner ? L.arms[L.spinner[0]][L.spinner[1]] : null; }
function openArms(L) { return L.spinner !== null ? ARMS : ["left", "right"]; }
function endOf(L, arm) {
  const a = L.arms[arm];
  if (a.length) return a[a.length - 1][1];
  if (arm === "up" || arm === "down") return spinnerTile(L)[0];
  return arm === "left" ? L.lead[0] : L.lead[1];
}
function fitsOf(L, t) { return L.lead === null ? ["lead"] : openArms(L).filter((a) => t.includes(endOf(L, a))); }
function place(L, t, arm) {
  if (arm === "lead") { L.lead = t; if (t[0] === t[1]) L.spinner = "lead"; return; }
  const e = endOf(L, arm);
  L.arms[arm].push([e, t[0] === e ? t[1] : t[0]]);
  L.seq.push(arm);
  if (L.spinner === null && t[0] === t[1]) L.spinner = [arm, L.arms[arm].length - 1];
}
/* What each open end adds to the count, by arm: a double at an end counts both
   halves, and so does the spinner, while either side of it along the line is
   open (once, if both are); up and down add nothing until they're played on.
   An arm that adds nothing is still open to play on. */
function countParts(L) {
  const parts = {};
  if (L.lead === null) return parts;
  const dbl = L.lead[0] === L.lead[1];
  for (const arm of ARMS) {
    const a = L.arms[arm];
    if (a.length) { const [x, y] = a[a.length - 1]; parts[arm] = x === y ? x + y : y; }
    else if (arm === "up" || arm === "down") continue;
    else if (dbl) { if (!(arm === "right" && !L.arms.left.length)) parts[arm] = 2 * L.lead[0]; }
    else parts[arm] = arm === "left" ? L.lead[0] : L.lead[1];
  }
  return parts;
}
const countOf = (L) => Object.values(countParts(L)).reduce((a, b) => a + b, 0);
const copyLayout = (L) => ({ lead: L.lead, spinner: L.spinner, seq: L.seq.slice(), arms: Object.fromEntries(ARMS.map((a) => [a, L.arms[a].slice()])) });
const scoreOf = (c) => (c && c % 5 === 0 ? c : 0);

/* ── the game ── */
let G, busy = false, chosen = null;

function newGame() {
  G = { scores: [0, 0], handNo: 0, lastOut: null, rows: [], over: false };
  frame.clearLog();
  frame.log("<b>A new game.</b> All Fives to 250: every multiple of five on the ends scores.");
  deal();
}
function deal() {
  const ts = shuffle(allTiles());
  G.hands = [ts.slice(0, HAND), ts.slice(HAND, 2 * HAND)];
  G.boneyard = ts.slice(2 * HAND);
  G.layout = newLayout(); G.ended = false; G.handNo++; G.last = null; G.handScores = [0, 0]; G.flash = "";
  chosen = null;
  if (G.lastOut !== null) { G.turn = G.lastOut; G.mustLead = null; }
  else {
    const held = G.hands.flatMap((h, s) => h.map((t) => [t, s]));
    const doubles = held.filter(([t]) => t[0] === t[1]);
    const pool = doubles.length ? doubles : held;
    const best = pool.reduce((a, b) => (b[0][0] + b[0][1] > a[0][0] + a[0][1] || (b[0][0] + b[0][1] === a[0][0] + a[0][1] && b[0][0] > a[0][0]) ? b : a));
    G.turn = best[1]; G.mustLead = best[0];
  }
  const lead = G.mustLead ? ` with the ${tileName(G.mustLead)}` : "";
  frame.log(`<b>Hand ${G.handNo}.</b> Nine tiles each, ten in the boneyard. ${WHO[G.turn]} lead${G.turn === ME ? "" : "s"}${lead}.`);
  render(); run();
}
const canPlay = (seat) => G.hands[seat].filter((t) => fitsOf(G.layout, t).length && (!G.mustLead || same(t, G.mustLead)));

function play(seat, t, arm) {
  place(G.layout, t, arm);
  G.hands[seat] = G.hands[seat].filter((x) => !same(x, t));
  G.mustLead = null;
  const c = countOf(G.layout), s = scoreOf(c);
  G.scores[seat] += s; G.handScores[seat] += s;
  G.last = arm === "lead" ? ["lead", 0] : [arm, G.layout.arms[arm].length - 1];
  const where = arm === "lead" ? "lead" + (seat === ME ? "" : "s") : `play${seat === ME ? "" : "s"} the ${tileName(t)} on the ${arm} arm`;
  frame.log(`<b>${WHO[seat]}</b> ${arm === "lead" ? `${where} the ${tileName(t)}` : where}: ${c} on the ends${s ? `, <b>scores ${s}</b>` : ""}.`);
  G.flash = s ? `<b>${WHO[seat]} score${seat === ME ? "" : "s"} ${s}.</b>` : "";
  after(seat);
}
function draw(seat) {
  const t = G.boneyard.shift(); G.hands[seat].push(t);
  frame.log(`${WHO[seat]} draw${seat === ME ? `: the ${tileName(t)}` : "s a tile"}.`);
}
function pass(seat) { frame.log(`${WHO[seat]} pass${seat === ME ? "" : "es"}: nothing fits and the boneyard is empty.`); after(seat); }
function after(seat) {
  const other = 1 - seat;
  if (G.scores[seat] >= TARGET) return endHand("target", seat, 0);
  if (!G.hands[seat].length) return endHand("out", seat, toFive(pipsOf(G.hands[other])));
  if (!G.boneyard.length && !canPlay(0).length && !canPlay(1).length) {
    const held = G.hands.map(pipsOf);
    if (held[0] === held[1]) return endHand("blocked", null, 0);
    const low = held[0] < held[1] ? 0 : 1;
    return endHand("blocked", low, toFive(held[1 - low]));
  }
  G.turn = other;
}
function endHand(how, seat, points) {
  G.ended = true; G.lastOut = how === "out" ? seat : null;
  if (seat !== null) { G.scores[seat] += points; G.handScores[seat] += points; }
  const said = how === "out" ? `<b>${WHO[seat]} ${seat === ME ? "are" : "is"} out</b>, and score${seat === ME ? "" : "s"} ${points} for the pips left.`
    : how === "target" ? `<b>${WHO[seat]} reach${seat === ME ? "" : "es"} ${TARGET}.</b>`
    : seat === null ? "<b>Blocked</b>, the pips tied: nobody scores."
    : `<b>Blocked.</b> ${WHO[seat]} hold${seat === ME ? "" : "s"} fewer pips, and score${seat === ME ? "" : "s"} ${points}.`;
  frame.log(said);
  G.rows.push({ label: String(G.handNo), cells: G.handScores.map((v, i) => (i === seat && how !== "target" ? `${v} ★` : String(v))) });
  if (seat !== null && G.scores[seat] >= TARGET) { G.over = true; frame.log(`<b>${WHO[seat]} win${seat === ME ? "" : "s"} the game, ${G.scores[seat]} to ${G.scores[1 - seat]}.</b>`); }
}

/* North: play-dominoes' fixed rule. Draw until it can play, then what scores
   most, then the heaviest tile, then the first arm in left, right, up, down. */
const above = (a, b) => { for (let i = 0; i < a.length; i++) if (a[i] !== b[i]) return a[i] > b[i]; return false; };
function chosenBy(seat) {
  let best = null;
  for (const t of canPlay(seat)) for (const arm of fitsOf(G.layout, t)) {
    const L = copyLayout(G.layout); place(L, t, arm);
    const key = [scoreOf(countOf(L)), t[0] + t[1], t[0], t[1], arm === "lead" ? 0 : -ARMS.indexOf(arm)];
    if (!best || above(key, best.key)) best = { key, t, arm };
  }
  return best;
}
async function run() {
  if (busy) return; busy = true;
  while (!G.over && !G.ended && G.turn === NORTH) {
    render(); await wait(700);
    while (!canPlay(NORTH).length && G.boneyard.length) { draw(NORTH); render(); await wait(250); }
    if (canPlay(NORTH).length) { const b = chosenBy(NORTH); play(NORTH, b.t, b.arm); } else pass(NORTH);
  }
  busy = false; render();
}

/* ── you ── */
function pick(i) {
  if (busy || G.ended || G.turn !== ME) return frame.refuse("it isn't your turn");
  G.flash = "";
  const t = G.hands[ME][i];
  if (G.mustLead && !same(t, G.mustLead)) return frame.refuse(`the ${tileName(G.mustLead)} leads this hand`);
  const fits = fitsOf(G.layout, t);
  if (!fits.length) return frame.refuse(`the ${tileName(t)} doesn't match an open end`);
  if (fits.length === 1) { chosen = null; play(ME, t, fits[0]); render(); return run(); }
  chosen = chosen && same(chosen, t) ? null : t;
  render();
}
function onArm(arm) {
  if (!chosen) return;
  const t = chosen; chosen = null;
  play(ME, t, arm); render(); run();
}
function onDraw() {
  if (busy || G.ended || G.turn !== ME) return;
  if (canPlay(ME).length) return frame.refuse("a seat that can play must play");
  if (!G.boneyard.length) return frame.refuse("the boneyard is empty: pass");
  draw(ME); render();
}
function onPass() {
  if (busy || G.ended || G.turn !== ME) return;
  if (canPlay(ME).length) return frame.refuse("a seat that can play must play");
  if (G.boneyard.length) return frame.refuse("draw first: the boneyard isn't empty");
  pass(ME); render(); run();
}

/* ── the picture: tiles with pips, doubles crosswise, the spinner's arms up and down ── */
const S = 30, GAP = 3;
const SPOTS = { 0: [], 1: [[0.5, 0.5]], 2: [[0.27, 0.27], [0.73, 0.73]], 3: [[0.27, 0.27], [0.5, 0.5], [0.73, 0.73]],
  4: [[0.27, 0.27], [0.73, 0.27], [0.27, 0.73], [0.73, 0.73]], 5: [[0.27, 0.27], [0.73, 0.27], [0.5, 0.5], [0.27, 0.73], [0.73, 0.73]],
  6: [[0.27, 0.25], [0.27, 0.5], [0.27, 0.75], [0.73, 0.25], [0.73, 0.5], [0.73, 0.75]] };
function halfSVG(x, y, n, rot) {
  return SPOTS[n].map(([px, py]) => { if (rot) [px, py] = [py, px]; return `<circle cx="${(x + px * S).toFixed(1)}" cy="${(y + py * S).toFixed(1)}" r="${(S * 0.09).toFixed(1)}" class="pp"/>`; }).join("");
}
function tileSVG(cx, cy, a, b, vertical, cls = "") {
  const w = vertical ? S : 2 * S, h = vertical ? 2 * S : S, x = cx - w / 2, y = cy - h / 2;
  const line = vertical ? `<line x1="${x + 5}" y1="${cy}" x2="${x + w - 5}" y2="${cy}" class="ln"/>` : `<line x1="${cx}" y1="${y + 5}" x2="${cx}" y2="${y + h - 5}" class="ln"/>`;
  const pips = vertical ? halfSVG(x, y, a, false) + halfSVG(x, y + S, b, false) : halfSVG(x, y, a, true) + halfSVG(x + S, y, b, true);
  return `<g class="tl ${cls}"><rect x="${x + 1.5}" y="${y + 2.5}" width="${w}" height="${h}" rx="5" class="sh"/><rect x="${x}" y="${y}" width="${w}" height="${h}" rx="5" class="fc"/>${line}${pips}</g>`;
}
/* The tiles go down in the order they were played, as at a table. Each arm runs
   out from where it starts and turns clockwise when a leg runs long, so each
   keeps its own quarter of the table and the picture stays near its size; a
   tile that would land on one already down turns the other way instead. A
   tile turning a corner goes against the side of the one before it. */
const LEGS = [6.5 * S, 9 * S, Infinity];
const cw = ([dx, dy]) => [-dy, dx], ccw = ([dx, dy]) => [dy, -dx];
const rectOf = (x, y, v) => { const w = v ? S : 2 * S, h = v ? 2 * S : S; return [x - w / 2, y - h / 2, x + w / 2, y + h / 2]; };
const meets = (a, b) => Math.min(a[2], b[2]) - Math.max(a[0], b[0]) > 0.5 && Math.min(a[3], b[3]) - Math.max(a[1], b[1]) > 0.5;
function boardTiles(L) {
  const out = [], rects = [], kept = {}, last = G.last, ends = {}, state = {};
  const isLast = (arm, i) => !!last && last[0] === arm && last[1] === i;
  const ld = L.lead[0] === L.lead[1];
  const put = (t) => { out.push(t); rects.push(rectOf(t.x, t.y, t.v)); };
  put({ x: 0, y: 0, a: L.lead[0], b: L.lead[1], v: ld, hot: isLast("lead", 0), spin: L.spinner === "lead" });
  const reach = (ld ? S / 2 : S) + GAP;
  state.right = { c: [reach, 0], d: [1, 0], leg: 0, used: 0, prev: null, i: 0 };
  state.left = { c: [-reach, 0], d: [-1, 0], leg: 0, used: 0, prev: null, i: 0 };
  const sides = (x, y, d) => {
    /* up and down go out from the spinner's long sides, across its line */
    const across = cw(d), back = [-across[0], -across[1]];
    const [dn, up] = d[0] >= 0 && d[1] >= 0 ? [across, back] : [back, across];
    state.down = { c: [x + dn[0] * (S + GAP), y + dn[1] * (S + GAP)], d: dn, leg: 0, used: 0, prev: null, i: 0 };
    state.up = { c: [x + up[0] * (S + GAP), y + up[1] * (S + GAP)], d: up, leg: 0, used: 0, prev: null, i: 0 };
    /* each side's first place is kept clear for its own arm */
    for (const side of ["down", "up"]) {
      const st = state[side], c = [st.c[0] + st.d[0] * S, st.c[1] + st.d[1] * S];
      kept[side] = rectOf(c[0], c[1], st.d[1] !== 0);
    }
  };
  if (L.spinner === "lead") sides(0, 0, [1, 0]);
  const at = (st, d, len) => {
    const [x, y] = [st.c[0] + (d[0] * len) / 2, st.c[1] + (d[1] * len) / 2];
    return { x, y };
  };
  const corner = (st, nd) => {
    const p = st.prev;
    let c = [p.x + nd[0] * (p.side + GAP), p.y + nd[1] * (p.side + GAP)];
    if (!p.dbl) c = [c[0] + st.d[0] * (S / 2), c[1] + st.d[1] * (S / 2)];
    return c;
  };
  for (const arm of L.seq) {
    const st = state[arm], [inner, outer] = L.arms[arm][st.i];
    const dbl = inner === outer, len = dbl ? S : 2 * S;
    const tries = [];
    const long = st.prev && st.used + len > LEGS[st.leg];
    if (!long) tries.push({ c: st.c, d: st.d, turned: false });
    if (st.prev) tries.push({ c: corner(st, cw(st.d)), d: cw(st.d), turned: true }, { c: corner(st, ccw(st.d)), d: ccw(st.d), turned: true });
    if (long) tries.push({ c: st.c, d: st.d, turned: false });
    let pick = null;
    for (const tr of tries) {
      const { x, y } = at({ c: tr.c }, tr.d, len), flat = tr.d[1] === 0;
      const r = rectOf(x, y, flat ? dbl : !dbl);
      const clear = Object.entries(kept).every(([side, q]) => side === arm || !meets(q, r));
      if (clear && !rects.some((q) => meets(q, r))) { pick = { ...tr, x, y, flat }; break; }
    }
    if (!pick) { const tr = tries[0]; const { x, y } = at({ c: tr.c }, tr.d, len); pick = { ...tr, x, y, flat: tr.d[1] === 0 }; }
    if (pick.turned) { st.leg = Math.min(st.leg + 1, LEGS.length - 1); st.used = 0; }
    st.d = pick.d;
    const forward = st.d[0] + st.d[1] > 0;
    const [a, b] = forward ? [inner, outer] : [outer, inner];
    const spin = Array.isArray(L.spinner) && L.spinner[0] === arm && L.spinner[1] === st.i;
    put({ x: pick.x, y: pick.y, a, b, v: pick.flat ? dbl : !dbl, hot: isLast(arm, st.i), spin });
    if (spin) sides(pick.x, pick.y, st.d);
    st.prev = { x: pick.x, y: pick.y, dbl, side: dbl ? S : S / 2 };
    st.c = [pick.c[0] + st.d[0] * (len + GAP), pick.c[1] + st.d[1] * (len + GAP)];
    st.used += len + GAP; st.i++;
  }
  for (const arm of openArms(L)) {
    const st = state[arm];
    ends[arm] = { x: st.c[0] + st.d[0] * S * 0.55, y: st.c[1] + st.d[1] * S * 0.55 };
  }
  return { tiles: out, ends };
}
function boardSVG() {
  const L = G.layout;
  if (L.lead === null) return `<div class="dm-empty">${G.mustLead ? `The ${tileName(G.mustLead)} leads.` : "Any tile leads."}</div>`;
  const { tiles, ends } = boardTiles(L);
  const targets = chosen ? fitsOf(L, chosen) : [];
  const pts = tiles.map((t) => [t.x, t.y]).concat(Object.values(ends).map((e) => [e.x, e.y]));
  const xs = pts.map((p) => p[0]), ys = pts.map((p) => p[1]);
  const pad = S * 1.2, x0 = Math.min(...xs) - pad, x1 = Math.max(...xs) + pad, y0 = Math.min(...ys) - pad, y1 = Math.max(...ys) + pad;
  const body = tiles.map((t) => tileSVG(t.x, t.y, t.a, t.b, t.v, (t.hot ? "hot " : "") + (t.spin ? "spin" : ""))).join("");
  const parts = countParts(L);
  const marks = openArms(L).map((arm) => {
    const e = ends[arm], on = targets.includes(arm), counts = arm in parts;
    const label = on || counts ? endOf(L, arm) : "";
    return `<g class="end ${on ? "on" : ""} ${counts ? "" : "quiet"}" data-arm="${arm}" ${on ? `role="button" tabindex="0" aria-label="play on the ${arm} arm"` : ""}><circle cx="${e.x}" cy="${e.y}" r="${S * 0.42}"/><text x="${e.x}" y="${e.y + 4.5}">${label}</text></g>`;
  }).join("");
  const w = x1 - x0, h = y1 - y0;
  return `<svg class="dm-board" viewBox="${x0} ${y0} ${w} ${h}" style="max-width:${Math.min(w * 1.6, 1100)}px" role="img" aria-label="the table: ${tiles.length} tiles; ends ${openArms(L).map((a) => `${a} ${endOf(L, a)}`).join(", ")}">${body}${marks}</svg>`;
}
function handTileHTML(t, i, o) {
  const svg = `<svg viewBox="-16 -31 32 62" width="38" height="74" aria-hidden="true">${tileSVG(0, 0, t[0], t[1], true)}</svg>`;
  return `<button class="dm-tile ${o.lit ? "lit" : ""} ${o.chosen ? "chosen" : ""}" data-i="${i}" ${o.disabled ? "disabled" : ""} aria-label="the ${tileName(t)}">${svg}</button>`;
}
function backsHTML(n) { return `<div class="dm-backs">${Array.from({ length: n }, () => '<span class="dm-back"></span>').join("")}</div>`; }

function render() {
  const mine = G.turn === ME && !G.ended && !G.over && !busy;
  const legal = mine ? canPlay(ME) : [];
  const L = G.layout;
  const count = L.lead === null ? 0 : countOf(L);
  const sum = Object.values(countParts(L));
  const north = `<div class="dm-seat ${G.turn === NORTH && !G.ended ? "turn" : ""}"><div class="seat-name">North<span class="meta">${G.hands[NORTH].length} tiles · ${G.scores[NORTH]}</span></div>${backsHTML(G.hands[NORTH].length)}</div>`;
  const hand = G.hands[ME].map((t, i) => [t, i]).sort((a, b) => b[0][0] + b[0][1] - (a[0][0] + a[0][1]) || b[0][0] - a[0][0]);
  const tiles = hand.map(([t, i]) => handTileHTML(t, i, { lit: frame.hints && legal.some((x) => same(x, t)), chosen: chosen && same(chosen, t), disabled: !mine })).join("");
  const you = `<div class="dm-seat ${mine ? "turn" : ""}"><div class="seat-name">${mine ? "▸ " : ""}You · south<span class="meta">${G.hands[ME].length} tiles · ${G.scores[ME]}</span></div><div class="dm-hand">${tiles}</div></div>`;
  frame.stage(`<div class="dm">${north}<div class="dm-felt"><div class="dm-count">${L.lead === null ? "" : `count ${sum.length > 1 ? sum.join(" + ") + " = " : ""}<b>${count}</b>${scoreOf(count) ? " ★" : ""}`}<span>boneyard ${G.boneyard.length}</span></div>${boardSVG()}</div>${you}</div>`);
  document.querySelectorAll(".dm-tile").forEach((b) => b.addEventListener("click", () => pick(Number(b.dataset.i))));
  document.querySelectorAll(".end.on").forEach((g) => {
    g.addEventListener("click", () => onArm(g.dataset.arm));
    g.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onArm(g.dataset.arm); } });
  });
  if (G.over) {
    frame.status(`<b>${G.scores[ME] > G.scores[NORTH] ? "You win" : "North wins"}</b>, ${Math.max(...G.scores)} to ${Math.min(...G.scores)}.`);
    frame.actions(`<button class="btn" id="a-new">New game</button>`);
  } else if (G.ended) {
    frame.status(G.flash || "The hand is over.");
    frame.actions(`<button class="btn" id="a-next">Next hand</button>`);
  } else if (mine) {
    frame.status((G.flash ? G.flash + " " : "") + (chosen ? `Where does the <b>${tileName(chosen)}</b> go? Tap a lit end.` : G.mustLead ? `Your lead: the <b>${tileName(G.mustLead)}</b>.` : "<b>Your turn.</b>"));
    frame.actions(`${chosen ? fitsOf(L, chosen).map((a) => `<button class="btn" data-arm="${a}">${a} · ${endOf(L, a)}</button>`).join("") : ""}<button class="btn ghost" id="a-draw">Draw</button><button class="btn ghost" id="a-pass">Pass</button>`);
  } else {
    frame.status(G.ended ? "" : G.flash || "North is playing…");
    frame.actions("");
  }
  const on = (id, f) => { const b = document.getElementById(id); if (b) b.addEventListener("click", f); };
  on("a-new", newGame); on("a-next", deal); on("a-draw", onDraw); on("a-pass", onPass);
  document.querySelectorAll("#actions [data-arm]").forEach((b) => b.addEventListener("click", () => onArm(b.dataset.arm)));
  if (xs) tallySheet();
  else frame.score({ cols: ["North", "You"], rows: G.rows, totals: G.scores, lead: G.scores[0] === G.scores[1] ? [] : [G.scores[0] > G.scores[1] ? 0 : 1], head: "Hand", you: ME, empty: "The first hand is on", note: `Fives as they're made, ★ for the hand's pips. First to ${TARGET}.` });
  frame.deck([["In the boneyard", String(G.boneyard.length)], ["In North's hand", String(G.hands[NORTH].length)], ["On the table", String(L.lead === null ? 0 : 1 + ARMS.reduce((n, a) => n + L.arms[a].length, 0))]], "A double-six set: 28 tiles.");
}

const style = document.createElement("style");
style.textContent = `
.dm { display: grid; gap: 14px; width: 100%; min-width: 0; }
.dm-seat { display: grid; gap: 8px; justify-items: center; }
.dm-seat.turn .seat-name { color: var(--go); }
.dm-felt { display: grid; gap: 6px; justify-items: center; min-width: 0; padding: 8px 0; }
.dm-count { display: flex; gap: 18px; font-family: var(--mono); font-size: 0.8rem; color: var(--chalk-dim); }
.dm-count b { color: var(--chalk); font-size: 1rem; }
.dm-board { width: 100%; height: auto; max-height: 62vh; display: block; }
.dm-empty { min-height: 140px; display: grid; place-items: center; font-family: var(--prose); color: var(--chalk-dim); }
.tl .fc { fill: #fbf6e8; stroke: #b9ab8c; stroke-width: 1.2; }
.tl .sh { fill: #000; opacity: 0.3; }
.tl .ln { stroke: #b9ab8c; stroke-width: 1.2; }
.tl .pp { fill: #1f1d1a; }
.tl.spin .fc { fill: #fff3cf; }
.tl.hot .fc { stroke: var(--go); stroke-width: 3; }
.end circle { fill: #ffffff10; stroke: #ffffff30; stroke-width: 1; }
.end text { fill: var(--chalk-faint); font: 700 13px var(--mono); text-anchor: middle; }
.end.quiet circle { fill: none; stroke-dasharray: 3 3; }
.end.on { cursor: pointer; }
.end.on circle { fill: var(--go); stroke: var(--go); }
.end.on text { fill: var(--go-ink); }
.end.on:focus-visible circle { stroke: #fff; stroke-width: 3; }
.dm-hand { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; padding-top: 10px; }
.dm-tile { border-radius: 7px; transition: transform .15s ease; line-height: 0; }
.dm-tile svg { display: block; }
.dm-tile:not(:disabled):hover, .dm-tile.chosen { transform: translateY(-10px); }
.dm-tile.chosen { outline: 3px solid var(--go); outline-offset: 2px; }
.dm-tile.lit { box-shadow: 0 0 0 3px color-mix(in srgb, var(--go) 70%, transparent); }
.dm-tile:disabled { filter: brightness(0.8); cursor: default; }
.dm-backs { display: flex; flex-wrap: wrap; gap: 4px; justify-content: center; max-width: 100%; }
.dm-back { width: 16px; height: 30px; border-radius: 3px; background: repeating-linear-gradient(45deg, var(--lid) 0 4px, color-mix(in srgb, var(--lid) 55%, #fff) 4px 7px); border: 2px solid #fbf6e8; }
@media (prefers-reduced-motion: reduce) { .dm-tile { transition: none; } }
.tally { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.tc { display: grid; gap: 6px; align-content: start; justify-items: start; padding: 4px 0; }
.tc + .tc { border-left: 1px solid var(--edge); padding-left: 12px; }
.tc .th { font-size: 0.72rem; letter-spacing: 0.06em; text-transform: uppercase; color: var(--chalk-dim); font-weight: 800; }
.tc.you .th { color: var(--go); }
.tt { display: grid; gap: 2px; min-height: 22px; }
.tr { display: flex; flex-wrap: wrap; gap: 6px; }
.tr.nil { color: var(--chalk-faint); }
.tf { width: 54px; height: 54px; }
.tf path { fill: none; stroke: var(--chalk); stroke-width: 1.8; stroke-linecap: round; }
.tf path.big { stroke-width: 2.4; }
.tc .tg { font-weight: 800; font-size: 1.15rem; font-variant-numeric: tabular-nums; border-top: 2px solid var(--chalk-faint); padding-top: 4px; min-width: 3ch; }
.tc .tg.lead { color: var(--go); }
@media (max-width: 560px) { .dm-tile svg { width: 30px; height: 58px; } .dm-hand { gap: 6px; } }`;
document.head.append(style);

/* the scoresheet kept the paper way: every stroke is five. A figure starts
   with a big X across the middle (two strokes, ten), then a small X in each of
   the four blanks between its arms, top, right, bottom, left (two strokes
   each), so a whole figure is fifty; figures go side by side, the grand total
   under them */
let xs = remembered("dn-dominoes-xs");
const STROKES = [
  "M5 5 L55 55", "M55 5 L5 55", // the big X
  ...[[30, 12], [48, 30], [30, 48], [12, 30]].flatMap(([x, y]) => [`M${x - 4.5} ${y + 4.5} L${x + 4.5} ${y - 4.5}`, `M${x - 4.5} ${y - 4.5} L${x + 4.5} ${y + 4.5}`]),
];
const figure = (n) => `<svg viewBox="0 0 60 60" class="tf" aria-hidden="true">${STROKES.slice(0, n).map((d, i) => `<path d="${d}" class="${i < 2 ? "big" : ""}"/>`).join("")}</svg>`;
function tallyHTML(points) {
  const strokes = Math.floor(points / 5);
  if (!strokes) return '<div class="tr nil">—</div>';
  const out = [];
  for (let left = strokes; left > 0; left -= 10) out.push(figure(Math.min(10, left)));
  return `<div class="tr">${out.join("")}</div>`;
}
function tallySheet() {
  const lead = G.scores[0] === G.scores[1] ? -1 : G.scores[0] > G.scores[1] ? 0 : 1;
  const col = (i) => `<div class="tc ${i === ME ? "you" : ""}"><div class="th">${WHO[i]}</div><div class="tt" role="img" aria-label="${G.scores[i]} points">${tallyHTML(G.scores[i])}</div><div class="tg ${i === lead ? "lead" : ""}">${G.scores[i]}</div></div>`;
  document.getElementById("score").innerHTML = `<div class="tally">${col(NORTH)}${col(ME)}</div>`;
  document.getElementById("score-note").textContent = `Every stroke is five; a whole figure is fifty. First to ${TARGET}.`;
}
frame.setup({ seats: false, score: true, deck: true, scoreTitle: "Scoresheet", deckTitle: "The tiles", redraw: () => render() });
{
  const b = document.createElement("button");
  b.className = "toggle"; b.id = "t-xs"; b.title = "Keep the score in X's, a stroke for every five"; b.textContent = "X's";
  b.setAttribute("aria-pressed", xs);
  b.addEventListener("click", () => { xs = !xs; remember("dn-dominoes-xs", xs); b.setAttribute("aria-pressed", xs); render(); });
  document.getElementById("toggles").append(b);
}
newGame();
