#!/usr/bin/env python3
"""Build the Anmay Defence multi-page site.

Every page is static HTML written to the repository root, so GitHub Pages can
serve it with no build step. Edit the copy in this file, then run:

    python3 tools/build_site.py

Page bodies live in the PAGES dict at the bottom.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

SPRITE = open(os.path.join("tools", "sprite.html"), encoding="utf-8").read()

NAV = [
    ("index.html", "Home"),
    ("strike.html", "STRIKE"),
    ("technology.html", "Technology"),
    ("work.html", "Work"),
    ("about.html", "About"),
    ("contact.html", "Contact"),
]


def head(title, desc, extra=""):
    return f"""<!DOCTYPE html>
<html lang="en-IN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;500&family=Inter:wght@400;500&family=JetBrains+Mono&display=swap" rel="stylesheet">
<link rel="stylesheet" href="site/site.css">
{extra}</head>
<body>
<a class="skip" href="#main">Skip to content</a>
"""


def header(active):
    items = "\n".join(
        f'<li><a href="{href}"{" aria-current=page" if href == active else ""}>{label}</a></li>'
        for href, label in NAV
    )
    mobile = "\n".join(f'<a href="{href}">{label}</a>' for href, label in NAV)
    return f"""<header class="site">
  <div class="wrap nav">
    <a class="logo" href="index.html" aria-label="Anmay Defence — home">
      <svg viewBox="0 0 138.4 48" role="img" aria-label="Anmay Defence"><use href="#lg"/><circle class="lp" cx="24" cy="9" r="6.5"/></svg>
    </a>
    <ul>
{items}
    </ul>
    <span class="bw"><a class="btn" href="contact.html">Request a briefing</a></span>
    <button class="menu-btn" aria-expanded="false" aria-controls="mobile-nav">Menu</button>
  </div>
  <nav class="mobile-nav" id="mobile-nav" aria-label="Mobile">
{mobile}
  </nav>
</header>
"""


def footer():
    return f"""<footer class="site">
  <div class="wrap">
    <div class="fg">
      <div>
        <a class="logo" href="index.html" aria-label="Anmay Defence — home">
          <svg viewBox="0 0 138.4 48" role="img" aria-label="Anmay Defence"><use href="#lg"/></svg>
        </a>
        <p>Securing the skies. Defending the future.</p>
        <p style="margin-top:.75rem;color:var(--g4);font-size:.875rem">An initiative by Robonut Project.</p>
      </div>
      <div>
        <h5>Platform</h5>
        <ul>
          <li><a href="strike.html">STRIKE Gen1</a></li>
          <li><a href="strike.html#gen2">STRIKE Gen2</a></li>
          <li><a href="strike.html#strike-m">STRIKE M</a></li>
          <li><a href="technology.html">Technology</a></li>
        </ul>
      </div>
      <div>
        <h5>Company</h5>
        <ul>
          <li><a href="about.html">About Anmay</a></li>
          <li><a href="work.html">Work &amp; assets</a></li>
          <li><a href="docs/assets-index.md">Asset index</a></li>
          <li><a href="contact.html">Contact</a></li>
        </ul>
      </div>
      <div>
        <h5>Resources</h5>
        <ul>
          <li><a href="strike.html#specs">Specifications</a></li>
          <li><a href="technology.html#roadmap">Roadmap</a></li>
          <li><a href="docs/assets-catalog.csv">Asset catalogue (CSV)</a></li>
          <li><a href="docs/shortlist.md">Image shortlist</a></li>
          <li><a href="legacy/index-single-page-v1.html">Original landing page</a></li>
        </ul>
      </div>
    </div>
    <div class="fine">
      <span>© <span id="year">2026</span> Anmay Defence. All rights reserved.</span>
      <span>Engineering and imagery by Robonut Project · Pune, India</span>
    </div>
  </div>
</footer>
{SPRITE}
<script src="site/site.js"></script>
</body>
</html>
"""


def page(filename, title, desc, body, active, extra_head=""):
    html = head(title, desc, extra_head) + header(active) + body + footer()
    with open(filename, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"wrote {filename}  ({len(html)/1024:.1f} KB)")


# --------------------------------------------------------------------------- data
CUR = json.load(open("assets/web/curated.json", encoding="utf-8"))
CAT_LABEL = {
    "platform": "Platform",
    "field": "Field &amp; vehicle",
    "detail": "Detail",
    "operations": "Operations",
    "engineering": "Engineering",
    "concepts": "Concepts &amp; posters",
    "brand": "Brand",
}
CAT_ORDER = ["platform", "field", "detail", "operations", "engineering", "concepts", "brand"]
CATALOG = json.load(open("docs/assets-catalog.json", encoding="utf-8"))
N_FILES = len(CATALOG)
N_REVIEWED = sum(1 for r in CATALOG if r["status"] == "visually-reviewed")
N_VIDEO = sum(1 for r in CATALOG if r["extension"] in ("mp4", "webm"))


def gallery_html(only=None, limit=None):
    rows = [c for c in CUR if only is None or c["category"] == only]
    if limit:
        rows = rows[:limit]
    out = []
    for c in rows:
        cap = f'{c["title"]} — {c["note"]}'.replace('"', "&quot;")
        out.append(
            f'<figure data-cat="{c["category"]}" data-caption="{cap}">'
            f'<span class="tag">{CAT_LABEL[c["category"]]}</span>'
            f'<a href="{c["full"]}"><img src="{c["thumb"]}" alt="{c["title"]}" loading="lazy" decoding="async"></a>'
            f'<figcaption><b>{c["title"]}</b><span>{c["note"]}</span></figcaption></figure>'
        )
    return "\n".join(out)


def filters_html():
    counts = {k: sum(1 for c in CUR if c["category"] == k) for k in CAT_ORDER}
    out = [f'<button data-cat="all" aria-pressed="true">All <span style="opacity:.6">{len(CUR)}</span></button>']
    for k in CAT_ORDER:
        if counts[k]:
            out.append(f'<button data-cat="{k}" aria-pressed="false">{CAT_LABEL[k]} <span style="opacity:.6">{counts[k]}</span></button>')
    return "\n".join(out)


def video_cards(n=9):
    """Highest-value video candidates, by what the archive tells us about them."""
    keys = ("compilation", "firing", "largest", "dji", "hero-potential", "high-priority", "strike-m")
    vids = [r for r in CATALOG if r["extension"] == "mp4"]
    def score(r):
        s = 0
        for i, k in enumerate(keys):
            if k in r["tags"]:
                s += (len(keys) - i) * 10
        if "pending-review" not in r["tags"]:
            s += 1
        return -s
    vids.sort(key=score)
    out = []
    for r in vids[:n]:
        mb = (int(r["lfs_size_bytes"] or 0)) / 1048576
        out.append(
            f'<figure class="card" style="display:flex;flex-direction:column;gap:.5rem">'
            f'<figcaption><b>{r["filename"]}</b>'
            f'<span style="font:400 .75rem/1.4 var(--m);color:var(--g4);display:block;margin-top:.5rem">'
            f'{mb:.1f} MB · LFS oid {r["lfs_oid"][:12]}…</span>'
            f'<span style="display:block;margin-top:.6rem;font-size:.875rem;color:var(--g4)">{r["alt"]}</span>'
            f'</figcaption></figure>'
        )
    return "\n".join(out)


def doc_cards():
    out = []
    for r in CATALOG:
        if r["extension"] in ("docx", "pptx"):
            state = "reviewed" if r["status"] == "visually-reviewed" else "pending"
            badge = f'<span class="badge {"ok" if state == "reviewed" else "pending"}">{state}</span>'
            out.append(
                f'<article class="card"><h4>{r["alt"]}{badge}</h4>'
                f'<p style="margin-top:.75rem">{r["description"][:420]}{"…" if len(r["description"]) > 420 else ""}</p>'
                f'<p style="margin-top:.9rem;font:400 .75rem/1.4 var(--m);color:var(--g4)">{r["path"]}</p></article>'
            )
    return "\n".join(out)


PAGES = {}

# =============================================================== 1. HOME
PAGES["index.html"] = dict(
    title="Anmay Defence — AI-powered counter-drone systems",
    desc="Anmay Defence builds STRIKE, an AI-powered counter-drone platform for real-time airspace awareness and rapid response.",
    active="index.html",
    body=f"""
