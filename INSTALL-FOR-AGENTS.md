# Install Raw OS For An Agent

This runbook is for the agent doing the installation.

Raw OS is an evidence layer. It sits beside a runtime, ingests normalized event
JSONL, writes append-only evidence, renders daily raw outputs, and audits the
result. Do not treat it as a chat plugin, a memory replacement, or a delivery
bot.

## Operating Boundaries

- Do not change the target agent's persona, model, secrets, or runtime config
  unless the human explicitly asks for that step.
- Do not restart shared services during install without explicit approval.
- Do not write into a live OpenClaw workspace unless the owner has approved it
  and the required `RAW_OS_ALLOW_*` guard is set.
- Do not publish or copy real raw data, assets, transcripts, tokens, or owner
  mappings into the Raw OS repo.
- Treat delivery as a later adapter step. Raw success means ledger/render/audit
  success, not message delivery success.

## Install Shape

Keep first deployment to four moving parts:

```text
core + config + normalized event spool adapter + daily command
```

The stable core contract is:

- normalized event JSONL input
- append-only ledger and registries
- `scripts/raw-os` CLI
- explicit JSON read APIs such as `evidence-search` and `raw-replay`

OpenClaw, Telegram commands, cron, systemd, launchd, and delivery are adapters
around the core. They are not required for the first install.

## 1. Identify The Target

Collect these facts before running commands:

- target agent id
- target workspace root
- timezone
- anchor time
- mainline name
- expected event spool path
- whether the workspace is live production or shadow/test
- whether delivery is in scope now

If any of these are unknown, stop and ask the owner. Do not guess sender ids,
mainline identity, timezone, or delivery target.

## 2. Get The Code

Preferred public install:

```bash
git clone <raw-os-repo-url> raw-os
cd raw-os
```

Private repo install is also valid, but first configure Git authentication:

```bash
git clone <private-raw-os-repo-url> raw-os
cd raw-os
```

Release artifact install is valid when the owner provides a tarball/zip:

```bash
mkdir -p raw-os
tar -xzf raw-os-<version>.tar.gz -C raw-os --strip-components=1
cd raw-os
```

Do not require the repo to be public. Public only removes the Git auth step.

## 3. Verify Core Environment

Run:

```bash
python3 -m py_compile src/raw_os_core.py
python3 -m unittest discover -s tests -v
scripts/raw-os-smoke
```

Expected:

- `py_compile` exits 0.
- unittest exits 0.
- smoke prints `raw-os smoke ok`.

If these fail, fix the environment before creating config or touching any live
workspace.

Minimum environment:

- Linux or macOS.
- Python 3.9+.
- POSIX shell tools: `bash`, `date`, `mkdir`, `cp`, `find`.
- valid IANA timezone data.
- UTF-8 filesystem/text handling.

`python-docx` is optional. If missing, Raw OS uses the built-in docx fallback.

## 4. Create Agent Config

Start from the generic config:

```bash
cp examples/community.raw-os.example.json examples/<agent-id>.raw-os.json
```

Edit at least:

- `agent.agentId`
- `agent.agentLabel`
- `agent.workspaceRoot`
- `time.timezone`
- `time.anchorTime`
- `mainlines[].name`
- `mainlines[].channels`
- `mainlines[].senderIds`
- `mainlines[].speakerLabels`
- `mainlines[].officialDelivery`

Keep storage paths relative unless there is a deployment-specific reason to
externalize them. Relative storage paths resolve under `agent.workspaceRoot`.

Do not put tokens, API keys, private paths, real raw data, or owner-only notes
inside public example configs.

## 5. Run Read-Only Validation

Run:

```bash
scripts/raw-os validate-config --config examples/<agent-id>.raw-os.json
scripts/raw-os doctor --config examples/<agent-id>.raw-os.json
```

Expected:

- `validate-config` returns `ok=true`.
- `doctor` returns `ok=true`.
- `fatal_count=0`.
- `root` is exactly the intended workspace root.

If an event spool already exists, validate it too:

```bash
scripts/raw-os doctor \
  --config examples/<agent-id>.raw-os.json \
  --spool /path/to/events.jsonl
```

Expected:

