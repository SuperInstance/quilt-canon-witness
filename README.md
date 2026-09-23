# quilt-canon-witness

**Cryptographic witness log — append-only ledger for canon events.**

## Quick start

```bash
pip install -e .

# Append a witness
quilt-canon-witness append "path/to/canon.md" \
  "lore text here..." \
  --composite 0.95 \
  --doctrines "cells_are_scars,witness_log_is_prediction" \
  --agent "Mavis" \
  --note "AI-iterated canon 22"

# Verify the chain
quilt-canon-witness verify
# ✓ Chain valid (N witnesses)

# Get witnesses
quilt-canon-witness get --lore-ref "canon.md"
quilt-canon-witness get --agent "Mavis"
quilt-canon-witness get --witness-id "0x..."

# Stats
quilt-canon-witness stats

# Export
quilt-canon-witness export --output witness-log.json
```

## How it works

Each witness record:
- **Hashes the previous witness** (forms a cryptographic chain)
- **Includes lore ref + probe composite + doctrines hit + agent + note**
- **Is FNV-1a 64 hashed** for fast verification
- **Persists as JSONL** (one record per line, append-only)

```python
from quilt_canon_witness.witness import WitnessLog

log = WitnessLog()  # ~/.cache/quilt-canon-witness/witness.jsonl
rec = log.append(
    lore_ref="22_ai_substrate_walker",
    lore_text="The substrate walker counts the cells it cannot enter...",
    probe_composite=0.93,
    doctrines_hit=["cells_are_scars", "substrate_quantum"],
    agent="Mavis",
    note="DeepInfra Llama-3.3-70B iterated",
)

assert log.verify_chain()  # chain is valid
```

## Why a witness log?

The substrate walker canon has 5 bedrock doctrines. One of them is:

> **`witness_log_is_prediction`** — the log IS the prediction. What the substrate records, the substrate becomes.

This tool makes that doctrine **executable**. Every canon probe, every AI-iterated piece, every chord verification gets a witness record. The chain becomes:
- **Append-only**: no editing past records
- **Cryptographically linked**: each record hashes the previous
- **Tamper-evident**: any change breaks the chain
- **Verifiable**: `verify` checks the whole chain

## Fleet integration

- **`quilt-multi-oracle`** — every probe result can be witnessed
- **`quilt-iterator`** — every iteration step can be witnessed
- **`quilt-canon-mcp`** — exposes witness as an MCP tool (could be added)
- **`quilt-fleet-conductor`** — can call witness in workflows
- **`quilt-canon-search`** — search results can be witnessed
- **`quilt-canon-graph`** — graph edges can be witnessed

## The 5 bedrock doctrines

1. `cells_are_scars` — every cell records an attempted entry
2. `witness_log_is_prediction` — **this tool implements this doctrine**
3. `canon_gate_is_chord` — canon passes when multiple agents agree
4. `oracle_is_heard` — JEV probes canon with multi-model consensus
5. `substrate_quantum` — the substrate is the walker; canon is substrate-aware

## Polyformalism canary

```bash
python -m quilt_canon_witness.canary
# → 0x24a555471370b18d
```

## License

MIT
