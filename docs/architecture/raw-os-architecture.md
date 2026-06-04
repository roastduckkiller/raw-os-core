# Raw OS Architecture

## 一句话

Raw OS 是 agent runtime 与 memory 之间的 near-lossless evidence substrate。

它不是“每天生成一份 raw 文档”的脚本，也不是某个 agent 的 raw patch。它是一套可安装、可配置、可审计、可迁移的证据层产品。

产品主链：

```text
runtime/channel event tap
  -> normalized event
  -> asset capture/store
  -> asset registry
  -> delivery registry
  -> mainline resolver
  -> append-only raw ledger
  -> render/audit/memory projection
```

## 核心原则

1. **runtime evidence first**
   - 生产主链必须接在 runtime ingress / egress / delivery 层。
   - mutable transcript 只能作为 backfill/debug source，不能作为 production source of truth。

2. **先事件，后 raw**
   - 各 channel / plugin 的输入不能直接进入 raw 主链。
   - Telegram、iMessage、Weixin、Slack、QQ、企业微信等输入必须先正规化为 normalized event。

3. **先证据，后认知**
   - Raw OS 记录的是可追溯证据层。
   - Memory 是认知层，不能替代 raw 证据。

4. **文本不是全部对话**
   - 真实对话包括 text、file、image、audio、video、link、reply/thread relation、delivery metadata。
   - 文件/图片/音频/视频本体不塞进 raw 文本，但 raw 必须记录 metadata 和 pointer。

5. **append-only 优先**
   - ledger 默认只追加。
   - 修复、回填、重渲染应该留下 audit trail，而不是静默覆盖历史。

6. **content / asset / delivery 分离**
   - 内容完整，不等于资产捕获成功。
   - 资产捕获成功，不等于投递成功。
   - 投递成功，也不等于 raw evidence 完整。

## 主链分层

### 1. Runtime / Channel Event Tap

职责：在消息发生时捕获证据事件。

生产 tap 应覆盖：
- inbound user message
- assistant outbound final reply
- delivery success/failure/ack
- file/media receive/send/capture result
- reply/thread metadata
- run/session/message correlation

Runtime integrations should expose low-risk hooks such as:

- `message_received`
- `message_sent`

v0 允许先写 append-only spool：

```text
runtime hooks -> raw-os-runtime-tap.jsonl -> ingest-tap-spool -> ledger
```

### 2. Normalized Event

职责：把 channel/runtime-specific event 转成 Raw OS 标准事件。

至少包含：
- event_id
- event_type
- channel / provider
- chat_type / chat_id
- session_key / run_id / trace_id
- sender_id / sender_label / speaker
- message_id / timestamp
- reply_to / thread relation
- content_parts
- attachment_refs
- delivery metadata（如适用）
- ingest_metadata
- source_ref

这里的 `attachment_refs` 只是引用，不是资产本体。

### 3. Asset Capture / Store

职责：捕获非文本资产本体，并落到可追溯位置。

资产包括：
- image
- file/document
- audio/voice
- video
- generated media
- external link snapshot（可选）

原则：
- raw 文本不内嵌资产本体
- 资产必须有稳定 pointer
- 资产必须可校验
- 资产捕获失败也要记录状态和原因

### 4. Asset Registry

职责：维护资产 metadata 与事件之间的映射。

每个 asset 至少应记录：
- asset_id
- source_event_id
- channel / provider
- chat_id / message_id
- original_filename
- mime_type
- byte_size
- sha256
- storage_uri 或 local_path
- capture_status
- created_at
- caption / surrounding_text
- derived_metadata
  - OCR text
  - transcription
  - image summary
  - document extracted text
  - model/version/source

### 5. Delivery Registry

职责：维护 outbound delivery evidence。

每次投递至少应记录：
- delivery_id
- source_event_id / deliverable_id
- channel / provider
- target / chat_id / thread_id
- channel_message_id（如果有）
- status: pending / sent / failed / retried / cancelled
- error / fallback reason
- sent_at / acknowledged_at
- media/file delivery result

