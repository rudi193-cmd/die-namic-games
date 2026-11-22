"""screen.py: the GM's screen, built from a night at the table. Python 3.9+.

    python ui/screen.py build --table DIR/table.json --to FILE.html

The table is what box/table_scene.py wrote. FILE.html is one self-contained
page, no network and no install: open it in a browser. It reads nothing but
table.json, as willow's annex_os.py reads only scene.json: never a box, a key
or a pile, so nothing on it is anything a seat's box did not already write.

The page is the maintainer's own table (boxes/looks/my-table.md), drawn as
boxes/looks/mock.md draws it, in the dress of Die-Namic's table frame
(ui/tables/frame.src.html: the felt, the rail, the chalk):

- **Left, the quick ref.** The lookup, the bestiary, planned battles,
  upcoming loot, the house rules. Anything on the left is called to the
  centre; the story steps aside, and comes back.
- **Centre.** The binder's planned story, scene by scene, the beat played
  and the one up next; the dice box in the middle, showing the roll on the
  record (its faces, its rows) and the odds for the next beat; your call,
  GM: what waits on your seal.
- **Right, the players.** Each seat's character, what they carry, what was
  sent to them and whether it held, and their chain.
- **Along the bottom.** What is clipped in the screen (yours alone) and what
  is on the table (sent, and received).

The page decides nothing and rolls nothing: a roll not on the record did not
happen (the house rules), so its buttons say what to run, and where. The
lookup on the page is a toy matcher over what the page holds, keeping to the
words of the question as the kernel's rank does (half the question's content
words, or nothing); the real lookup is the binder's own box.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GM's screen</title>
<style>
:root {
  color-scheme: dark;
  --lid: #b8263f; --lid-ink: #fff0f2;
  --felt: color-mix(in srgb, var(--lid) 22%, #0d1513);
  --felt-2: color-mix(in srgb, var(--lid) 10%, #070b0a);
  --rail: color-mix(in srgb, var(--lid) 30%, #2a1a10);
  --board: #2b2118; --board-2: #1d160f; --board-edge: #4a3826;
  --chalk: #f4ecdc; --chalk-dim: #c6c0b2; --chalk-faint: #8d897e;
  --edge: #ffffff1c; --card: #fffaf0; --card-edge: #d8ccb4; --ink: #2a1f22;
  --go: #ffd34d; --go-ink: #3a2a00; --ok: #8fd18f; --wait: #f0b45a;
  --lid-font: "Bowlby One", "Arial Black", Impact, sans-serif;
  --ui: "Bricolage Grotesque", "Avenir Next", "Segoe UI", system-ui, sans-serif;
  --prose: "Literata", "Iowan Old Style", Georgia, serif;
  --mono: "JetBrains Mono", ui-monospace, "SF Mono", Menlo, monospace;
}
* { box-sizing: border-box; }
html, body { margin: 0; }
body { background: #0b1110; color: var(--chalk); font-family: var(--ui); font-size: 15px; line-height: 1.45; }
button { font: inherit; color: inherit; cursor: pointer; background: none; border: 0; padding: 0; text-align: left; }
:focus-visible { outline: 3px solid var(--go); outline-offset: 2px; }
.band { background: var(--lid); color: var(--lid-ink); }
.band-in { max-width: 1320px; margin: 0 auto; padding: 14px 16px 16px; display: flex; flex-wrap: wrap; gap: 6px 24px; align-items: end; justify-content: space-between; }
h1 { font-family: var(--lid-font); font-weight: 400; font-size: clamp(1.6rem, 4vw, 2.4rem); line-height: 1; margin: 2px 0 0; }
.kicker { font-weight: 800; font-size: 0.78rem; letter-spacing: 0.08em; text-transform: uppercase; opacity: 0.85; }
.line { font-family: var(--prose); margin: 4px 0 0; max-width: 64ch; opacity: 0.92; }
.demo { font-family: var(--mono); font-size: 0.72rem; padding: 4px 10px; border-radius: 999px; border: 1px solid color-mix(in srgb, var(--lid-ink) 50%, transparent); }
.wrap { max-width: 1320px; margin: 0 auto; padding: 18px 16px 40px; }

/* the screen: three panels standing on the felt */
.screen { display: grid; grid-template-columns: minmax(0, 0.95fr) minmax(0, 1.5fr) minmax(0, 0.95fr); gap: 10px; align-items: stretch; }
.leaf {
  background: linear-gradient(180deg, var(--board), var(--board-2));
  border: 2px solid var(--board-edge); border-radius: 10px;
  box-shadow: inset 0 1px 0 #ffffff14, 0 18px 30px -18px #000;
  padding: 14px; display: grid; gap: 14px; align-content: start; min-width: 0;
}
.leaf.centre { background: radial-gradient(120% 90% at 50% 40%, var(--felt), var(--felt-2)); border: 8px solid var(--rail); border-radius: 18px; box-shadow: inset 0 0 40px #0008, 0 18px 30px -18px #000; }
.leaf-name { font-family: var(--lid-font); font-weight: 400; font-size: 0.95rem; letter-spacing: 0.04em; color: var(--chalk-dim); margin: 0; display: flex; justify-content: space-between; gap: 8px; }
.leaf-name small { font-family: var(--mono); font-size: 0.68rem; color: var(--chalk-faint); align-self: center; }
@media (max-width: 980px) { .screen { grid-template-columns: minmax(0, 1fr); } .leaf.centre { order: -1; } }

h3 { margin: 0 0 6px; font-size: 0.74rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--chalk-faint); font-weight: 800; }
.list { display: grid; gap: 4px; }
.item { display: block; width: 100%; padding: 6px 8px; border-radius: 7px; border: 1px solid transparent; }
.item:hover { border-color: var(--edge); background: #ffffff08; }
.item b { font-weight: 700; }
.item .sub { display: block; font-size: 0.78rem; color: var(--chalk-dim); }
.gap { font-size: 0.8rem; color: var(--chalk-faint); font-style: italic; padding: 2px 8px; }
.cite { font-family: var(--mono); font-size: 0.7rem; color: var(--chalk-faint); }
.state { font-family: var(--mono); font-size: 0.68rem; padding: 1px 6px; border-radius: 4px; white-space: nowrap; }
.state.ok { color: var(--ok); border: 1px solid color-mix(in srgb, var(--ok) 40%, transparent); }
.state.wait { color: var(--wait); border: 1px solid color-mix(in srgb, var(--wait) 40%, transparent); }

/* the lookup */
.ask { display: flex; gap: 6px; }
.ask input { flex: 1; min-width: 0; font: inherit; color: var(--ink); background: var(--card); border: 2px solid var(--card-edge); border-radius: 8px; padding: 7px 10px; }
.ask button { background: var(--go); color: var(--go-ink); font-weight: 800; border-radius: 8px; padding: 0 12px; }

/* centre: the binder page, the dice box */
.page { background: var(--card); color: var(--ink); border-radius: 6px; padding: 14px 16px 12px 38px; position: relative; box-shadow: 0 6px 14px -8px #000; }
.page::before { content: ""; position: absolute; left: 9px; top: 10px; bottom: 10px; width: 14px; background: radial-gradient(circle, #0b1110 3px, #8d897e 3.5px, #8d897e 5px, transparent 5.5px) center / 14px 33.33% repeat-y; } /* the binder's three rings */
.page h2 { font-family: var(--prose); font-size: 1.25rem; margin: 0; }
.page .where { font-size: 0.78rem; color: #6b5d55; margin: 0 0 8px; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; }
.page p { font-family: var(--prose); margin: 0 0 6px; }
.beats { list-style: none; margin: 8px 0 0; padding: 0; display: grid; gap: 4px; }
.beats li { font-size: 0.88rem; padding: 4px 8px; border-radius: 6px; border-left: 3px solid #d8ccb4; }
.beats li.done { color: #6b5d55; text-decoration: line-through; text-decoration-color: #6b5d5588; }
.beats li.now { border-left-color: var(--lid); background: #b8263f12; font-weight: 700; }
.beats .tag { font-family: var(--mono); font-size: 0.7rem; color: #6b5d55; }
.back { font-weight: 800; font-size: 0.85rem; color: var(--go); }
.dicebox { justify-self: center; display: grid; gap: 8px; justify-items: center; padding: 14px 22px; border: 3px solid #0006; border-radius: 14px; background: #0003; box-shadow: inset 0 0 18px #0009; min-width: min(100%, 300px); }
.dice-row { display: flex; gap: 10px; align-items: center; }
.d6 { --s: 54px; width: var(--s); height: var(--s); border-radius: calc(var(--s) * 0.2); background: var(--card); box-shadow: inset 0 -3px 0 #d9ccb4, 0 4px 8px -4px #000c; display: grid; grid-template: repeat(3, 1fr) / repeat(3, 1fr); padding: calc(var(--s) * 0.16); }
.d6 b { width: calc(var(--s) * 0.17); height: calc(var(--s) * 0.17); border-radius: 50%; background: var(--ink); place-self: center; visibility: hidden; }
.d6 b.on { visibility: visible; }
.sum { font-family: var(--mono); font-size: 0.85rem; color: var(--chalk-dim); }
.band-word { font-family: var(--lid-font); font-size: 1.3rem; color: var(--go); line-height: 1; }
.told { font-family: var(--prose); text-align: center; max-width: 36ch; }
.odds { font-family: var(--mono); font-size: 0.72rem; color: var(--chalk-dim); white-space: pre; overflow-x: auto; max-width: 100%; }
.btns { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; }
.btn { border-radius: 9px; padding: 7px 14px; font-weight: 800; background: var(--go); color: var(--go-ink); }
.btn.ghost { background: transparent; color: var(--chalk); border: 2px solid var(--edge); }
.say { font-size: 0.8rem; color: var(--chalk-dim); text-align: center; min-height: 1.2em; max-width: 46ch; }
.say code, .call code { font-family: var(--mono); font-size: 0.72rem; color: var(--chalk); background: #0005; padding: 1px 4px; border-radius: 4px; overflow-wrap: anywhere; }
.call { border: 2px dashed var(--wait); border-radius: 10px; padding: 10px 12px; display: grid; gap: 6px; }
.call h3 { color: var(--wait); }
.call ul { margin: 0; padding-left: 18px; font-size: 0.88rem; }

/* right: the players */
.seat { background: #ffffff08; border: 1px solid var(--edge); border-radius: 10px; padding: 10px 12px; display: grid; gap: 4px; }
.seat .who { display: flex; justify-content: space-between; align-items: baseline; gap: 8px; }
.seat .who b { font-family: var(--lid-font); font-weight: 400; font-size: 1.05rem; }
.seat .role { font-size: 0.8rem; color: var(--chalk-dim); }
.stats { font-family: var(--mono); font-size: 0.82rem; }
.seat .row { font-size: 0.82rem; }

/* along the bottom */
.tray { margin-top: 12px; display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 10px; }
.tray > div { border: 1px solid var(--edge); border-radius: 10px; padding: 10px 12px; background: #ffffff06; }
.card { background: var(--card); color: var(--ink); border-radius: 6px; padding: 8px 10px; font-size: 0.86rem; margin-top: 6px; }
.card .cite { color: #6b5d55; }
.note { margin-top: 14px; font-size: 0.78rem; color: var(--chalk-faint); max-width: 90ch; }
</style>
</head>
<body>
<header class="band"><div class="band-in">
  <div>
    <div class="kicker">Die·Namic · the GM's screen</div>
    <h1 id="title"></h1>
    <p class="line" id="setting"></p>
  </div>
  <span class="demo" id="demo"></span>
</div></header>
<main class="wrap">
  <div class="screen">
    <section class="leaf" aria-label="Left panel: quick reference">
      <h2 class="leaf-name">QUICK REF <small>left</small></h2>
      <form class="ask" id="ask"><input id="q" placeholder="ask anything… (hound, draws)" aria-label="Ask the quick ref"><button>Ask</button></form>
      <div><h3>Bestiary</h3><div class="list" id="bestiary"></div></div>
      <div><h3>Planned battles</h3><div class="gap">none planned: no story here names its foes yet</div></div>
      <div><h3>Upcoming loot</h3><div class="gap">not built: nothing keeps loot not yet found</div></div>
      <div><h3>People</h3><div class="list" id="people"></div></div>
      <div><h3>House rules</h3><div class="list" id="rules"></div></div>
      <div><h3>Previously on…</h3><div class="list" id="previously"></div></div>
    </section>
    <section class="leaf centre" aria-label="Centre panel" id="centre"></section>
    <section class="leaf" aria-label="Right panel: the players">
      <h2 class="leaf-name">PLAYERS <small>right</small></h2>
      <div class="list" id="players"></div>
    </section>
  </div>
  <div class="tray">
    <div><h3>In the screen (yours alone)</h3><div id="screen-cards"></div></div>
    <div><h3>On the table (sent to everyone)</h3><div id="table-cards"></div></div>
  </div>
  <p class="note" id="note"></p>
</main>
<script id="table" type="application/json">/*__TABLE__*/</script>
<script>
"use strict";
const T = JSON.parse(document.getElementById("table").textContent);
const G = T.gm, W = T.world;
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const $ = (id) => document.getElementById(id);
const PIPS = { 1: [4], 2: [0, 8], 3: [0, 4, 8], 4: [0, 2, 6, 8], 5: [0, 2, 4, 6, 8], 6: [0, 2, 3, 5, 6, 8] };
const die = (n) => `<span class="d6" role="img" aria-label="${n}">${[...Array(9)].map((_, i) => `<b class="${PIPS[n].includes(i) ? "on" : ""}"></b>`).join("")}</span>`;
const chars = Object.fromEntries(T.seats.map((s) => [s.plays.toLowerCase(), s]));

$("title").textContent = W.title;
$("setting").textContent = W.setting;
$("demo").textContent = T.demo_keys ? "fictional seats · demo keys · " + T.made : T.made;

// everything the left can call to the centre, and the toy lookup over it
const refs = [];
const add = (kind, title, lines, where) => { refs.push({ kind, title, lines, where }); return refs.length - 1; };
const listInto = (id, items) => { $(id).innerHTML = items.join(""); };
listInto("bestiary", G.bestiary.map((m) => {
  const i = add("bestiary", m.title, m.lines, m.where);
  return `<button class="item" data-ref="${i}"><b>▸ ${esc(m.title)}</b><span class="sub">${esc(m.lines.find((l) => /Grit|Hits/.test(l)) || m.lines[0] || "")}</span></button>`;
}));
listInto("people", G.people.map((p) => {
  const i = add("person", p.title, p.lines, p.where);
  return `<button class="item" data-ref="${i}"><b>▸ ${esc(p.title)}</b></button>`;
}));
listInto("rules", G.house_rules.map((r) => {
  const i = add("house rule", r.title, [r.text], "house-rules.md");
  const st = r.state ? `<span class="state ${r.state.startsWith("sent") ? "ok" : "wait"}">${esc(r.state)}</span>` : "";
  return `<button class="item" data-ref="${i}"><b>${esc(r.title)}</b> ${st}</button>`;
}));
listInto("previously", G.previously.map((s) => {
  const i = add("session", s.title, s.lines, s.where);
  return `<button class="item" data-ref="${i}"><b>${esc(s.title)}</b><span class="sub">${esc(s.lines[0] || "")}</span></button>`;
}));

const STOP = new Set("a an the of to in on at is are was what who how does do it its and or for with stats".split(" "));
const words = (s) => s.toLowerCase().match(/[a-z0-9]+/g) || [];
function lookup(q) {
  const want = [...new Set(words(q).filter((w) => !STOP.has(w)))];
  if (!want.length) return [];
  return refs.map((r, i) => {
    const have = new Set(words(r.title + " " + r.lines.join(" ")));
    return { i, hit: want.filter((w) => have.has(w) || have.has(w + "s") || have.has(w.replace(/s$/, ""))).length };
  }).filter((x) => x.hit * 2 >= want.length).sort((a, b) => b.hit - a.hit).slice(0, 5);
}

// a card's lines, the ones that hold the asked words first, then the rest, four at most
function asked(lines, q) {
  const want = words(q).filter((w) => !STOP.has(w));
  const holds = (l) => want.some((w) => words(l).some((x) => x === w || x === w + "s" || x.replace(/s$/, "") === w));
  return [...lines.filter(holds), ...lines.filter((l) => !holds(l))].slice(0, 4);
}

// the centre: the binder's story, unless something was called to it
let called = null;
function centre() {
  const c = $("centre");
  if (called) {
    c.innerHTML = `<h2 class="leaf-name">CALLED TO THE CENTRE <small>${esc(called.kind)}</small></h2>
      <button class="back" id="back">◂ back to the scene</button>${called.html}`;
    $("back").onclick = () => { called = null; centre(); };
    return;
  }
  const done = new Set(G.done);
  let nowSet = false;
  const scenes = W.scenes.map((sc, n) => {
    const beats = sc.beats.map((b) => {
      let cls = done.has(b.id) ? "done" : "";
      if (!cls && !nowSet) { cls = "now"; nowSet = true; }
      const who = b.by ? b.by[0].toUpperCase() + b.by.slice(1) : "";
      return `<li class="${cls}">${cls === "now" ? "▶ " : ""}${esc(b.prompt || b.fact || b.id)} <span class="tag">${esc(b.kind)}${b.suggests ? " · " + esc(b.suggests) : ""}${who ? " · " + esc(who) : ""}</span></li>`;
    }).join("");
    return `<article class="page"><p class="where">Binder · scene ${n + 1} of ${W.scenes.length} · ${esc(W.places[sc.place] || sc.place)}</p>
      <h2>${esc(sc.title)}</h2>${(sc.opening || []).map((l) => `<p>${esc(l)}</p>`).join("")}<ol class="beats">${beats}</ol></article>`;
  });
  const d = G.dice;
  c.innerHTML = `<h2 class="leaf-name">THE BINDER · THE DICE BOX <small>centre</small></h2>
    ${scenes[0]}
    <div class="dicebox" aria-label="The dice box">
      <h3>The dice box · last roll on the record</h3>
      <div class="dice-row">${d.faces.map(die).join("")}</div>
      <div class="sum">${esc(chars[d.by] ? chars[d.by].plays : d.by)} · ${esc(d.stat)}: ${d.faces.join(" + ")} + ${d.bonus} = ${d.total}</div>
      <div class="band-word">${esc(d.band)}</div>
      <div class="told">${esc(d.text)}</div>
      <div class="cite">rows ${d.rows.join(", ")} on the GM's record</div>
      <h3 style="margin-top:6px">Up next: ${esc(G.next.beat)}</h3>
      <div class="odds">${G.next.odds.map(esc).join("\n")}</div>
      <div class="btns"><button class="btn" id="roll">Roll</button><button class="btn ghost" id="hidden">Roll hidden</button></div>
      <div class="say" id="say" aria-live="polite"></div>
    </div>
    <div class="call"><h3>✋ Your call, GM · ${G.your_call.length} waiting on your seal</h3>
      <ul>${G.your_call.map((r) => `<li>house rule: ${esc(r)}</li>`).join("")}</ul>
      <div class="say" style="text-align:left">Only the key's holder seals: <code>python kernel.py seal --box RECORD proposal:&lt;id&gt;</code></div></div>
    ${W.scenes.length > 1 ? `<details><summary class="cite">the rest of the binder (${W.scenes.length - 1} more scene${W.scenes.length > 2 ? "s" : ""})</summary>${scenes.slice(1).join("")}</details>` : ""}`;
  $("roll").onclick = () => { $("say").innerHTML = "A roll not on the record didn't happen, so the page rolls nothing. At the table: <code>python box/play.py</code>, or <code>game_master.py act " + esc((G.next.odds.find((o) => o.startsWith("*")) || "").replace(/^\*\s*/, "").split(/\s+/)[0] || "STAT") + "</code>."; };
  $("hidden").onclick = () => { $("say").innerHTML = "Not built: willow's <code>dice-tower</code> is, and <code>act --tower</code> takes it, but the play path doesn't reach it yet."; };
}
function call(i) {
  const r = refs[i];
  called = { kind: r.kind, html: `<article class="page"><p class="where">${esc(r.kind)}</p><h2>${esc(r.title)}</h2>${r.lines.map((l) => `<p>${esc(l)}</p>`).join("")}<p class="cite">${esc(r.where)}</p></article>` };
  centre();
}
document.addEventListener("click", (e) => { const b = e.target.closest("[data-ref]"); if (b) call(+b.dataset.ref); });
$("ask").onsubmit = (e) => {
  e.preventDefault();
  const q = $("q").value.trim();
  if (!q) return;
  const got = lookup(q);
  called = { kind: "the lookup", html: got.length
    ? `<p class="cite">asked: “${esc(q)}” · where to look, best first (a toy matcher over this page)</p>` + got.map((g) => { const r = refs[g.i]; return `<article class="page"><p class="where">${esc(r.kind)} · ${esc(r.where)}</p><h2>${esc(r.title)}</h2>${asked(r.lines, q).map((l) => `<p>${esc(l)}</p>`).join("")}</article>`; }).join("")
    : `<article class="page"><h2>Nothing on record</h2><p>Nothing on this screen holds half the words of “${esc(q)}”. The binder's own box is the real lookup.</p></article>` };
  centre();
};

// right: the players
$("players").innerHTML = T.seats.map((s) => {
  const st = Object.entries(s.stats).map(([k, v]) => `${k}+${v}`).join(" ");
  const rec = s.received.map((r) => `<div class="row">got: ${esc(r.what)} <span class="state ${r.verdict === "good" ? "ok" : "wait"}">${esc(r.verdict)}</span></div>`).join("");
  return `<div class="seat"><div class="who"><b>${esc(s.plays)}</b><span class="cite">${esc(s.name)}'s seat</span></div>
    <div class="role">${esc(s.role)}</div><div class="stats">${esc(st)}</div>
    <div class="row">carries: ${esc(s.carries.join(", "))}</div>${rec}
    <div class="cite">${esc(s.chain)}</div></div>`;
}).join("") + `<div class="gap">their sheets to the table: <code class="cite">open_table.py sheets</code></div>`;

// along the bottom
$("screen-cards").innerHTML = G.on_screen.map((c) => `<div class="card">${esc(c.what)}<div class="cite">${esc(c.cite)} · sealed</div></div>`).join("");
$("table-cards").innerHTML = G.on_table.map((c) => `<div class="card">${esc(c.what)}<div class="cite">sealed, and sent to ${c.sent.map((s) => esc(s.to) + " (" + esc(s.received) + ")").join(", ")}</div></div>`).join("");
$("note").textContent = (T.demo_keys
  ? "Every seat here is fictional and its key was made by the scene and thrown away with it: the seals stand in for a GM's yes, so a page can be seen crossing. "
  : "") + "Built from table.json alone: never a box, a key or a pile. The GM's record: " + G.chain + "; prep: " + G.prep;
centre();
</script>
</body>
</html>
"""


def build(table: Path, to: Path) -> None:
    doc = json.loads(table.read_text(encoding="utf-8"))
    data = json.dumps(doc, ensure_ascii=False).replace("</", "<\\/")
    to.write_text(PAGE.replace("/*__TABLE__*/", data, 1), encoding="utf-8")


def main(argv: list[str]) -> int:
    if (
        len(argv) != 5
        or argv[0] != "build"
        or argv[1] != "--table"
        or argv[3] != "--to"
    ):
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    table, to = Path(argv[2]), Path(argv[4])
    if not table.is_file():
        print(
            f"refused: no table at {table}; run box/table_scene.py first",
            file=sys.stderr,
        )
        return 2
    build(table, to)
    print(f"wrote {to}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
