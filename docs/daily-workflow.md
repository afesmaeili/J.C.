# Daily Journal Club workflow

**Update effective 12 November 2026:** use the three-task research and publication
protocol in [split-workflow.md](split-workflow.md). It supersedes the original
combined-task scheduling and chat delivery paragraphs below. The scientific
standards and website validation requirements remain in force.

Effective 14 October 2026. The recurring task starts daily at 08:00
**Europe/Berlin**, including daylight-saving transitions. Research and
publication take place after the task starts. The first recurring run is
15 October; the 14 October edition is the initial manual run.

The connected GitHub App was installed on 14 October to provide repository
access for publishing. Each run must verify both its commit and the live
deployment; a configured connection alone is not evidence of publication.

## Dates and scope

- Determine the actual Berlin date and the latest available arXiv announcement
  batch. Record the listing date independently of submission and revision dates.
- Screen astrophysics, astroparticle physics, particle and high-energy physics,
  and cosmology, with priority for cosmic rays, multimessenger astronomy,
  gamma rays, neutrinos and oscillation phenomenology. Deduplicate cross-lists
  and check earlier reports before selecting an item.
- Daily paper selection targets first announcements in that day's UTC arXiv
  batch. Exclude replacements and older papers newly cross-listed that day.
  A cross-listed entry is eligible only if its first announcement belongs to
  the same batch; count it once by primary category. Prioritize scientific
  relevance over a numerical quota. Earlier literature belongs in History,
  unless an explicit request calls for a separate update or historical study.
- On days without new arXiv announcements, say that accurately in the chat;
  publish useful news or explicitly labeled follow-ups without inventing a
  fresh paper batch. Do not relabel old submissions as new discoveries.
- For every selected paper, read the full text, especially methods, numerical
  results and limitations. If access prevents a full assessment, say so and do
  not imply full-text review.

## Required report content

1. **ArXiv Highlights.** Give exact identifiers, versions, authors, dates,
   evidence status, scientific question, method, result and limitations.
   Every highlight has a nested **History** section based on relevant primary
   literature, including independent checks beyond the bibliography when useful.
   Define parameters and compare prior bounds only after aligning units,
   reference scales, confidence levels, models and assumptions. Separate
   observed limits, expected sensitivities, forecasts and illustrative scans.
2. **Science News.** Prioritize official neutrino, gamma-ray, gravitational-wave
   and cosmic-ray alerts, localizations, retractions and counterpart searches.
   Search GCN, ATel, collaboration notices and appropriate official alert archives;
   then cover significant instruments, awards, deaths and events. Keep event,
   announcement and follow-up dates distinct. Quote association claims with
   their actual evidence status. Do not convert sensitivities into observed limits.
3. **Science Radar.** Select particularly interesting work across other sciences.
   Include primary sources, exact publication dates and evidence limitations.
   Present scientific disputes neutrally and avoid treating publicity as proof.

Include a news cutoff and an explicit end-of-report marker. Deliver the complete
report in the current chat, including History, Science News and Science Radar.
Use clear primary-source links on the website. Keep public prose consistent
with the existing README; exclude conversational and account-specific details.

## Publication

The repository name is **afesmaeili/J.C.**, with a trailing period. The website is
<https://afesmaeili.github.io/J.C./>. Preserve the existing design and archive.

1. Read the current repository instructions and branch head.
2. Add or update `content/YYYY-MM-DD.md` with JSON front matter. Match each
   `papers[].id` to a body marker. Count selected primary categories once and
   record news and Radar subsection counts accurately.
3. Run `python3 scripts/build_archive.py`. Check all three substantive sections,
   History headings, dates, paper anchors, rendered equations, the latest link,
   search data, Markdown download and offline archive.
4. Commit source and generated artifacts together to `main`, preserving any
   concurrent changes. Do not force-push or rewrite earlier reports routinely.
5. Check GitHub Pages deployment and fetch the live dated page. Report a live
   website link only after confirming it contains the intended report. If
   publishing fails, still deliver the report in chat and explain the actual
   failure without claiming the website was updated.

The ChatGPT task is the scheduler; no second GitHub cron job is required.


## Daily opening and listing totals — 11 November 2026

Begin each public daily report with one sentence giving the verified number of **new primary submissions** in that UTC arXiv listing for astro-ph, hep-ph, hep-ex, hep-th, gr-qc, nucl-ex and nucl-th. Exclude cross-lists and replacements; include HE/CO subcounts where verified. These are listing totals, separate from selected-paper statistics. Use dated catchup pages, not a mutable /new URL. If the counts cannot be checked, state that briefly rather than substituting selection counts or inventing zeroes.

The arxiv handoff must include `listing_statistics`: `date`, `basis: "new_primary_submissions"`, a `counts` mapping containing all seven categories, dated primary `sources`, and `verified_at`. Optional `astro_subcategories` records verified primary-category breakdowns. The assembler validates the date and count types.

Do not repeat the multi-paragraph source-check/date-control/partial-coverage preamble on each public page. General methodology appears on the homepage. Keep exact cutoffs, source URLs, date distinctions, actual screening scope and specific retrieval gaps in `source_audit` metadata (and each task's coverage field). Keep scientifically material limitations beside the affected paper or news story. A missing source must never be described as verified absence of news. Preserve historical audit information when simplifying an existing opening; do not erase it.


## Public paper presentation

Public report pages use neutral editorial prose. Begin with the verified category
listing totals, then the selected papers. Do not display production notes such as
"retrospective expansion", "added on [review date]", "revised edition", or a
conversation about what was originally included. Keep editorial revision dates
and change history in source_audit metadata; retain actual submission, version,
publication and observation dates beside the scientific content. Scientific
corrections and limitations remain explicit.

Each paper is rendered as an initially collapsed entry showing its bibliographic
title and authors. Opening the entry reveals its complete study and History.
Continue writing ordinary Markdown with the existing paper anchors and metadata;
the build supplies the disclosure markup. Preserve deep links, full-text search,
complete Markdown downloads and full-content printing. Do not write HTML details
elements or manual expand/collapse instructions into the report source.
