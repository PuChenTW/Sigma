from unittest.mock import MagicMock, patch

import pytest

from source_tools.rss import entry_external_id, entry_to_item, fetch_feed_items, parse_published


def test_entry_to_item_normalizes_feed_entry():
    item = entry_to_item({"id": "1", "title": "News", "summary": "Desc", "link": "https://example.com", "published": "Mon, 01 Jan 2024 00:00:00 GMT"})

    assert item.external_id == "1"
    assert item.title == "News"
    assert item.description == "Desc"
    assert item.published == "2024-01-01T00:00:00Z"


def test_entry_external_id_falls_back_to_link_then_title():
    assert entry_external_id({"link": "https://example.com/a", "title": "A"}) == "https://example.com/a"
    assert entry_external_id({"title": "A"}) == "A"


def test_parse_published_returns_none_for_bad_dates():
    assert parse_published({"published": "not a date"}) is None


@pytest.mark.asyncio
async def test_fetch_feed_items_applies_limit():
    parsed = MagicMock()
    parsed.entries = [{"id": "1", "title": "A"}, {"id": "2", "title": "B"}]

    with patch("feedparser.parse", return_value=parsed):
        items = await fetch_feed_items("https://example.com/feed.xml", limit=1)

    assert [item.external_id for item in items] == ["1"]
