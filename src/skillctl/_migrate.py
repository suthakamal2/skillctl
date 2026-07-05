"""Migrate rules from external formats into skillctl."""
import re
import shutil
from pathlib import Path

import yaml


def _slugify(text: str) -> str:
    slug = re.sub(r'[^a-zA-Z0-9\-]+', '-', text.lower()).strip('-')
    return slug


def _derive_triggers(filename: str, description: str) -> list[str]:
    triggers = []
    slug = _slugify(filename)
    if slug:
        for word in slug.split('-'):
            if word and word not in triggers:
                triggers.append(word)

    if description:
        words = re.findall(r'\b[a-zA-Z]{4,}\b', description)
        for w in words:
            w_lower = w.lower()
            if w_lower not in triggers:
                triggers.append(w_lower)
            if len(triggers) >= 3 + len(slug.split('-')):
                break

    return triggers


def _parse_cursor_frontmatter(text: str) -> tuple[dict | None, str, str]:
    FRONTMATTER_FENCE = "---"
    if not text.startswith(FRONTMATTER_FENCE):
        return None, text, text
    end = text.find("\n" + FRONTMATTER_FENCE, len(FRONTMATTER_FENCE))
    if end == -1:
        return None, text, text
    fm_raw = text[len(FRONTMATTER_FENCE) : end].strip()
    body = text[end + len(FRONTMATTER_FENCE) + 1 :].lstrip("\n")
    try:
        meta = yaml.safe_load(fm_raw) or {}
    except yaml.YAMLError:
        return None, text, text
    if not isinstance(meta, dict):
        return None, text, text
    return meta, body, text


def _write_migrated_file(
    out_dir: Path,
    file_id: str,
    meta: dict,
    body: str,
    force: bool,
    dry_run: bool,
    needs_review: bool = False,
) -> bool:
    out_path = out_dir / f"{file_id}.md"
    if out_path.exists() and not force:
        print(f"Conflict: {out_path} already exists. Use --force to overwrite.")
        return False

    if dry_run:
        print(f"Would write {out_path}")
        return True

    out_dir.mkdir(parents=True, exist_ok=True)

    lines = ["---"]
    yaml_lines = yaml.safe_dump(meta, sort_keys=False, default_flow_style=False).strip().split('\n')
    lines.extend(yaml_lines)
    lines.append("---")
    lines.append("")
    
    if needs_review:
        lines.append("<!-- TODO: review triggers -->")
        lines.append("")
        
    lines.append(body.strip())
    lines.append("")

    out_path.write_text("\n".join(lines))
    out_path.chmod(0o644)
    return True


def migrate_cursor(
    source_path: Path,
    skillctl_home: Path,
    dry_run: bool = False,
    force: bool = False,
) -> None:
    source_path = source_path.resolve()
    skillctl_home = skillctl_home.resolve()

    if not source_path.exists():
        print(f"no source files found at {source_path}")
        return

    mdc_files = list(source_path.rglob("*.mdc"))
    if not mdc_files:
        print(f"no source files found at {source_path}")
        return

    out_dir = skillctl_home / "rules" / "imported" / "cursor"
    
    imported_count = 0
    review_count = 0

    for mdc in sorted(mdc_files):
        meta, body, _ = _parse_cursor_frontmatter(mdc.read_text())
        if meta is None:
            continue

        file_id = mdc.stem
        skillctl_meta = {"id": file_id}
        
        if "title" in meta:
            skillctl_meta["title"] = meta["title"]
        else:
            skillctl_meta["title"] = file_id.replace('-', ' ').title()

        if meta.get("alwaysApply") is True:
            skillctl_meta["tier"] = 1
            needs_review = False
        else:
            skillctl_meta["tier"] = 2
            desc = meta.get("description", "")
            if desc:
                skillctl_meta["summary"] = desc
            
            skillctl_meta["triggers"] = _derive_triggers(file_id, desc)
            needs_review = True
            
        if "globs" in meta:
            skillctl_meta["globs"] = meta["globs"]

        if _write_migrated_file(
            out_dir, file_id, skillctl_meta, body, force, dry_run, needs_review=needs_review
        ):
            imported_count += 1
            if needs_review:
                review_count += 1

    summary = f"Imported {imported_count} rules from {source_path}"
    if review_count > 0:
        summary += f"; {review_count} had auto-derived triggers (review marked)."
    print(summary)


def migrate_agents(
    source_path: Path,
    skillctl_home: Path,
    dry_run: bool = False,
    force: bool = False,
) -> None:
    source_path = source_path.resolve()
    skillctl_home = skillctl_home.resolve()

    if not source_path.exists():
        print(f"no source files found at {source_path}")
        return

    text = source_path.read_text()
    if not text:
        print(f"no source files found at {source_path}")
        return
        
    deny_list = {"license", "contributing", "status", "changelog"}
    sections = re.split(r'^##\s+(.+)$', text, flags=re.MULTILINE)
    
    if len(sections) < 2:
         print(f"no source files found at {source_path}")
         return

    out_dir = skillctl_home / "rules" / "imported" / "agents"
    imported_count = 0

    for i in range(1, len(sections), 2):
        heading = sections[i].strip()
        body = sections[i+1].strip() if i+1 < len(sections) else ""
        
        if heading.lower() in deny_list:
            continue
            
        file_id = _slugify(heading)
        if not file_id:
            continue
            
        skillctl_meta = {
            "id": file_id,
            "title": heading,
            "tier": 1
        }
        
        if _write_migrated_file(out_dir, file_id, skillctl_meta, body, force, dry_run):
            imported_count += 1

    print(f"Imported {imported_count} rules from {source_path}")


def migrate_skill_md(
    source_dir: Path,
    skillctl_home: Path,
    dry_run: bool = False,
    force: bool = False,
) -> None:
    source_dir = source_dir.resolve()
    skillctl_home = skillctl_home.resolve()

    if not source_dir.exists():
        print(f"no source files found at {source_dir}")
        return

    md_files = list(source_dir.rglob("*.md"))
    if not md_files:
        print(f"no source files found at {source_dir}")
        return

    out_dir = skillctl_home / "rules" / "imported" / "skill-md"
    imported_count = 0

    for md in sorted(md_files):
        meta, _, raw = _parse_cursor_frontmatter(md.read_text())
        if meta and "id" in meta:
            file_id = str(meta["id"])
            out_path = out_dir / f"{file_id}.md"
            
            if out_path.exists() and not force:
                print(f"Conflict: {out_path} already exists. Use --force to overwrite.")
                continue
                
            if dry_run:
                print(f"Would copy {md} to {out_path}")
                imported_count += 1
                continue
                
            out_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(md, out_path)
            out_path.chmod(0o644)
            imported_count += 1
            
    if imported_count == 0:
        print(f"no source files found at {source_dir}")
        return

    print(f"Imported {imported_count} rules from {source_dir}")
