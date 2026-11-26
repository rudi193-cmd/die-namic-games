/* Lantern Fair: build the night market on the river, you against North.
   Draw a tile, turn it, and set it against the fair so every edge it touches
   matches: canal to canal, lane to lane, square to square, quay to quay. Then
   you may set one piece on that tile, on a lane, canal or square nobody holds
   yet: a lantern (seven each), your boat (on a canal) or your lamplighter (on
   a lane). Whoever has the most pieces on a lane, canal or square when it
   closes scores it (both, when tied), and the pieces come home.
     a lane    1 a tile, 2 a lit stall, 4 a dark one; its stalls' goods too
     a canal   1 a tile, 2 a bridge over it; double for the boat's owner
     a square  1 a tile, 3 a lane that opens onto it
   The lamplighter lights each dark stall on its lane, 2 points apiece as it
   does. Three moons are in the deck: when one comes up, night falls, and every
   lit stall on a lane you hold pays you 1. When the tiles run out, what is
   still open scores 1 a tile (a square 1 a lane), and each set of all four
   goods (spice, silk, sweets, masks) scores 10. A page of its own: nothing here
   is kept. */
const NORTH = 0, ME = 1, WHO = ["North", "You"];
const LANTERNS = 7, SET = 10, MOONS = 3;


/* ── the deal ── */
let G, chosenSpot = null, pieceKind = "lantern", board = null;

function newGame() {
  const goods = shuffle(GOODS.flatMap((g) => [g, g, g, g]));
  const deck = shuffle([...TILES.flatMap((t) => Array(t.n).fill(t.id)), ...Array(MOONS).fill("moon")])
    .map((id) => (id === "moon" ? { id } : { id, goods: stallsOf(id).map(() => goods.pop()) }));
  G = { board: new Map(), deck, scores: [0, 0], left: [LANTERNS, LANTERNS], boat: [true, true], lamp: [true, true],
        pieces: new Map(), done: new Set(), rows: [], goods: [{}, {}], turn: rnd(2), phase: "place", held: null,
        rot: 0, last: null, over: false, flash: "" };
  G.board.set(key(0, 0), { x: 0, y: 0, id: "start", rot: 0, stalls: stallsOf("start").map((s) => ({ ...s, good: goods.pop() })) });
  frame.clearLog();
  frame.log(`<b>The fair opens.</b> One bridge over the canal, one stall lit. ${WHO[G.turn]} ${G.turn === ME ? "go" : "goes"} first.`);
  if (board) board.view = null;
  chosenSpot = null; pieceKind = "lantern";
  nextTurn(true);
}

