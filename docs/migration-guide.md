# AegisTrace Migration Guide

Last Material Revision: 2026-08-01

## Version Migration

AegisTrace follows semantic versioning. Major version changes require a documented migration path. See `spec/VERSIONING_POLICY.md`.

## Schema Migration

Schema changes are versioned. The schema version is recorded in every event. Backward-incompatible schema changes require a major version bump and a documented migration path.

## Key Migration (Rotation)

To rotate a signing key:

```python
new_sk = keys.rotate(old_key_id, new_key_id)
# Old key is marked as 'rotated'; new key is active.
# Old signatures remain verifiable; new events are signed with the new key.
```

## Cryptographic Migration

To migrate from Ed25519 to a post-quantum scheme (when standardized):

1. Adopt the new scheme in the signing interface.
2. Re-sign existing events with the new scheme.
3. Record the re-signing as new signed events.
4. Preserve the original signatures.

See `spec/PERMANENT_RECORD_PROTOCOL.md` for the full migration procedure.

## Storage Migration

To migrate from SQLite to PostgreSQL (production):

1. Export the SQLite database to JSONL.
2. Import the JSONL into PostgreSQL.
3. Verify consistency between the JSONL and PostgreSQL.
4. Switch the storage backend.

The storage interface is abstract; the migration does not change the ledger semantics.

# AegisTrace Migration Guide
