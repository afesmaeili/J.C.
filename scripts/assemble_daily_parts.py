#!/usr/bin/env python3
"""Assemble independently researched sections; never publish an unfinished set."""
import argparse
from collections import Counter
from datetime import date, datetime
from hashlib import sha256
import json
from pathlib import Path
import re

PARTS = ("arxiv", "alerts", "news")
SECTIONS = ("ArXiv Highlights", "Science News", "Science Radar")
OWNERSHIP = {"arxiv": {SECTIONS[0]}, "alerts": {SECTIONS[1]},
             "news": {SECTIONS[1], SECTIONS[2]}}


def assemble(root, edition):
    date.fromisoformat(edition)
    directory = root / "content-parts" / edition
    missing = [p for p in PARTS if not (directory / (p + ".json")).exists()]
    if missing:
        return None, missing
    parts, hashes = {}, {}
    for name in PARTS:
        raw = (directory / (name + ".json")).read_bytes()
        p = json.loads(raw)
        assert p["date"] == edition and p["part"] == name, "Part/date mismatch"
        assert p["status"] in ("complete", "partial"), "Research still in progress"
        assert datetime.fromisoformat(p["cutoff"]).tzinfo, "Cutoff requires UTC offset"
        assert isinstance(p["coverage"], str) and p["coverage"].strip(), "Missing coverage"
        assert set(p["sections"]) == OWNERSHIP[name], "Incorrect section ownership"
        assert isinstance(p["topics"], list) and all(isinstance(t, str) for t in p["topics"])
        assert isinstance(p["papers"], list)
        for heading, body in p["sections"].items():
            assert isinstance(body, str), "Section body must be Markdown"
            assert not re.search(r"^#{1,3} ", body, re.M), "Use only story/history headings"
            assert "END OF JOURNAL CLUB" not in body, "End marker belongs to assembly"
        for field, section in (("news_count", SECTIONS[1]), ("science_radar_count", SECTIONS[2])):
            assert type(p[field]) is int and p[field] >= 0
            actual = len(re.findall(r"^#### ", p["sections"].get(section, ""), re.M))
            assert p[field] == actual, "Story count differs from headings"
        if name != "arxiv":
            assert not p["papers"], "Only arXiv part owns physics paper metadata"
        parts[name], hashes[name] = p, sha256(raw).hexdigest()

    papers = parts["arxiv"]["papers"]
    ids = [p["id"] for p in papers]
    arxiv_ids = [p["arxiv"] for p in papers]
    assert len(ids) == len(set(ids)) and len(arxiv_ids) == len(set(arxiv_ids)), "Duplicate paper"
    body = parts["arxiv"]["sections"][SECTIONS[0]]
    anchors = re.findall(r"<!-- paper:([a-z0-9-]+) -->", body)
    assert Counter(ids) == Counter(anchors), "Paper anchors do not match metadata"
    assert len(re.findall(r"^##### History\s*$", body, re.M)) == len(papers), "Missing History"
    for p in papers:
        for field in ("id", "arxiv", "title", "authors", "primary_category", "label", "teaser"):
            assert isinstance(p[field], str) and p[field], "Incomplete paper metadata"
        assert p["tags"] and isinstance(p["tags"], list), "Missing paper tags"
    counts = dict(sorted(Counter(p["primary_category"] for p in papers).items()))
    news_count = sum(p["news_count"] for p in parts.values())
    radar_count = parts["news"]["science_radar_count"]
    partial = [name for name, p in parts.items() if p["status"] == "partial"]
    intro = [f"**Report date: {edition} (Europe/Berlin).**"]
    if partial:
        intro.append("**Partial coverage:** " + ", ".join(partial) + ". See the coverage notes below.")
    for name, p in parts.items():
        intro.append(f"**{name.capitalize()} source-check cutoff: {p['cutoff']}.** {p['coverage']}")
    metadata = {
        "date": edition, "kind": "Daily report",
        "description": f"{len(papers)} selected papers · {news_count} science-news stories · {radar_count} Science Radar stories" + (" · Partial coverage" if partial else ""),
        "scope": " ".join(f"{name}: {p['coverage']}" for name, p in parts.items()),
        "topics": list(dict.fromkeys(t for p in parts.values() for t in p["topics"])),
        "papers": papers, "news_count": news_count, "science_radar_count": radar_count,
        "statistics": {"basis": "selected_papers_by_primary_category", "date": edition,
                       "counts": counts, "selected_papers_by_primary_category": counts,
                       "provenance": "Unique selected papers, not whole-list totals."},
        "source_parts_sha256": hashes,
    }
    output = "---\n" + json.dumps(metadata, indent=2, ensure_ascii=False) + "\n---\n\n"
    output += "\n\n".join(intro)
    for heading in SECTIONS:
        sections = [p["sections"].get(heading, "").strip() for p in parts.values()]
        output += "\n\n### " + heading + "\n\n" + "\n\n".join(s for s in sections if s)
    output += f"\n\nEND OF JOURNAL CLUB — {edition}\n"
    target = root / "content" / (edition + ".md")
    if target.exists():
        old = target.read_text()
        if old == output:
            return target, []
        old_metadata = json.loads(re.split(r"^---[ \t]*$", old, maxsplit=2, flags=re.M)[1])
        assert "source_parts_sha256" in old_metadata, "Refusing to overwrite a legacy/manual edition"
        assert old_metadata["source_parts_sha256"] != hashes, "Report edited independently; review before replacing"
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(".md.tmp")
    temporary.write_text(output)
    temporary.replace(target)
    return target, []


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("date")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    target, missing = assemble(args.root, args.date)
    if missing:
        print("Pending parts: " + ", ".join(missing) + "; no report changed.")
        raise SystemExit(2)
    print("Assembled " + str(target))