function fits(x, y, id, rot) {
  if (G.board.has(key(x, y))) return false;
  let touches = false;
  for (let d = 0; d < 4; d++) {
    const nb = G.board.get(key(x + DIRS[d][0], y + DIRS[d][1]));
    if (!nb) continue;
    touches = true;
    if (edgeOf(id, rot, d) !== edgeOf(nb.id, nb.rot, (d + 2) % 4)) return false;
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

/* the lanes, canals and squares as they stand: every segment of every tile,
   joined across the edges where tiles meet; one is closed when no edge of it
   is open */
function features(pieces = G.pieces) {
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
    if (!groups.has(r)) groups.set(r, { nodes: [], kind: null, tiles: new Set(), open: 0, lit: 0, dark: 0, bridges: 0, mouths: 0, goods: [], held: [0, 0], boat: null, lamp: null });
    const f = groups.get(r), [tk, si] = node.split(":"), t = G.board.get(tk), s = T[t.id].segs[+si];
    f.nodes.push(node); f.kind = s.k; f.tiles.add(tk); f.open += open.get(node) || 0;
    for (const st of t.stalls) if (st.seg === +si) { st.lit ? f.lit++ : f.dark++; f.goods.push(st.good); }
    if (s.k === "C" && T[t.id].bridge) f.bridges++;
    if (s.k === "P") f.mouths += T[t.id].segs.filter((g) => g.end === "square").length;
    const p = pieces.get(node);
    if (p) { f.held[p.who]++; if (p.kind === "boat") f.boat = p.who; if (p.kind === "lamp") f.lamp = p.who; }
  }
  return [...groups.values()];
}
const fid = (f) => f.nodes.slice().sort()[0];
function worth(f, closed) {
  if (!closed) return f.kind === "P" ? f.mouths : f.tiles.size;
  if (f.kind === "L") return f.tiles.size + 2 * f.lit + 4 * f.dark;
  if (f.kind === "C") return f.tiles.size + 2 * f.bridges;
  return f.tiles.size + 3 * f.mouths;
}
const winners = (f) => { const [a, b] = f.held; return a + b === 0 ? [] : a === b ? [0, 1] : [a > b ? 0 : 1]; };
const featSaid = (f) => {
  const n = f.tiles.size, bits = [];
  if (f.kind === "L" && f.lit + f.dark) bits.push(`${f.lit + f.dark} stall${f.lit + f.dark > 1 ? "s" : ""}${f.dark ? ` (${f.dark} dark)` : ""}`);
  if (f.kind === "C" && f.bridges) bits.push(`${f.bridges} bridge${f.bridges > 1 ? "s" : ""}`);
  if (f.kind === "P") bits.push(`${f.mouths} lane${f.mouths === 1 ? "" : "s"} onto it`);
  return `${KIND_NAME[f.kind]} of ${n} tile${n > 1 ? "s" : ""}${bits.length ? `, ${bits.join(", ")}` : ""}`;
};
const verb = (who, v) => (who.length === 1 && who[0] !== ME ? v + "s" : v);
const names = (who) => who.map((w) => WHO[w]).join(" and ");
function bring(f) {
  for (const n of f.nodes) {
    const p = G.pieces.get(n);
    if (!p) continue;
    if (p.kind === "lantern") G.left[p.who]++; else if (p.kind === "boat") G.boat[p.who] = true; else G.lamp[p.who] = true;
    G.pieces.delete(n);
  }
}

/* the lamplighter walks its lane: every dark stall on it is lit, 2 apiece */
function lampWalk() {
  for (const [node, p] of G.pieces) {
    if (p.kind !== "lamp") continue;
    const f = features().find((g) => g.nodes.includes(node));
    let lit = 0;
    for (const n of f.nodes) { const [tk, si] = n.split(":"); for (const st of G.board.get(tk).stalls) if (st.seg === +si && !st.lit) { st.lit = true; lit++; } }
    if (lit) {
      G.scores[p.who] += 2 * lit;
      G.rows.push({ label: "lamplighter", cells: [0, 1].map((i) => (i === p.who ? `+${2 * lit}` : "")) });
      frame.log(`${WHO[p.who]}'s lamplighter lights ${lit} dark stall${lit > 1 ? "s" : ""}: <b>${2 * lit}</b>.`);
      G.flash = `<b>${WHO[p.who]}'s lamplighter lights ${lit === 1 ? "a stall" : `${lit} stalls`}.</b>`;
    }
  }
}

/* what closes now scores, and its pieces come home */
function settle(final = false) {
  for (const f of features()) {
    const id = fid(f);
    if (G.done.has(id)) continue;
    const closed = f.open === 0;
    if (!closed && !final) continue;
    G.done.add(id);
    const who = winners(f);
    if (!who.length) continue;
    const pts = worth(f, closed);
    if (!pts) { bring(f); continue; }
    for (const w of who) G.scores[w] += pts;
    const boat = closed && f.kind === "C" && f.boat !== null && who.includes(f.boat);
    if (boat) G.scores[f.boat] += pts;
    if (closed && f.kind === "L") for (const w of who) for (const g of f.goods) G.goods[w][g] = (G.goods[w][g] || 0) + 1;
    bring(f);
    G.rows.push({ label: `${closed ? "" : "open "}${KIND_NAME[f.kind]} ${f.tiles.size}${boat ? " ⛵" : ""}`, cells: [0, 1].map((i) => (who.includes(i) ? `+${pts * (boat && f.boat === i ? 2 : 1)}` : "")) });
    const goods = closed && f.kind === "L" && f.goods.length ? `, and the ${f.goods.join(", ")}` : "";
    frame.log(`${closed ? "Closed" : "Still open"}: a ${featSaid(f)}. <b>${names(who)} ${verb(who, "score")} ${pts}</b>${boat ? `, doubled by ${WHO[f.boat]}'s boat` : ""}${goods}.`);
    if (!final) G.flash = `<b>${names(who)} ${verb(who, "score")} ${pts * (boat ? 2 : 1)}</b> for the ${KIND_NAME[f.kind]}${goods ? " and its goods" : ""}.`;
  }
}

/* night falls: every lit stall on a lane you hold pays 1 */
function nightFalls() {
  const pay = [0, 0];
  for (const f of features()) {
    if (f.kind !== "L" || G.done.has(fid(f))) continue;
    for (const w of winners(f)) pay[w] += f.lit;
  }
  for (const w of [0, 1]) G.scores[w] += pay[w];
  G.rows.push({ label: "night falls", cells: pay.map((v) => (v ? `+${v}` : "")) });
  frame.log(`<b>Night falls.</b> The lit stalls pay: North ${pay[NORTH]}, you ${pay[ME]}.`);
  G.flash = `<b>Night falls:</b> you ${pay[ME]}, North ${pay[NORTH]}.`;
}

function nextTurn(first = false) {
  if (!first) G.turn = 1 - G.turn;
  while (G.deck.length) {
    const card = G.deck.pop();
    if (card.id === "moon") { nightFalls(); continue; }
    if (placements(card.id).length) { G.held = card; G.rot = 0; G.phase = "place"; chosenSpot = null; pieceKind = "lantern"; render(); if (G.turn === NORTH) northTurn(); return; }
    frame.log(`A ${tileName(card.id)} tile fits nowhere, and is set aside.`);
  }
  settle(true);
  const sets = G.goods.map((g) => Math.min(...GOODS.map((k) => g[k] || 0)));
  for (const w of [0, 1]) G.scores[w] += SET * sets[w];
  if (sets[0] + sets[1]) {
    G.rows.push({ label: "sets of goods", cells: sets.map((n) => (n ? `+${SET * n}` : "")) });
    frame.log(`Sets of all four goods: North ${sets[NORTH]}, you ${sets[ME]}, ${SET} each.`);
  }
  G.over = true; G.phase = "over"; G.held = null;
  frame.log(`<b>The fair is built.</b> ${G.scores[ME] === G.scores[NORTH] ? "A tie" : G.scores[ME] > G.scores[NORTH] ? "You win" : "North wins"}, ${Math.max(...G.scores)} to ${Math.min(...G.scores)}.`);
  render();
}

function put(seat, x, y, rot) {
  const card = G.held;
  G.board.set(key(x, y), { x, y, id: card.id, rot, stalls: stallsOf(card.id).map((s, i) => ({ ...s, good: card.goods[i] })) });
  G.last = key(x, y);
  frame.log(`${WHO[seat]} set${seat === ME ? "" : "s"} a ${tileName(card.id)} tile.`);
  G.held = null;
  lampWalk();
}
/* the segments of the tile just set a piece of this kind may go on */
function settable(k, kind, seat = G.turn) {
  if (kind === "lantern" && !G.left[seat]) return [];
  if (kind === "boat" && !G.boat[seat]) return [];
  if (kind === "lamp" && !G.lamp[seat]) return [];
  const t = G.board.get(k), fs = features();
  return T[t.id].segs.map((s, i) => [s, `${k}:${i}`]).filter(([s, n]) => {
    if (kind === "boat" && s.k !== "C") return false;
    if (kind === "lamp" && s.k !== "L") return false;
    const f = fs.find((g) => g.nodes.includes(n));
    return f.held[0] + f.held[1] === 0 && !G.done.has(fid(f));
  }).map(([, n]) => n);
}
function setPiece(seat, node, kind) {
  if (node) {
    G.pieces.set(node, { who: seat, kind });
    if (kind === "lantern") G.left[seat]--; else if (kind === "boat") G.boat[seat] = false; else G.lamp[seat] = false;
    frame.log(`${WHO[seat]} ${kind === "lantern" ? `hang${seat === ME ? "" : "s"} a lantern` : kind === "boat" ? `launch${seat === ME ? "" : "es"} the boat` : `send${seat === ME ? "" : "s"} out the lamplighter`}.`);
    if (kind === "lamp") lampWalk();
  }
  settle();
  nextTurn();
}

/* ── North: tries every place and turn, and every piece, and takes the best ── */
function judge(id, x, y, r, node, kind) {
  const k = key(x, y);
  const pieces = new Map(G.pieces);
  if (node) pieces.set(node, { who: NORTH, kind });
  const fs = features(pieces);
  let s = 0;
  for (const f of fs) {
    if (![...f.tiles].includes(k) || G.done.has(fid(f))) continue;
    const w = winners(f), closed = f.open === 0;
    let v = worth(f, closed);
    if (!closed) v = f.kind === "P" ? 1 + f.tiles.size + 3 * f.mouths : f.kind === "L" ? f.tiles.size + 2 * f.lit + 4 * f.dark : f.tiles.size + 2 * f.bridges;
    const boatN = f.boat === NORTH ? 2 : 1, boatY = f.boat === ME ? 2 : 1;
    const odds = closed ? 1 : 0.55 / (1 + 0.3 * f.open);
    if (w.includes(NORTH)) s += v * boatN * odds;
    if (w.includes(ME)) s -= v * boatY * odds * 0.9;
    if (f.kind === "L" && f.lamp !== null && f.dark) s += (f.lamp === NORTH ? 2 : -2) * f.dark;
    if (closed && f.kind === "L" && w.includes(NORTH)) s += 1.5 * f.goods.length;
  }
  if (node) s -= kind === "lantern" ? (G.left[NORTH] <= 2 ? 2.5 : 0.8) : 2;
  return s;
}
async function northTurn() {
  render(); await wait(650);
  const id = G.held.id;
  let best = null;
  for (const [x, y, r] of placements(id)) {
    const k = key(x, y);
    G.board.set(k, { x, y, id, rot: r, stalls: stallsOf(id).map((s, i) => ({ ...s, good: G.held.goods[i] })) });
    const options = [[null, null]];
    for (const kind of ["lantern", "boat", "lamp"]) for (const n of settable(k, kind, NORTH)) options.push([n, kind]);
    for (const [n, kind] of options) {
      const s = judge(id, x, y, r, n, kind) + rnd(100) / 1000;
      if (!best || s > best.s) best = { x, y, r, n, kind, s };
    }
    G.board.delete(k);
  }
  put(NORTH, best.x, best.y, best.r);
  render(); await wait(450);
  setPiece(NORTH, best.n, best.kind);
}

/* ── you ── */
function tapBoard(bx, by) {
  if (G.phase === "piece" && G.turn === ME) {
    const t = G.board.get(G.last);
    for (const node of settable(G.last, pieceKind)) {
      const [px, py] = onBoard(t, ...anchor(T[t.id].segs[+node.split(":")[1]]));
      if (Math.hypot(px - bx, py - by) < 30) return tapPiece(node);
    }
    return;
  }
  tapCell(Math.floor(bx / 100), Math.floor(by / 100));
}
function tapCell(x, y) {
  if (G.turn !== ME || G.over || G.phase !== "place") return;
  if (G.board.has(key(x, y)) || !frontier().some(([a, b]) => a === x && b === y)) return;
  chosenSpot = [x, y];
  if (frame.hints && !fits(x, y, G.held.id, G.rot)) { for (let r = 1; r < 4; r++) if (fits(x, y, G.held.id, (G.rot + r) % 4)) { G.rot = (G.rot + r) % 4; break; } }
  render();
}
function turnTile() {
  if (G.turn !== ME || G.phase !== "place") return;
  G.rot = (G.rot + 1) % 4;
  if (frame.hints && chosenSpot && placements(G.held.id).some(([x, y]) => x === chosenSpot[0] && y === chosenSpot[1])) {
    for (let i = 0; i < 4 && !fits(chosenSpot[0], chosenSpot[1], G.held.id, G.rot); i++) G.rot = (G.rot + 1) % 4;
  }
  render();
}
function placeIt() {
  if (!chosenSpot) return frame.refuse("tap a spot beside the fair first");
  const [x, y] = chosenSpot;
  if (!fits(x, y, G.held.id, G.rot)) return frame.refuse("every edge it touches has to match: canal to canal, lane to lane, square to square, quay to quay");
  G.flash = "";
  put(ME, x, y, G.rot);
  chosenSpot = null;
  const any = ["lantern", "boat", "lamp"].filter((k) => settable(G.last, k).length);
  if (any.length) { pieceKind = any[0]; G.phase = "piece"; render(); }
  else setPiece(ME, null);
}
function tapPiece(node) {
  if (G.phase === "piece" && G.turn === ME && settable(G.last, pieceKind).includes(node)) { G.phase = "place"; setPiece(ME, node, pieceKind); }
}

/* ── the picture ── */
function pieceSVG(kind, who, ax, ay) {
  const c = who === ME ? COL.you : COL.north;
  if (kind === "boat") return `<g transform="translate(${ax} ${ay})"><path d="M-15 0 h30 l-6 8 h-18 z" fill="${c}" stroke="#15131f" stroke-width="2"/><path d="M0 -16 V0 M0 -15 l10 10 h-10" fill="${c}" stroke="#15131f" stroke-width="2"/></g>`;
  if (kind === "lamp") return `<g transform="translate(${ax} ${ay})"><circle cx="9" cy="-15" r="7" fill="${c}" opacity="0.45" filter="url(#lit)"/><path d="M6 -14 V10" stroke="#15131f" stroke-width="3"/><circle cx="9" cy="-15" r="3.5" fill="#fff2b0"/><circle cx="-3" cy="-8" r="5" fill="${c}" stroke="#15131f" stroke-width="2"/><path d="M-10 10 Q-3 -6 4 10 z" fill="${c}" stroke="#15131f" stroke-width="2"/></g>`;
  return `<circle cx="${ax}" cy="${ay}" r="15" fill="${c}" opacity="0.4" filter="url(#lit)"/><circle cx="${ax}" cy="${ay}" r="9" fill="${c}" stroke="#15131f" stroke-width="2"/>`;
}

function boardSVG() {
  const mine = G.turn === ME && !G.over;
  let s = FAIR_DEFS;
  if (mine && G.phase === "place") {
    const ok = frame.hints ? new Set(placements(G.held.id).map(([x, y]) => key(x, y))) : null;
    for (const [x, y] of frontier()) if (!ok || ok.has(key(x, y))) s += `<rect x="${x * 100 + 4}" y="${y * 100 + 4}" width="92" height="92" rx="8" class="lf-spot"/>`;
  }
  for (const t of G.board.values()) s += tileG(t.x, t.y, t.id, t.rot, t.stalls);
  if (G.last) { const [x, y] = G.last.split(",").map(Number); s += `<rect x="${x * 100 + 1.5}" y="${y * 100 + 1.5}" width="97" height="97" class="lf-last"/>`; }
  for (const [node, p] of G.pieces) {
    const [k, i] = node.split(":"), t = G.board.get(k), [ax, ay] = anchor(T[t.id].segs[+i]);
    s += onTile(t, pieceSVG(p.kind, p.who, ax, ay));
  }
  if (mine && G.phase === "place" && chosenSpot) {
    const [x, y] = chosenSpot, ok = fits(x, y, G.held.id, G.rot);
    s += tileG(x, y, G.held.id, G.rot, stallsOf(G.held.id).map((st, i) => ({ ...st, good: G.held.goods[i] })), `opacity="0.92"`);
    for (let d = 0; d < 4; d++) {
      const nb = G.board.get(key(x + DIRS[d][0], y + DIRS[d][1]));
      if (nb && edgeOf(G.held.id, G.rot, d) !== edgeOf(nb.id, nb.rot, (d + 2) % 4)) {
        const [mx, my] = MID[d];
        s += `<line x1="${x * 100 + (d % 2 ? mx : 8)}" y1="${y * 100 + (d % 2 ? 8 : my)}" x2="${x * 100 + (d % 2 ? mx : 92)}" y2="${y * 100 + (d % 2 ? 92 : my)}" class="lf-bad"/>`;
      }
    }
    s += `<rect x="${x * 100 + 1.5}" y="${y * 100 + 1.5}" width="97" height="97" class="lf-held ${ok ? "ok" : "no"}"/>`;
  }
  if (mine && G.phase === "piece") {
    const t = G.board.get(G.last);
    for (const node of settable(G.last, pieceKind)) {
      const [ax, ay] = anchor(T[t.id].segs[+node.split(":")[1]]);
      s += onTile(t, `<circle cx="${ax}" cy="${ay}" r="18" class="lf-hang"/>`);
    }
  }
  return s;
}

const goodsHTML = (g) => GOODS.map((k) => `<span class="lf-good" style="--c:${GOOD_COL[k]}" title="${k}">${g[k] || 0}</span>`).join("");
function render() {
  const mine = G.turn === ME && !G.over;
  const lamps = (who) => `<span class="lf-lamps ${who === ME ? "you" : "north"}" aria-label="${G.left[who]} lanterns">${"●".repeat(G.left[who])}<i>${"●".repeat(LANTERNS - G.left[who])}</i></span><span class="lf-tok ${G.boat[who] ? "" : "out"}" title="boat">⛵</span><span class="lf-tok ${G.lamp[who] ? "" : "out"}" title="lamplighter">🏮</span>`;
  const top = `<div class="lf-row"><b class="lf-you">You ${G.scores[ME]}</b>${lamps(ME)}<span class="lf-goods">${goodsHTML(G.goods[ME])}</span></div><div class="lf-row"><b class="lf-north">North ${G.scores[NORTH]}</b>${lamps(NORTH)}<span class="lf-goods">${goodsHTML(G.goods[NORTH])}</span></div>`;
  if (!document.getElementById("lf-wrap")) {
    frame.stage(`<div class="lf"><div class="lf-top"></div><div class="lf-wrap fb-wrap" id="lf-wrap"><svg id="lf-svg" class="fb-svg"></svg></div><div class="lf-bottom" id="lf-bottom"></div></div>`);
    board = new FairBoard(document.getElementById("lf-svg"), document.getElementById("lf-wrap"), tapBoard);
  }
  document.querySelector(".lf-top").innerHTML = top;
  if (!board.view) board.fit(G.board.values());
  board.lastTiles = [...G.board.values()];
  if (G.last) { const [lx, ly] = G.last.split(",").map(Number); board.keep(lx, ly); }
  board.apply();
  document.getElementById("lf-svg").innerHTML = boardSVG();
  const left = `<div class="lf-deck">${G.deck.length} left in the deck</div>`;
  let bottom = "";
  if (G.over) bottom = `${left}<button class="btn" id="lf-new">New fair</button>`;
  else if (!mine) bottom = `${left}<div class="lf-wait">North is building…</div>`;
  else if (G.phase === "piece") {
    const kinds = [["lantern", `Lantern · ${G.left[ME]}`], ["boat", "Boat"], ["lamp", "Lamplighter"]];
    bottom = `<div class="lf-pick" role="group" aria-label="which piece">${kinds.map(([k, l]) => `<button class="lf-kind ${pieceKind === k ? "on" : ""}" data-kind="${k}" ${settable(G.last, k).length ? "" : "disabled"} aria-pressed="${pieceKind === k}">${l}</button>`).join("")}</div><div class="lf-acts"><div class="lf-ask">Tap a ring on the tile.</div><button class="btn ghost" id="lf-none">Nothing</button></div>`;
  } else {
    const st = stallsOf(G.held.id).map((x, i) => ({ ...x, good: G.held.goods[i] }));
    bottom = `<button class="lf-hand" id="lf-turn" aria-label="the tile in hand: tap to turn it"><svg viewBox="0 0 100 100" width="84" height="84">${tileG(0, 0, G.held.id, G.rot, st)}</svg><span>tap to turn</span></button><div class="lf-acts">${left}<button class="btn" id="lf-place" ${chosenSpot ? "" : "disabled"}>Place</button></div>`;
  }
  document.getElementById("lf-bottom").innerHTML = bottom;
  const on = (id, f) => { const b = document.getElementById(id); if (b) b.onclick = f; };
  on("lf-new", newGame); on("lf-none", () => { if (G.phase === "piece") { G.phase = "place"; setPiece(ME, null); } }); on("lf-place", placeIt); on("lf-turn", turnTile);
  document.querySelectorAll(".lf-kind").forEach((b) => (b.onclick = () => { pieceKind = b.dataset.kind; render(); }));
  frame.status(G.over ? `<b>${G.scores[ME] === G.scores[NORTH] ? "A tie" : G.scores[ME] > G.scores[NORTH] ? "You win" : "North wins"}</b>, ${Math.max(...G.scores)} to ${Math.min(...G.scores)}.`
    : (G.flash ? G.flash + " " : "") + (!mine ? "" : G.phase === "piece" ? "Set a piece?" : chosenSpot ? "Turn it till it fits, then <b>Place</b>." : "<b>Your tile.</b> Tap a spot beside the fair."));
  frame.score({ cols: ["North", "You"], rows: G.rows, totals: G.scores, lead: G.scores[0] === G.scores[1] ? [] : [G.scores[0] > G.scores[1] ? 0 : 1], head: "Scored", you: ME, empty: "Nothing scored yet", note: "" });
  frame.deck([["Left in the deck", String(G.deck.length)], ["Moons still to come", String(G.deck.filter((c) => c.id === "moon").length)], ["On the fair", String(G.board.size)]], "");
}

const style = document.createElement("style");
style.textContent = `
.lf { display: grid; gap: 10px; width: 100%; min-width: 0; }
.lf-top { display: grid; gap: 4px; }
.lf-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; font-size: 0.85rem; }
.lf-row b { min-width: 6.5em; font-size: 0.95rem; }
.lf-you { color: ${COL.you}; } .lf-north { color: ${COL.north}; }
.lf-lamps { font-size: 0.62rem; letter-spacing: 1px; } .lf-lamps i { font-style: normal; opacity: 0.2; }
.lf-lamps.you { color: ${COL.you}; } .lf-lamps.north { color: ${COL.north}; }
.lf-tok { font-size: 0.95rem; } .lf-tok.out { opacity: 0.2; filter: grayscale(1); }
.lf-goods { display: inline-flex; gap: 4px; margin-left: auto; }
.lf-good { min-width: 22px; text-align: center; border-radius: 6px; padding: 1px 4px; font: 700 0.75rem var(--mono); background: color-mix(in srgb, var(--c) 30%, transparent); border: 1px solid var(--c); }
.lf-wrap { height: min(60vh, 560px); min-height: 300px; }
.lf-spot { fill: #ffffff08; stroke: #ffffff40; stroke-width: 2; stroke-dasharray: 8 6; }
.lf-last { fill: none; stroke: #ffffff70; stroke-width: 3; }
.lf-held { fill: none; stroke-width: 4; } .lf-held.ok { stroke: var(--go); } .lf-held.no { stroke: #ff7a66; stroke-dasharray: 10 6; }
.lf-bad { stroke: #ff5a45; stroke-width: 7; stroke-linecap: round; }
.lf-hang { fill: #ffcf5a33; stroke: var(--go); stroke-width: 3; stroke-dasharray: 5 4; }
.lf-bottom { display: flex; gap: 12px; align-items: center; justify-content: center; flex-wrap: wrap; min-height: 104px; }
.lf-hand { display: grid; justify-items: center; gap: 2px; padding: 6px; border-radius: 12px; border: 2px solid var(--go); background: #0006; }
.lf-hand svg { display: block; border-radius: 6px; }
.lf-hand span { font-size: 0.7rem; color: var(--chalk-dim); }
.lf-acts { display: grid; gap: 8px; justify-items: center; }
.lf-acts .btn { min-width: 120px; min-height: 48px; font-size: 1.05rem; }
.lf-pick { display: flex; gap: 6px; flex-wrap: wrap; justify-content: center; }
.lf-kind { padding: 10px 14px; min-height: 44px; border-radius: 10px; border: 2px solid var(--edge); font-weight: 800; }
.lf-kind.on { border-color: var(--go); color: var(--go); }
.lf-kind:disabled { opacity: 0.3; }
.lf-deck { font-family: var(--mono); font-size: 0.75rem; color: var(--chalk-dim); }
.lf-ask, .lf-wait { font-weight: 700; }
.lf-bottom .btn { min-height: 44px; }
.lf-rules { margin: 0; padding-left: 18px; display: grid; gap: 4px; font-size: 0.85rem; color: var(--chalk-dim); }
.lf-rules b { color: var(--chalk); }`;
document.head.append(style);

frame.setup({ seats: false, score: true, deck: true, scoreTitle: "Scoresheet", deckTitle: "The fair", redraw: () => render() });
document.getElementById("p-record").hidden = true;
frame.panel("rules", "How the fair scores", `<ul class="lf-rules">
  <li><b>A lane</b> closed: 1 a tile, 2 a lit stall, 4 a dark one, and its stalls' goods.</li>
  <li><b>A canal</b> closed: 1 a tile, 2 a bridge; double for the boat's owner.</li>
  <li><b>A square</b> closed: 1 a tile, 3 for each lane that opens onto it.</li>
  <li><b>The lamplighter</b> lights each dark stall on its lane: 2 apiece.</li>
  <li><b>Night falls</b> (three moons): each lit stall on a lane you hold pays 1.</li>
  <li><b>At the end</b> what is open scores 1 a tile (a square 1 a lane), and each set of all four goods 10.</li>
  <li>The most pieces on a lane, canal or square takes it; tied, both do.</li></ul>`);
newGame();
