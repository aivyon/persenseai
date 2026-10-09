#!/usr/bin/env python3
"""Validate the public social package and generate its asset manifest."""

from __future__ import annotations

import argparse
from datetime import timedelta
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

from PIL import Image


ROOT = Path(__file__).resolve().parent
WIDTH, HEIGHT = 1080, 1350
EXACT_POLICY = "The current agent uses a deterministic utility-driven policy; no language model is used for planning."


def expected_paths() -> tuple[list[Path], list[Path]]:
    svgs = [ROOT / "pipeline-carousel" / "source" / f"slide-{index:02d}.svg" for index in range(1, 9)]
    svgs += [ROOT / "agent-reward-carousel" / "source" / f"slide-{index:02d}.svg" for index in range(1, 10)]
    svgs += [
        ROOT / "cheatsheets" / "source" / "persenseai-pipeline-cheatsheet.svg",
        ROOT / "cheatsheets" / "source" / "agent-progress-reward-cheatsheet.svg",
    ]
    pngs = [ROOT / "pipeline-carousel" / "png" / f"pipeline-{index:02d}.png" for index in range(1, 9)]
    pngs += [ROOT / "agent-reward-carousel" / "png" / f"agent-reward-{index:02d}.png" for index in range(1, 10)]
    pngs += [
        ROOT / "cheatsheets" / "png" / "persenseai-pipeline-cheatsheet.png",
        ROOT / "cheatsheets" / "png" / "agent-progress-reward-cheatsheet.png",
    ]
    return svgs, pngs


def validate_svg(path: Path) -> None:
    root = ET.parse(path).getroot()
    assert root.attrib.get("width") == str(WIDTH), f"wrong SVG width: {path}"
    assert root.attrib.get("height") == str(HEIGHT), f"wrong SVG height: {path}"
    assert root.attrib.get("viewBox") == f"0 0 {WIDTH} {HEIGHT}", f"wrong SVG viewBox: {path}"
    sizes: list[float] = []
    for element in root.iter():
        if element.tag.endswith("text"):
            sizes.append(float(element.attrib["font-size"]))
            x = float(element.attrib["x"])
            y = float(element.attrib["y"])
            assert 72 <= x <= 1008, f"text outside horizontal safe area in {path}: x={x}"
            assert 72 <= y < HEIGHT, f"text outside canvas in {path}: y={y}"
    assert sizes and min(sizes) >= 30, f"unexpectedly small text in {path}: {min(sizes)}"


def validate_png(path: Path) -> None:
    with Image.open(path) as image:
        assert image.size == (WIDTH, HEIGHT), f"wrong PNG dimensions: {path} {image.size}"
        assert image.mode == "RGB", f"PNG is not RGB: {path} {image.mode}"
        assert image.getpixel((4, 4)) != (255, 255, 255), f"white render edge in {path}"
        assert image.getpixel((4, HEIGHT - 4)) != (255, 255, 255), f"white render edge in {path}"


def parse_srt_duration(path: Path) -> float:
    timestamps = re.findall(r"(\d{2}):(\d{2}):(\d{2}),(\d{3})", path.read_text(encoding="utf-8"))
    assert len(timestamps) == 16, "subtitle file must contain eight complete cues"
    values = []
    for hours, minutes, seconds, millis in timestamps:
        values.append(timedelta(hours=int(hours), minutes=int(minutes), seconds=int(seconds), milliseconds=int(millis)).total_seconds())
    assert values[0] == 0 and values[-1] == 40, f"subtitle duration is {values[0]}–{values[-1]}"
    for index in range(0, len(values), 2):
        assert values[index] < values[index + 1], "subtitle cue has non-positive duration"
        if index: assert values[index] >= values[index - 1], "subtitle cues overlap"
    return values[-1]


def text_files() -> list[Path]:
    extensions = {".md", ".html", ".css", ".js", ".json", ".srt", ".svg", ".py"}
    excluded = {"asset-manifest.json", "validate_social.py"}
    return sorted(path for path in ROOT.rglob("*") if path.is_file() and path.suffix in extensions and path.name not in excluded)


def safety_scan(paths: list[Path]) -> None:
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    forbidden = {
        "local home path": re.compile("/" + "home/", re.I),
        "local user path": re.compile("/" + "Users/", re.I),
        "GitHub Actions run link": re.compile("actions/" + "runs/", re.I),
        "credential token": re.compile("gh" + r"[opsu]_[A-Za-z0-9]{20,}|github_pat_|bearer\s+[A-Za-z0-9._-]{20,}", re.I),
        "private key": re.compile("BEGIN " + "(?:RSA |OPENSSH )?PRIVATE KEY", re.I),
        "unsupported novelty claim": re.compile(r"world['’]s first|first[- ]ever|state[- ]of[- ]the[- ]art|breakthrough", re.I),
        "LLM agent claim": re.compile(r"\bLLM agent\b", re.I),
        "private commit hash": re.compile(r"\b[0-9a-f]{40}\b", re.I),
    }
    for label, pattern in forbidden.items():
        assert not pattern.search(combined), f"safety scan found {label}"
    assert EXACT_POLICY in combined, "exact deterministic-policy disclosure is missing"
    assert "persenseai-labs" not in combined.lower(), "private supporting repository name found"
    assert "github.com/" not in combined.lower(), "repository URL found in public social package"


