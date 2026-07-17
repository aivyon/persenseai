from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


class DocumentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(); self.ids=set(); self.links=[]; self.images=[]; self.title=False; self.description=False
    def handle_starttag(self, tag, attrs):
        values=dict(attrs)
        if values.get("id"): self.ids.add(values["id"])
        if tag == "a" and values.get("href"): self.links.append(values["href"])
        if tag == "img": self.images.append((values.get("src"), values.get("alt")))
        if tag == "title": self.title=True
        if tag == "meta" and values.get("name") == "description" and values.get("content"): self.description=True


def local_target(source: Path, href: str) -> Path | None:
    if href.startswith(("http://", "https://", "mailto:", "#")): return None
    path=urlsplit(href).path
    return (source.parent / path).resolve() if path else source


def main() -> None:
    html_files=sorted(ROOT.rglob("*.html")); assert len(html_files) == 5
    forbidden=re.compile(r"(/home/|github\.com/aivyon/persenseai-labs|gho_|korinl|blackroverai|employer)",re.I)
    for page in html_files:
        text=page.read_text(encoding="utf-8"); assert not forbidden.search(text), f"private marker in {page}"
        parser=DocumentParser(); parser.feed(text); assert parser.title and parser.description, f"metadata missing in {page}"
        for src,alt in parser.images:
            assert src and alt, f"image accessibility missing in {page}"
            target=(page.parent / src).resolve(); assert target.is_file(), f"broken image {src} in {page}"
        for href in parser.links:
            target=local_target(page,href)
            if target is not None: assert target.is_file(), f"broken link {href} in {page}"
    projects=json.loads((ROOT/"data/projects.json").read_text()); demo=json.loads((ROOT/"data/evidence-utility-demo.json").read_text())
    assert len(projects)==3 and all((ROOT/item["page"]).is_file() for item in projects)
    assert len(demo["scenarios"])>=3 and all(s["evidence"] for s in demo["scenarios"])
    assert (ROOT/"CNAME").read_text().strip()=="persenseai.com"
    assert (ROOT/"assets/og/persenseai-social.png").is_file()
    print(f"Validated {len(html_files)} pages, {len(projects)} project cards, and {len(demo['scenarios'])} mini-demo scenarios.")


if __name__ == "__main__":
    try: main()
    except AssertionError as error: print(error, file=sys.stderr); raise SystemExit(1)