- `spool_readable` is ok.
- `spool_jsonl_shape` is ok.
- sample records have stable `event_id` and `timestamp` or `ts`.

If the target root is a live OpenClaw workspace, `doctor` may warn that writes
are blocked. That is expected until the owner approves the write step.

## 6. Initialize Storage

For a non-live test workspace:

```bash
scripts/raw-os init --config examples/<agent-id>.raw-os.json
```

For an approved live OpenClaw workspace:

```bash
RAW_OS_ALLOW_OPENCLAW_WORKSPACE=1 \
scripts/raw-os init --config examples/<agent-id>.raw-os.json
```

For protected production roots, configure the root list and use the stronger
guard only when explicitly approved:

```bash
RAW_OS_PROTECTED_WORKSPACE_ROOTS=/path/to/protected/workspace \
RAW_OS_ALLOW_OPENCLAW_WORKSPACE=1 \
RAW_OS_ALLOW_PROTECTED_WORKSPACE=1 \
scripts/raw-os init --config examples/<agent-id>.raw-os.json
```

Expected storage lanes:

- `raw-ledger/`
- `asset-registry/`
- `delivery-registry/`
- `assets/`
- `raw-md/`
- `raw-docx/`
- `raw-memory-md/`
- `tmp/raw-os-state/`
- `tmp/raw-report-incidents/`

## 7. Connect A Normalized Event Spool

The target runtime needs a thin adapter that appends normalized event JSONL.
The adapter may be OpenClaw, Codex/ACP, another runtime hook, or a custom
bridge.

Minimum event fields:

```json
{
  "schema": "raw-os-normalized-event/v1",
  "event_id": "stable-source-id",
  "timestamp": "2026-05-27T08:00:00+08:00",
  "speaker": "user",
  "sender": {"id": "example-user-1", "label": "User"},
  "content_parts": [{"type": "text", "text": "hello"}]
}
```

Recommended fields:

- `channel`
- `provider`
- `chat_id`
- `message_id`
- `session_key`
- `attachment_refs`
- `delivery`
- `ingest_metadata`

The adapter must not render raw-md/docx directly. It only writes normalized
events.

## 8. Run First Daily Pipeline

Set the day using the deployment timezone:

```bash
DAY=$(TZ=<timezone> date +%F)
```

Run the standard pipeline:

```bash
scripts/raw-os daily \
  --config examples/<agent-id>.raw-os.json \
  --anchor-day "$DAY" \
  --mainline <mainline> \
  --spool /path/to/events.jsonl \
  --stateful
```

For approved live OpenClaw roots, add the write guard:

```bash
RAW_OS_ALLOW_OPENCLAW_WORKSPACE=1 \
scripts/raw-os daily \
  --config examples/<agent-id>.raw-os.json \
  --anchor-day "$DAY" \
  --mainline <mainline> \
  --spool /path/to/events.jsonl \
  --stateful
```

`daily` runs:

1. ingest normalized event spool
2. render raw-md
3. render official docx
4. render memory projection
5. audit

Expected output:

- `ok=true`
- `audit.ok=true`
- `ingest.ingested` or `ingest.state_skipped` reflects the spool state
- paths are under the intended workspace root

## 9. Verify Installed Artifacts

After one successful `daily` run, the target workspace should contain these
artifact lanes:

```text
raw-ledger/                 append-only source evidence events
asset-registry/             asset metadata and capture status
assets/                     captured asset files when available
delivery-registry/          delivery attempts and outcomes, if delivery is enabled
raw-md/                     rendered daily raw Markdown
raw-docx/                   rendered official daily docx
raw-memory-md/              distilled memory projection
tmp/raw-os-state/audits/    audit JSON per day/mainline
tmp/raw-os-state/           ingest checkpoints and runtime state
tmp/raw-report-incidents/   incident records when checks fail
```

For a promoted automated deployment, also leave explicit operational artifacts:

```text
<deployment-wrapper>        owner-approved script that runs the daily command
<scheduler-entry>           cron, systemd timer, launchd plist, or equivalent
tmp/raw-os-logs/            scheduler/daily logs
<delivery-adapter>          optional sender for official docx/raw-md
<operator-command>          optional runtime command such as /raw
```

