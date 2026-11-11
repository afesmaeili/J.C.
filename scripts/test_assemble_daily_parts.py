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
                topics=[], papers=[], news_count=0, science_radar_count=0,
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
        self.parts["alerts"]["sections"]["Science News"] = "#### Alert\n\nVerified test content."
        self.parts["alerts"]["news_count"] = 1
        self.parts["news"]["sections"]["Science News"] = "#### Mission\n\nVerified test content."
        self.parts["news"]["news_count"] = 1
        self.parts["news"]["status"] = "partial"
        for name in self.parts:
            self.save(name)
        target, missing = assemble(self.root, self.day)
        first = target.read_bytes()
        self.assertFalse(missing)
        self.assertEqual(first.count(b"### Science News\n"), 1)
        self.assertIn(b'"news_count": 2', first)
        self.assertIn(b"Partial coverage", first)
        self.assertTrue(first.decode().endswith("END OF JOURNAL CLUB — 2026-11-12\n"))
        assemble(self.root, self.day)
        self.assertEqual(target.read_bytes(), first)

    def test_invalid_handoff_is_rejected(self):
        for name in self.parts:
            self.save(name)
        for field, value in (("date", "2026-11-11"), ("status", "in_progress"),
                             ("news_count", 4), ("cutoff", "2026-11-12T08:00:00")):
            with self.subTest(field=field):
                p = copy.deepcopy(self.parts["alerts"])
                p[field] = value
                self.save("alerts", p)
                with self.assertRaises(AssertionError):
                    assemble(self.root, self.day)

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


if __name__ == "__main__":
    unittest.main()
