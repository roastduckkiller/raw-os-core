# Raw OS Memory Architecture Decision

## Decision

Raw OS memory direction will not use `raw-md` as a default memory collection.

Raw OS will split memory into four lanes:

```text
1. default memory      -> small, stable, distilled, prompt-safe
2. topic memory        -> project/topic/task episodes with provenance
3. evidence search     -> explicit source lookup over ledger/assets/delivery
4. raw replay          -> audit/reconstruction bundle from source-of-truth stores
```

The source of truth remains:

```text
normalized event
  -> asset registry
  -> delivery registry
  -> append-only ledger
```

Human-readable raw outputs remain render artifacts:

```text
ledger -> raw-md / docx / audit reports
```

Memory projections are derived products:

```text
ledger + asset registry + delivery registry
  -> memory projection
  -> default/topic memory handoff
  -> explicit evidence retrieval index
```

## Why raw-md must not be default memory

`raw-md` is useful for humans and audit, but harmful as a default recall collection.

Observed / expected failure modes:

- high noise: timestamps, delivery metadata, asset ids, sha256, paths, partial intermediate states
- long retrieval chunks: a daily raw file can dominate prompt budget
- wrong abstraction level: daily raw answers with fragments, not stable facts / preferences / SOPs
- stale state risk: intermediate statements may be recalled as current truth
- provenance inversion: memory would depend on a rendered artifact instead of ledger source of truth
- asset/delivery pollution: evidence metadata is useful for proof, not for ordinary conversational recall
- search instability: repeated same-topic messages create false positives and duplicate recall

Therefore:

```text
raw-md default_recall = false
raw-ledger default_recall = false
raw-memory projection default_recall = allowed only when compact + provenance-safe
```

## Reference designs reviewed

### TencentDB Agent Memory

Useful patterns:

- long-term hierarchy: `L0 Conversation -> L1 Atom -> L2 Scenario -> L3 Persona`
- short-term offload: `refs/*.md -> offload jsonl -> Mermaid MMD -> prompt injection`
- recall split:
  - dynamic relevant memories in user prompt prefix
  - stable persona / scene navigation in system append
- provenance:
  - L1 keeps `source_message_ids`, `sessionKey`, timestamps
  - offload MMD node id drills down to jsonl entry and raw `refs/*.md`
- token control:
  - max results, score threshold, timeout
  - MMD token budget ratio
  - active MMD only; historical MMD only when needed

Do not copy blindly:

- Persona generation can over-generalize; Raw OS needs confidence, validity windows, contradiction handling.
- LLM-written scene/persona files require schema validation, diff/audit, rollback.
- Mermaid is good for engineering task maps, but not necessarily all memory domains.
- LLM-only task-boundary detection is too soft for multi-agent / multi-channel Raw OS; deterministic routing is still needed.

### Zep / Graphiti

Most relevant external model for Raw OS.

Useful patterns:

```text
Episode(raw event) -> Fact/entity/relation -> temporal graph -> summary/community
```

Key idea:

- raw episodes are ground truth
- derived facts trace back to episodes
- facts can have temporal validity: `valid_from`, `valid_to`, `learned_at`
- retrieval returns fact + provenance, not orphaned summary

Raw OS should adopt this shape, but start with simple JSONL/SQLite before graph complexity.

### Letta / MemGPT

Useful memory hierarchy:

- core memory: small, always visible
- recall memory: searchable history
- archival memory: external large store
- message buffer: recent context

Raw OS mapping:

```text
core memory      -> stable default projection / SOP / active constraints
recall memory    -> topic memory / recent episode summaries
archival memory  -> evidence search over ledger/assets/delivery
message buffer   -> runtime/session context outside Raw OS
```

### Mem0 / OpenMemory

Useful for lifecycle:

```text
extract -> consolidate -> update/delete -> retrieve
```

But not enough as Raw OS foundation because source lineage is weaker than Raw OS requires.

### LlamaIndex / LangGraph

Useful patterns:

- token-budgeted memory blocks
- citation/source nodes
- namespace separation

But provenance and audit must be enforced by Raw OS itself.

## Raw OS memory model

Raw OS will use evidence-first layered memory:

```text
R0 Evidence Event
  append-only ledger event + asset/delivery pointers

R1 Evidence Atom
  minimal extracted fact from one or more events
  includes provenance refs

R2 Episode / Topic Memory
  clustered task/topic/day scene summary
  includes event refs and open loops

R3 Stable Memory Candidate
  durable preference / SOP / system rule / relationship fact
  includes confidence, validity, source refs, review state

R4 Working Memory Block
  small token-budgeted prompt surface
  selected from approved R2/R3, never from raw-md directly

R5 Evidence Map
  symbolic navigation graph over R0/R1/R2
  used for drill-down, not as fact source
```

## Required schemas

### raw-memory-projection/v1

