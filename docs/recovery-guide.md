# AegisTrace Recovery Guide

Last Material Revision: 2026-08-01

## Project Recovery

If the autonomous execution context is lost, follow `project-control/RECOVERY_INSTRUCTIONS.md`.

## Ledger Recovery

If the ledger file is corrupted or lost:

1. Restore from the most recent independent replication (e.g., regulator-controlled vault, independent archive, public verification repository).
2. Verify the restored ledger using `aegistrace verify`.
3. If verification fails, identify the corruption point and restore from an earlier known-good state.

## Key Recovery

If a signing key is compromised:

1. Revoke the key using the KeyService.
2. Rotate to a new key.
3. Re-sign any pending events with the new key.
4. Notify affected parties (controller, regulator if high-severity).
5. Record the compromise as an incident.

## Registry Recovery

If the registry is corrupted:

1. Restore from the most recent backup.
2. Verify the registry's consistency with the ledger.
3. Re-register any entities that were not yet persisted.

## Database Recovery

If the SQLite database is corrupted:

1. Restore from the most recent backup.
2. Verify the database's consistency with the JSONL ledger.
3. Re-index if necessary.

# AegisTrace Recovery Guide
