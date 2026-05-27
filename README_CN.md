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

## 怎么知道装好了？

Raw OS 装好不是指 repo clone 成功，而是目标 agent 能拿出这些证据：

- 环境检查通过：`doctor.ok=true` 且 `fatal_count=0`
- storage 建在预期 workspace root 下
- normalized event spool 可以被 ingest
- `daily` 能生成 raw-md、official docx、memory projection、audit
- `audit.ok=true`
- `evidence-search` 能搜回已知原文
- `raw-replay` 能按 event id 还原已知事件

最小验收命令：

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

## 装好以后会产出什么？

首次安装并成功跑完一次 `daily` 后，目标 workspace 里应该有：

- `raw-ledger/` - append-only source evidence events
- `asset-registry/` - 资产 metadata 和 capture 状态
- `assets/` - 成功捕获的资产文件
- `delivery-registry/` - delivery attempts / outcomes，只有启用 delivery 时才有意义
- `raw-md/` - 每日 raw Markdown
- `raw-docx/` - official daily docx
- `raw-memory-md/` - 给下游 memory importer 用的 distilled projection
- `tmp/raw-os-state/audits/` - 每天/每条 mainline 的 audit JSON
- `tmp/raw-os-state/` - ingest checkpoint 和运行状态
- `tmp/raw-report-incidents/` - 检查失败时的 incident records

promotion 到自动化部署后，agent 还可能加：

- deployment-owned daily wrapper script
- cron/systemd/launchd schedule，定时跑 `scripts/raw-os daily`
- 日志文件，例如 `tmp/raw-os-logs/official.log`
- optional delivery adapter，用来发送 official docx/raw-md
- optional operator command，例如 `/raw`

cron 和 delivery 不是首次安装的必要条件。首次安装的验收线是 ledger、render、
audit、retrieval 跑通；自动化属于 promotion。

Raw OS 首次安装时不会自动安装 service。promotion 阶段由 agent 按平台选择：

- macOS：`launchd` user agent
- Linux 且有 systemd：user-level `systemd` service + timer
- 便携 fallback：`cron`

agent 应先展示生成的 wrapper、scheduler 文件/行、log path、enable command、
rollback command，再启用自动化。

## 装好了怎么用？

人通常不直接操作 Raw OS。正确用法是让你的 agent 安装它，并接一个 runtime
adapter，把消息/事件写成 normalized event JSONL。

之后日常链路是：

```text
runtime adapter 写 events.jsonl
  -> agent 跑 scripts/raw-os daily
  -> Raw OS 生成 raw-ledger、raw-md、raw-docx、raw-memory-md、audit
  -> 需要证据或还原时，用 evidence-search / raw-replay 查询
```

常用命令：

```bash
# daily production/shadow run
scripts/raw-os daily --config <config> --anchor-day <day> --mainline <mainline> --spool <events.jsonl> --stateful

# 搜 source evidence
scripts/raw-os evidence-search --config <config> --anchor-day <day> --mainline <mainline> --query "<text>"

# 还原单个 source event
scripts/raw-os raw-replay --config <config> --anchor-day <day> --mainline <mainline> --event-id <event-id>
```

Raw OS 不是聊天界面，不替代 memory，也不是 delivery bot。它是这些能力下面的证据层。

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
