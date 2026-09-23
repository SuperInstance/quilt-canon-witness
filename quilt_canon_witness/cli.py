"""CLI for quilt-canon-witness."""
import argparse
import json
import sys
from pathlib import Path

from .witness import WitnessLog, GENESIS_HASH


DEFAULT_PATH = Path.home() / ".cache" / "quilt-canon-witness" / "witness.jsonl"


def _get_log(args):
    return WitnessLog(path=Path(args.path) if args.path else DEFAULT_PATH)


def cmd_append(args):
    log = _get_log(args)
    rec = log.append(
        lore_ref=args.lore_ref,
        lore_text=args.lore_text,
        probe_composite=args.composite,
        doctrines_hit=args.doctrines.split(",") if args.doctrines else [],
        agent=args.agent,
        note=args.note or "",
    )
    print(json.dumps(rec.to_dict(), indent=2))


def cmd_verify(args):
    log = _get_log(args)
    if log.verify_chain():
        print(f"✓ Chain valid ({log.stats()['n_witnesses']} witnesses)")
        sys.exit(0)
    else:
        print("✗ Chain BROKEN — witnesses have been tampered with")
        sys.exit(1)


def cmd_get(args):
    log = _get_log(args)
    if args.witness_id:
        rec = log.get(args.witness_id)
        if rec:
            print(json.dumps(rec.to_dict(), indent=2))
        else:
            print(f"Not found: {args.witness_id}")
            sys.exit(1)
    elif args.lore_ref:
        recs = log.get_by_lore(args.lore_ref)
        for r in recs:
            print(f"{r.witness_id}  {r.lore_ref}  composite={r.probe_composite}")
    elif args.agent:
        recs = log.get_by_agent(args.agent)
        for r in recs:
            print(f"{r.witness_id}  {r.lore_ref}  composite={r.probe_composite}")
    else:
        for r in log.tail(args.limit):
            print(f"{r.witness_id}  {r.lore_ref}  composite={r.probe_composite}")


def cmd_stats(args):
    log = _get_log(args)
    stats = log.stats()
    print(json.dumps(stats, indent=2))


def cmd_export(args):
    log = _get_log(args)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "genesis_hash": GENESIS_HASH,
        "tip_hash": log.last_hash(),
        "chain_valid": log.verify_chain(),
        "n_witnesses": len(log.records),
        "witnesses": [r.to_dict() for r in log.records],
    }, indent=1))
    print(f"✓ Exported {len(log.records)} witnesses → {out}")


def main():
    p = argparse.ArgumentParser(description="quilt-canon-witness — cryptographic witness log")
    p.add_argument("--path", help=f"Path to witness log (default: {DEFAULT_PATH})")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_a = sub.add_parser("append", help="Append a witness")
    p_a.add_argument("lore_ref", help="Reference (path or name) of the canon lore")
    p_a.add_argument("lore_text", help="The lore text (or excerpt)")
    p_a.add_argument("--composite", type=float, required=True, help="JEV probe composite")
    p_a.add_argument("--doctrines", default="", help="Comma-separated doctrines")
    p_a.add_argument("--agent", default="fleet")
    p_a.add_argument("--note", default="")
    p_a.set_defaults(func=cmd_append)

    sub.add_parser("verify", help="Verify chain integrity").set_defaults(func=cmd_verify)

    p_g = sub.add_parser("get", help="Get witnesses")
    p_g.add_argument("--witness-id", help="Specific witness ID")
    p_g.add_argument("--lore-ref", help="By lore reference")
    p_g.add_argument("--agent", help="By agent")
    p_g.add_argument("--limit", type=int, default=10)
    p_g.set_defaults(func=cmd_get)

    sub.add_parser("stats", help="Show log statistics").set_defaults(func=cmd_stats)

    p_e = sub.add_parser("export", help="Export witness log")
    p_e.add_argument("--output", required=True)
    p_e.set_defaults(func=cmd_export)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
