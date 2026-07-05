from skillctl._migrate import migrate_agents, migrate_cursor, migrate_skill_md


def test_migrate_cursor_basic(tmp_path):
    source_dir = tmp_path / ".cursor" / "rules"
    source_dir.mkdir(parents=True)
    (source_dir / "rule1.mdc").write_text("---\ndescription: test desc\nglobs: '*.py'\n---\nbody1")
    (source_dir / "rule2.mdc").write_text("---\ntitle: Rule 2\nalwaysApply: true\n---\nbody2")
    
    skillctl_home = tmp_path / ".skillctl"
    migrate_cursor(source_dir, skillctl_home)
    
    imported_dir = skillctl_home / "rules" / "imported" / "cursor"
    assert (imported_dir / "rule1.md").exists()
    assert (imported_dir / "rule2.md").exists()
    
    content1 = (imported_dir / "rule1.md").read_text()
    assert "id: rule1" in content1
    assert "tier: 2" in content1
    assert "summary: test desc" in content1
    assert "globs: '*.py'" in content1
    assert "<!-- TODO: review triggers -->" in content1
    assert content1.endswith("body1\n")
    
    content2 = (imported_dir / "rule2.md").read_text()
    assert "id: rule2" in content2
    assert "title: Rule 2" in content2
    assert "tier: 1" in content2
    assert "alwaysApply" not in content2
    assert "<!-- TODO: review triggers -->" not in content2

def test_migrate_cursor_always_apply_becomes_tier_1(tmp_path):
    source_dir = tmp_path / "rules"
    source_dir.mkdir(parents=True)
    (source_dir / "always.mdc").write_text("---\nalwaysApply: true\n---\nbody")
    
    home = tmp_path / ".skillctl"
    migrate_cursor(source_dir, home)
    content = (home / "rules" / "imported" / "cursor" / "always.md").read_text()
    assert "tier: 1" in content
    assert "<!-- TODO" not in content

def test_migrate_cursor_no_triggers_derives_from_filename(tmp_path):
    source_dir = tmp_path / "rules"
    source_dir.mkdir(parents=True)
    (source_dir / "safe-deploy.mdc").write_text("---\ndescription: Important shipping rule\n---\nbody")
    
    home = tmp_path / ".skillctl"
    migrate_cursor(source_dir, home)
    content = (home / "rules" / "imported" / "cursor" / "safe-deploy.md").read_text()
    assert "tier: 2" in content
    assert "triggers:" in content
    assert "- safe" in content
    assert "- deploy" in content
    assert "- important" in content
    assert "<!-- TODO: review triggers -->" in content

def test_migrate_agents_splits_on_h2(tmp_path):
    source = tmp_path / "AGENTS.md"
    source.write_text("intro\n## Rule 1\nbody 1\n## License\nmit\n## Rule 2\nbody 2")
    home = tmp_path / ".skillctl"
    
    migrate_agents(source, home)
    imported = home / "rules" / "imported" / "agents"
    assert (imported / "rule-1.md").exists()
    assert (imported / "rule-2.md").exists()
    assert not (imported / "license.md").exists()
    
    content1 = (imported / "rule-1.md").read_text()
    assert "id: rule-1" in content1
    assert "title: Rule 1" in content1
    assert "tier: 1" in content1
    assert "body 1" in content1

def test_migrate_skill_md_copies_unchanged(tmp_path):
    source_dir = tmp_path / "skills"
    source_dir.mkdir(parents=True)
    content = "---\nid: my-skill\n---\nbody"
    (source_dir / "skill.md").write_text(content)
    
    home = tmp_path / ".skillctl"
    migrate_skill_md(source_dir, home)
    imported = home / "rules" / "imported" / "skill-md"
    assert (imported / "my-skill.md").read_text() == content

def test_migrate_dry_run_writes_nothing(tmp_path):
    source_dir = tmp_path / "skills"
    source_dir.mkdir(parents=True)
    (source_dir / "skill.md").write_text("---\nid: sk1\n---\nbody")
    
    home = tmp_path / ".skillctl"
    migrate_skill_md(source_dir, home, dry_run=True)
    assert not (home / "rules").exists()

def test_migrate_force_overwrites(tmp_path):
    source_dir = tmp_path / "skills"
    source_dir.mkdir(parents=True)
    (source_dir / "skill.md").write_text("---\nid: sk1\n---\nnew")
    
    home = tmp_path / ".skillctl"
    out_dir = home / "rules" / "imported" / "skill-md"
    out_dir.mkdir(parents=True)
    out_path = out_dir / "sk1.md"
    out_path.write_text("old")
    
    migrate_skill_md(source_dir, home)
    assert out_path.read_text() == "old"
    
    migrate_skill_md(source_dir, home, force=True)
    assert out_path.read_text() == "---\nid: sk1\n---\nnew"

def test_migrate_empty_source_succeeds(tmp_path):
    home = tmp_path / ".skillctl"
    source = tmp_path / "empty"
    migrate_cursor(source, home)
    migrate_agents(source, home)
    migrate_skill_md(source, home)
    assert not (home / "rules").exists()