Delivery Registry 不替代 Raw Ledger；它记录“证据是否送达”。

### 6. Identity / Mainline Resolver

职责：把不同 channel 的身份映射到同一条 mainline。

不能把 mainline 等同于单个 Telegram sender_id。

需要支持：
- cross-channel identity mapping
- relation-level identity
- group/member context
- principal / assistant role resolution
- deployment-specific routing policy

### 7. Append-only Raw Ledger

职责：保存 Raw OS 的底账。

ledger event 应记录：
- normalized event snapshot
- clean_text
- content parts
- asset pointers
- delivery refs
- source refs
- mainline attribution
- classification / drop reason
- anchor window attribution
- audit metadata

ledger 不是 raw-md。ledger 是 source of truth。

### 8. Render / Stage / Official

职责：从 ledger 渲染人可读产物。

Raw OS 应保留经过生产验证的 raw discipline：
- anchor-time discipline
- stage/fragment as first-class output
- noop window
- backfill
- repair
- validation / audit

输出可包括：
- official raw md
- official raw docx/html/pdf（按部署需要）
- raw-memory-md / memory projection
- audit report

资产在 raw-md 中应渲染为 metadata block，例如：

```md
[18:21] 你：看这个图
附件：
- image/png · IMG_1234.png
  asset_id: asset_20260428_xxx
  sha256: ...
  path: assets/2026-04-28/asset_20260428_xxx.png
  source: telegram:<chat-id>/message/<message-id>
  capture: captured
```

### 9. Audit / Incident

职责：把证据链完整性变成可检查结果。

Audit 至少检查：
- ledger 可读、event schema 合法
- render 与 ledger 对账
- asset pointer 不断链
- capture failure 有 reason
- delivery status 与 delivery registry 对账
- stateful ingest 没有重复/漏处理

Incident 用于记录失败和修复上下文；不能靠静默 fallback 掩盖缺证据。

### 10. Memory / Evidence Retrieval

职责：把 raw 证据层接入检索和记忆，但不污染默认 recall。

- ledger / raw-md 给显式 evidence search、audit、reconstruction、memory extraction 使用
- asset derived metadata 可以进入 evidence index
- asset 本体通常不进 memory，只保留 pointer 和摘要
- raw evidence 不应默认混入 conversational memory search
- 默认 recall 应优先使用 distilled memory / topic memory
- 需要原话、现场、审计或证明时，再显式查 raw evidence index

Observed regressions in agent memory deployments show the same pattern:
putting long raw-md documents directly into default memory search amplifies
JSON-output failures, timeouts, rerank noise, and index-shape problems. Raw OS
therefore keeps **default recall** and **evidence retrieval** as two separate
entry points.

## 产品形态

Raw OS 作为完整产品，应至少包含：

- installable package
- config schema / validation / doctor
- runtime tap plugin / adapter
- normalized event ingest
- asset store / registry
- delivery registry
- append-only ledger
- render / audit / incident
- stateful spool ingest / backfill ingest
- deployment wrappers
- shadow mode
- rollback / repair tooling

## 实验与环境边界

- development/incubation environment: design, implementation, static checks
- test host: live integration and runtime hook experiments
- production host: read-only checks or low-risk static inspection until the
  deployment owner explicitly approves promotion

## v0 产品边界

Raw OS v0 应证明：

1. runtime tap 事件可以进入 append-only spool
2. spool 可以 stateful ingest 到 ledger
3. normalized event schema 能覆盖 user / assistant / delivery 基本事件
4. asset capture / failed capture 能进入 registry
5. ledger 可以 render raw-md / raw-memory-md
6. audit 能发现断链和缺失
7. transcript adapter 只作为 backfill/debug，不是生产主链

v0 可以先不做复杂 UI，但不能省略 runtime tap、asset pointer、audit/incident 这些产品骨架。
