# Wiki Schema

## Domain
This wiki covers the `ai-lab` profile: home AI lab learning, experiments, model training notes, datasets, evaluation habits, and reproducible workflows spanning VPS, MacBook, and remote GPU services.

## Conventions
- File names: lowercase, hyphens, no spaces
- Every wiki page starts with YAML frontmatter
- Use `[[wikilinks]]` between pages
- When updating a page, always bump the `updated` date
- Every new page must be added to `index.md`
- Every action must be appended to `log.md`
- Keep raw sources immutable under `raw/`

## Frontmatter
```yaml
---
title: Page Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: entity | concept | comparison | query | summary
tags: [from taxonomy below]
sources: [raw/articles/source-name.md]
---
```

## Tag Taxonomy
- training
- inference
- dataset
- evaluation
- agent
- workflow
- infrastructure
- vps
- macbook
- modal
- huggingface
- unsloth
- research
- notes
- experiment

## Page Thresholds
- Create a page when a topic is central to a learning task or experiment
- Prefer updating existing pages over duplicates
- Split pages when they become hard to scan

## Update Policy
When information changes, prefer newer experiment notes and current docs over stale assumptions.
