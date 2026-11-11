"""Keep dated arXiv listing totals separate from editorial selection counts."""
from datetime import date
CATEGORIES = ('astro-ph', 'hep-ph', 'hep-ex', 'hep-th', 'gr-qc', 'nucl-ex', 'nucl-th')

def listing_sentence(statistics):
    assert statistics['basis'] == 'new_primary_submissions'
    day = date.fromisoformat(statistics['date'])
    counts = statistics['counts']
    assert set(counts) == set(CATEGORIES), 'All seven listing counts are required'
    assert all(type(n) is int and n >= 0 for n in counts.values())
    assert statistics.get('sources'), 'Listing counts require primary sources'
    label = day.strftime('%-d %B %Y')
    if not any(counts.values()):
        return f'**arXiv · {label}:** no new primary submissions in the seven tracked categories.'
    values = []
    for category in CATEGORIES:
        value = f'{category}: {counts[category]}'
        if category == 'astro-ph' and statistics.get('astro_subcategories'):
            sub = statistics['astro_subcategories']
            value += f" (HE: {sub.get('astro-ph.HE', 0)}, CO: {sub.get('astro-ph.CO', 0)})"
        values.append(value)
    return f'**arXiv · {label} — new papers:** ' + '; '.join(values) + ' (cross-lists and replacements excluded).'