<main id="main">
<section class="hero">
  <div class="radar" aria-hidden="true"></div>
  <div class="wrap grid2">
    <div class="rv">
      <p class="lab">Counter-drone systems · India</p>
      <h1>Detect. Track. Respond.</h1>
      <p class="sub">STRIKE is Anmay Defence's AI-powered counter-drone platform for real-time airspace awareness and rapid response — engineered, built and tested in-house.</p>
      <div class="row">
        <span class="bw"><a class="btn" href="contact.html">Request a briefing</a></span>
        <span class="bw"><a class="btn on-dark" href="strike.html">Explore STRIKE</a></span>
      </div>
    </div>
    <div class="hero-media rv">
      <img src="assets/web/strike-vehicle-on-barracks-road-dusk-overhead-drone-two-people-talking.jpg"
           alt="Overhead view of the camouflaged STRIKE vehicle with its rifle mast raised on a barracks road">
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="grid4">
      <div class="stat rv"><b>5</b><span>Independent trigger units per mount</span></div>
      <div class="stat rv"><b>360°</b><span>Continuous azimuth rotation</span></div>
      <div class="stat rv"><b>75°</b><span>Vertical elevation</span></div>
      <div class="stat rv"><b>&lt;10 min</b><span>Deployment from transport</span></div>
    </div>
  </div>
</section>

<section class="sec dark">
  <div class="wrap">
    <p class="lab rv">The threat</p>
    <h2 class="rv" style="max-width:34ch">Drone threats are evolving. Airspace protection has to keep up.</h2>
    <p class="sub rv" style="color:#c9cfd8">Small, fast, low-altitude UAVs are cheap, commercially available and increasingly autonomous. They disrupt secure facilities, critical infrastructure, public events and industrial operations — and a single countermeasure may not cover every scenario.</p>
    <div class="grid3">
      <div class="card rv"><span class="num">01</span><h4>Low-altitude threats</h4><p>Small drones are hard to see, tell apart and follow across large sites, especially below conventional radar coverage.</p></div>
      <div class="card rv"><span class="num">02</span><h4>Fragmented awareness</h4><p>Separate sensors produce separate pictures. Operators need one view, not four.</p></div>
      <div class="card rv"><span class="num">03</span><h4>Delayed decisions</h4><p>When alerts arrive late or unclear, the window for a proportionate response closes.</p></div>
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <p class="lab rv">The approach</p>
    <h2 class="rv">One integrated counter-drone workflow</h2>
    <p class="sub rv">STRIKE brings detection, tracking, threat prioritisation and response support into a single operational view — on a vehicle, on a mast, or on a fixed installation.</p>
    <div class="pipe rv">
      <div><b>01</b><span>Detect</span></div>
      <div><b>02</b><span>Identify</span></div>
      <div><b>03</b><span>Track</span></div>
      <div><b>04</b><span>Prioritise</span></div>
      <div><b>05</b><span>Respond</span></div>
    </div>
    <div class="row"><span class="bw"><a class="btn ghost" href="technology.html">How the system works</a></span></div>
  </div>
</section>

