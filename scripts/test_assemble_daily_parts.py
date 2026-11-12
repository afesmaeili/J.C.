import copy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from assemble_daily_parts import assemble, OWNERSHIP


class AssemblyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.day = "2026-11-12"
        self.directory = self.root / "content-parts" / self.day
        self.directory.mkdir(parents=True)
        self.parts = {}
        for name, headings in OWNERSHIP.items():
            self.parts[name] = dict(date=self.day, part=name, status="complete",
                cutoff="2026-11-12T08:00:00+01:00", coverage="Test fixture only.",
                topics=[], papers=[], alerts_count=0, news_count=0,
                sections={h: "" for h in headings})

    def save(self, name, part=None):
        (self.directory / (name + ".json")).write_text(json.dumps(part or self.parts[name]))

    def test_pending_leaves_existing_report_untouched(self):
        target = self.root / "content" / (self.day + ".md")
        target.parent.mkdir()
        target.write_text("existing report")
        self.save("arxiv")
        self.assertEqual(assemble(self.root, self.day), (None, ["alerts", "news"]))
        self.assertEqual(target.read_text(), "existing report")

    def test_three_parts_merge_deterministically(self):
        self.parts["alerts"]["sections"]["Astrophysical Alerts"] = "#### Alert\n\nVerified test content."
        self.parts["alerts"]["alerts_count"] = 1
        self.parts["news"]["sections"]["Science News"] = "#### Mission\n\nVerified test content.\n\n#### Biology\n\nVerified broader-science content."
        self.parts["news"]["news_count"] = 2
        self.parts["news"]["status"] = "partial"
        for name in self.parts:
            self.save(name)
        target, missing = assemble(self.root, self.day)
        first = target.read_bytes()
        self.assertFalse(missing)
        self.assertEqual(first.count(b"### Science News\n"), 1)
        self.assertEqual(first.count(b"### Astrophysical Alerts\n"), 1)
        self.assertNotIn(b"### Science Radar", first)
        self.assertIn(b'"alerts_count": 1', first)
        self.assertIn(b'"news_count": 2', first)
        self.assertLess(first.index(b"#### Alert"), first.index(b"### Science News"))
        self.assertGreater(first.index(b"#### Mission"), first.index(b"### Science News"))
        self.assertGreater(first.index(b"#### Biology"), first.index(b"### Science News"))
        self.assertIn(b"Partial coverage", first)
        self.assertTrue(first.decode().endswith("END OF JOURNAL CLUB — 2026-11-12\n"))
        assemble(self.root, self.day)
        self.assertEqual(target.read_bytes(), first)

    def test_invalid_handoff_is_rejected(self):
        for name in self.parts:
            self.save(name)
        for field, value in (("date", "2026-11-11"), ("status", "in_progress"),
                             ("alerts_count", 4), ("news_count", 4),
                             ("cutoff", "2026-11-12T08:00:00")):
            with self.subTest(field=field):
                p = copy.deepcopy(self.parts["alerts"])
                p[field] = value
                self.save("alerts", p)
                with self.assertRaises(AssertionError):
                    assemble(self.root, self.day)

    def test_wrong_section_owner_and_legacy_radar_are_rejected(self):
        for name in self.parts:
            self.save(name)
        for name, sections in (
                ("alerts", {"Science News": ""}),
                ("news", {"Astrophysical Alerts": ""}),
                ("news", {"Science News": "", "Science Radar": ""}),
                ("arxiv", {"ArXiv Highlights": "", "Science News": ""})):
            with self.subTest(name=name, sections=sections):
                p = copy.deepcopy(self.parts[name])
                p["sections"] = sections
                self.save(name, p)
                with self.assertRaisesRegex(AssertionError, "section ownership"):
                    assemble(self.root, self.day)
                self.save(name)
        p = copy.deepcopy(self.parts["news"])
        p["science_radar_count"] = 1
        self.save("news", p)
        with self.assertRaisesRegex(AssertionError, "Merge Science Radar"):
            assemble(self.root, self.day)

    def test_independent_report_edit_is_preserved(self):
        for name in self.parts:
            self.save(name)
        target, _ = assemble(self.root, self.day)
        edited = target.read_text().replace("### Science News", "### Science News\n\nEditorial correction.")
        target.write_text(edited)
        with self.assertRaisesRegex(AssertionError, "edited independently"):
            assemble(self.root, self.day)
        self.assertEqual(target.read_text(), edited)

    def test_manual_report_is_not_overwritten(self):
        for name in self.parts:
            self.save(name)
        target = self.root / "content" / (self.day + ".md")
        target.parent.mkdir()
        original = '---\n{"date": "2026-11-12"}\n---\nManual report\n'
        target.write_text(original)
        with self.assertRaisesRegex(AssertionError, "legacy/manual"):
            assemble(self.root, self.day)
        self.assertEqual(target.read_text(), original)


    def test_listing_totals_are_not_selection_counts(self):
        self.parts["arxiv"]["listing_statistics"] = {
            "date": self.day, "basis": "new_primary_submissions",
            "counts": {"astro-ph": 79, "hep-ph": 22, "hep-ex": 4, "hep-th": 23,
                       "gr-qc": 21, "nucl-ex": 1, "nucl-th": 7},
            "sources": {"astro-ph": "https://arxiv.org/catchup/astro-ph/"+self.day}}
        for name in self.parts:
            self.save(name)
        target, _ = assemble(self.root, self.day)
        text = target.read_text()
        metadata = json.loads(text.split("---")[1])
        body = text.split("---", 2)[2]
        self.assertIn("astro-ph: 79", body)
        self.assertEqual(metadata["statistics"]["counts"], {})
        self.assertNotIn("source-check cutoff", body)
        self.assertEqual(metadata["source_audit"]["alerts"]["status"], "complete")

    def test_wrong_listing_day_is_rejected(self):
        self.parts["arxiv"]["listing_statistics"] = {
            "date": "2026-11-11", "basis": "new_primary_submissions",
            "counts": {}, "sources": {"astro-ph": "https://arxiv.org"}}
        for name in self.parts:
            self.save(name)
        with self.assertRaisesRegex(AssertionError, "Listing date"):
            assemble(self.root, self.day)


if __name__ == "__main__":
    unittest.main()