```json
{
  "schema": "raw-memory-projection/v1",
  "projection_id": "memproj_...",
  "lane": "default|topic",
  "anchor_day": "2026-05-14",
  "mainline": "sheng-shu",
  "scope": {
    "user": "sheng-shu",
    "agent": "adit",
    "project": "raw-os",
    "topic": "memory-architecture"
  },
  "summary": "compact summary",
  "facts": [
    {
      "fact_id": "fact_...",
      "type": "preference|sop|decision|task_state|relationship|incident",
      "content": "...",
      "confidence": 0.8,
      "valid_from": "2026-05-14T00:00:00Z",
      "valid_to": null,
      "source_event_ids": ["evt_..."],
      "source_asset_ids": [],
      "source_delivery_ids": [],
      "last_verified_at": "2026-05-14T00:00:00Z"
    }
  ],
  "open_loops": [],
  "default_recall_allowed": true,
  "token_budget_hint": 1200,
  "created_at": "..."
}
```

### raw-evidence-search-result/v1

```json
{
  "schema": "raw-evidence-search-result/v1",
  "query": "...",
  "matches": [
    {
      "rank": 1,
      "kind": "event|asset|delivery",
      "event_id": "evt_...",
      "snippet": "...",
      "source_ref": {},
      "asset_refs": [],
      "delivery_refs": [],
      "ranking_reason": "keyword match"
    }
  ]
}
```

### raw-replay-bundle/v1

```json
{
  "schema": "raw-replay-bundle/v1",
  "replay_id": "replay_...",
  "window": {
    "anchor_day": "2026-05-14",
    "start": null,
    "end": null,
    "event_ids": []
  },
  "events": [],
  "assets": [],
  "deliveries": [],
  "integrity": {
    "ledger_ok": true,
    "asset_refs_ok": true,
    "delivery_refs_ok": true,
    "issues": []
  }
}
```

## Retrieval policy

### Default memory

Allowed:

- stable user preferences
- durable SOPs
- active project constraints
- unresolved open loops
- high-confidence task state

Not allowed:

- full raw-md chunks
- unreviewed large raw snippets
- sha256/path-heavy asset metadata
- delivery/capture failure details unless directly relevant
- intermediate contradictory statements without validity markers

### Topic memory

Allowed:

- project/topic summaries
- decisions and alternatives
- open questions
- relevant event refs

Used when user asks about a project or ongoing workstream.

### Evidence search

Explicit only.

Triggers:

- “给我看证据”
- “原话是什么”
- “哪里能看到”
- audit/debug/reconstruction
- delivery/file/asset proof

Returns refs and snippets, not whole raw days.

### Raw replay

Explicit only.

Used for:

- incident review
- legal/audit style proof
- reconstructing a time window
- checking ledger/render/asset/delivery consistency

## Commands to add

```bash
scripts/raw-os project-default-memory \
  --config <config> \
  --anchor-day <day> \
  --mainline <mainline>

scripts/raw-os project-topic-memory \
  --config <config> \
  --anchor-day <day> \
  --mainline <mainline> \
  --topic <topic-or-query>

scripts/raw-os evidence-search \
  --config <config> \
  --anchor-day <day> \
  --mainline <mainline> \
  --query <query> \
  --limit 10

scripts/raw-os raw-replay \
  --config <config> \
  --anchor-day <day> \
  --mainline <mainline> \
  --event-id <event-id>
```

`render-memory-day` may remain as a legacy/simple projection, but should not be the main product surface.

## Implementation order

### Phase 1: boundary and schemas

- add architecture docs for four lanes
- add schema constants in `src/raw_os_core.py`
- update README retrieval boundary
- update production acceptance lines

### Phase 2: stdlib MVP

- implement `project-default-memory`
- implement `project-topic-memory` with keyword/topic filtering
- implement `evidence-search` as linear JSONL search
- implement `raw-replay` from ledger + asset registry + delivery registry
- extend smoke tests

No embedding dependency in Phase 2.

### Phase 3: ranking and graph

- add SQLite FTS / BM25 index for evidence search
- add fact store with validity windows
- add optional entity/relation graph
- add token-budgeted context assembler

### Phase 4: OpenClaw integration

- expose explicit tools:
  - `raw_os_evidence_search`
  - `raw_os_raw_replay`
  - `raw_os_topic_memory`
- default prompt only receives compact approved memory blocks
- raw evidence tools remain explicit and bounded

## Acceptance lines

A Raw OS memory implementation is acceptable only if:

- raw-md is not part of default recall
- every default/topic memory item has source event refs
- evidence search returns event/asset/delivery refs
- raw replay reads from ledger/registries, not from rendered raw-md
- asset and delivery semantics are not silently flattened into ordinary memory
- stale facts can be marked with validity windows or superseded state
- memory projection is reproducible from evidence stores
- smoke tests verify lane separation

## One-line architecture

Raw OS memory is not “put raw into memory”.

It is:

```text
evidence-first ledger
  -> provenance-preserving projection
  -> token-budgeted memory blocks
  -> explicit drill-down when proof is needed
```
