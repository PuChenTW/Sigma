import asyncio
import calendar
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any


@dataclass(frozen=True)
class FeedItem:
    external_id: str
    title: str
    published: str | None
    description: str
    link: str | None
    raw: dict[str, Any]


def parse_published(entry: dict[str, Any]) -> str | None:
    parsed = entry.get("published_parsed")
    if parsed:
        return datetime.fromtimestamp(calendar.timegm(parsed), tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    raw = entry.get("published")
    if not raw:
        return None
    try:
        dt = parsedate_to_datetime(raw)
    except Exception:
        return None
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def entry_external_id(entry: dict[str, Any]) -> str:
    return entry.get("id") or entry.get("guid") or entry.get("link") or entry.get("title", "")


def entry_to_item(entry: dict[str, Any]) -> FeedItem:
    return FeedItem(
        external_id=entry_external_id(entry),
        title=entry.get("title", "Untitled"),
        published=parse_published(entry),
        description=entry.get("summary") or entry.get("description") or "",
        link=entry.get("link"),
        raw=entry,
    )


async def fetch_feed(url: str):
    import feedparser

    return await asyncio.to_thread(feedparser.parse, url)


async def fetch_feed_entries(rss_url: str, limit: int | None = 20) -> list[dict[str, Any]]:
    parsed = await fetch_feed(rss_url)
    entries = list(parsed.entries)
    return entries if limit is None else entries[:limit]


async def fetch_feed_items(rss_url: str, limit: int | None = 20) -> list[FeedItem]:
    return [entry_to_item(entry) for entry in await fetch_feed_entries(rss_url, limit)]
