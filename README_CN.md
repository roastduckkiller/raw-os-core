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

### 首次安装 vs 转入自动化部署

首次安装只证明 Raw OS 核心链路能跑通。它不是常驻服务，也不会安装守护进程。

首次安装的验收线：

- normalized event 能进入 `raw-ledger/`
- `scripts/raw-os daily` 能完成 render
- audit 通过
- evidence search / replay 能找回证据

转入自动化部署后，agent 才可能加：

- 部署方自有的 daily 封装脚本
- cron/systemd/launchd 调度配置，在固定时间跑一次 daily 封装脚本
- 日志文件，例如 `tmp/raw-os-logs/official.log`
- 可选的投递适配器，用来发送 official docx/raw-md
- 可选的操作命令，例如 `/raw`

cron 和 delivery 不是首次安装的必要条件。首次安装的验收线是 ledger、render、
audit、retrieval 跑通；自动化部署是下一阶段，不属于首次安装。

这里必须分成两条链路。先看正向方案：

- 运行时捕获链路：负责把消息/事件持续写入 spool，并定期或事件触发地执行
  `scripts/raw-os ingest-spool --stateful`。推荐先用低频 tick，例如每 10 分钟一次；
  如果平台支持消息 hook，则由 adapter 事件触发写入 spool。
- 正式日报链路：负责在锚点时间汇总、渲染、audit、生成 official docx/raw-md。
  它只在每天锚点时间跑一次 `scripts/raw-os daily`，例如 08:00。

推荐 cron 形状：

```cron
*/10 * * * * cd /path/to/raw-os && RAW_OS_ALLOW_OPENCLAW_WORKSPACE=1 scripts/raw-os ingest-spool --config examples/<agent-id>.raw-os.json --anchor-day "$(TZ=Asia/Shanghai date +\%F)" --mainline <mainline> --spool /path/to/workspace/tmp/raw-os-runtime-tap.jsonl --stateful >> /path/to/workspace/tmp/raw-os-logs/tick.log 2>&1
0 8 * * * cd /path/to/raw-os && RAW_OS_ALLOW_OPENCLAW_WORKSPACE=1 scripts/raw-os daily --config examples/<agent-id>.raw-os.json --anchor-day "$(TZ=Asia/Shanghai date +\%F)" --mainline <mainline> >> /path/to/workspace/tmp/raw-os-logs/official.log 2>&1
```

也就是说，新增内容由 capture/ingest 链路处理；official raw 由每天 08:00 的日报链路生成。

Raw OS 首次安装时不会自动安装 service。转入自动化部署时，由 agent 按平台选择：

- macOS：`launchd` user agent
- Linux 且有 systemd：user-level `systemd` service + timer
- 便携 fallback：`cron`

agent 应先展示生成的封装脚本、调度器文件/行、日志路径、启用命令、
回滚命令，再启用自动化。

例子：

- 首次安装：跑 `init`，写入或 ingest 一条示例 normalized event，手动跑一次
  `scripts/raw-os daily`，然后验 ledger/render/audit/retrieval。到这里就结束。
  不安装 cron、systemd、launchd、delivery，也不加 `/raw`。
- 转入自动化部署：影子验收通过、负责人批准后，才加一个部署封装脚本和一个平台调度器。
  Linux 且有 systemd 时，用用户级 service + timer 每天跑一次封装脚本；
  macOS 用 launchd user agent；cron 只是便携 fallback。

避免一个常见误装：不要把 `daily` 调度器改成几十秒一次；需要更快捕获时，另建
capture/ingest 任务。

封装脚本就是部署方自己拥有的一小段命令脚本。它把 repo 路径、
config 路径、mainline、spool 路径、timezone 和准确的 `scripts/raw-os daily`
命令固定下来。调度器只负责在指定时间运行这个封装脚本，不负责理解 Raw OS。

最小封装脚本形状：

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