<section class="sec alt">
  <div class="wrap">
    <p class="lab rv">Platform family</p>
    <h2 class="rv">One platform. Multiple configurations.</h2>
    <p class="sub rv">The same base platform carries different sensors, effectors and mission packages, so capability grows without replacing the hardware.</p>
    <div class="grid3">
      <div class="card rv">
        <figure class="frame"><a href="strike.html"><img src="assets/web/thumbs/strike-gen1-turret-five-rifle-mount-cutout-white-bg-front-quarter.jpg" alt="STRIKE Gen1 five-rifle mount" class="ratio-4-3" loading="lazy"></a></figure>
        <h4 style="margin-top:1.1rem">STRIKE Gen1</h4>
        <p>AI-assisted detection and tracking with a five-point modular mounting platform. Built for rapid deployment on vehicle or static mounts.</p>
      </div>
      <div class="card rv">
        <figure class="frame"><a href="strike.html#gen2"><img src="assets/web/thumbs/strike-gen2-concept-tubular-frame-eo-ir-gimbal-desert-outpost-render.jpg" alt="STRIKE Gen2 concept render" class="ratio-4-3" loading="lazy"></a></figure>
        <h4 style="margin-top:1.1rem">STRIKE Gen2 <span class="badge">concept</span></h4>
        <p>Layered defence: kinetic and electronic, with day/night PTZ optics, LiDAR, edge AI and extended communications.</p>
      </div>
      <div class="card rv">
        <figure class="frame"><a href="strike.html#strike-m"><img src="assets/web/thumbs/strike-m-turret-two-ak-and-two-lmg-white-drum-indoor-bench-clean.jpg" alt="STRIKE M turret with two AK-pattern rifles and two LMGs" class="ratio-4-3" loading="lazy"></a></figure>
        <h4 style="margin-top:1.1rem">STRIKE M</h4>
        <p>Multi-weapon fit-out: the same mount carrying mixed effectors, demonstrated with two rifles and two belt-fed machine guns.</p>
      </div>
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <p class="lab rv">In the field</p>
    <h2 class="rv">Designed for real deployment, not showroom conditions</h2>
    <div class="grid2" style="margin-top:2.5rem;align-items:start">
      <figure class="frame rv">
        <img src="assets/web/strike-vehicle-front-quarter-with-mast-near-portico-buildings.jpg" alt="STRIKE vehicle with mast raised beside portico buildings" loading="lazy">
        <figcaption>STRIKE vehicle configuration, field trial site.</figcaption>
      </figure>
      <div class="rv">
        <p class="sub" style="margin-top:0">Vehicle-mounted, static and mast-based configurations have been built and exercised on site — including a tracked-rover concept for autonomous deployment.</p>
        <ul class="checks">
          <li>Rapid mast deployment from the vehicle bed</li>
          <li>Operator console with manual and automatic engagement modes</li>
          <li>Modular mission packages: RF early warning, optical fibre, electronic warfare, solar power, multi-weapon</li>
          <li>Day and night operation, with thermal-ready architecture</li>
        </ul>
        <div class="row"><span class="bw"><a class="btn ghost" href="work.html">See the build archive</a></span></div>
      </div>
    </div>
  </div>
</section>

<section class="sec alt">
  <div class="wrap">
    <p class="lab rv">Use cases</p>
    <h2 class="rv">Protection for critical spaces</h2>
    <div class="grid3">
      <div class="card rv"><h4>Defence installations</h4><p>Perimeter airspace awareness and unauthorised drone detection.</p></div>
      <div class="card rv"><h4>Armoured &amp; mechanised columns</h4><p>Mobile protection for movement through contested or urban terrain.</p></div>
      <div class="card rv"><h4>Borders &amp; forward areas</h4><p>Wide-area awareness for remote or difficult terrain.</p></div>
      <div class="card rv"><h4>Critical infrastructure</h4><p>Monitoring for power, ports, refineries and industrial assets.</p></div>
      <div class="card rv"><h4>Public events</h4><p>Temporary deployment for venue and crowd airspace awareness.</p></div>
      <div class="card rv"><h4>Convoy &amp; route protection</h4><p>Real-time drone threat monitoring during movement.</p></div>
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <p class="lab rv">Why Anmay</p>
    <h2 class="rv">Engineering-driven defence technology</h2>
    <div class="grid4">
      <div class="stat rv"><b>In-house</b><span>Mechanical, electronics and software built by the same team</span></div>
      <div class="stat rv"><b>Iterative</b><span>Prototype-first development, measured and re-machined on site</span></div>
      <div class="stat rv"><b>India-focused</b><span>Engineered for the environments and users we know best</span></div>
      <div class="stat rv"><b>Operator-led</b><span>Reliability and clarity of the operating picture come first</span></div>
    </div>
  </div>
</section>

<section class="sec dark">
  <div class="wrap">
    <p class="lab rv">Next step</p>
    <h2 class="rv" style="max-width:30ch">Ready to strengthen your airspace security?</h2>
    <p class="sub rv" style="color:#c9cfd8">Request a briefing, a site assessment, or a technical walkthrough of the STRIKE platform and its mission packages.</p>
    <div class="row">
      <span class="bw"><a class="btn" href="contact.html">Request a briefing</a></span>
      <span class="bw"><a class="btn on-dark" href="work.html">Browse the archive</a></span>
    </div>
  </div>
</section>
</main>
""",
)

# =============================================================== 2. STRIKE
PAGES["strike.html"] = dict(
    title="STRIKE — modular counter-UAS platform family | Anmay Defence",
    desc="STRIKE Gen1, Gen2 and STRIKE M: the Anmay Defence modular counter-UAS platform family — detection, tracking, prioritisation and response.",
    active="strike.html",
    body="""
<main id="main">
<section class="page-hero">
  <div class="wrap">
    <p class="crumbs"><a href="index.html">Home</a> / STRIKE</p>
    <p class="lab">Flagship platform</p>
    <h1>STRIKE</h1>
    <p class="sub">An AI-powered counter-UAS platform family engineered to detect, track and respond to evolving aerial threats — designed to evolve with the mission.</p>
    <div class="chips">
      <span class="chip">Modular</span><span class="chip">Vehicle or static</span>
      <span class="chip">Auto / manual</span><span class="chip">Indigenous</span>
    </div>
  </div>
</section>

