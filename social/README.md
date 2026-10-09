# PersenseAI social launch package

This directory contains the publication-ready launch package for the full PersenseAI multimodal reasoning pipeline and the latest Agent Progress Reward feature. Review the complete package on the [local preview page](preview.html) or at `https://persenseai.com/social/preview.html` after deployment.

## Package contents

- `pipeline-carousel/`: eight-slide overview from multimodal inputs to a grounded answer or inconclusive stop
- `agent-reward-carousel/`: nine-slide explanation of bounded action selection and Agent Progress Reward
- `cheatsheets/`: standalone pipeline and reward infographics
- `video-prompts/`: two production-ready 40-second video prompts, voiceover, subtitles, and scene timing
- `metadata/`: package metadata and generated asset manifest
- `generate_assets.py`: reproducible SVG-source and optimized RGB PNG exporter
- `validate_social.py`: dimensions, source, sequence, copy, and safety checks

## Reproduce and review

```bash
python3 social/generate_assets.py
python3 social/validate_social.py
python3 -m http.server 8000
```

Then open `http://127.0.0.1:8000/social/preview.html`.

## Claim boundary

The current agent uses a deterministic utility-driven policy; no language model is used for planning.

All scenarios and evidence are synthetic. Progress reward is an explanatory evaluation heuristic, not truth or legal weight. No forensic, operational, surveillance, production, or legal validity is claimed.
