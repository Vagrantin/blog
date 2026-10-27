# Nekkuma Journal

A small Hugo site served by GitHub Pages. Articles are written in Markdown;
Jenkins builds and publishes them. The site uses the existing Nekkuma artwork,
system fonts, responsive images, and Light / Dark / System appearance. System
is the default and follows operating-system changes without reloading.

## Write an article

Create `content/posts/my-article/index.md` using this front matter:

```yaml
---
title: "My article"
publishDate: 2026-11-04T09:00:00+09:00
draft: true
description: "A short description for the homepage and sharing previews."
tags: ["Rust"]
---

Write ordinary Markdown here.

![Describe the image](diagram.png)
```

Put `diagram.png` beside `index.md`. Set the date to your month's **first
Wednesday, 09:00 Asia/Tokyo**, and set `draft: false` when the article is ready.
Commit it in advance: Hugo excludes it until that timestamp. `draft: true`
continues to exclude it even after its date. New ready articles with an invalid
monthly timestamp fail validation, rather than quietly publishing on another day.
Editing an already published article updates it on the next Jenkins SCM run.

Historical articles retain their original date and case-sensitive URL. Their
front matter is JSON (also native Hugo); new articles may use YAML as above.
The migration inventory, not a user-supplied flag, identifies historical exceptions.
The `20360404` article remains an unfinished draft.

## Preview and publication

Use the dedicated **Blog / publish** Jenkins job from `Vagrantin/jenkins-infra`.
No workstation build workflow is required. Hugo is pinned in `.hugo-version`.

- Leave `PUBLISH` unchecked for a preview. `BLOG_REF` accepts `main`, a branch,
  or `PR-<number>` from this repository. Download `site-output/site.tar.gz` from
  the job's artifacts and serve its contents under `/blog/` to inspect it.
- Preview runs use the current clock and production draft/future exclusions.
  To inspect a not-yet-due article, use `PREVIEW_CLOCK` with a future timestamp
  on a preview branch; drafts must still be marked ready in that branch.
- Publication accepts only `main` and the actual current clock. The daily
  09:00 JST timer releases due articles; SCM polling handles edits. A missed
  release is included on the next successful run. GitHub Pages deployment and
  queueing add some latency after the scheduled build starts.
- Failed validation leaves the `publish` branch untouched. No-change builds
  make no new publication commit. Each artifact records its source commit,
  build clock, visible article URLs, and output digest.

Jenkins publishes generated files plus `.nojekyll` to `publish`; GitHub Pages
performs its native final deployment. There is no ODT conversion or title AI in
the publication path. See `jenkins-infra/docs/blog-publishing.md` for setup.

## Cutover and rollback

1. Merge/deploy the reviewed Jenkins infrastructure change from its `main`
   branch. Leave automatic publication disabled initially.
2. Provision the blog-only GitHub credential and run a preview of this PR.
   Check homepage, appearance modes, article rendering, and the archive.
3. Merge the reviewed blog PR. This removes the old GitHub Actions converter
   so that it cannot overwrite Hugo output. Let any old converter finish or
   cancel it before the first Hugo publication.
4. Run `blog/publish` for `main` with `PUBLISH=true`, verify the Pages result,
   then enable `BLOG_PUBLISH_ENABLED=true` in the Jenkins bootstrap environment
   and redeploy configuration. Confirm the next timed run's defaults.

For rollback, first disable automatic publication and pause the job. Restore
the previous generated tree from a known-good `publish` commit as a **new commit**
on `publish`, then let Pages deploy it. Keep history; do not force-push. Record
the pre-cutover commit before the first publication. Fix the source before
re-enabling automation, otherwise the next run will reapply it.

## Verification and archive provenance

`ci/check.sh` is the CI check contract: schedule unit tests, real Hugo builds
before/at the monthly boundary and after an outage, complete archive coverage,
local link/media and anchor checks, absence of withheld URLs from generated
HTML/feeds/sitemaps/JSON, and the homepage transfer budget. Reading and navigation
work without JavaScript; the small script only stores appearance preferences.

The homepage budget is 250 KiB for compressed HTML/CSS/JS plus the largest JPEG
header fallback. WebP is served to supporting browsers. Screenshot media is
lazy-loaded and original media paths remain available. This byte budget is
automated; a mobile Lighthouse score is a deployment-time measurement, not a
guarantee of a particular network's loading speed.

`data/migration.json` records all 22 ODT sources, source SHA-256 values, URLs,
and extracted media; 21 were published before migration. Originals remain in
git history at `6c27445de1c99b48933b6a6f266b3cab5ab07c7a`.
`scripts/migrate_legacy.py` reproduces the import with Pandoc, including the
Markdown-in-ODT repair. Do not rerun it over articles you have edited. The
historical prose, including old technical descriptions, has been preserved.