<section class="sec" id="gen1">
  <div class="wrap grid2" style="align-items:start">
    <div class="rv">
      <p class="lab">Gen1 · the foundation</p>
      <h2>STRIKE Gen1</h2>
      <p class="sub">A rapidly deployable counter-UAS mount: AI-assisted detection and tracking on a 360° azimuth drive with 75° elevation, carrying up to five independently actuated trigger units.</p>
      <table class="spec">
        <tr><th>Detection range</th><td>Up to 700 m (Gen1, per programme documents)</td></tr>
        <tr><th>Rotation</th><td>360° continuous azimuth, stepper-driven</td></tr>
        <tr><th>Elevation</th><td>Up to 75°</td></tr>
        <tr><th>Trigger units</th><td>5, individually or simultaneously controlled</td></tr>
        <tr><th>Deployment</th><td>Under 10 minutes; vehicle-mounted or static</td></tr>
        <tr><th>Modes</th><td>Automatic tracking · manual joystick control</td></tr>
        <tr><th>Power</th><td>24 VDC</td></tr>
      </table>
      <div class="row"><span class="bw"><a class="btn ghost" href="technology.html">Engineering detail</a></span></div>
    </div>
    <div class="media-stack rv">
      <figure class="frame">
        <img src="assets/web/strike-gen1-turret-five-rifle-mount-cutout-white-bg-front-quarter.jpg" alt="STRIKE Gen1 five-rifle mount, isolated on white">
        <figcaption>Five-rifle mount: camo rifles, blue trigger servos, tubular camera on a curved arm.</figcaption>
      </figure>
      <figure class="frame">
        <img src="assets/web/strike-turret-five-rifles-with-tan-slings-rear-view-square-crop.jpg" alt="Rear view of the five-rifle turret with tan slings" loading="lazy">
        <figcaption>The same mount from the rear, on the silver pedestal drum.</figcaption>
      </figure>
    </div>
  </div>
</section>

<section class="sec alt">
  <div class="wrap">
    <p class="lab rv">Mission packages</p>
    <h2 class="rv">One platform, multiple mission configurations</h2>
    <p class="sub rv">Capability is added around the base platform rather than replacing it.</p>
    <div class="grid3">
      <div class="card rv"><span class="num">STRIKE RF</span><h4>RF early warning</h4><p>Detector for control-link activity, with a mobile app interface for the operator.</p></div>
      <div class="card rv"><span class="num">STRIKE OF</span><h4>Optical fibre</h4><p>Fibre-linked operation where radio silence is required.</p></div>
      <div class="card rv"><span class="num">STRIKE EW</span><h4>Electronic warfare</h4><p>Soft-kill jamming, stated as effective up to 2 km in the programme documents.</p></div>
      <div class="card rv"><span class="num">STRIKE SP</span><h4>Solar power</h4><p>Extended endurance for long-dwell positions.</p></div>
      <div class="card rv"><span class="num">STRIKE M</span><h4>Multi-weapon</h4><p>Mixed effectors on one mount — see the STRIKE M build below.</p></div>
      <div class="card rv"><span class="num">R&amp;D</span><h4>Future payloads</h4><p>Electromagnetic and non-kinetic payloads are studied as future options, not current capability.</p></div>
    </div>
  </div>
</section>

<section class="sec" id="gen2">
  <div class="wrap grid2" style="align-items:start">
    <div class="media-stack rv">
      <figure class="frame">
        <img src="assets/web/strike-gen2-concept-tubular-frame-eo-ir-gimbal-desert-outpost-render.jpg" alt="Concept render of STRIKE Gen2 with an EO/IR gimbal in a desert outpost">
        <figcaption>STRIKE Gen2 concept render — tubular frame, EO/IR gimbal, fixed installation.</figcaption>
      </figure>
      <figure class="frame">
        <img src="assets/web/strike-turret-fixed-installation-radar-dome-ai-render-mountains-drone.jpg" alt="Concept render pairing a turret with a radar dome" loading="lazy">
        <figcaption>Concept study pairing the mount with a surveillance radar dome.</figcaption>
      </figure>
    </div>
    <div class="rv">
      <p class="lab">Gen2 · layered defence</p>
      <h2>STRIKE Gen2 <span class="badge">concept / in development</span></h2>
      <p class="sub">Two layers of defence in one architecture: a kinetic layer and an electronic layer, with next-generation sensing and edge processing.</p>
      <table class="spec">
        <tr><th>Layers</th><td>1 — kinetic · 2 — electronic warfare</td></tr>
        <tr><th>Optics</th><td>Day/night PTZ with 30× optical zoom</td></tr>
        <tr><th>Sensing</th><td>Integrated LiDAR, EO/IR</td></tr>
        <tr><th>Compute</th><td>NVIDIA edge AI for detection and tracking</td></tr>
        <tr><th>Coverage</th><td>360° azimuth / 80° elevation</td></tr>
        <tr><th>Comms</th><td>2 km wireless video · 5 km fibre</td></tr>
        <tr><th>Trigger units</th><td>5 independent</td></tr>
        <tr><th>Deployment</th><td>24 VDC, under 10 minutes</td></tr>
      </table>
      <div class="note warn" style="margin-top:1.75rem">
        <b>How to read these figures</b>
        Gen2 is a development programme. Renders on this page are concept visualisations. Swarm defeat, autonomous networks and directed energy are R&amp;D directions — not fielded capability.
      </div>
    </div>
  </div>
</section>

<section class="sec alt" id="strike-m">
  <div class="wrap grid2" style="align-items:start">
    <div class="rv">
      <p class="lab">STRIKE M · multi-weapon</p>
      <h2>Mixed effectors, one mount</h2>
      <p class="sub">STRIKE M demonstrates the mounting platform carrying dissimilar weapons simultaneously — here two AK-pattern rifles and two belt-fed light machine guns on a fabricated drum base.</p>
      <ul class="checks">
        <li>Independent servo actuation per weapon</li>
        <li>Quick-change mounting hardware</li>
        <li>Same 360° azimuth drive and control console as Gen1</li>
        <li>Bench-tested indoors before field fitment</li>
      </ul>
      <div class="row"><span class="bw"><a class="btn ghost" href="work.html#gallery">More STRIKE M frames</a></span></div>
    </div>
    <figure class="frame rv">
      <img src="assets/web/strike-m-turret-two-ak-and-two-lmg-white-drum-indoor-bench-clean.png" alt="STRIKE M turret with two AK rifles and two LMGs on a white drum">
      <figcaption>STRIKE M on the bench: two AK-pattern rifles, two LMGs with ammunition belts.</figcaption>
    </figure>
  </div>
</section>

