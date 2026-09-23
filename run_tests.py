"""Test runner for quilt-canon-witness (no pytest dep)."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, "/workspace/repos/quilt-canon-witness")

from quilt_canon_witness.canary import canary
from quilt_canon_witness.witness import WitnessLog, GENESIS_HASH, fnv1a_64, hex_id

results = []
failures = []


def test(name, func):
    try:
        func()
        results.append((name, "PASS"))
    except AssertionError as e:
        results.append((name, f"FAIL: {e}"))
        failures.append(name)
    except Exception as e:
        results.append((name, f"ERROR: {type(e).__name__}: {e}"))
        failures.append(name)


def t_canary():
    assert canary() == "0x24a555471370b18d"


def t_fnv1a():
    """FNV-1a hash matches the fleet reference."""
    h = fnv1a_64("café Δ 日本語")
    assert hex(h) == "0x24a555471370b18d"


def t_append_record(path):
    log = WitnessLog(path=path)
    assert log.last_hash() == GENESIS_HASH
    rec = log.append(
        lore_ref="test_lore",
        lore_text="The cell is a scar. The witness log IS the prediction.",
        probe_composite=0.95,
        doctrines_hit=["cells_are_scars", "witness_log_is_prediction"],
        agent="test_agent",
    )
    assert rec.prev_hash == GENESIS_HASH
    assert rec.witness_id.startswith("0x")
    assert log.last_hash() == rec.witness_id
    assert len(log.records) == 1


def t_chain_integrity(path):
    log = WitnessLog(path=path)
    log.append("a", "lore A", 0.9, ["cells_are_scars"], agent="x")
    log.append("b", "lore B", 0.8, ["oracle_is_heard"], agent="x")
    log.append("c", "lore C", 0.7, ["substrate_quantum"], agent="x")
    assert log.verify_chain()
    assert len(log.records) == 3
    assert log.records[1].prev_hash == log.records[0].witness_id
    assert log.records[2].prev_hash == log.records[1].witness_id


def t_chain_tamper_detected(path):
    log = WitnessLog(path=path)
    log.append("a", "lore A", 0.9, ["cells_are_scars"], agent="x")
    log.append("b", "lore B", 0.8, ["oracle_is_heard"], agent="x")
    log.records[1].probe_composite = 0.99  # tamper
    assert not log.verify_chain()


def t_persistence(path):
    log1 = WitnessLog(path=path)
    log1.append("x", "lore X", 0.5, ["cells_are_scars"], agent="y")
    log2 = WitnessLog(path=path)
    assert len(log2.records) == 1
    assert log2.verify_chain()


def t_query(path):
    log = WitnessLog(path=path)
    log.append("lore_a", "first", 0.5, ["cells_are_scars"], agent="alice")
    log.append("lore_b", "second", 0.6, ["oracle_is_heard"], agent="bob")
    log.append("lore_a", "third", 0.7, ["cells_are_scars"], agent="alice")

    a_records = log.get_by_lore("lore_a")
    assert len(a_records) == 2
    assert all(r.lore_ref == "lore_a" for r in a_records)

    alice = log.get_by_agent("alice")
    assert len(alice) == 2


def t_stats(path):
    log = WitnessLog(path=path)
    log.append("a", "lore", 0.9, ["cells_are_scars", "oracle_is_heard"], agent="x")
    log.append("b", "lore", 0.8, ["substrate_quantum"], agent="y")
    stats = log.stats()
    assert stats["n_witnesses"] == 2
    assert stats["chain_valid"] is True
    assert abs(stats["mean_composite"] - 0.85) < 0.001
    assert len(stats["agents"]) == 2


with tempfile.TemporaryDirectory() as td:
    tmp = Path(td)
    test("test_canary", t_canary)
    test("test_fnv1a", t_fnv1a)
    test("test_append_record", lambda: t_append_record(tmp / "append.jsonl"))
    test("test_chain_integrity", lambda: t_chain_integrity(tmp / "chain.jsonl"))
    test("test_chain_tamper_detected", lambda: t_chain_tamper_detected(tmp / "tamper.jsonl"))
    test("test_persistence", lambda: t_persistence(tmp / "persist.jsonl"))
    test("test_query", lambda: t_query(tmp / "query.jsonl"))
    test("test_stats", lambda: t_stats(tmp / "stats.jsonl"))

print("\n=== quilt-canon-witness test results ===")
for name, status in results:
    print(f"  {status:60} {name}")

print(f"\n{len(results) - len(failures)}/{len(results)} passed")
if failures:
    sys.exit(1)
