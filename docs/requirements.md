# Raw OS Requirements

This document defines the minimum environment for deploying Raw OS as a
harness-neutral evidence layer.

Raw OS core must not require OpenClaw, Telegram, Codex, ACP, Gemini, or any
agent runtime. Those are adapters around the core contract.

## Minimum Environment

- OS: Linux or macOS with a POSIX-like shell.
- Python: 3.9 or newer.
- Shell tools: `bash`, `date`, `mkdir`, `cp`, `find`.
- Timezone data: valid IANA timezone support, for example `Asia/Shanghai`.
- Filesystem: local or mounted storage that supports append-only JSONL files.
- Encoding: UTF-8 text files.

Raw OS intentionally keeps the v0 core stdlib-first. `python-docx` is optional:
if it is missing, the official docx renderer uses a built-in OOXML fallback.
Install `python-docx` when richer docx formatting is required.

## Storage Requirements

Each deployed agent needs a dedicated workspace root. Do not share one live
Raw OS storage root across unrelated agents.

Required storage lanes:

- `raw-ledger/`: append-only event ledger.
- `asset-registry/`: asset metadata and capture status.
- `delivery-registry/`: delivery evidence, independent of content validity.
- `assets/`: captured asset bytes.
- `raw-md/`: canonical human-readable raw projection.
- `raw-docx/`: official docx projection when enabled.
- `raw-memory-md/`: explicit distilled memory handoff.
- `tmp/raw-os-state/`: stateful ingest checkpoints and audits.
- `tmp/raw-report-incidents/`: incident and failure records.

Operational rule: ledger, asset registry, delivery registry, and assets are
evidence. They need backup and retention before automated cleanup is added.

## Input Requirements

Raw OS core ingests normalized event JSONL. The adapter may come from any
runtime, but it must append one JSON object per line.

Minimum event fields:

- `schema`: `raw-os-normalized-event/v1`
- `event_id`: stable idempotency key from the source runtime.
- `timestamp` or `ts`: event time.
- `speaker`: `user`, `assistant`, `tool`, `system`, or adapter-specific value.
- `sender` or `sender_id`: source identity.
- `content_parts`: text/media references.

Recommended event fields:

- `channel`
- `provider`
- `chat_id`
- `message_id`
- `session_key`
- `attachment_refs`
- `delivery`
- `ingest_metadata`

The adapter should translate runtime events into normalized events. It should
not render raw-md/docx directly.

## Runtime Requirements

Required first-run commands:

```bash
scripts/raw-os validate-config --config examples/<agent-id>.raw-os.json
scripts/raw-os doctor --config examples/<agent-id>.raw-os.json --spool /path/to/events.jsonl
scripts/raw-os init --config examples/<agent-id>.raw-os.json
scripts/raw-os daily --config examples/<agent-id>.raw-os.json --anchor-day "$DAY" --mainline <mainline> --spool /path/to/events.jsonl --stateful
```

`daily` is the normal deployment entrypoint. It can ingest a spool, render
raw-md, render official docx, render memory projection, and run audit.

Delivery remains a deployment adapter. Rendering and audit success must not be
treated as delivery success.

## Optional Requirements

- Node.js: only required for optional OpenClaw adapter plugins.
- OpenClaw: optional harness adapter, not core.
- Telegram command registration: optional operator UI, not core.
- Codex/Gemini/ACP CLIs: not required for Raw OS core deployment.
- `python-docx`: optional richer docx rendering.

## Production Checklist

Before promotion:

- `doctor` has no fatal checks.
- Timezone and anchor day are explicit.
- Spool contains real inbound and outbound events.
- Stateful ingest reruns without duplicates.
- `raw-md` and docx render in timestamp order.
- Audit returns `ok=true`.
- Evidence search and replay can recover source events.
- Delivery, if enabled, records separate delivery evidence.
- Ledger and assets have a backup/retention plan.
