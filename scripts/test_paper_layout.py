import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent / 'vendor'))
from paper_layout import collapsible_papers


class PaperLayoutTests(unittest.TestCase):
    def test_news_and_end_marker_stay_outside_disclosures(self):
        paper = {'id': 'paper-one', 'title': 'A & B', 'authors': 'A. Author'}
        study = '<h3 id="original-heading">Finding</h3><p>Result</p><h4>History</h4><p>Earlier work</p>'
        rendered = '<h2 id="arxiv-highlights">Papers</h2><div class="paper-anchor" id="paper-one"></div>' + study
        rendered += '<h2 id="science-news">Science News</h2><p>Event</p><p>END OF JOURNAL CLUB</p>'
        output = collapsible_papers(rendered, [paper])
        self.assertIn(study, output)
        self.assertIn('id="paper-one"', output)
        self.assertIn('A &amp; B', output)
        self.assertLess(output.index('</details>'), output.index('<h2 id="science-news">'))
        self.assertNotIn(' open', output)

    def test_joint_study_keeps_both_bibliographies(self):
        papers = [{'id': 'paper-joint', 'title': title, 'authors': author}
                  for title, author in [('First paper', 'Author One'), ('Second paper', 'Author Two')]]
        output = collapsible_papers('<div class="paper-anchor" id="paper-joint"></div><h3>Joint study</h3><p>Analysis</p>', papers)
        self.assertEqual(output.count('<details '), 1)
        for p in papers:
            self.assertIn(p['title'], output)
            self.assertIn(p['authors'], output)

    def test_missing_study_is_rejected_and_title_math_renders(self):
        paper = {'id': 'paper-math', 'title': r'Photons at $\sqrt{s}$', 'authors': 'A. Author'}
        with self.assertRaises(AssertionError):
            collapsible_papers('<p>No paper body</p>', [paper])
        output = collapsible_papers('<div class="paper-anchor" id="paper-math"></div><p>Result</p><p>END OF JOURNAL CLUB</p>', [paper])
        self.assertIn('<math', output)
        self.assertLess(output.index('</details>'), output.index('<p>END OF JOURNAL CLUB'))


if __name__ == '__main__':
    unittest.main()
