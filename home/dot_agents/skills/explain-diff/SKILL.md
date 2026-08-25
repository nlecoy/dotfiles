---
name: explain-diff
description: Use when the user asks for a rich explanation of a code change, diff, branch, or PR. Produces HTML output.
disable-model-invocation: true
---

# Explain Diff

Make a short, interactive explanation of the specified code change. The reader should get through the whole page in under five minutes.

**Brevity is the point.** Explore the surrounding code as widely as you need in order to understand the change — then write up only what the reader needs. Research broadly, write narrowly.

## Sections

Four sections, in this order, with a table of contents at the top.

**Background** — 150 words max. Only the parts of the existing system the change actually touches. Skip the beginner primer unless the change is meaningless without it; if you include one, keep it to a paragraph inside a collapsed `<details>`.

**Intuition** — 200 words max, plus one or two diagrams. The essence of the change, illustrated with a single concrete toy example. If the diagram makes the point, don't restate it in prose.

**Code** — 200 words max. Group the changes into 3–5 buckets, one or two sentences each. Quote only the lines that matter; never dump whole files or the raw diff.

**Quiz** — five interactive multiple-choice questions, medium difficulty: answerable only by someone who understood the substance of the change, but not gotchas. Feedback on click, one or two sentences.

## What to cut

- Summary, conclusion, or "key takeaways" sections — the quiz is the recap
- Section preambles ("In this section we'll look at…")
- Any point already made by a diagram or code block
- File-by-file enumeration; renames, mechanical edits, test churn
- Caveats, scope notes, and alternative approaches nobody asked about
## Style

Clear, direct prose in classic style — Kleppmann-like, but tighter. Short sentences. Open each section with the point itself and let sections flow into each other without connective throat-clearing.

## Diagrams

Pick one or two diagram families and reuse them throughout rather than inventing a new visual language for each concept. Useful families:

- a stripped-down mock of the app UI, for UI changes
- a component / data-flow diagram — always include example data
Two to four diagrams total. Never ASCII art: use simple HTML and CSS (HTML lists for lists of things, etc.).

## Output

A single self-contained HTML file with inline CSS and JavaScript, as one long scrolling page — no tabs for the top-level structure. Basic responsive styling so it reads on a phone.

Save it outside the code repo, with today's date as a `YYYY-MM-DD-` filename prefix so the files stay time-sorted and out of version control. For example: `/tmp/2026-01-12-explanation-<slug>.html`.

Code blocks must use `<pre>` tags. If you use a custom styled div instead, it **must** set `white-space: pre-wrap`, or the browser collapses every newline into one line. Before saving, scan each code block in the HTML source and confirm its CSS includes `white-space: pre` or `pre-wrap`.

Use callouts sparingly — key definitions and genuinely surprising edge cases only.
