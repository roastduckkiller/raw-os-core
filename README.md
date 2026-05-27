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
