# PersenseAI

Static public website for [persenseai.com](https://persenseai.com), presenting PersenseAI as an independent multimodal AI research lab.

## Architecture

- Framework-free HTML and CSS
- Vanilla JavaScript for project cards, the Evidence Utility mini-demo, and the bounded Evidence Orchestration Agent demo
- Static JSON data; no backend, external API, model call, analytics, or build step
- GitHub Pages compatible with the custom domain in `CNAME`
- Public project pages contain only reviewed presentation images and public descriptions—not private research source code

## Local validation

```bash
python3 -m http.server 8000
python3 scripts/validate_site.py
node --check js/site.js
node --check js/evidence-utility-demo.js
node --check js/evidence-agent-demo.js
```

Then open `http://127.0.0.1:8000` and test the homepage, project pages, and mini-demo at desktop, tablet, and mobile widths.

## Social package

The publication assets, captions, video-production prompts, and direct review page are indexed in [`social/README.md`](social/README.md).