Do not mark cron, delivery, or an operator command as first-install
requirements. First install is accepted by ledger/render/audit/retrieval.
Automation is promotion work and should be added only after shadow acceptance.

`scripts/raw-os daily` is a one-shot batch command. It is not a resident
watchdog, and it should not be scheduled every 30 seconds. During promotion,
schedule it at the chosen daily anchor time. If the deployment needs
near-real-time capture, wire a runtime adapter / spool ingest path separately;
do not simulate that by high-frequency cron.

Concrete examples:

- First install only: run `init`, write or ingest one sample normalized event,
  run `scripts/raw-os daily` once by hand, verify ledger/render/audit/retrieval,
  and stop. Do not install cron, systemd, launchd, delivery, or `/raw`.
- Promoted automated deployment: after shadow acceptance and owner approval,
  add one wrapper plus one scheduler. Linux with systemd uses a user-level
  service plus timer. macOS uses a launchd user agent. Cron is the portable
  fallback.

Wrong implementation:

```text
*/30 * * * * scripts/raw-os daily ...
```

That is wrong because `daily` is the daily render/audit batch, not the runtime
capture loop. Near-real-time capture must be implemented as an adapter or spool
ingest path.

## 10. Verify Evidence

Check files:

```bash
ls -la <workspace-root>/raw-ledger/
ls -la <workspace-root>/raw-md/
ls -la <workspace-root>/raw-docx/
ls -la <workspace-root>/raw-memory-md/
ls -la <workspace-root>/tmp/raw-os-state/audits/
```

Run explicit evidence retrieval:

```bash
scripts/raw-os evidence-search \
  --config examples/<agent-id>.raw-os.json \
  --anchor-day "$DAY" \
  --mainline <mainline> \
  --query "<known text>"

scripts/raw-os raw-replay \
  --config examples/<agent-id>.raw-os.json \
  --anchor-day "$DAY" \
  --mainline <mainline> \
  --event-id <event-id>
```

Acceptance:

- rendered raw is in timestamp order.
- known conversation snippets are present.
- assets are represented by registry records and pointers, not pasted bodies.
- capture failures are recorded with reasons.
- delivery evidence, if present, is separate from content evidence.
- rerunning stateful ingest does not duplicate ledger events.

## 11. Shadow Soak

Before promotion, run shadow mode for at least 3 consecutive local days.

Daily acceptance:

- inbound human events and outbound assistant events are both represented.
- `audit.ok=true`.
- evidence search and replay can recover a known event.
- no unresolved incident exists under `tmp/raw-report-incidents/`.
- spot checks match the actual channel conversation.
- missing media or unsupported media becomes audit evidence, not silent loss.

Do not replace an existing production raw/reporting path during the soak.

## 12. Optional Automation

Only after manual acceptance, add a deployment-owned wrapper and scheduler.

Raw OS does not automatically install a service during first install. The agent
must choose the scheduler explicitly during promotion, based on the target
platform and owner approval:

- macOS: prefer `launchd` user agent.
- Linux with systemd: prefer a user-level `systemd` service + timer.
- Minimal Linux / portable fallback: use `cron`.

Always dry-run by writing the proposed wrapper and scheduler files into the
workspace first. Show the owner:

- wrapper path
- scheduler path or crontab line
- daily command
- log path
- enable/load command
- rollback command

Do not run `launchctl load`, `systemctl enable`, or `crontab` until the owner
approves the exact generated files/line.

Promotion means the deployment owner has accepted the shadow output and wants
Raw OS to run automatically on that machine. It is not part of first install,
and it is not a generic "make it run constantly" step.

Required wrapper shape:

```bash
#!/usr/bin/env bash
set -euo pipefail
cd /path/to/raw-os
DAY="$(TZ=<timezone> date +%F)"
exec scripts/raw-os daily \
  --config examples/<agent-id>.raw-os.json \
  --anchor-day "$DAY" \
  --mainline <mainline> \
  --spool /path/to/events.jsonl \
  --stateful
```

For live OpenClaw roots, include `RAW_OS_ALLOW_OPENCLAW_WORKSPACE=1` inside the
wrapper only after owner approval.

Cron fallback shape:

