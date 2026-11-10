---
name: clean_results
track: core
kind: local_formatter
requires_env: []
inputs: [items, trusted_domains, similarity_threshold]
outputs: [items, input_count, item_count, removed_count, removed, source_assessments, trust_boundary]
side_effect: false
---
# clean_results

Clean actual retrieved results before formatting a research digest. Runs locally,
without a model, network, API key, or additional dependency. Does not perform research itself.

Duplicates match by canonical URL (tracking parameters and fragments removed),
normalized summary (title fallback), or conservative text similarity. Different
numeric claims cannot fuzzy-match. Different summaries sharing a title are kept.
At most 200 items and 20,000 normalized characters per item are accepted.

Preference: task-specific `trusted_domains` > recognized primary/institutional
sources > recognized reporting > unknown sources > social/forum sources.
The implementation contains small, explicit domain lists, not a comprehensive
credibility database. Domain matches use hostname boundaries, never display names
or caller-supplied credibility scores. Ties keep the first input item. Subdomains
inherit domain preferences. Only set task-specific preferred domains when the
user or established research context supports that choice.

Each removed result records the retained URL, original indices, match reason,
and ranks. Retained item fields/URLs are preserved; the tool does not mutate input.
Malformed input returns an error dictionary. Empty arrays return empty results.

This is source preference, not verification: official statements may be biased,
arXiv is not automatically peer reviewed, paraphrases can remain, and distinct
claims on the same URL may represent updates. Review these cases manually.
Do not lower the threshold merely to force unrelated results into one group.