<section class="sec" id="specs">
  <div class="wrap">
    <p class="lab rv">Deployment</p>
    <h2 class="rv">Built for multi-domain deployment</h2>
    <div class="grid3">
      <div class="card rv">
        <figure class="frame"><img src="assets/web/thumbs/strike-vehicle-under-tin-shed-aerial-dry-ground-soldier-standing.jpg" alt="Vehicle configured STRIKE under a shed" class="ratio-4-3" loading="lazy"></figure>
        <h4 style="margin-top:1rem">Vehicle-mounted</h4>
        <p>Mast and mount fitted to a 4×4 flatbed; deploy and stow from the bed in under ten minutes.</p>
      </div>
      <div class="card rv">
        <figure class="frame"><img src="assets/web/thumbs/strike-turret-desert-concrete-base-ai-render-with-drone-overhead.jpg" alt="Static installation concept" class="ratio-4-3" loading="lazy"></figure>
        <h4 style="margin-top:1rem">Static / fixed installation</h4>
        <p>Plinth or mast-mounted for perimeter protection, with optional radar and sensor packages.</p>
      </div>
      <div class="card rv">
        <figure class="frame"><img src="assets/web/thumbs/poster-autonomous-cuas-tracked-rover-alpha-01-desert-ai-render.jpg" alt="Autonomous C-UAS tracked rover concept" class="ratio-4-3" loading="lazy"></figure>
        <h4 style="margin-top:1rem">Tracked rover <span class="badge">concept</span></h4>
        <p>Autonomous ALPHA-01 concept study: the same mount on a tracked unmanned ground vehicle.</p>
      </div>
    </div>
    <div class="note warn" style="margin-top:2.5rem">
      <b>Specification note</b>
      Figures on this page are taken from Anmay Defence's own programme documents (storyboard, catalogue and specification sheets). They are indicative, depend on configuration and are subject to qualification. Maritime and shipboard use is <em>designed for adaptation</em>, not qualified.
    </div>
  </div>
</section>

<section class="sec dark">
  <div class="wrap">
    <h2 class="rv" style="max-width:28ch">Discuss the right configuration for your site.</h2>
    <div class="row"><span class="bw"><a class="btn" href="contact.html">Request a briefing</a></span></div>
  </div>
</section>
</main>
""",
)

# =============================================================== 3. TECHNOLOGY
PAGES["technology.html"] = dict(
    title="Technology — AI detection, tracking and control | Anmay Defence",
    desc="How the STRIKE counter-drone system works: AI detection and tracking, grid-based acquisition, actuator design, stepper drives, operator console and roadmap.",
    active="technology.html",
    body="""
<main id="main">
<section class="page-hero">
  <div class="wrap">
    <p class="crumbs"><a href="index.html">Home</a> / Technology</p>
    <p class="lab">How it works</p>
    <h1>Detection, tracking and control — built as one system.</h1>
    <p class="sub">Computer vision identifies and follows the target; the mechanical platform keeps it framed; the operator decides. Every layer in that chain is designed in-house.</p>
    <div class="chips"><span class="chip">Computer vision</span><span class="chip">Servo actuation</span><span class="chip">Stepper azimuth</span><span class="chip">Operator console</span></div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <p class="lab rv">Pipeline</p>
    <h2 class="rv">From pixels to a decision</h2>
    <div class="pipe rv">
      <div><b>01</b><span>Detect</span></div>
      <div><b>02</b><span>Identify</span></div>
      <div><b>03</b><span>Track</span></div>
      <div><b>04</b><span>Prioritise</span></div>
      <div><b>05</b><span>Respond</span></div>
    </div>
    <div class="grid2" style="margin-top:3.5rem;align-items:start">
      <div class="rv">
        <p class="sub" style="margin-top:0">The tracker runs on an edge computer at the site. A live camera feed is divided into a search grid; each cell is scored continuously, and a confidence label follows the best candidate. When confidence holds, the platform locks and the gimbal follows the target.</p>
        <ul class="checks">
          <li>Grid-based search with per-cell confidence scoring</li>
          <li>Target box with acquisition state: <span style="font-family:var(--m);font-size:.85em">acq → lock → coast</span></li>
          <li>Telemetry for lock, focus, digital zoom, gimbal settling and command TX rate</li>
          <li>Multiple simultaneous tracks with priority selection</li>
        </ul>
      </div>
      <figure class="frame rv">
        <video controls preload="metadata" poster="assets/web/drone-tracker-telemetry-poster.jpg" style="width:100%;border-radius:var(--rad);border:1px solid var(--ln);background:#000">
          <source src="assets/videos/drone-tracker-app-screen-recording-grid-hud-live-acquisition-1080p.webm" type="video/webm">
          Your browser cannot play this WebM file. It is available in the repository at assets/videos/drone-tracker-app-screen-recording-grid-hud-live-acquisition-1080p.webm
        </video>
        <figcaption>Actual screen recording of the operator application acquiring and tracking a drone (12 minutes, 1080p).</figcaption>
      </figure>
    </div>
  </div>
</section>

<section class="sec alt" id="engineering">
  <div class="wrap">
    <p class="lab rv">Engineering</p>
    <h2 class="rv">Actuation designed and measured in-house</h2>
    <p class="sub rv">The trigger units are servo-driven, bracketed to the receiver and measured by hand before every iteration. The azimuth drive uses a stepper motor with a geared slew column; the elevation arm uses a machined screw mechanism.</p>
    <div class="grid3">
      <figure class="frame rv">
        <img src="assets/web/ak-trigger-servo-linkage-with-ruler-and-green-sling-closeup.jpg" alt="Servo trigger linkage measured with a steel rule" class="ratio-4-3" loading="lazy">
        <figcaption>Trigger actuator: servo horn, pushrod and trigger guard, measured against a steel rule.</figcaption>
      </figure>
      <figure class="frame rv">
        <img src="assets/web/stepper-driver-dq542ma-wiring-and-dip-switch-closeup.jpg" alt="DQ542MA stepper driver wiring" class="ratio-4-3" loading="lazy">
        <figcaption>DQ542MA stepper driver on the azimuth axis, wired and documented.</figcaption>
      </figure>
      <figure class="frame rv">
        <img src="assets/web/slew-drive-shaft-spur-gear-and-bearing-plate-on-workshop-floor.jpg" alt="Slew drive test fit with spur gear and bearing plate" class="ratio-4-3" loading="lazy">
        <figcaption>Slew column test-fit: spur gear, bearing plate and bolted base.</figcaption>
      </figure>
      <figure class="frame rv">
        <img src="assets/web/electronics-enclosure-clear-box-esp32-mosfet-led-glow-burst-01.jpg" alt="Clear electronics enclosure with ESP32 and MOSFET" class="ratio-4-3" loading="lazy">
        <figcaption>Control electronics: microcontroller, MOSFET stage and terminal blocks in a clear case.</figcaption>
      </figure>
      <figure class="frame rv">
        <img src="assets/web/aluminium-timing-pulley-held-in-palm-dark-background.jpg" alt="Machined aluminium timing pulley" class="ratio-4-3" loading="lazy">
        <figcaption>Machined parts are made and checked locally.</figcaption>
      </figure>
      <figure class="frame rv">
        <img src="assets/web/cad-strike-gen1-turret-exploded-assembly-labelled-diagram.jpg" alt="Labelled exploded CAD diagram of the turret" class="ratio-4-3" loading="lazy">
        <figcaption>Exploded CAD of the Gen1 mount: domes, gears, elevation arm, stepper, base.</figcaption>
      </figure>
    </div>
  </div>
