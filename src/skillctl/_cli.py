"""``skillctl`` CLI entry point."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from . import __version__
from ._audit import audit_registry
from ._build import build_registry
from ._config import find_home
from ._inject import inject
from ._install import (
    install_claude_code,
    print_codex_docs,
    print_cursor_docs,
    uninstall_claude_code,
)
from ._loader import load_bundle, load_topics, resolve_deps
from ._matching import explain_match, match_by_topic, suggest_bundles, suggest_topics
from ._migrate import migrate_agents, migrate_cursor, migrate_skill_md
from ._registry import (
    DEFAULT_MAX_TOKENS,
    clear_cache,
    get_rule,
    get_rules_by_tier,
    load_registry,
    read_rule_body,
)


def _emit(obj, args) -> None:
    if getattr(args, "json", False):
        print(json.dumps(obj, indent=2, default=str))
    else:
        # Fallback prose printer for objects emitted by the JSON path
        print(json.dumps(obj, indent=2, default=str))


def cmd_init(args) -> None:
    target = Path(args.path or Path.cwd()) / ".skillctl"
    rules_dir = target / "rules"
    target.mkdir(parents=True, exist_ok=True)
    rules_dir.mkdir(parents=True, exist_ok=True)

    bundles_path = target / "bundles.yaml"
    if not bundles_path.exists():
        bundles_path.write_text(
            "# Bundles group related rules and resolve their transitive deps.\n"
            "# Example:\n"
            "# deploy: [safe-deploy, docker-control, branch-management]\n"
        )

    sample = rules_dir / "example.md"
    if not sample.exists():
        sample.write_text(
            "---\n"
            "id: example\n"
            "title: Example rule\n"
            "tier: 2\n"
            "triggers: [example, sample]\n"
            "summary: A starter rule. Delete me and write your own.\n"
            "---\n\n"
            "# Example rule\n\n"
            "Replace this file with a rule that matters in your project.\n"
        )

    print(f"Initialised {target}")
    print(f"  - {rules_dir}/ (put your rules here)")
    print(f"  - {bundles_path} (declare named bundles)")
    print()
    print("Next: skillctl build")


def cmd_build(args) -> None:
    home = Path(args.home).resolve() if args.home else find_home()
    if home is None:
        home = (Path.cwd() / ".skillctl").resolve()
        home.mkdir(parents=True, exist_ok=True)
    rules_dir = Path(args.rules).resolve() if args.rules else home / "rules"
    if not rules_dir.exists():
        print(f"No rules directory at {rules_dir}", file=sys.stderr)
        sys.exit(2)

    from ._errors import Reporter
    reporter = Reporter()
    reg = build_registry(rules_dir, home, reporter=reporter)
    clear_cache()
    
    if args.json:
        reporter.print(use_json=True)
    else:
        reporter.print()
        print(f"Built {reg['total_rules']} rules; {reporter.skipped_count} skipped, {len(reporter.errors)} error.")
        
    if reporter.has_errors():
        sys.exit(1)


def cmd_list(args) -> None:
    reg = load_registry()
    if args.json:
        print(json.dumps(reg, indent=2))
        return
    console = Console()
    
    table = Table(title="Rules Registry", show_header=True, header_style="bold magenta")
    table.add_column("Tier", justify="right", style="cyan", no_wrap=True)
    table.add_column("ID", style="magenta")
    table.add_column("Tokens", justify="right", style="green")
    table.add_column("Triggers (first 3)")

    rows = []
    for r in reg["rules"]:
        if args.tier is not None and r["tier"] != args.tier:
            continue
        rows.append(
            (r["tier"], r["id"], r["tokens_approx"], ", ".join(r.get("triggers", [])[:3]))
        )
    rows.sort()

    for tier, rid, tok, trigs in rows:
        style = "bold green" if tier == 1 else "dim" if tier == 3 else None
        table.add_row(str(tier), rid, f"{tok:,}", trigs, style=style)
        
    console.print(table)
    
    tt = reg["token_totals"]
    rt = reg["tier_totals"]
    summary = (
        f"Tier 1 total: ~{tt['tier_1']:,} tokens ({rt['tier_1']} rules)\n"
        f"Tier 2 total: ~{tt['tier_2']:,} tokens ({rt['tier_2']} rules)\n"
        f"Tier 3 total: ~{tt['tier_3']:,} tokens ({rt['tier_3']} rules)"
    )
    console.print(Panel(summary, title="Totals", expand=False))


def cmd_show(args) -> None:
    r = get_rule(args.rule_id)
    if not r:
        print(f"Unknown rule: {args.rule_id}", file=sys.stderr)
        sys.exit(1)
    if args.json:
        print(json.dumps(r, indent=2))
        return
    
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value")
    
    for k, v in r.items():
        if k == "body":
            continue
        table.add_row(str(k), str(v))
        
    console.print(table)
    console.print("\n")
    
    body = read_rule_body(args.rule_id)
    console.print(Markdown(body))


def cmd_load(args) -> None:
    if args.json:
        rule_ids: list[str] = []
        for topic in args.topics:
            for m in match_by_topic(topic):
                if m.rule_id not in rule_ids:
                    rule_ids.append(m.rule_id)
        if not args.no_deps:
            rule_ids = resolve_deps(rule_ids)

        max_chars = args.max_tokens * 4
        budget_used = 0
        loaded_rules = []
        dropped_rules = []
        for rid in rule_ids:
            rule = get_rule(rid)
            if not rule:
                continue
            body = read_rule_body(rid)
            if budget_used + len(body) > max_chars:
                dropped_rules.append(rid)
                continue
            loaded_rules.append(
                {
                    "id": rid,
                    "title": rule["title"],
                    "path": rule["path"],
                    "tier": rule["tier"],
                    "body": body,
                    "tokens_approx": rule["tokens_approx"],
                }
            )
            budget_used += len(body)
        print(
            json.dumps(
                {
                    "topics": args.topics,
                    "max_tokens": args.max_tokens,
                    "tokens_used_approx": budget_used // 4,
                    "rules": loaded_rules,
                    "dropped": dropped_rules,
                },
                indent=2,
            )
        )
    else:
        text = load_topics(
            args.topics,
            max_tokens=args.max_tokens,
            include_deps=not args.no_deps,
        )
        print(text)


def cmd_suggest(args) -> None:
    matches = suggest_topics(args.prompt)
    if not matches:
        if args.json:
            print(json.dumps({"bundles": [], "rules": []}))
            return
        print("# No trigger matches for that prompt.")
        return

    bundle_suggestions = suggest_bundles(args.prompt, matches)

    if args.json:
        print(
            json.dumps(
                {
                    "bundles": [
                        {"name": n, "overlap": o} for n, o in bundle_suggestions
                    ],
                    "rules": [
                        {
                            "id": m.rule_id,
                            "tier": m.tier,
                            "triggers": m.matched_triggers,
                        }
                        for m in matches
                    ],
                },
                indent=2,
            )
        )
        return

    console = Console()

    if bundle_suggestions:
        reg = load_registry()
        bundle_text = ""
        for name, overlap in bundle_suggestions[:3]:
            members = reg["bundles"][name]
            bundle_text += f"[bold]- {name}[/bold] (overlap {overlap}/{len(members)}):\n"
            bundle_text += f"  `skillctl bundle {name}`\n"
            
        console.print(Panel(bundle_text.strip(), title="Suggested bundles", expand=False))
        console.print()

    table = Table(title="Suggested rules to load (in tier order)", show_header=True)
    table.add_column("Tier", justify="right", style="cyan")
    table.add_column("ID", style="magenta")
    table.add_column("Triggers")
    for m in matches:
        table.add_row(str(m.tier), m.rule_id, ", ".join(m.matched_triggers))
    console.print(table)
    
    console.print()
    ids = " ".join(m.rule_id for m in matches if m.tier >= 2)
    if ids:
        print("Or load specific rules:")
        print(f"skillctl load {ids}")


def cmd_why(args) -> None:
    info = explain_match(args.topic)
    if args.json:
        print(json.dumps(info, indent=2))
        return
    
    console = Console()
    console.print(f"[bold]Why topic {args.topic!r} matches:[/bold]")
    
    if info["matched_rules"]:
        table = Table(title="Matched rules", show_header=True)
        table.add_column("Rule", style="magenta")
        table.add_column("Tier", style="cyan")
        table.add_column("Reason")
        table.add_column("Triggers")
        for m in info["matched_rules"]:
            table.add_row(m['rule'], str(m['tier']), m['reason'], ", ".join(m['triggers']))
        console.print(table)
    else:
        console.print("  (no matches)")
        
    if info["near_misses"]:
        table = Table(title="Near misses (trigger-substring overlaps)", show_header=True)
        table.add_column("Rule", style="magenta")
        table.add_column("Tier", style="cyan")
        table.add_column("Trigger")
        for nm in info["near_misses"]:
            table.add_row(nm['rule'], str(nm['tier']), nm['trigger'], style="dim")
        console.print(table)


def cmd_bundles(args) -> None:
    reg = load_registry()
    bundles = reg.get("bundles", {})
    if args.json:
        print(json.dumps(bundles, indent=2))
        return
        
    console = Console()
    for name, members in sorted(bundles.items()):
        tree = Tree(f"[bold]{name}[/bold]")
        for m in members:
            rule = get_rule(m)
            if rule:
                tree.add(f"{m} (~{rule['tokens_approx']:,} tokens)")
            else:
                tree.add(f"{m} (missing — not in registry)")
        console.print(tree)
        console.print()


def cmd_bundle(args) -> None:
    text = load_bundle(args.name, max_tokens=args.max_tokens)
    print(text)


def cmd_audit(args) -> None:
    issues = audit_registry()
    
    from ._errors import Reporter
    reporter = Reporter()
    
    for rule_id in issues["missing_files"]:
        reporter.error(path=rule_id, category="missing_file", message="File missing from registry.")
    for issue in issues["checksum_mismatches"]:
        reporter.error(path=issue["id"], category="checksum_mismatch", message="Checksum mismatch.")
    for issue in issues["orphan_deps"]:
        reporter.error(path=issue["id"], category="orphan_dep", message=f"Orphan dependency: {issue['dep']}")
    for issue in issues["orphan_bundle_refs"]:
        reporter.error(path="bundles.yaml", category="orphan_bundle_ref", message=f"Bundle '{issue['bundle']}' references missing rule '{issue['member']}'.")
    for issue in issues["over_broad_triggers"]:
        reporter.warning(path=issue["id"], category="over_broad_trigger", message=f"Trigger '{issue['trigger']}' is too short.")
    for rule_id in issues["no_triggers_in_tier_2"]:
        reporter.error(path=rule_id, category="no_triggers_in_tier_2", message="Tier 2 rule without triggers.")
    for issue in issues["duplicate_ids"]:
        reporter.error(path=issue["id"], category="duplicate_id", message=f"Duplicate ID '{issue['id']}' ({issue['count']} occurrences).")
    for issue in issues["unreachable_rules"]:
        reporter.warning(path=issue["path"], category="unreachable_rules", message=f"unreachable rule: trigger '{issue['trigger']}' is too generic to ever match.")
        
    if args.json:
        reporter.print(use_json=True)
        sys.exit(1 if reporter.has_errors() else 0)
        
    if not reporter.has_errors() and not reporter.warnings:
        console = Console()
        console.print(Panel("[bold green]Registry clean:[/bold green] no integrity issues found.", expand=False, border_style="green"))
        return
        
    reporter.print()
    if reporter.has_errors():
        sys.exit(1)


def cmd_tier(args) -> None:
    rules = get_rules_by_tier(args.tier)
    if args.json:
        print(json.dumps(rules, indent=2))
        return
    for r in rules:
        triggers = ",".join(r.get("triggers", [])[:5])
        print(f"  {r['id']:<35}{r['tokens_approx']:>7,} tok  {triggers}")



def cmd_inject(args) -> None:
    result = inject(args.prompt)
    if result:
        print(result)

def cmd_install(args) -> None:
    if args.target == "claude-code":
        if args.uninstall:
            uninstall_claude_code()
        else:
            install_claude_code()
    elif args.target == "cursor":
        if args.uninstall:
            print("Uninstall not supported for cursor.")
            sys.exit(1)
        print_cursor_docs()
        sys.exit(0)
    elif args.target == "codex":
        if args.uninstall:
            print("Uninstall not supported for codex.")
            sys.exit(1)
        print_codex_docs()
        sys.exit(0)
    else:
        print(f"Unknown target: {args.target}")
        sys.exit(1)



def cmd_migrate_cursor(args) -> None:
    from pathlib import Path
    source = Path(args.path) if args.path else Path(".cursor/rules")
    home = Path(args.home) if args.home else Path(".skillctl")
    migrate_cursor(source, home, dry_run=args.dry_run, force=args.force)

def cmd_migrate_agents(args) -> None:
    from pathlib import Path
    source = Path(args.file) if args.file else Path("AGENTS.md")
    home = Path(args.home) if args.home else Path(".skillctl")
    migrate_agents(source, home, dry_run=args.dry_run, force=args.force)

def cmd_migrate_skill_md(args) -> None:
    from pathlib import Path
    source = Path(args.dir)
    home = Path(args.home) if args.home else Path(".skillctl")
    migrate_skill_md(source, home, dry_run=args.dry_run, force=args.force)

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="skillctl",
        description=(
            "Dependency resolver, bundle manager, and deterministic trigger "
            "engine for Agent Skills, Cursor Rules, and CLAUDE.md."
        ),
    )
    p.add_argument("--version", action="version", version=f"skillctl {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    i = sub.add_parser("init", help="Initialise a new .skillctl/ directory")
    i.add_argument("path", nargs="?", help="Project root (default: cwd)")
    i.set_defaults(func=cmd_init)

    b = sub.add_parser("build", help="Rebuild the registry from a rules directory")
    b.add_argument("rules", nargs="?", help="Rules directory (default: <home>/rules)")
    b.add_argument("--home", help="Path to .skillctl/ home (default: auto-detect)")
    b.add_argument("--json", action="store_true", help="Emit build report as JSON")
    b.set_defaults(func=cmd_build)

    ls = sub.add_parser("list", help="List all rules")
    ls.add_argument("--tier", type=int, choices=[1, 2, 3])
    ls.add_argument("--json", action="store_true")
    ls.set_defaults(func=cmd_list)

    s = sub.add_parser("show", help="Show one rule's registry entry")
    s.add_argument("rule_id")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_show)

    ld = sub.add_parser("load", help="Load rules by topic")
    ld.add_argument("topics", nargs="+")
    ld.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    ld.add_argument("--no-deps", action="store_true", help="Skip transitive deps")
    ld.add_argument("--json", action="store_true")
    ld.set_defaults(func=cmd_load)

    sg = sub.add_parser("suggest", help="Suggest rules to load from a prompt")
    sg.add_argument("prompt")
    sg.add_argument("--json", action="store_true")
    sg.set_defaults(func=cmd_suggest)

    w = sub.add_parser("why", help="Explain why a topic matches (or doesn't)")
    w.add_argument("topic")
    w.add_argument("--json", action="store_true")
    w.set_defaults(func=cmd_why)

    bls = sub.add_parser("bundles", help="List named bundles")
    bls.add_argument("--json", action="store_true")
    bls.set_defaults(func=cmd_bundles)

    bl = sub.add_parser("bundle", help="Load a named bundle")
    bl.add_argument("name")
    bl.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    bl.set_defaults(func=cmd_bundle)

    a = sub.add_parser("audit", help="Check registry integrity")
    a.add_argument("--json", action="store_true")
    a.set_defaults(func=cmd_audit)

    t = sub.add_parser("tier", help="List rules at a specific tier")
    t.add_argument("tier", type=int, choices=[1, 2, 3])
    t.add_argument("--json", action="store_true")
    t.set_defaults(func=cmd_tier)

    

    mig = sub.add_parser("migrate", help="Migrate rules from existing conventions")
    mig_sub = mig.add_subparsers(dest="mig_cmd", required=True)
    
    mig_cur = mig_sub.add_parser("cursor", help="Migrate from .cursor/rules/*.mdc")
    mig_cur.add_argument("--path", help="Path to cursor rules (default: .cursor/rules)")
    mig_cur.add_argument("--home", help="Path to .skillctl/ home")
    mig_cur.add_argument("--dry-run", action="store_true")
    mig_cur.add_argument("--force", action="store_true")
    mig_cur.set_defaults(func=cmd_migrate_cursor)

    mig_ag = mig_sub.add_parser("agents", help="Migrate from AGENTS.md / CLAUDE.md")
    mig_ag.add_argument("--file", help="Path to agents file (default: AGENTS.md)")
    mig_ag.add_argument("--home", help="Path to .skillctl/ home")
    mig_ag.add_argument("--dry-run", action="store_true")
    mig_ag.add_argument("--force", action="store_true")
    mig_ag.set_defaults(func=cmd_migrate_agents)

    mig_sk = mig_sub.add_parser("skill-md", help="Migrate from a directory of SKILL.md files")
    mig_sk.add_argument("dir", help="Directory containing SKILL.md files")
    mig_sk.add_argument("--home", help="Path to .skillctl/ home")
    mig_sk.add_argument("--dry-run", action="store_true")
    mig_sk.add_argument("--force", action="store_true")
    mig_sk.set_defaults(func=cmd_migrate_skill_md)

    inj = sub.add_parser("inject", help="Inject rules context for a prompt")
    inj.add_argument("prompt")
    inj.set_defaults(func=cmd_inject)

    inst = sub.add_parser("install", help="Install skillctl hooks/docs for a target")
    inst.add_argument("target", choices=["claude-code", "cursor", "codex"])
    inst.add_argument("--uninstall", action="store_true", help="Uninstall the hook")
    inst.set_defaults(func=cmd_install)

    return p


def main(argv: list[str] | None = None) -> None:
    p = build_parser()
    args = p.parse_args(argv)
    try:
        args.func(args)
    except SystemExit:
        raise
    except (FileNotFoundError, ValueError) as e:
        # Expected user-facing states (no registry built yet, unknown rule id, …).
        # These carry their own actionable message; don't mislabel them "Internal bug".
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Internal bug: {e}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
