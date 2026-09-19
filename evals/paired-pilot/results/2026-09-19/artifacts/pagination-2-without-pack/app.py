"""Newest-first event pagination for a team's activity view."""
import base64
import binascii
import json
from datetime import datetime, timedelta


def _decode_cursor(cursor, team):
    try:
        if not isinstance(cursor, str):
            raise ValueError
        payload = json.loads(base64.b64decode(cursor.encode("ascii"), altchars=b"-_", validate=True))
        if not isinstance(payload, dict) or set(payload) != {"team", "created_at", "id"}:
            raise ValueError
        if not all(isinstance(value, str) for value in payload.values()):
            raise ValueError
        if payload["team"] != team:
            raise ValueError
        stamp = datetime.fromisoformat(payload["created_at"].replace("Z", "+00:00"))
        if stamp.utcoffset() != timedelta(0):
            raise ValueError
        return payload["created_at"], payload["id"]
    except (ValueError, TypeError, UnicodeError, binascii.Error) as exc:
        raise ValueError("Invalid cursor for this team") from exc


def list_events(events, team, limit=2, cursor=None):
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
        raise ValueError("Limit must be an integer from 1 through 100")
    anchor = _decode_cursor(cursor, team) if cursor is not None else None
    rows = sorted(
        [e for e in events if e["team"] == team],
        key=lambda e: (e["created_at"], e["id"]),
        reverse=True,
    )
    if anchor is not None:
        rows = [e for e in rows if (e["created_at"], e["id"]) < anchor]
    page = rows[:limit]
    next_cursor = None
    if len(rows) > limit:
        next_cursor = base64.urlsafe_b64encode(json.dumps({
            "team": team,
            "created_at": page[-1]["created_at"],
            "id": page[-1]["id"],
        }).encode()).decode()
    return {"items": page, "next_cursor": next_cursor}