</section>

<section class="sec" id="control">
  <div class="wrap grid2" style="align-items:start">
    <div class="rv">
      <p class="lab">Command &amp; control</p>
      <h2>An operator console you can carry</h2>
      <p class="sub">Control runs from a laptop or a handheld console with joysticks and toggles, over a radio or wired link. Automatic mode lets the system search, lock and follow; manual mode hands full authority back to the operator.</p>
      <ul class="checks">
        <li>Automatic and manual engagement modes</li>
        <li>Handheld console with dual thumb-sticks and function toggles</li>
        <li>Relay board and field wiring serviceable on the vehicle bed</li>
        <li>Runbook-driven startup so any crew member can bring the system up</li>
      </ul>
      <div class="row"><span class="bw"><a class="btn ghost" href="work.html#gallery">See operations frames</a></span></div>
    </div>
    <div class="media-stack rv">
      <figure class="frame">
        <img src="assets/web/operator-soldier-in-camo-with-pistol-grip-controller-on-truck-bed.jpg" alt="Soldier in camouflage operating a pistol-grip controller on the truck bed">
        <figcaption>Operator with the pistol-grip controller, on the vehicle bed.</figcaption>
      </figure>
      <figure class="frame">
        <img src="assets/web/control-console-black-joystick-red-buttons-on-camo-vehicle.jpg" alt="Black joystick console with red buttons">
        <figcaption>The console: thumb-sticks, function buttons, status display.</figcaption>
      </figure>
    </div>
  </div>
</section>

<section class="sec alt" id="roadmap">
  <div class="wrap">
    <p class="lab rv">Roadmap</p>
    <h2 class="rv">Designed to evolve with the threat</h2>
    <div class="grid2" style="margin-top:2.5rem;align-items:start">
      <ol class="tl rv">
        <li><b>Gen1 · in service</b><h4>Intelligent surveillance and response</h4><p>AI detection and tracking, 360° azimuth, 75° elevation, five trigger units, vehicle or static mount.</p></li>
        <li><b>Gen2 · in development</b><h4>Layered defence</h4><p>Kinetic plus electronic warfare, day/night PTZ with 30× zoom, LiDAR, edge AI, 2 km wireless video, 5 km fibre.</p></li>
        <li><b>Gen3 · concept</b><h4>Autonomous and networked</h4><p>Networked sensors, autonomous coordination and future payload options. Published as a direction of work, not as delivered capability.</p></li>
      </ol>
      <div class="rv">
        <div class="note">
          <b>Messaging discipline</b>
          We describe only what is built and measured. Swarm defeat, autonomous networks and directed energy appear on this site as R&amp;D directions. Where a render is used, it is labelled as a concept.
        </div>
        <div class="note warn" style="margin-top:1rem">
          <b>Standards</b>
          Military-grade compliance is a target of the development programme, not a certification already held.
        </div>
        <div class="note" style="margin-top:1rem">
          <b>Documentation</b>
          The approved storyboard and specification sheets are part of the asset archive and listed on the <a href="work.html#documents">work page</a>.
        </div>
      </div>
    </div>
  </div>
</section>

<section class="sec dark">
  <div class="wrap">
    <h2 class="rv" style="max-width:30ch">Want the technical walkthrough?</h2>
    <div class="row"><span class="bw"><a class="btn" href="contact.html">Request a briefing</a></span></div>
  </div>
</section>
</main>
""",
)

# =============================================================== 4. WORK
PAGES["work.html"] = dict(
    title="Work — build archive and asset library | Anmay Defence",
    desc="The Anmay Defence build archive: field trials, engineering iterations, control consoles, concept renders and the catalogue of every media asset.",
    active="work.html",
    body=f"""
<main id="main">
<section class="page-hero">
  <div class="wrap">
    <p class="crumbs"><a href="index.html">Home</a> / Work</p>
    <p class="lab">Build archive</p>
    <h1>Work, as it was built.</h1>
    <p class="sub">Frames from the workshop and the field, in the order they were made: servo brackets measured by hand, mounts welded and re-welded, masts raised on trial grounds, consoles wired on the truck bed.</p>
    <div class="chips">
      <span class="chip">{N_FILES} assets catalogued</span>
      <span class="chip">{N_REVIEWED} described from the original pixels</span>
      <span class="chip">{N_VIDEO} video files</span>
      <span class="chip">Catalogue: CSV + JSON</span>
    </div>
  </div>
</section>

<section class="sec" id="gallery">
  <div class="wrap">
    <p class="lab rv">Image library</p>
    <h2 class="rv">Selected frames</h2>
    <p class="lede rv">Every frame below was opened, described and renamed from its camera name. Use the filters to browse by what the image shows.</p>
    <div class="filters" id="filters" role="group" aria-label="Filter images by category">
      {filters_html()}
      <span id="count" style="font:400 .75rem/1 var(--m);color:var(--g4);align-self:center;margin-left:auto">{len(CUR)} frames</span>
    </div>
    <div class="gallery" id="gallery">
      {gallery_html()}
    </div>
    <p class="lede" style="margin-top:2rem">Full-size originals live in <code>assets/</code>; the web versions here are resized derivatives in <code>assets/web/</code>. The complete list — with description, tags, role and duplicate flags — is in <a href="docs/assets-index.md">docs/assets-index.md</a> and <a href="docs/assets-catalog.csv">the CSV catalogue</a>.</p>
  </div>
