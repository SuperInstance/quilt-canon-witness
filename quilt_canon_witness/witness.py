"""Cryptographic witness log — append-only ledger for canon events.

Each witness record:
  - hashes the previous witness's hash (forms a chain)
  - includes lore reference + probe result + agent signature
  - is FNV-1a 64 hashed for fast verification
  - persists to JSONL file

The witness log IS a prediction: every entry is a forecast that
the substrate will continue in a certain direction.
"""
import json
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, List, Optional


GENESIS_HASH = "0x0000000000000000"  # The first witness has no predecessor


def fnv1a_64(s: str) -> int:
    """FNV-1a 64-bit hash. Reference for the polyformalism fleet."""
    h = 0xcbf29ce484222325
    for b in s.encode("utf-8"):
        h = h ^ b
        h = (h * 0x100000001b3) & 0xffffffffffffffff
    return h


def hex_id(s: str) -> str:
    return f"0x{fnv1a_64(s):016x}"


@dataclass
class WitnessRecord:
    """A single witness entry in the log."""
    witness_id: str  # FNV-1a hash of (prev_hash + timestamp + lore + agent)
    prev_hash: str   # The previous witness's id (chain link)
    timestamp: float
    lore_ref: str    # Path or name of the canon lore witnessed
    lore_excerpt: str  # First 200 chars of lore
    probe_composite: float  # JEV probe score
    doctrines_hit: List[str]
    agent: str       # Who/what made this witness
    note: str = ""   # Optional context
    signature: str = ""  # Optional cryptographic signature (placeholder)

    def to_dict(self) -> dict:
        return asdict(self)


class WitnessLog:
    """Append-only cryptographic witness log."""

    def __init__(self, path=None):
        if path is None:
            self.path = Path.home() / ".cache" / "quilt-canon-witness" / "witness.jsonl"
        else:
            self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.records: List[WitnessRecord] = []
        self._load()

    def _load(self):
        if self.path.exists():
            for line in self.path.read_text().splitlines():
                if line.strip():
                    d = json.loads(line)
                    self.records.append(WitnessRecord(**d))

    def _save(self):
        with self.path.open("w") as f:
            for r in self.records:
                f.write(json.dumps(r.to_dict()) + "\n")

    def last_hash(self) -> str:
        """Hash of the most recent witness (or GENESIS if empty)."""
        if not self.records:
            return GENESIS_HASH
        return self.records[-1].witness_id

    def append(self, lore_ref: str, lore_text: str, probe_composite: float,
               doctrines_hit: List[str], agent: str = "fleet", note: str = "") -> WitnessRecord:
        """Append a new witness record. Returns it."""
        prev_hash = self.last_hash()
        timestamp = time.time()
        excerpt = lore_text[:200].strip()
        # The witness_id is a hash of (prev + timestamp + lore + agent)
        # This is what makes the chain cryptographically linked.
        composite_str = (
            f"{prev_hash}|{timestamp}|{lore_ref}|{excerpt}|"
            f"{probe_composite}|{','.join(sorted(doctrines_hit))}|{agent}|{note}"
        )
        witness_id = hex_id(composite_str)

        rec = WitnessRecord(
            witness_id=witness_id,
            prev_hash=prev_hash,
            timestamp=timestamp,
            lore_ref=lore_ref,
            lore_excerpt=excerpt,
            probe_composite=probe_composite,
            doctrines_hit=doctrines_hit,
            agent=agent,
            note=note,
        )
        self.records.append(rec)
        self._save()
        return rec

    def verify_chain(self) -> bool:
        """Verify the cryptographic chain integrity."""
        prev = GENESIS_HASH
        for r in self.records:
            if r.prev_hash != prev:
                return False
            # Re-derive the witness_id and compare
            composite_str = (
                f"{r.prev_hash}|{r.timestamp}|{r.lore_ref}|{r.lore_excerpt}|"
                f"{r.probe_composite}|{','.join(sorted(r.doctrines_hit))}|{r.agent}|{r.note}"
            )
            expected = hex_id(composite_str)
            if r.witness_id != expected:
                return False
            prev = r.witness_id
        return True

    def get_by_lore(self, lore_ref: str) -> List[WitnessRecord]:
        """Get all witnesses for a specific lore reference."""
        return [r for r in self.records if r.lore_ref == lore_ref]

    def get_by_agent(self, agent: str) -> List[WitnessRecord]:
        return [r for r in self.records if r.agent == agent]

    def get(self, witness_id: str) -> Optional[WitnessRecord]:
        for r in self.records:
            if r.witness_id == witness_id:
                return r
        return None

    def tail(self, n: int = 10) -> List[WitnessRecord]:
        return self.records[-n:]

    def stats(self) -> Dict:
        return {
            "n_witnesses": len(self.records),
            "first_timestamp": self.records[0].timestamp if self.records else None,
            "last_timestamp": self.records[-1].timestamp if self.records else None,
            "agents": sorted(set(r.agent for r in self.records)),
            "doctrines_count": len(set(d for r in self.records for d in r.doctrines_hit)),
            "mean_composite": (
                sum(r.probe_composite for r in self.records) / len(self.records)
                if self.records else 0
            ),
            "chain_valid": self.verify_chain(),
            "genesis_hash": GENESIS_HASH,
            "tip_hash": self.last_hash(),
        }
