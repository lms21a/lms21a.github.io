# Research notes

Lukas Slifierz’s research blog, built with [Astro](https://astro.build) for GitHub Pages.

**Current state: private repository; GitHub Pages is not enabled.** The workflow checks every push but cannot deploy unless the repository variable `PAGES_ENABLED` is explicitly set to `true`.

## Start writing

Use Node.js 24 (also specified in `.node-version`).

```sh
npm ci
npm run new:post -- "Your research note title"
npm run dev:drafts
```

Open the local address printed in your terminal. New posts are created in `src/content/posts/` with `draft: true`. The draft preview shows unpublished posts and a notice; draft pages are excluded from every production build, even if it is built with `--mode drafts`.

There is a complete unpublished example in [`src/content/posts/research-note-template.mdx`](src/content/posts/research-note-template.mdx). The introductory post is starter copy; edit or delete it before launch.

To preview only ready posts, use `npm run dev`. To view exactly what would be deployed, use `npm run build` followed by `npm run preview`.

## Post format

Write plain Markdown (`.md`) or MDX (`.mdx`). Use lowercase, hyphenated filenames; the filename determines the URL, such as `/writing/your-research-note-title/`.

```yaml
---
title: "Your research note title"
description: "A short summary of the question and finding."
date: 2026-11-05
draft: true
tags: [Research, Experiments]
---
```

Set `draft: false` when a post is ready. Omitting `draft` keeps the post unpublished. Future-dated posts are also excluded until a build runs on or after their date; publishing a future date does not schedule a build. Dates display in UTC so a date-only entry always keeps the intended calendar day.

Supported content:

- Inline math: `$x_i$`; display math between `$$` lines.
- Highlighted fenced code blocks, for example triple backticks followed by `python`.
- Markdown tables and footnotes such as `[^source]` with a matching `[^source]: ...` definition.
- Figures: place exports in `public/figures/` and write `![Description](/figures/filename.png)`. Include captions and cite data sources.
- MDX components when a note needs an interactive or reusable element.

Only add material you intend to be part of the blog. Existing research directories and datasets are not part of this repository. A draft’s source is still present in the repository history, so review that history before any future change to repository visibility.

You can also write directly on GitHub: open `src/content/posts`, choose **Add file → Create new file**, name it `your-title.md`, and include the frontmatter above. Save drafts with `draft: true`.

## Personalize

- Author, description, and profile: `src/site.ts`.
- About page: `src/pages/about.astro`.
- Colors, fonts, and layout: `src/styles/global.css`.
- Canonical URL: `site` in `astro.config.mjs` and `public/robots.txt`.

Fonts and equation assets are served locally. The blog has no analytics, cookies, or third-party font requests. RSS is available at `/rss.xml`; a sitemap is generated automatically.

## Validate

```sh
npm run check
npm run build
npm run verify
```

Verification checks that draft and future posts have no generated pages or entries in the homepage, RSS feed, or sitemap. It also checks the generated pages for broken local links and asset references. GitHub Actions runs the same checks on pushes and pull requests.

## Publish later

Nothing below has been enabled yet. Publication is a separate, deliberate step.

1. Review the starter copy and every post marked `draft: false`.
2. In this repository’s **Settings → Pages**, choose **GitHub Actions** as the build source. GitHub Free requires a public repository for Pages; a supported paid plan can publish from a private repository. Keep the repository private unless you decide otherwise.
3. In **Settings → Secrets and variables → Actions → Variables**, create the repository variable `PAGES_ENABLED` with value `true`.
4. Run **Actions → Check blog and optionally publish → Run workflow**, or push to `main`.

The intended address is `https://lms21a.github.io/`. It is not a deployed site yet. Once enabled, ready posts deploy on pushes to `main`; pull requests only run checks. Setting `PAGES_ENABLED` back to `false` stops subsequent deployments but does not remove a site already published; disable Pages in Settings to take a live site down.

[GitHub Pages documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site) explains that a site can be publicly accessible even when its source repository is private.
