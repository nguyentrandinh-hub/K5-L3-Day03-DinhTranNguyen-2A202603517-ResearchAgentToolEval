"""Deterministic, offline source classification; never a fact-check verdict."""
from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlsplit


# Explicit local policy lists, not a complete or automatically verified directory.
OFFICIAL_DOMAINS = frozenset({
    "openai.com", "anthropic.com", "google.com", "microsoft.com",
    "who.int", "un.org", "europa.eu", "nasa.gov", "chinhphu.vn",
})
NEWS_DOMAINS = frozenset({
    "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk",
    "vnexpress.net", "tuoitre.vn", "thanhnien.vn", "vietnamnet.vn",
})
SOCIAL_DOMAINS = frozenset({
    "x.com", "twitter.com", "facebook.com", "instagram.com",
    "threads.net", "threads.com", "tiktok.com", "reddit.com",
    "youtube.com", "youtu.be", "linkedin.com", "t.me", "telegram.me",
})
LIMITATION = (
    "Domain-based heuristic only; does not verify authorship, page content, "
    "redirects or factual accuracy. Official sources may be self-interested; "
    "social posts may be official accounts. Unknown does not mean false."
)


def _matches(domain: str, root: str) -> bool:
    return domain == root or domain.endswith("." + root)


def source_tire(url: str = "") -> dict:
    """Classify an absolute HTTP(S) URL using ordered, label-boundary rules."""
    try:
        if not isinstance(url, str) or not url.strip():
            raise ValueError("url must be a non-empty string")
        value = url.strip()
        if re.search(r"\s|[\x00-\x1f\x7f\\]", value):
            raise ValueError("URL cannot contain whitespace, controls or backslashes")
        parsed = urlsplit(value)
        if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
            raise ValueError("An absolute http:// or https:// URL is required")
        if parsed.username is not None or parsed.password is not None:
            raise ValueError("URLs containing credentials are not accepted")
        port = parsed.port  # Validate malformed and out-of-range ports.
        if port == 0 or parsed.netloc.endswith(":"):
            raise ValueError("Invalid URL port")
        domain = parsed.hostname.removesuffix(".").encode("idna").decode("ascii").lower()
        try:
            ipaddress.ip_address(domain)
        except ValueError:
            pass
        else:
            raise ValueError("A public domain name is required, not an IP address")
        labels = domain.split(".")
        if len(domain) > 253 or len(labels) < 2 or any(
            not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", label)
            for label in labels
        ) or not re.search(r"[a-z]", labels[-1]):
            raise ValueError("Invalid domain name")
    except (ValueError, UnicodeError) as exc:
        return {"error": "invalid_url", "message": str(exc)}

    category, tier, rule, matched = "unknown", "unrated", "no_matching_rule", None
    # Social first: the platform domain cannot identify the account's authority.
    for roots, candidate_category, candidate_tier, candidate_rule in (
        (SOCIAL_DOMAINS, "social", "T3", "social_domain_allowlist"),
        (NEWS_DOMAINS, "news", "T2", "news_domain_allowlist"),
        (OFFICIAL_DOMAINS, "official", "T1", "official_domain_allowlist"),
        ({"gov", "gov.vn"}, "official", "T1", "government_domain_suffix"),
    ):
        matched = next((root for root in sorted(roots) if _matches(domain, root)), None)
        if matched:
            category, tier, rule = candidate_category, candidate_tier, candidate_rule
            break
    return {
        "url": value, "domain": domain, "category": category, "tier": tier,
        "rule": rule, "matched_domain": matched, "limitation": LIMITATION,
    }
