# Settings updater

`update_settings(path, patch)` updates a local JSON object and returns the merged object.

Contract:
- The existing root and patch must both be objects (dicts). Reject other roots with ValueError.
- Merge nested objects recursively. Lists and other values replace the old value; null is a stored value, not deletion. Keep unknown keys. Do not mutate the patch.
- Only standards-compliant JSON may be written (NaN and Infinity are invalid). Serialization/validation failures must leave any existing file byte-for-byte unchanged, or leave a missing destination absent.
- Use a same-directory temporary file and atomic replacement with os.replace or pathlib.Path.replace. If replacement fails, leave the original intact and clean up the temporary file. Propagate I/O errors.
- Preserve permission bits on existing files. Do not create missing parent directories.

No third-party dependencies. Run `python3 -B -m unittest -v`.
