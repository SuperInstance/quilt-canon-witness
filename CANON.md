# Canon — quilt-canon-witness

## What this tool is

A cryptographic witness log. Each record chains to the previous via FNV-1a 64 hash. Append-only, tamper-evident, verifiable. JSONL persistence.

## How it proves itself

**It runs.** `pip install -e .` then `quilt-canon-witness append ... && quilt-canon-witness verify`. Tested with 8 tests in `run_tests.py`.

**It polyformalisms.** The canary hash `0x24a555471370b18d` matches across the fleet's 5 ports.

**It measures.** Records carry `probe_composite` (JEV score). Chain validates cryptographic continuity. Tampering is detected.

## Doctrines it instantiates

- **`witness_log_is_prediction`** — this IS the witness log doctrine, made executable
- **`canon_gate_is_chord`** — multiple agents witness → multiple records → chord consensus
- **`cells_are_scars`** — every record is a scar; the log remembers everything

## Chain design

Each witness:
- `witness_id` = FNV-1a-64(prev_hash | timestamp | lore_ref | excerpt | composite | doctrines | agent | note)
- `prev_hash` = the previous witness's `witness_id` (or GENESIS_HASH if first)

Tampering with any field breaks the chain. `verify_chain()` walks all records and re-derives each `witness_id`, comparing to stored values.

## Commands

1. `append <lore_ref> <lore_text> --composite X --doctrines A,B --agent Y` — append witness
2. `verify` — verify chain integrity
3. `get [--witness-id X | --lore-ref Y | --agent Z]` — query witnesses
4. `stats` — log statistics (n_witnesses, agents, mean_composite, chain_valid)
5. `export --output FILE` — export full chain as JSON

## Fleet usage

- **`quilt-multi-oracle`** — every probe can be witnessed
- **`quilt-iterator`** — every iteration step can be witnessed
- **`quilt-canon-mcp`** — exposes witness as MCP tool (extension point)
- **`quilt-fleet-conductor`** — can call witness in workflows

## Why this matters

The substrate walker canon has been mostly text. Now it has a **ledger**. Every canon event has a witness. The chain IS the prediction: the next witness will reference the previous one's hash, and so on, forever.
