# Raw OS Publish Audit

Use this checklist before publishing Raw OS as a public repo or public release
artifact.

The public package should contain generic core code, schemas, docs, example
configs, tests, and installers. It must not contain live agent data or secrets.

## Must Not Publish

- Real raw ledger files.
- Real transcripts or session exports.
- Real assets, images, audio, video, documents, or captured attachments.
- Tokens, API keys, bot tokens, OAuth state, cookies, or private keys.
- Real Telegram ids, chat ids, phone numbers, emails, or owner mappings.
- Customer/user names or private relationship context.
- Private hostnames, internal IPs, SSH aliases, launchd/systemd labels, or
  machine-specific paths that identify a live deployment.
- AD production raw snapshot data.
- Deployment logs containing private message bodies or identifiers.

## Repo Split

Public:

- Raw OS core implementation.
- `scripts/raw-os` CLI wrapper.
- JSON schemas and normalized event examples with fake values.
- Generic deployment docs.
- Tests using synthetic fixtures.
- Apache-2.0 `LICENSE`.

Private or local:

- Real config files.
- Adapter credentials.
- Delivery credentials.
- Raw ledgers.
- Asset stores.
- Delivery registries.
- Owner/mainline mappings.
- Host-specific cron, launchd, or systemd wrappers.
- Any private production snapshot unless it has been separately sanitized and
  explicitly approved for publication.

Optional adapters:

- Harness-specific adapters may be public if they contain no private runtime
  internals or secrets.
- Adapters with internal OpenClaw assumptions can remain private while the core
  stays public.

## Example Config Rules

Example configs must use fake values:

- Fake agent id and label.
- Fake workspace path such as `/opt/raw-os/workspaces/example-agent`.
- Fake sender ids such as `example-user-1`.
- Fake channel ids such as `telegram:example`.
- No real delivery target.
- No real token environment variable values.

It is acceptable to name environment variable placeholders, for example
`RAW_OS_DELIVERY_TOKEN`, but not to include actual values.

## Mechanical Checks

Run these before publication:

```bash
git status --short
rg -n "OPENAI_API_KEY|BOT_TOKEN|TOKEN|SECRET|PRIVATE KEY|BEGIN .*KEY|telegram:[0-9]+|[0-9]{9,}|/(Users|home)/[^[:space:]]+|192\\.168\\." .
find . -type f \( -name "*.jsonl" -o -name "*.docx" -o -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.mp3" -o -name "*.mp4" \) -print
```

Any hit must be reviewed. Some docs may mention patterns intentionally; private
identifiers and artifacts must be removed or replaced with synthetic values.

## Release Gate

A public release is acceptable only when:

- The repo contains a license.
- The public tree contains no live data or secrets.
- Tests and smoke pass on a clean checkout.
- `docs/requirements.md` and deployment guide describe the environment clearly.
- Public examples can run without OpenClaw, Telegram, or private credentials.
