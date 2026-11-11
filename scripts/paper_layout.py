"""Accessible paper disclosures, with stable links and unchanged study content."""
import html
import re

from latex2mathml.converter import convert as render_math


def title_html(title):
    """Render the inline TeX used in arXiv titles; escape all ordinary text."""
    pieces, start = [], 0
    for match in re.finditer(r'\\\((.*?)\\\)|\$([^$\n]+)\$', title):
        pieces.append(html.escape(title[start:match.start()]))
        formula = match.group(1) if match.group(1) is not None else match.group(2)
        pieces.append('<span class="math-inline">' + render_math(formula, display='inline') + '</span>')
        start = match.end()
    pieces.append(html.escape(title[start:]))
    return ''.join(pieces)


def collapsible_papers(rendered, papers):
    if not papers:
        return rendered
    by_id = {}
    for paper in papers:
        by_id.setdefault(paper['id'], []).append(paper)
    seen = []
    pattern = (r'<div class="paper-anchor" id="([a-z0-9-]+)"></div>'
               r'(.*?)(?=<div class="paper-anchor" id="|<h2\b|<p>END OF JOURNAL CLUB|\Z)')

    def wrap(match):
        anchor, content = match.groups()
        group = by_id[anchor]
        number = 1 + sum(len(by_id[previous]) for previous in seen)
        seen.append(anchor)
        assert content.strip(), 'Empty paper: ' + anchor
        headings = ''.join(
            '<span class="paper-heading">'
            f'<span class="paper-title" role="heading" aria-level="3">{title_html(paper["title"])}</span>'
            f'<span class="paper-authors">{html.escape(paper["authors"])}</span></span>'
            for paper in group)
        return (f'<details class="paper-entry" id="{anchor}">'
                f'<summary class="paper-summary">'
                f'<span class="paper-number" aria-hidden="true">{number:02d}</span>'
                f'<span class="paper-heading-group">{headings}</span>'
                '<span class="paper-toggle" aria-hidden="true"></span></summary>'
                f'<div class="paper-content">{content}</div></details>\n')

    result = re.sub(pattern, wrap, rendered, flags=re.S)
    assert len(seen) == len(by_id) and set(seen) == set(by_id), 'Paper disclosures differ from metadata'
    controls = ('<div class="paper-controls" hidden>'
                '<button type="button" data-papers-expand>Expand all</button>'
                '<button type="button" data-papers-collapse>Collapse all</button></div>\n')
    return result.replace('<details class="paper-entry"', controls + '<details class="paper-entry"', 1)
