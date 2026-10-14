# Daily Journal Club workflow

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
