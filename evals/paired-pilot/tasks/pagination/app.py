"""Newest-first event pagination for a team's activity view."""
import base64
import json


def list_events(events, team, limit=2, cursor=None):
    rows = sorted([e for e in events if e["team"] == team], key=lambda e: e["created_at"], reverse=True)
    if cursor:
        stamp = json.loads(base64.urlsafe_b64decode(cursor.encode()))["created_at"]
        rows = [e for e in rows if e["created_at"] < stamp]
    page = rows[:limit]
    next_cursor = None
    if len(rows) > limit:
        next_cursor = base64.urlsafe_b64encode(json.dumps({"created_at": page[-1]["created_at"]}).encode()).decode()
    return {"items": page, "next_cursor": next_cursor}
