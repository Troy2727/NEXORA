// Shared builder for the README diagrams. Each function draws one diagram into a composition root
// and returns its GSAP timeline: boxes appear first, then each wire draws with a glowing dot
// leading it, each label glows in as its wire lands, and the caption comes in last.
window.NexoraDiagram =
  window.NexoraDiagram ||
  (function () {
    const SVG_NS = "http://www.w3.org/2000/svg";
    const ORANGE = "#ff8a1f";
    const YELLOW = "#ffd54a";
    const GREEN = "#34c759";
    const GRAY = "#d4d4d8";
    const GLOW_ON = "drop-shadow(0 0 10px rgba(255, 138, 31, 0.95))";
    const GLOW_OFF = "drop-shadow(0 0 0px rgba(255, 138, 31, 0))";
    let diagramCount = 0;

    function el(tag, attrs, parent, text) {
      const node = document.createElementNS(SVG_NS, tag);
      for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
      if (text) node.textContent = text;
      parent.appendChild(node);
      return node;
    }

    function html(parent, className, style, inner) {
      const div = document.createElement("div");
      div.className = className;
      Object.assign(div.style, style);
      div.innerHTML = inner;
      parent.appendChild(div);
      return div;
    }

    // Same mark as web/assets/logo.svg; the gradient id is per diagram because index.html inlines both.
    const logo = (id) => `<svg viewBox="0 0 32 32" fill="none"><defs>
      <linearGradient id="${id}-logo" x1="4" y1="2" x2="28" y2="30" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#FFD54A"/><stop offset="0.55" stop-color="#FFB81C"/><stop offset="1" stop-color="#E88A00"/>
      </linearGradient></defs>
      <path d="M3.88 23V9L16 2L19 3.73V22.5L23.12 20.12V6.11L28.12 9V23L16 30L13 28.27V9.5L8.88 11.88V25.89Z" fill="url(#${id}-logo)"/></svg>`;

    /** Background, logo + title, optional caption, footer, and the SVG layer wires are drawn on. */
    function frame(root, title, caption) {
      // Not the root's DOM id: index.html inlines the compositions and their roots lose it,
      // but SVG mask/marker ids must stay unique across both diagrams.
      const id = `diagram${++diagramCount}`;
      root.classList.add("scene");
      const header = html(root, "header", {}, `${logo(id)}<h1>${title}</h1>`);
      const footer = html(root, "footer", {}, "nexora-five-dun.vercel.app");
      const svg = el("svg", { class: "wires", viewBox: "0 0 1600 1150" }, root);
      const defs = el("defs", {}, svg);
      const glow = el("filter", { id: `${id}-glow`, x: "-200%", y: "-200%", width: "500%", height: "500%" }, defs);
      el("feGaussianBlur", { stdDeviation: "5", result: "blur" }, glow);
      const merge = el("feMerge", {}, glow);
      el("feMergeNode", { in: "blur" }, merge);
      el("feMergeNode", { in: "SourceGraphic" }, merge);
      // Caption is created last so it sits above the wires.
      const cap = caption ? html(root, "caption", {}, caption) : null;
      const tl = gsap.timeline({ paused: true });
      tl.fromTo([header, footer], { opacity: 0, y: -12 }, { opacity: 1, y: 0, duration: 0.6, ease: "power2.out" }, 0);
      return { id, root, svg, defs, cap, tl, wires: 0, heads: {} };
    }

    /** One arrowhead marker per wire color. */
    function head(f, color) {
      if (!f.heads[color]) {
        const id = `${f.id}-head${Object.keys(f.heads).length}`;
        const marker = el(
          "marker",
          { id, viewBox: "0 0 10 10", refX: "9", refY: "5", markerWidth: "8", markerHeight: "8", orient: "auto-start-reverse" },
          f.defs
        );
        el("path", { d: "M0 0 L10 5 L0 10 z", fill: color }, marker);
        f.heads[color] = id;
      }
      return f.heads[color];
    }

    /**
     * A wire that draws from its start to its end, revealed through a mask so dashed wires and
     * arrowheads draw the same way as solid ones, with a glowing dot riding the tip.
     */
    function wire(f, d, { color = GRAY, dashed = false, arrow = true, ends = false }, at, duration) {
      const n = f.wires++;
      const mask = el("mask", { id: `${f.id}-m${n}`, maskUnits: "userSpaceOnUse", x: 0, y: 0, width: 1600, height: 1150 }, f.defs);
      const reveal = el("path", { d, fill: "none", stroke: "#fff", "stroke-width": 34 }, mask);
      const len = reveal.getTotalLength();
      reveal.setAttribute("stroke-dasharray", `${len} ${len}`);
      el("path", {
        d, fill: "none", stroke: color, "stroke-width": 3.5, mask: `url(#${f.id}-m${n})`,
        ...(dashed ? { "stroke-dasharray": "10 8" } : {}),
        ...(arrow ? { "marker-end": `url(#${head(f, color)})` } : {}),
      }, f.svg);
      const start = reveal.getPointAtLength(0);
      const finish = reveal.getPointAtLength(len);
      const startDot = el("circle", { cx: start.x, cy: start.y, r: 6, fill: color }, f.svg);
      const endDot = ends ? el("circle", { cx: finish.x, cy: finish.y, r: 6, fill: color }, f.svg) : null;
      const halo = el("circle", { r: 15, fill: ORANGE, opacity: 0, filter: `url(#${f.id}-glow)` }, f.svg);
      const dot = el("circle", { r: 6, fill: "#ffe8d1", opacity: 0, filter: `url(#${f.id}-glow)` }, f.svg);
      const ride = { p: 0 };
      const place = () => {
        const pt = reveal.getPointAtLength(ride.p * len);
        for (const c of [dot, halo]) {
          c.setAttribute("cx", pt.x);
          c.setAttribute("cy", pt.y);
        }
      };
      place();

      f.tl.fromTo(startDot, { opacity: 0, scale: 0, transformOrigin: "50% 50%" }, { opacity: 1, scale: 1, duration: 0.2 }, at);
      f.tl.fromTo(reveal, { attr: { "stroke-dashoffset": len } }, { attr: { "stroke-dashoffset": 0 }, duration, ease: "power1.inOut" }, at);
      f.tl.fromTo(ride, { p: 0 }, { p: 1, duration, ease: "power1.inOut", onUpdate: place }, at);
      f.tl.fromTo([dot, halo], { attr: { opacity: 0 } }, { attr: { opacity: (i) => (i ? 0.35 : 1) }, duration: 0.15 }, at);
      f.tl.to([dot, halo], { attr: { opacity: 0 }, duration: 0.3 }, at + duration);
      if (endDot) f.tl.fromTo(endDot, { opacity: 0, scale: 0, transformOrigin: "50% 50%" }, { opacity: 1, scale: 1, duration: 0.2 }, at + duration - 0.05);
    }

    /** A mono label on the wire layer; `lines` stack 28px apart. */
    function label(f, text, x, y, { anchor = "middle", fill = "#e4e4e7", size = 23, spacing = "0.06em" } = {}) {
      return [].concat(text).map((line, i) =>
        el("text", {
          x, y: y + i * 28, "text-anchor": anchor, fill, "font-family": "JetBrains Mono",
          "font-size": size, "font-weight": 500, "letter-spacing": spacing,
        }, f.svg, line)
      );
    }

    /** Fade an element in with a glow that settles. */
    function glowIn(f, targets, at) {
      f.tl.fromTo(targets, { opacity: 0, y: 6, filter: GLOW_ON }, { opacity: 1, y: 0, duration: 0.35, ease: "power2.out" }, at);
      f.tl.to(targets, { filter: GLOW_OFF, duration: 0.7, ease: "power1.out" }, at + 0.35);
    }

    /** Pad the timeline to the composition's data-duration so the last frame holds. */
    function finish(f) {
      const total = Number(f.root.dataset.duration);
      f.tl.to({}, { duration: Math.max(0, total - f.tl.duration()) });
      return f.tl;
    }

    /** Boxes and arrows at fixed positions, with an optional dashed group around some of them. */
    function boxes(root, title, { groups = [], nodes, links, dots = [] }) {
      const f = frame(root, title);
      const groupEls = groups.map((g) => {
        const rect = el("rect", {
          x: g.x1, y: g.y1, width: g.x2 - g.x1, height: g.y2 - g.y1, rx: 24,
          fill: "rgba(255,255,255,0.02)", stroke: "#71717a", "stroke-dasharray": "9 8", "stroke-width": 2,
        }, f.svg);
        const name = html(root, "group-label", { left: `${g.x1 + 24}px`, top: `${g.y1 + 18}px` }, g.label);
        return [rect, name];
      });
      const nodeEls = nodes.map((n) =>
        html(root, `node${n.core ? " core" : ""}${n.done ? " done" : ""}`, { left: `${n.x}px`, top: `${n.y}px`, width: `${n.w}px`, height: `${n.h}px` },
          `${n.tag ? `<div class="tag">${n.tag}</div>` : ""}<div class="title">${n.title}</div><div class="sub">${n.sub}</div>`)
      );
      const dotEls = dots.map((d) => el("circle", { cx: d.x, cy: d.y, r: 16, fill: "#fafafa" }, f.svg));
      if (groupEls.length) f.tl.fromTo(groupEls.flat(), { opacity: 0 }, { opacity: 1, duration: 0.5 }, 0.4);
      if (dotEls.length) f.tl.fromTo(dotEls, { opacity: 0, scale: 0, transformOrigin: "50% 50%" }, { opacity: 1, scale: 1, duration: 0.4 }, 0.5);
      f.tl.fromTo(nodeEls, { opacity: 0, y: 16, scale: 0.96 }, { opacity: 1, y: 0, scale: 1, duration: 0.5, stagger: 0.18, ease: "power2.out" }, 0.6);

      let t = 0.6 + nodes.length * 0.18 + 0.6;
      for (const link of links) {
        wire(f, link.d, { color: link.color, dashed: link.dashed }, t, 0.6);
        if (link.label) glowIn(f, label(f, link.label, link.lx, link.ly, { anchor: link.anchor }), t + 0.35);
        t += 0.6 + 0.35;
      }
      return finish(f);
    }

    /**
     * Data model: tables at fixed coordinates, joined by wires whose paths are given, with a
     * relationship label and a cardinality at each end.
     */
    function tables(root, title, caption, tableDefs, links) {
      const f = frame(root, title, caption);
      const cards = tableDefs.map((t) => {
        // "# " marks a primary key and "→ " a foreign key; both markers get the accent colors.
        const mark = (col) => col.replace(/^# /, '<span class="pk">#</span> ').replace(/^→ /, '<span class="fk">→</span> ');
        const rows = t.rows.map(([col, type]) => `<div class="row">${mark(col)}<span class="type">${type}</span></div>`).join("");
        return html(root, `table${t.core ? " core" : ""}`, { left: `${t.x}px`, top: `${t.y}px`, width: `${t.w}px` },
          `<div class="head"><div class="tag">${t.tag || "TABLE"}</div><div class="name">${t.name}</div></div>${rows}`);
      });
      f.tl.fromTo(cards, { opacity: 0, y: 16, scale: 0.97 }, { opacity: 1, y: 0, scale: 1, duration: 0.5, stagger: 0.18, ease: "power2.out" }, 0.4);

      let t = 0.4 + cards.length * 0.18 + 0.6;
      for (const link of links) {
        wire(f, link.d, { arrow: false, ends: true }, t, 0.8);
        const texts = label(f, link.label, link.lx, link.ly, { anchor: link.anchor, fill: "#a1a1aa", size: 19, spacing: "0.1em" });
        for (const [text, x, y] of link.card) texts.push(...label(f, text, x, y, { fill: "#fafafa", size: 24, spacing: "0" }));
        glowIn(f, texts, t + 0.5);
        t += 0.8 + 0.3;
      }
      if (f.cap) glowIn(f, f.cap, t + 0.2);
      return finish(f);
    }

    /** Sequence diagram: lane boxes on top, dashed lifelines, numbered arrows between lanes. */
    function sequence(root, title, { lanes, steps, end }) {
      const f = frame(root, title);
      const tl = f.tl;
      const LANE_TOP = 180, LANE_BOTTOM = 290;
      const nodes = lanes.map((lane) =>
        html(root, "node", { left: `${lane.x - lane.w / 2}px`, top: `${LANE_TOP}px`, width: `${lane.w}px`, height: `${LANE_BOTTOM - LANE_TOP}px` },
          `<div class="tag">${lane.tag}</div><div class="title">${lane.title}</div>`)
      );
      const lifelines = lanes.map((lane) =>
        el("line", { x1: lane.x, y1: LANE_BOTTOM, x2: lane.x, y2: end, stroke: "#3f3f46", "stroke-width": 2, "stroke-dasharray": "4 7" }, f.svg)
      );
      tl.fromTo(nodes, { opacity: 0, y: 16, scale: 0.96 }, { opacity: 1, y: 0, scale: 1, duration: 0.5, stagger: 0.15, ease: "power2.out" }, 0.4);
      tl.fromTo(lifelines, { attr: { y2: LANE_BOTTOM } }, { attr: { y2: end }, duration: 0.8, ease: "power1.inOut" }, 1.1);

      let t = 2.0;
      steps.forEach((s, i) => {
        const x1 = lanes[s.from].x, x2 = lanes[s.to].x, dir = Math.sign(x2 - x1);
        const duration = Math.min(0.9, 0.5 * (Math.abs(x2 - x1) / 400));
        wire(f, `M${x1 + dir * 6} ${s.y} L${x2 - dir * 4} ${s.y}`, { color: s.color || GRAY, dashed: s.dashed }, t, duration);
        const mid = (x1 + x2) / 2;
        const text = el("text", { x: mid, y: s.y - 16, "text-anchor": "middle", fill: "#f4f4f5", "font-family": "JetBrains Mono", "font-size": 23, "font-weight": 500 }, f.svg);
        el("tspan", { fill: ORANGE, "font-weight": 700 }, text, `${i + 1}  `);
        el("tspan", {}, text, s.label);
        const texts = [text];
        if (s.sub) texts.push(...label(f, s.sub, mid, s.y + 32, { fill: "#c4c4cc", size: 20, spacing: "0" }));
        glowIn(f, texts, t + duration * 0.6);
        t += duration + 0.3;
      });
      return finish(f);
    }

    return { boxes, tables, sequence, ORANGE, YELLOW, GREEN, GRAY };
  })();
