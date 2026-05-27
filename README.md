# Raw OS

[English](README.md) | [中文](README_CN.md)

Raw OS is a trustworthy event, asset, and raw substrate for agent systems.

Raw OS is not an operating system kernel. It is an evidence operating substrate
for agent runtimes.

Core chain:

```text
harness/channel adapter input
  -> normalized event
  -> asset capture/store
  -> asset registry
  -> append-only raw ledger
  -> render
  -> official raw
  -> delivery adapter
  -> explicit evidence retrieval / memory handoff
```

## Install

Human entrypoint:

```text
Ask your agent to read INSTALL-FOR-AGENTS.md and execute it.
```

Agent quick gate:

```bash
scripts/raw-os validate-config --config examples/community.raw-os.example.json
scripts/raw-os doctor --config examples/community.raw-os.example.json
scripts/raw-os-smoke
```

## How Do I Know It Is Installed?

Raw OS is installed when the target agent can show evidence for these checks:

- environment check passes: `doctor.ok=true` and `fatal_count=0`
- storage exists under the intended workspace root
- a normalized event spool can be ingested
- `daily` creates raw-md, official docx, memory projection, and audit output
- `audit.ok=true`
- `evidence-search` finds known source text
- `raw-replay` can reconstruct a known event by event id

Minimum verification commands:

```bash
scripts/raw-os validate-config --config examples/<agent-id>.raw-os.json
scripts/raw-os doctor --config examples/<agent-id>.raw-os.json --spool /path/to/events.jsonl

DAY=$(TZ=<timezone> date +%F)
scripts/raw-os daily \
  --config examples/<agent-id>.raw-os.json \
  --anchor-day "$DAY" \
  --mainline <mainline> \
  --spool /path/to/events.jsonl \
  --stateful

scripts/raw-os evidence-search \
  --config examples/<agent-id>.raw-os.json \
  --anchor-day "$DAY" \
  --mainline <mainline> \
  --query "<known text>"
```

The install is not accepted just because the repository cloned successfully.
The acceptance line is working ledger, render, audit, and retrieval evidence.

## What Does It Produce?

After first install and one successful `daily` run, the target workspace should
contain:

- `raw-ledger/` - append-only source evidence events
- `asset-registry/` - asset metadata and capture status
- `assets/` - captured asset files when available
- `delivery-registry/` - delivery attempts and outcomes, if delivery is enabled
- `raw-md/` - rendered daily raw Markdown
- `raw-docx/` - rendered official daily docx
- `raw-memory-md/` - distilled memory projection for downstream importers
- `tmp/raw-os-state/audits/` - audit JSON for each day/mainline
- `tmp/raw-os-state/` - ingest checkpoints and runtime state
- `tmp/raw-report-incidents/` - incident records when checks fail

After promotion to an automated deployment, the agent may also add:

- a deployment-owned wrapper script for the daily run
- a cron/systemd/launchd schedule that runs `scripts/raw-os daily`
- log files such as `tmp/raw-os-logs/official.log`
- an optional delivery adapter that sends the official docx/raw-md
- an optional operator command such as `/raw`

Cron or delivery is not required for first install. First install is accepted by
ledger, render, audit, and retrieval. Automation is promotion work.

## How Do I Use It?

Humans normally do not use Raw OS directly. Ask your agent to install it and
connect a runtime adapter that writes normalized event JSONL.

After that, the normal operating loop is:

```text
runtime adapter writes events.jsonl
  -> agent runs scripts/raw-os daily
  -> Raw OS writes raw-ledger, raw-md, raw-docx, raw-memory-md, audit
  -> agent uses evidence-search / raw-replay when proof or reconstruction is needed
```

Common commands:

```bash
# daily production/shadow run
scripts/raw-os daily --config <config> --anchor-day <day> --mainline <mainline> --spool <events.jsonl> --stateful

# search source evidence
scripts/raw-os evidence-search --config <config> --anchor-day <day> --mainline <mainline> --query "<text>"

# replay one source event
scripts/raw-os raw-replay --config <config> --anchor-day <day> --mainline <mainline> --event-id <event-id>
```

Raw OS is not a chat UI, not a memory replacement, and not a delivery bot. It is
the evidence layer underneath those features.

## Public Boundary

The public core contains generic code, schemas, synthetic examples, docs, and
tests. Real deployment configs, credentials, raw ledgers, asset stores, owner
mappings, host-specific scripts, and private runtime snapshots do not belong in
the public core.

See `docs/publish-audit.md` before publishing a repo or release artifact.

## Key Docs

- `INSTALL.md` - human-facing install entrypoint
- `INSTALL-FOR-AGENTS.md` - agent-facing install runbook
- `docs/requirements.md` - deployment environment requirements
- `docs/publish-audit.md` - public release sanitization checklist
- `docs/naming.md` - naming and terminology boundary

## License

Apache-2.0. See `LICENSE`.