</section>

<section class="sec alt" id="video">
  <div class="wrap">
    <p class="lab rv">Video</p>
    <h2 class="rv">Footage, and how to get it</h2>
    <p class="lede rv">Video is stored with Git LFS. In this checkout only pointer files are present, so the clips below are catalogued and named but not yet viewable in the browser. Run <code>git lfs install &amp;&amp; git lfs pull</code> to bring the bytes down, then re-open this page.</p>
    <div class="note warn rv" style="margin-top:1.5rem">
      <b>Why the names say “pending-review”</b>
      Images were described from their pixels. Videos could not be opened here, so their filenames are derived from folder, date and neighbouring frames, and carry a <code>pending-review</code> marker. After fetching LFS objects, watch each clip and drop the marker while adding the real description — the catalogue already records the LFS oid so nothing is lost.
    </div>
    <div class="grid3 rv" style="margin-top:2rem">
      {video_cards(9)}
    </div>
    <div class="row"><span class="bw"><a class="btn ghost" href="docs/assets-index.md">Full video list</a></span></div>
  </div>
</section>

<section class="sec" id="documents">
  <div class="wrap">
    <p class="lab rv">Documents</p>
    <h2 class="rv">Scripts, storyboards and catalogues</h2>
    <p class="lede rv">The written programme is part of the archive: scripts that define the story, storyboards that define the claims, and product catalogues.</p>
    <div class="grid3 rv">
      {doc_cards()}
    </div>
  </div>
</section>

<section class="sec dark">
  <div class="wrap">
    <h2 class="rv" style="max-width:30ch">Need a specific frame or clip for a pitch?</h2>
    <p class="sub rv" style="color:#c9cfd8">Tell us the use case and we will pull the right assets — the catalogue makes it a two-minute search.</p>
    <div class="row"><span class="bw"><a class="btn" href="contact.html">Ask for assets</a></span></div>
  </div>
</section>
</main>

<div class="lb" id="lb" role="dialog" aria-modal="true" aria-label="Image viewer">
  <button type="button">Close</button>
  <figure><img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" alt=""><figcaption></figcaption></figure>
</div>
""",
)

# =============================================================== 5. ABOUT
PAGES["about.html"] = dict(
    title="About — Anmay Defence, an initiative by Robonut Project",
    desc="Anmay Defence is an engineering-led defence technology initiative by Robonut Project, building indigenous counter-UAS systems in India.",
    active="about.html",
    body="""
<main id="main">
<section class="page-hero">
  <div class="wrap">
    <p class="crumbs"><a href="index.html">Home</a> / About</p>
    <p class="lab">About</p>
    <h1>An engineering-led defence initiative.</h1>
    <p class="sub">Anmay Defence is an initiative by Robonut Project. Every system we show has been designed, built, measured and re-built by the same small team — mechanical, electronics, software and the people who operate it.</p>
    <div class="chips"><span class="chip">Pune, India</span><span class="chip">Indigenous design</span><span class="chip">Prototype to product</span></div>
  </div>
</section>

<section class="sec">
  <div class="wrap grid2" style="align-items:start">
    <div class="rv">
      <p class="lab">Approach</p>
      <h2>Engineering comes first.</h2>
      <p class="sub">We started with a problem our own environment makes obvious: small drones are cheap, quiet and hard to see, and the systems meant to stop them are often slow, fragmented or imported. So we built the whole stack ourselves — the mount, the actuators, the drives, the electronics and the software that ties them together.</p>
      <ul class="checks">
        <li>Prototypes are measured, documented and re-machined rather than outsourced</li>
        <li>Mechanical, electronics and computer vision developed as one system</li>
        <li>Operator clarity treated as a design requirement, not a UI afterthought</li>
        <li>Claims limited to what has actually been built and tested</li>
      </ul>
    </div>
    <div class="media-stack rv">
      <figure class="frame">
        <img src="assets/web/steel-slew-shaft-with-collars-and-spur-gear-held-by-engineer.jpg" alt="Engineer holding a machined slew shaft with spur gear">
        <figcaption>Slew shaft, held by the engineer who machined it.</figcaption>
      </figure>
      <figure class="frame">
        <img src="assets/web/scissor-jack-on-oily-workshop-bench-with-drill-bits.jpg" alt="Workshop bench with scissor jack and drill bits">
        <figcaption>The bench, unposed.</figcaption>
      </figure>
    </div>
  </div>
</section>

<section class="sec alt">
  <div class="wrap">
    <p class="lab rv">Milestones</p>
    <h2 class="rv">How the build progressed</h2>
    <p class="lede rv">Taken from the dates carried by the archive itself.</p>
    <ol class="tl rv">
      <li><b>July 2025</b><h4>Trigger actuation</h4><p>Servo brackets fitted to AK receivers, measured with a steel rule; the five-unit trigger concept takes shape.</p></li>
      <li><b>Late July – August 2025</b><h4>Drives and structure</h4><p>Stepper driver, slew column with spur gear and bearing plate, elevation hardware, machined pulleys.</p></li>
      <li><b>October 2025</b><h4>On the vehicle</h4><p>Mast, mount and console installed on the 4×4; command station wired on the flatbed.</p></li>
      <li><b>2026</b><h4>Trial grounds</h4><p>Field photography and drone footage of the complete system; STRIKE M multi-weapon build on the bench.</p></li>
      <li><b>Next</b><h4>Gen2 and qualification</h4><p>Layered defence with day/night PTZ, LiDAR and edge AI; compliance targets for defence procurement.</p></li>
    </ol>
  </div>
</section>

