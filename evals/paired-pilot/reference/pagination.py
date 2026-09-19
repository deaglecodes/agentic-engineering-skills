import base64
import binascii
import json


def list_events(events, team, limit=2, cursor=None):
    if type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError("Invalid limit")
    key = lambda row: (row["created_at"], row["id"])
    rows = sorted((row for row in events if row["team"] == team), key=key, reverse=True)
    if cursor is not None:
        try:
            payload = json.loads(base64.b64decode(cursor.encode(), altchars=b"-_", validate=True))
            if not isinstance(payload, dict) or payload.get("team") != team:
                raise ValueError("Invalid cursor")
            if not isinstance(payload.get("created_at"), str) or not isinstance(payload.get("id"), str):
                raise ValueError("Invalid cursor")
            anchor = payload["created_at"], payload["id"]
        except (ValueError, TypeError, AttributeError, binascii.Error) as error:
            raise ValueError("Invalid cursor") from error
        rows = [row for row in rows if key(row) < anchor]
    page = rows[:limit]
    next_cursor = None
    if len(rows) > limit:
        payload = {"created_at": page[-1]["created_at"], "id": page[-1]["id"], "team": team}
        next_cursor = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
    return {"items": page, "next_cursor": next_cursor}