```cron
0 8 * * * /path/to/raw-os/run-raw-os-daily.sh >> /path/to/workspace/tmp/raw-os-logs/official.log 2>&1
```

Linux systemd user timer shape:

```ini
# ~/.config/systemd/user/raw-os-daily.service
[Unit]
Description=Raw OS daily run

[Service]
Type=oneshot
ExecStart=/path/to/raw-os/run-raw-os-daily.sh
```

```ini
# ~/.config/systemd/user/raw-os-daily.timer
[Unit]
Description=Run Raw OS daily

[Timer]
OnCalendar=*-*-* 08:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable only after approval:

```bash
systemctl --user daemon-reload
systemctl --user enable --now raw-os-daily.timer
systemctl --user list-timers raw-os-daily.timer
```

macOS launchd user agent shape:

```xml
<!-- ~/Library/LaunchAgents/com.example.raw-os.daily.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.example.raw-os.daily</string>
  <key>ProgramArguments</key>
  <array>
    <string>/path/to/raw-os/run-raw-os-daily.sh</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key><integer>8</integer>
    <key>Minute</key><integer>0</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>/path/to/workspace/tmp/raw-os-logs/official.out.log</string>
  <key>StandardErrorPath</key>
  <string>/path/to/workspace/tmp/raw-os-logs/official.err.log</string>
</dict>
</plist>
```

Load only after approval:

```bash
launchctl load ~/Library/LaunchAgents/com.example.raw-os.daily.plist
launchctl list | grep raw-os
```

Prefer a small checked-in wrapper script per deployment so the schedule is
auditable.

## 13. Optional Delivery

Delivery is not part of first install.

When enabling delivery:

- use a deployment adapter, not `daily --send`.
- send canonical deliverables such as official docx or raw-md.
- record delivery evidence in `delivery-registry/`.
- keep content audit separate from delivery success.

## 14. Optional Operator UI

A runtime command such as `/raw` is optional.

Do not use command visibility as the acceptance line. Acceptance is:

- CLI contract works.
- ledger/render/audit works.
- evidence search/replay works.

Only enable an operator command after the core install is accepted.

## 15. Public Repo Boundary

If installing from or preparing a public repo:

- public core uses Apache-2.0.
- real configs, tokens, raw ledgers, assets, delivery registries, and owner
  mappings stay private/local.
- private production snapshots must not be published as public
  core unless separately sanitized and approved.
- run `docs/publish-audit.md` before changing visibility or cutting a release.

Public repo is not required. Private repo or release artifact installs are
valid when authentication is configured.

## 16. Failure Handling

If `doctor` fails:

- read `fatal_count` and failed check names.
- fix Python, shell tools, timezone, config, root, or spool shape first.
- do not run `init` or `daily` until fatal checks are resolved.

If `daily` fails:

- inspect the JSON output.
- check `tmp/raw-report-incidents/`.
- validate the spool with `doctor --spool`.
- run lower-level commands only for debugging:

```bash
scripts/raw-os ingest-spool --config examples/<agent-id>.raw-os.json --anchor-day "$DAY" --mainline <mainline> --spool /path/to/events.jsonl --stateful
scripts/raw-os render-day --config examples/<agent-id>.raw-os.json --anchor-day "$DAY" --mainline <mainline>
scripts/raw-os render-official-docx --config examples/<agent-id>.raw-os.json --anchor-day "$DAY" --mainline <mainline>
scripts/raw-os render-memory-day --config examples/<agent-id>.raw-os.json --anchor-day "$DAY" --mainline <mainline>
scripts/raw-os audit-day --config examples/<agent-id>.raw-os.json --anchor-day "$DAY" --mainline <mainline>
```

If rendered content is wrong:

- verify event timestamps.
- verify the adapter did not mislabel speaker/channel/mainline.
- verify stateful ingest did not skip the expected event.
- replay the event from ledger before changing renderer logic.

## Done Definition

The install is done when:

- environment checks pass.
- storage is initialized in the intended root.
- a real normalized event spool is ingested.
- daily render creates raw-md, docx, memory projection, and audit.
- audit is ok.
- evidence search and replay recover known source events.
- the owner accepts the shadow output.

Anything beyond that is promotion work, not first install.
