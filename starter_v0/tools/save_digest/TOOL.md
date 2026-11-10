---
name: save_digest
description: Save a completed AI news digest as a Markdown file after explicit user confirmation.
---

# save_digest

## Purpose
Save a completed AI news digest to a local Markdown file.

## Parameters
- `title` (string): Digest title.
- `content` (string): Complete Markdown digest.
- `confirmed` (boolean): Whether the user explicitly confirmed saving.

## Behavior
- If `confirmed` is false, do not save.
- If `confirmed` is true, validate the title and content before saving.
- Do not overwrite an existing digest.
- Return the save status and file path when successful.

## Safety
- Never save automatically without explicit user confirmation.
- Never use this tool for unrelated content.