<section class="sec" id="brand">
  <div class="wrap grid2" style="align-items:start">
    <div class="rv">
      <p class="lab">Identity</p>
      <h2>The mark</h2>
      <p class="sub">The Anmay emblem is built from the trishul (trident), the damru (drum) and a spiked wheel — a work-in-progress drawing held in the archive. The Robonut honeycomb marks the engineering studio behind it.</p>
      <div class="note" style="margin-top:1.5rem">
        <b>Note on these files</b>
        Both mark files are working drafts: the emblem still carries its transparency checkerboard, and the Robonut lockup exists as two separate exports. Placeholder artwork — do not use as final logo files.
      </div>
    </div>
    <div class="media-stack rv">
      <figure class="frame" style="background:var(--s2);padding:2rem;border-radius:var(--rad)">
        <img src="assets/web/anmay-emblem-black-trishul-damru-spiked-wheel-with-dand.jpg" alt="Anmay emblem: trishul, damru and spiked wheel in black line art" style="max-height:22rem;margin:0 auto">
        <figcaption>Anmay emblem — work in progress.</figcaption>
      </figure>
      <figure class="frame" style="background:#000;padding:2rem;border-radius:var(--rad)">
        <img src="assets/web/robonut-logo-honeycomb-hexagons-with-nut-wordmark-black-bg.png" alt="Robonut Project logo" style="max-height:12rem;margin:0 auto">
        <figcaption>Robonut Project lockup.</figcaption>
      </figure>
    </div>
  </div>
</section>

<section class="sec dark">
  <div class="wrap">
    <p class="lab rv">Collaboration</p>
    <h2 class="rv" style="max-width:34ch">The next generation of airspace security will be built with partners.</h2>
    <p class="sub rv" style="color:#c9cfd8">We work with defence organisations, system integrators, research groups and technology partners on development, trials and certification.</p>
    <div class="row">
      <span class="bw"><a class="btn" href="contact.html">Start a conversation</a></span>
      <span class="bw"><a class="btn on-dark" href="work.html">See the archive</a></span>
    </div>
  </div>
</section>
</main>
""",
)

# =============================================================== 6. CONTACT
PAGES["contact.html"] = dict(
    title="Contact — request a briefing | Anmay Defence",
    desc="Request a briefing, site assessment or technical walkthrough of the STRIKE counter-drone platform.",
    active="contact.html",
    body="""
<main id="main">
<section class="page-hero">
  <div class="wrap">
    <p class="crumbs"><a href="index.html">Home</a> / Contact</p>
    <p class="lab">Contact</p>
    <h1>Request a briefing.</h1>
    <p class="sub">Tell us the site, the airspace and the constraint. We will come back with a configuration, a deployment plan and an honest statement of what is proven and what is still in development.</p>
  </div>
</section>

<section class="sec">
  <div class="wrap grid2" style="align-items:start">
    <div>
      <h2 style="font-size:2rem">Briefing request</h2>
      <form class="form" id="briefing-form" novalidate>
        <div>
          <label for="name">Name</label>
          <input id="name" name="name" type="text" autocomplete="name" required>
        </div>
        <div>
          <label for="org">Organisation</label>
          <input id="org" name="org" type="text" autocomplete="organization">
        </div>
        <div>
          <label for="email">Email</label>
          <input id="email" name="email" type="email" autocomplete="email" required>
        </div>
        <div>
          <label for="topic">What do you need?</label>
          <select id="topic" name="topic">
            <option>Product briefing</option>
            <option>Site or airspace assessment</option>
            <option>Trial or demonstration</option>
            <option>Technology partnership</option>
            <option>Media or asset request</option>
          </select>
        </div>
        <div>
          <label for="message">Context</label>
          <textarea id="message" name="message" placeholder="Site type, airspace, timeline, constraints"></textarea>
        </div>
        <div class="row" style="margin-top:.5rem"><button class="btn" type="submit">Send request</button></div>
        <p class="hint" id="form-status" hidden></p>
      </form>
      <div class="form-note">
        <b>Front-end stub:</b> this form does not post anywhere yet. Point it at your form service (Formspree, Netlify Forms, your own endpoint) in <code>contact.html</code> before publishing. No personal data is collected by this page.
      </div>
    </div>
    <div>
      <div class="card">
        <h4>Direct channels</h4>
        <table class="spec" style="margin-top:1rem">
          <tr><th>Email</th><td><span class="todo">add address</span></td></tr>
          <tr><th>Phone</th><td><span class="todo">add number</span></td></tr>
          <tr><th>WhatsApp</th><td><span class="todo">add link</span></td></tr>
          <tr><th>Studio</th><td>Robonut Project, Pune, Maharashtra, India</td></tr>
        </table>
        <p style="margin-top:1rem;font-size:.875rem;color:var(--g4)">Contact details are intentionally blank placeholders — replacing them is the only edit needed to make this page live.</p>
      </div>
      <div class="card" style="margin-top:1rem">
        <h4>What to include</h4>
        <ul class="checks">
          <li>Site type and approximate area to protect</li>
          <li>Typical airspace activity and known threats</li>
          <li>Vehicle-mounted, static or both</li>
          <li>Operating window (day only, or 24×7)</li>
          <li>Procurement route and timeline</li>
        </ul>
      </div>
      <div class="card" style="margin-top:1rem">
        <h4>For media and partners</h4>
        <p>Stills, footage and specification sheets can be supplied on request. Most of the archive is catalogued with descriptions and tags — see the <a href="work.html">work page</a>.</p>
      </div>
    </div>
  </div>
</section>
</main>
""",
)


def fix_extensions(filename):
    """Derivatives may be .jpg or .png (alpha sources keep PNG). Rewrite any
    local assets/web reference that does not exist to the sibling extension."""
    s = open(filename, encoding="utf-8").read()
    def repl(m):
        path = m.group(2)
        if os.path.exists(path) or not path.startswith("assets/web/"):
            return m.group(0)
        stem, ext = os.path.splitext(path)
        for other in (".jpg", ".png", ".jpeg"):
            if other != ext and os.path.exists(stem + other):
                return m.group(1) + stem + other + m.group(3)
        return m.group(0)
    s2 = re.sub(r'(src="|href=")([^"]*assets/web/[^"]*?)(")', repl, s)
    if s2 != s:
        open(filename, "w", encoding="utf-8").write(s2)


if __name__ == "__main__":
    for fn, cfg in PAGES.items():
        page(fn, cfg["title"], cfg["desc"], cfg["body"], cfg["active"])
    for fn in PAGES:
        fix_extensions(fn)
    print("done")
