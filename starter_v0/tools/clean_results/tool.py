from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from typing import Any

from tools._shared import err

# Source preference is a heuristic, not a fact-check or a universal authority list.
PRIMARY_DOMAINS = ('arxiv.org', 'doi.org', 'openai.com', 'anthropic.com')
REPORTING_DOMAINS = ('reuters.com', 'apnews.com', 'bbc.com', 'bbc.co.uk')
SOCIAL_DOMAINS = ('x.com', 'twitter.com', 'reddit.com', 'facebook.com', 'tiktok.com')


def _matches(host: str, domains: tuple[str, ...] | list[str]) -> bool:
    return any(host == domain or host.endswith('.' + domain) for domain in domains)


def _url(value: str) -> str:
    parts = urlsplit(value.strip())
    if parts.scheme not in ('http', 'https') or not parts.hostname or parts.username or parts.password:
        raise ValueError('Each item needs a valid public-style http(s) URL without credentials')
    host = parts.hostname.lower().removeprefix('www.')
    port = parts.port
    netloc = host + (f':{port}' if port and port != {'http': 80, 'https': 443}[parts.scheme] else '')
    query = sorted((key, val) for key, val in parse_qsl(parts.query, keep_blank_values=True)
                   if not key.lower().startswith('utm_') and key.lower() not in ('fbclid', 'gclid'))
    return urlunsplit((parts.scheme.lower(), netloc, parts.path or '/', urlencode(query), ''))


def _text(value: str) -> str:
    return ' '.join(re.findall(r'\w+', unicodedata.normalize('NFKC', value).casefold()))


def _rank(url: str, trusted_domains: list[str]) -> tuple[int, str]:
    host = urlsplit(url).hostname or ''
    if _matches(host, trusted_domains):
        return 4, 'Explicitly preferred domain for this research task'
    if _matches(host, PRIMARY_DOMAINS) or host.endswith(('.gov', '.edu')):
        return 3, 'Recognized primary/institutional domain; relevance and claims still need review'
    if _matches(host, REPORTING_DOMAINS):
        return 2, 'Recognized reporting domain; verify the cited evidence'
    if _matches(host, SOCIAL_DOMAINS):
        return 0, 'Social/forum source; treat as an unverified signal'
    return 1, 'Unclassified source; no automatic verification'


def _duplicate(a: dict, b: dict, threshold: float) -> str | None:
    if a['canonical_url'] == b['canonical_url']:
        return 'same_url'
    # Prefer summaries to titles: two different updates can share a headline.
    left, right = a['content'], b['content']
    if left and left == right:
        return 'same_content'
    # Require substantial content and matching numeric claims before fuzzy matching.
    if (len(left) >= 80 and len(right) >= 80
            and re.findall(r'\d+', left) == re.findall(r'\d+', right)
            and SequenceMatcher(None, left, right, autojunk=False).ratio() >= threshold):
        return 'near_duplicate_content'
    return None


def clean_results(items: list[dict[str, Any]], trusted_domains: list[str] | None = None,
                  similarity_threshold: float = 0.94) -> dict[str, Any]:
    """Conservatively deduplicate retrieved items and retain preferred source provenance."""
    try:
        if not isinstance(items, list) or len(items) > 200:
            raise ValueError('items must be an array of at most 200 results')
        if (isinstance(similarity_threshold, bool) or not isinstance(similarity_threshold, (int, float))
                or not 0.85 <= similarity_threshold <= 1):
            raise ValueError('similarity_threshold must be a number between 0.85 and 1')
        preferred = trusted_domains if trusted_domains is not None else []
        if not isinstance(preferred, list) or any(
            not isinstance(d, str) or not re.fullmatch(r'[a-zA-Z0-9]+(?:[.-][a-zA-Z0-9]+)*\.[a-zA-Z]{2,}', d)
            for d in preferred
        ):
            raise ValueError('trusted_domains must contain bare domain names, not URLs')
        preferred = [d.lower().removeprefix('www.') for d in preferred]
        candidates = []
        for index, item in enumerate(items):
            if not isinstance(item, dict) or not isinstance(item.get('url'), str):
                raise ValueError(f'Item {index} must be an object with a URL')
            for field in ('title', 'summary'):
                if field in item and not isinstance(item[field], str):
                    raise ValueError(f'Item {index}: {field} must be a string')
            canonical = _url(item['url'])
            content = _text(item.get('summary', '').strip() or item.get('title', ''))
            if len(content) > 20000:
                raise ValueError('Item text exceeds 20000 normalized characters')
            rank, reason = _rank(canonical, preferred)
            candidates.append(dict(index=index, item=dict(item), canonical_url=canonical,
                                   content=content, rank=rank, reason=reason))
        # Rank first so each removed item directly matches its retained representative;
        # avoid transitive merging of distinct stories through a weak bridge match.
        kept, removed = [], []
        for candidate in sorted(candidates, key=lambda c: (-c['rank'], c['index'])):
            for representative in kept:
                match = _duplicate(candidate, representative, similarity_threshold)
                if match:
                    removed.append({'removed_index': candidate['index'], 'removed_url': candidate['item']['url'],
                                    'kept_index': representative['index'], 'kept_url': representative['item']['url'],
                                    'match_reason': match, 'selection_reason': representative['reason'],
                                    'removed_source_rank': candidate['rank'], 'kept_source_rank': representative['rank']})
                    break
            else:
                kept.append(candidate)
        kept.sort(key=lambda c: c['index'])
        return {'tool': 'clean_results', 'items': [c['item'] for c in kept],
                'input_count': len(items), 'item_count': len(kept), 'removed_count': len(removed),
                'removed': sorted(removed, key=lambda r: r['removed_index']),
                'source_assessments': [{'index': c['index'], 'url': c['item']['url'],
                                        'rank': c['rank'], 'reason': c['reason']} for c in kept],
                'trust_boundary': 'Heuristic source preference, not fact verification. Paraphrases and conflicting claims may require manual review.'}
    except Exception as exc:
        return err('clean_results', exc)
