# Team event feed

`list_events(events, team, limit=2, cursor=None)` returns `items` and `next_cursor`.

Contract:
- Events contain unique string `id`, string `team`, and ISO UTC `created_at` timestamps in the same fixed format.
- Filter by team, then order newest first by `(created_at, id)` descending, comparing IDs lexicographically.
- A cursor represents the last emitted sort key and its team. Resume strictly after that key, even if the anchor event has been deleted.
- Reject malformed cursors and cursors for a different team with ValueError. Cursor format can change; no legacy cursor compatibility is required.
- Limit must be an integer from 1 through 100, not a boolean; invalid limits raise ValueError.
- Return a next cursor only if more matching events remain. Empty feeds return an empty list and no cursor.
- Never mutate the input events or their list order.

No third-party dependencies. Run `python3 -B -m unittest -v`.
