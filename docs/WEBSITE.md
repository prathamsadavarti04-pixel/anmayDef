# Website

Multi-page site for Anmay Defence. Static HTML, no build step, no framework — open
`index.html` or serve the folder.

| page | purpose |
| --- | --- |
| `index.html` | Home: positioning, the problem, the platform family, how it works, engineering credibility |
| `strike.html` | STRIKE Gen 1, Gen 2 concept architecture, STRIKE-M, C-UAS rover, at-a-glance table |
| `technology.html` | The detect → track → prioritise → respond loop, software, mechanism close-ups, deployment forms |
| `use-cases.html` | Six deployment contexts and the four deployment configurations |
| `gallery.html` | All 134 photographs with category filters and a keyboard-navigable lightbox |
| `about.html` | Robonut Project, why the hardware is built in-house, build log |
| `contact.html` | Briefing request and enquiry routing |

Shared assets:

```
assets/css/site.css     design system (tokens, layout, components, responsive rules)
assets/js/site.js       mobile nav, scroll reveal, gallery filters, lightbox
assets/web/            1200 px derivatives of every photograph, used by the pages
```

## How to add a photograph

1. Drop the original into the right folder under `assets/` and rename it using the
   convention in [ASSET-LIBRARY.md](ASSET-LIBRARY.md).
2. Regenerate the derivatives: `python3 tools/make_web_images.py`
3. Add a `<figure class="gi" data-cat="…" data-full="assets/web/…" data-desc="…">` block
   to `gallery.html`, or reference `assets/web/…` directly on any page.
4. Add a row to `ASSET-MANIFEST.csv`.

## Design notes

* Palette: near-black `#17181a`, one accent `#1e5af9`, hairline rules `#e2e3e5`.
* Type: Inter Tight for display, Inter for text, JetBrains Mono for labels and metadata.
* Photography is the layout: sections are built around a single image rather than a grid of them.
* Product cut-outs sit on white with `object-fit: contain` (`.pcard__media--contain`) so the
  hardware is never cropped.
* Concept work (Gen 2, rover, AI renders) is labelled as concept on the page — that matches
  the messaging guardrails in the video brief.

## Deploying

The repository root is the site root, so GitHub Pages can serve it directly from the
`main` branch. No build step is required.