def caption_sections() -> list[str]:
    paths = [
        ROOT / "pipeline-carousel" / "caption.md",
        ROOT / "agent-reward-carousel" / "caption.md",
        ROOT / "video-prompts" / "caption.md",
    ]
    sections = [path.read_text(encoding="utf-8") for path in paths]
    cheats = (ROOT / "cheatsheets" / "captions.md").read_text(encoding="utf-8")
    sections.extend("## " + section for section in cheats.split("\n## ")[1:])
    assert len(sections) == 5, f"expected five captions, found {len(sections)}"
    for section in sections:
        assert "https://persenseai.com" in section, "caption missing site URL"
        assert "?" in section, "caption missing professional feedback question"
        assert len(re.findall(r"(?<!\w)#[A-Za-z0-9]+", section)) <= 8, "caption has more than eight hashtags"
    return sections


def intended_use(path: Path) -> str:
    value = path.as_posix()
    if "pipeline-carousel" in value: return "Full pipeline carousel editable source" if path.suffix == ".svg" else "Full pipeline carousel publication export"
    if "agent-reward-carousel" in value: return "Agent Progress Reward carousel editable source" if path.suffix == ".svg" else "Agent Progress Reward carousel publication export"
    if "cheatsheets" in value: return "Standalone cheatsheet editable source" if path.suffix == ".svg" else "Standalone cheatsheet publication export"
    return "Preview-page review capture"


def write_manifest(svgs: list[Path], pngs: list[Path]) -> Path:
    assets = []
    screenshot_paths = [ROOT / "preview-desktop.png", ROOT / "preview-mobile.png"]
    for path in [*svgs, *pngs, *(item for item in screenshot_paths if item.is_file())]:
        item = {
            "path": path.relative_to(ROOT).as_posix(),
            "bytes": path.stat().st_size,
            "media_type": "image/svg+xml" if path.suffix == ".svg" else "image/png",
            "intended_use": intended_use(path),
        }
        if path.suffix == ".svg":
            item["dimensions"] = {"width": WIDTH, "height": HEIGHT}
        else:
            with Image.open(path) as image:
                item["dimensions"] = {"width": image.width, "height": image.height}
                item["color_mode"] = image.mode
        assets.append(item)
    payload = {
        "schema_version": 1,
        "asset_count": len(assets),
        "publication_canvas": {"width": WIDTH, "height": HEIGHT, "ratio": "4:5", "color_mode": "RGB"},
        "assets": assets,
    }
    destination = ROOT / "metadata" / "asset-manifest.json"
    destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return destination


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-manifest", action="store_true")
    parser.add_argument("--require-screenshots", action="store_true")
    args = parser.parse_args()

    svgs, pngs = expected_paths()
    required = [
        ROOT / "README.md", ROOT / "CONTENT_PLAN.md", ROOT / "POSTING_SEQUENCE.md",
        ROOT / "preview.html", ROOT / "preview.css", ROOT / "preview.js",
        ROOT / "video-prompts" / "pipeline-with-hero-actress.md",
        ROOT / "video-prompts" / "pipeline-without-presenter.md",
        ROOT / "video-prompts" / "voiceover-script.md",
        ROOT / "video-prompts" / "subtitle-script.srt",
        ROOT / "video-prompts" / "scene-timeline.md",
        ROOT / "metadata" / "social-package.json",
        *svgs, *pngs,
    ]
    assert all(path.is_file() for path in required), "required social-package file is missing"
    assert len(list((ROOT / "pipeline-carousel" / "source").glob("slide-*.svg"))) == 8
    assert len(list((ROOT / "agent-reward-carousel" / "source").glob("slide-*.svg"))) == 9
    for path in svgs: validate_svg(path)
    for path in pngs: validate_png(path)

    preview = (ROOT / "preview.html").read_text(encoding="utf-8")
    script = (ROOT / "preview.js").read_text(encoding="utf-8")
    assert preview.index('id="agent-carousel"') < preview.index('id="pipeline-carousel"'), "preview launch order is wrong"
    assert "ArrowLeft" in script and "ArrowRight" in script and "fetch(" in script, "preview controls are incomplete"
    assert 'name="viewport"' in preview and "analytics" not in preview.lower(), "preview mobile or privacy requirement failed"

    captions = caption_sections()
    assert len(captions) == 5
    duration = parse_srt_duration(ROOT / "video-prompts" / "subtitle-script.srt")
    voiceover = (ROOT / "video-prompts" / "voiceover-script.md").read_text(encoding="utf-8").split("\n\n")[1]
    words = len(voiceover.split())
    assert 85 <= words <= 105, f"voiceover word count is {words}"

    agent_copy = (ROOT / "agent-reward-carousel" / "slide-copy.md").read_text(encoding="utf-8")
    for value in ("12 steps", "cost 1.44", "4 steps", "cost 0.32"):
        assert value.lower() in agent_copy.lower(), f"verified metric missing: {value}"
    package = json.loads((ROOT / "metadata" / "social-package.json").read_text(encoding="utf-8"))
    assert package["formats"]["pipeline_carousel_slides"] == 8
    assert package["formats"]["agent_reward_carousel_slides"] == 9
    assert package["formats"]["captions"] == 5
    safety_scan(text_files())

    if args.require_screenshots:
        for name in ("preview-desktop.png", "preview-mobile.png"):
            path = ROOT / name
            assert path.is_file(), f"missing review capture: {name}"
            with Image.open(path) as image: assert image.mode == "RGB", f"review capture is not RGB: {name}"
    manifest = write_manifest(svgs, pngs) if args.write_manifest else ROOT / "metadata" / "asset-manifest.json"
    if not args.write_manifest: assert manifest.is_file(), "asset manifest is missing"
    print(f"Validated {len(svgs)} SVGs, {len(pngs)} RGB PNGs, 5 captions, {words} voiceover words, and {duration:.0f}s of subtitles.")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, ET.ParseError, json.JSONDecodeError) as error:
        print(error, file=sys.stderr)
        raise SystemExit(1)
