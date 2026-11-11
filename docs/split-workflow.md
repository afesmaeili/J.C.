# Three focused Journal Club tasks

Effective 12 November 2026: three independent research tasks replace the combined
task. All retain the weekday 08:00 Europe/Berlin start, with daylight saving.
This is a start time, not a completion deadline. Each task delivers its complete
section in its chat. The website retains one daily report with the existing design.

## Responsibilities

- `arxiv`: arXiv literature only. Screen the full available dated listings in
  the requested categories before selecting, then perform an independent second
  topic pass. No fixed quota or cap. Keep a screening log with paper IDs, category,
  disposition and brief reason, distinguishing screening from full-text review.
  Include substantive History for every selected paper. Explicitly account for
  unreviewed high-priority candidates rather than silently dropping them.
- `alerts`: astrophysical event alerts, follow-ups, corrections and retractions.
  Own GCN, ATel, neutrino, gamma-ray, GW, X-ray and cosmic-ray event coverage.
- `news`: non-alert field news plus Science Radar across the sciences. Own
  instruments, missions, awards, deaths, meetings, and other-science research.

All retain the original scientific requirements in daily-workflow.md, exact dates,
source links, limitations and explicit partial-coverage disclosures. A quiet section
is not a failure and must not be padded. On Mondays include weekend developments.
Coverage windows are per task, beginning at its last verified cutoff. Initial
cutoff comes from the last combined report. A delayed run uses the actual Berlin
date; do not mix parts for different dates or pretend pending parts are finished.

## Durable handoff

Do not assume separate runs share chat history or a local filesystem. Each task
saves its finished work to `content-parts/YYYY-MM-DD/<part>.json` on fresh `main`.
These files are public: include scientific content only, no account information
or private instructions. The JSON structure is:

```json
{
  "date": "YYYY-MM-DD",
  "part": "arxiv",
  "status": "complete",
  "cutoff": "YYYY-MM-DDTHH:MM:SS+01:00",
  "coverage": "Actual dated listings, checks, gaps, and version-date policy.",
  "topics": [],
  "papers": [],
  "news_count": 0,
  "science_radar_count": 0,
  "sections": {"ArXiv Highlights": "Markdown body, with #### stories and ##### History"}
}
```

Use the actual UTC offset (or UTC) for cutoff. `status` is `complete` or `partial`;
both mean the task has finished its attempt. `partial` must identify missing
coverage. Never commit an in-progress placeholder as a finished part.

`arxiv` owns only `ArXiv Highlights`, `alerts` owns only `Science News`, and `news`
owns `Science News` and `Science Radar`. Include these exact keys, with an empty
string for a quiet owned section. Section values contain no ### heading or end
marker; the assembler supplies those. Count #### story headings exactly. News
and alerts have empty `papers`; only arxiv supplies the standard paper metadata
and matching `<!-- paper:... -->` markers. Save the arXiv screening audit alongside
its part as `content-parts/YYYY-MM-DD/arxiv-screening.json`, including checked
listing URLs/dates, retrieval gaps, unique IDs and selection decisions. Never
invent counts for inaccessible listings or claim abstract reading was full reading.

## Concurrent publication and recovery

1. Read README.md, any AGENTS.md, these instructions, previous content and fresh
   main. Resume a valid saved part instead of repeating completed research.
2. Save only your own part (and arXiv audit when applicable), using an atomic
   fast-forward commit on the latest main. With the API use Git blobs/tree/commit
   and update main with `force=false` plus `expected_sha`. Record the returned SHA.
3. **After the part commit succeeds, fetch main again.** Run
   `python3 scripts/assemble_daily_parts.py YYYY-MM-DD`.
   Exit 2 means another part is pending; do not publish a partial placeholder
   edition, wait indefinitely, or take over another task's research. Deliver your
   complete section in chat and state which parts are still pending.
4. If all three parts exist, the task that sees them assembles the report, runs
   `python3 scripts/build_archive.py`, and validates all sections, History,
   anchors, metadata, latest links, search, Markdown and offline downloads.
   Commit source and regenerated files together. Preserve all other parts and
   reports. On a concurrent-main conflict, refetch and reassemble/rebuild from
   the new head; never push a stale generated tree or force-push.
5. A second finishing task may also assemble: if the same fingerprints and
   generated files are already committed, do not create a duplicate commit.
   Verify the live dated page or a Pages run for the returned head SHA. Do not
   use PR-only workflow lookup as proof of Pages. Poll only a few times and
   distinguish committed from live.
6. The assembling task delivers the complete combined report in chat, ending
   `END OF JOURNAL CLUB — YYYY-MM-DD`. Other tasks deliver their own complete
   section, clearly labeled as that section, without claiming the other sections
   or website are complete. Never end with only a progress update or a link.
7. At the next run, check for prior sets of three finished parts awaiting assembly
   and resume publication before new research. Do not fill a missing past part
   with current news or erase another task's work. Report unresolved gaps.

Research failures must still be disclosed. A task can save a truthful partial
part with useful verified results and explicit gaps so that the other completed
work can be published. An absent part is pending, not verified lack of news.
This protocol does not guarantee scheduling, task completion or platform uptime.

The three recurring tasks should remain enabled after a successful edition.
Do not create extra scheduled tasks during their runs. No additional GitHub cron
or fourth research/publishing automation is needed.


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
