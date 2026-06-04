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

### First Install vs Automated Promotion

First install only proves the Raw OS core works. It is not a daemon and it does
not install a service.

First-install acceptance means:

- normalized events can enter `raw-ledger/`
- `scripts/raw-os daily` can render outputs
- audit passes
- evidence search / replay can recover source evidence

After promotion to an automated deployment, the agent may add:

- a deployment-owned wrapper script for the daily run
- a cron/systemd/launchd schedule that runs the daily wrapper once at the chosen
  anchor time
- log files such as `tmp/raw-os-logs/official.log`
- an optional delivery adapter that sends the official docx/raw-md
- an optional operator command such as `/raw`

Cron or delivery is not required for first install. First install is accepted by
ledger, render, audit, and retrieval. Automation is promotion work.

Keep two loops separate. Start from the positive deployment shape:

- Runtime capture loop: continuously writes messages/events into the spool and
  runs `scripts/raw-os ingest-spool --stateful` on a timer or from an event hook.
  Start with a low-frequency tick, for example every 10 minutes. If the platform
  supports message hooks, use an adapter to append events into the spool.
- Official daily loop: aggregates, renders, audits, and produces the official
  docx/raw-md at the anchor time. It runs `scripts/raw-os daily` once per anchor
  day, for example at 08:00.

Recommended cron shape:

```cron
*/10 * * * * cd /path/to/raw-os && RAW_OS_ALLOW_OPENCLAW_WORKSPACE=1 scripts/raw-os ingest-spool --config examples/<agent-id>.raw-os.json --anchor-day "$(TZ=Asia/Shanghai date +\%F)" --mainline <mainline> --spool /path/to/workspace/tmp/raw-os-runtime-tap.jsonl --stateful >> /path/to/workspace/tmp/raw-os-logs/tick.log 2>&1
0 8 * * * cd /path/to/raw-os && RAW_OS_ALLOW_OPENCLAW_WORKSPACE=1 scripts/raw-os daily --config examples/<agent-id>.raw-os.json --anchor-day "$(TZ=Asia/Shanghai date +\%F)" --mainline <mainline> >> /path/to/workspace/tmp/raw-os-logs/official.log 2>&1
```

In short: capture/ingest handles new content; the 08:00 official daily loop
creates the official raw output.

Raw OS does not auto-install a service during first install. During promotion,
the agent should choose the scheduler by platform:

- macOS: `launchd` user agent
- Linux with systemd: user-level `systemd` service + timer
- portable fallback: `cron`

The agent should show the generated wrapper, scheduler file/line, log path,
enable command, and rollback command before enabling automation.

Example:

- First install: run `init`, append or ingest one sample normalized event, run
  `scripts/raw-os daily` once by hand, then verify ledger/render/audit/retrieval.
  Stop there. Do not install cron, systemd, launchd, delivery, or `/raw`.
- Promoted deployment: after shadow acceptance, add one owner-approved wrapper
  and one platform scheduler. On Linux with systemd, that means a user-level
  service plus timer that runs the wrapper once per day. On macOS, that means a
  launchd user agent. Cron is only the portable fallback.

Avoid one common misconfiguration: do not make the `daily` scheduler run every
few seconds. If faster capture is needed, create a separate capture/ingest job.

The wrapper is a small shell script owned by the deployment. It records the
repo path, config path, mainline, spool path, timezone, and the exact
`scripts/raw-os daily` command. The scheduler only runs that wrapper at the
chosen time.

Minimal wrapper shape:

```bash
#!/usr/bin/env bash
set -euo pipefail
RAW_OS_DIR="/path/to/raw-os"
CONFIG="$RAW_OS_DIR/examples/<agent-id>.raw-os.json"
MAINLINE="<mainline>"
SPOOL="/path/to/events.jsonl"
TIMEZONE="<timezone>"

cd "$RAW_OS_DIR"
DAY="$(TZ="$TIMEZONE" date +%F)"
exec scripts/raw-os daily \
  --config "$CONFIG" \
  --anchor-day "$DAY" \
  --mainline "$MAINLINE" \
  --spool "$SPOOL" \
  --stateful
```

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
