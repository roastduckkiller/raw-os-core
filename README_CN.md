# Raw OS

[English](README.md) | [中文](README_CN.md)

Raw OS 是给智能体系统使用的可信事件、资产与 raw 证据底座。

Raw OS 不是操作系统内核。它是 agent runtime 和 memory 之间的 evidence
operating substrate。

主链路：

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

## 安装

给人看的入口：

```text
请让你的 agent 阅读 INSTALL-FOR-AGENTS.md 并执行安装。
```

给 agent 的最小检查：

```bash
scripts/raw-os validate-config --config examples/community.raw-os.example.json
scripts/raw-os doctor --config examples/community.raw-os.example.json
scripts/raw-os-smoke
```

## 公开边界

public core 只包含通用代码、schema、合成示例、文档和测试。真实部署配置、
credential、raw ledger、asset store、owner mapping、host-specific script、
private runtime snapshot 都不属于 public core。

发布 repo 或 artifact 前先看 `docs/publish-audit.md`。

## 关键文档

- `INSTALL.md` - 给人看的安装入口
- `INSTALL-FOR-AGENTS.md` - 给 agent 看的安装 runbook
- `docs/requirements.md` - 部署环境要求
- `docs/publish-audit.md` - 公开发布前清理清单
- `docs/naming.md` - 命名边界

## License

Apache-2.0. 见 `LICENSE`。
