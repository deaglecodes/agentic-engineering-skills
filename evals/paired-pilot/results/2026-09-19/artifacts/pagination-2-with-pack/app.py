"""Newest-first event pagination for a team's activity view."""
import base64
import binascii
import json
from datetime import datetime, timedelta


def _decode_cursor(cursor, team):
    try:
        if not isinstance(cursor, str):
            raise ValueError
        data = json.loads(base64.b64decode(cursor.encode("ascii"), altchars=b"-_", validate=True))
        if (not isinstance(data, dict)
                or set(data) != {"created_at", "id", "team"}
                or not all(isinstance(value, str) for value in data.values())
                or data["team"] != team):
            raise ValueError
        stamp = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        if "T" not in data["created_at"] or stamp.utcoffset() != timedelta(0):
            raise ValueError
        return data["created_at"], data["id"]
    except (ValueError, TypeError, UnicodeError, binascii.Error) as exc:
        raise ValueError("Invalid cursor for this team") from exc


def list_events(events, team, limit=2, cursor=None):
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
        raise ValueError("Limit must be an integer from 1 through 100")
    anchor = _decode_cursor(cursor, team) if cursor is not None else None
    rows = sorted([e for e in events if e["team"] == team],
                  key=lambda e: (e["created_at"], e["id"]), reverse=True)
    if anchor is not None:
        rows = [e for e in rows if (e["created_at"], e["id"]) < anchor]
    page = rows[:limit]
    next_cursor = None
    if len(rows) > limit:
        next_cursor = base64.urlsafe_b64encode(json.dumps({
            "created_at": page[-1]["created_at"], "id": page[-1]["id"], "team": team
        }).encode()).decode()
    return {"items": page, "next_cursor": next_cursor}
