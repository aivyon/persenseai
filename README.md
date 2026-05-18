# PersenseAI

Purpose-built static website for **PersenseAI** at `persenseai.com`.

PersenseAI is positioned as a visual debugging agent concept for Computer Vision, tracking, ReID, detection, occlusion, and video pipeline reliability.

## Website

- Static HTML and CSS only
- SVG assets committed in-repo
- No framework
- No build step
- GitHub Pages compatible
- Custom domain configured with `CNAME`

## Visual product concept

The homepage communicates the product in a few seconds:

`Video + Logs + Tracks → Feature Table → Anomaly Detection → Agent Diagnosis → Report`

It uses public, non-confidential product language and pure HTML/CSS/SVG mockups for:

- hero product visual with bounding boxes and an ID-switch verdict
- workflow diagram image slot
- Computer Vision failure cards
- track feature table mockup
- SHAP-style feature contribution blocks
- example diagnostic report mockup
- optional animated/video demo placeholder

## Assets

- `assets/hero-visual.svg` — synthetic video diagnostic hero visual
- `assets/workflow-diagram.svg` — product workflow diagram
- `assets/report-mockup.svg` — debug report and SHAP-style chart mockup
- `assets/og-image.svg` — Open Graph preview image

## Deployment

Serve the repository root with GitHub Pages. No package install, build command, or generated artifact is required.
