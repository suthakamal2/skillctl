#!/usr/bin/env python3
"""Generate the synthetic example rule corpus used by the eval suite.

This is the fixture for the eval suite: a fictional but realistically-shaped corpus for a generic
software-engineering org's coding agent. It exercises skillctl at real scale —
~3 tiers, deterministic triggers, bundles with transitive deps — without shipping
anyone's internals, and doubles as a worked example of a non-trivial skillctl setup.

Deterministic: same input → same output. Regenerate with:
    python scripts/gen_example_corpus.py
Outputs into eval/example-rules/.skillctl/ (rules/*.md + bundles.yaml).
"""

from __future__ import annotations

from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "eval" / "example-rules" / ".skillctl"

# (id, tier, triggers, deps, summary)
# tier 1 = always-on behavioural policy (no triggers); tier 2 = trigger-loaded;
# tier 3 = on-demand reference. Triggers are deterministic word-boundary keywords.
RULES: list[tuple[str, int, list[str], list[str], str]] = [
    # ── Tier 1: always-on behavioural policy ─────────────────────────────────
    ("code-style", 1, [], [], "House code style: formatter is authority, no bikeshedding in review."),
    ("commit-conventions", 1, [], [], "Conventional Commits; one logical change per commit; imperative subject."),
    ("ask-before-assuming", 1, [], [], "Surface unknowns and tradeoffs before implementing; don't guess silently."),
    ("test-required", 1, [], [], "Every behavioural change ships with a test that fails before and passes after."),
    ("security-baseline", 1, [], [], "Never log secrets; validate all input; least privilege by default."),
    ("surgical-changes", 1, [], [], "Every edited line traces to the request; don't refactor unrelated code."),
    # ── Tier 2: deploy / infra ───────────────────────────────────────────────
    ("safe-deploy", 2, ["deploy", "ship", "release", "rollout", "production", "staging"], ["docker", "ci-cd", "rollback"], "Blue/green or canary; run the suite first; never deploy on red."),
    ("docker", 2, ["docker", "container", "image", "dockerfile"], [], "Pin base images, multi-stage builds, non-root user, minimal layers."),
    ("kubernetes", 2, ["kubernetes", "k8s", "pod", "helm", "kubectl"], ["docker"], "Set resource requests/limits, liveness/readiness probes, no :latest tags."),
    ("ci-cd", 2, ["pipeline", "continuous integration", "github actions", "build pipeline"], [], "Fast feedback first; cache deps; fail the pipeline on lint, type, and test."),
    ("rollback", 2, ["rollback", "revert", "roll back", "hotfix"], [], "Prefer rollback over forward-fix under incident; keep the last good artifact."),
    ("feature-flags", 2, ["feature flag", "flag", "toggle", "gradual rollout"], [], "Gate risky changes behind a flag; default off; clean up stale flags."),
    ("infra-as-code", 2, ["terraform", "infrastructure", "iac", "provisioning"], [], "All infra in code, planned before apply, state locked and remote."),
    # ── Tier 2: data ─────────────────────────────────────────────────────────
    ("database-migrations", 2, ["migration", "schema", "alter table", "ddl"], ["rollback"], "Additive + backward-compatible first; expand/contract; never destructive in one step."),
    ("sql-optimization", 2, ["slow query", "query plan", "sql performance", "explain"], ["database-indexing"], "Read the plan; avoid N+1; select only needed columns; watch sequential scans."),
    ("database-indexing", 2, ["index", "indexing", "composite index"], [], "Index for the query, not the table; concurrent creation in prod; drop unused."),
    ("connection-pooling", 2, ["connection pool", "pool", "max connections"], [], "Bound the pool; set timeouts; one pool per service; watch for leaks."),
    ("data-retention", 2, ["retention", "purge", "archive", "gdpr", "data deletion"], [], "Define retention per data class; soft-delete then purge; honour erasure requests."),
    ("backups", 2, ["backup", "restore", "snapshot", "disaster recovery"], [], "Automate backups, test restores, store off-host, encrypt at rest."),
    # ── Tier 2: backend / API ────────────────────────────────────────────────
    ("api-design", 2, ["api design", "endpoint", "rest", "api contract"], ["rest-conventions"], "Design the contract first; version it; keep responses consistent and typed."),
    ("rest-conventions", 2, ["rest", "http status", "resource", "verb"], [], "Nouns for resources, correct verbs and status codes, idempotent PUT/DELETE."),
    ("graphql", 2, ["graphql", "resolver", "schema stitching"], [], "Guard against deep/expensive queries; dataloader for N+1; persisted queries."),
    ("pagination", 2, ["pagination", "paginate", "cursor", "page size"], [], "Cursor-based for large sets; cap page size; stable sort key."),
    ("rate-limiting", 2, ["rate limit", "throttle", "quota", "429"], [], "Per-principal limits; return 429 + Retry-After; token bucket over fixed window."),
    ("caching", 2, ["cache", "caching", "ttl", "invalidation"], [], "Cache the expensive and stable; explicit TTL; name an invalidation strategy."),
    ("webhooks", 2, ["webhook", "callback url", "event delivery"], ["queue-processing"], "Verify signatures, respond fast then process async, retry with backoff, dedupe."),
    ("background-jobs", 2, ["background job", "worker", "async task", "job queue"], ["queue-processing"], "Idempotent jobs, bounded retries, dead-letter on repeated failure."),
    ("queue-processing", 2, ["queue", "message queue", "consumer", "kafka", "sqs"], [], "At-least-once by default; idempotent consumers; monitor lag and DLQ depth."),
    ("cron-jobs", 2, ["cron", "scheduled task", "scheduler"], ["background-jobs"], "Idempotent + overlap-safe; alert on missed runs; record last success."),
    # ── Tier 2: security ─────────────────────────────────────────────────────
    ("secrets-management", 2, ["secret", "credentials", "api key", "vault", "env var"], [], "Secrets in a manager, never in code or logs; rotate; scope per service."),
    ("authentication", 2, ["authentication", "login", "auth", "session"], ["jwt"], "Standard flows only; secure session handling; MFA where it matters."),
    ("authorization", 2, ["authorization", "permission", "rbac", "access control"], [], "Deny by default; check on every request; scope tokens to least privilege."),
    ("password-hashing", 2, ["password", "hash", "bcrypt", "argon2"], [], "Argon2/bcrypt with per-user salt; never roll your own; rehash on cost bump."),
    ("jwt", 2, ["jwt", "token", "bearer", "claims"], [], "Short-lived access tokens, verify signature + audience + expiry, rotate keys."),
    ("cors", 2, ["cors", "cross-origin", "preflight"], [], "Allow-list origins; never reflect arbitrary Origin; restrict methods/headers."),
    ("input-validation", 2, ["validation", "sanitize", "injection", "xss"], [], "Validate at the boundary, parameterize queries, encode on output."),
    ("dependency-audit", 2, ["dependency", "vulnerability", "cve", "audit", "supply chain"], [], "Pin and lock deps; scan for CVEs in CI; review transitive additions."),
    # ── Tier 2: observability / ops ──────────────────────────────────────────
    ("logging", 2, ["logging", "log", "structured logs"], [], "Structured JSON logs, correlation IDs, no PII, levels used consistently."),
    ("monitoring", 2, ["monitoring", "metrics", "dashboard", "prometheus"], [], "RED/USE metrics, dashboards per service, alert on symptoms not causes."),
    ("observability", 2, ["observability", "tracing", "span", "opentelemetry"], ["logging", "monitoring"], "Traces + metrics + logs correlated; instrument boundaries; sample sanely."),
    ("alerting", 2, ["alert", "alerting", "pager", "on-call"], ["monitoring"], "Alert on user-facing symptoms; every alert actionable; tune out noise."),
    ("incident-response", 2, ["incident", "outage", "sev1", "postmortem"], ["rollback", "alerting"], "Declare early, assign a lead, communicate, mitigate first, blameless postmortem."),
    ("slo", 2, ["slo", "sli", "error budget", "uptime"], [], "Define SLIs from the user's view; spend error budget deliberately."),
    # ── Tier 2: frontend ─────────────────────────────────────────────────────
    ("component-design", 2, ["component", "react", "ui component", "props"], [], "Small, composable, single-responsibility components; lift state deliberately."),
    ("frontend-state", 2, ["state management", "redux", "store", "client state"], [], "Keep server state in a query cache; minimal global client state."),
    ("accessibility", 2, ["accessibility", "a11y", "aria", "screen reader"], [], "Semantic HTML first, keyboard navigable, labelled controls, sufficient contrast."),
    ("i18n", 2, ["i18n", "localization", "translation", "locale"], [], "Externalise strings, format dates/numbers per locale, no string concatenation."),
    ("performance-web", 2, ["web performance", "lighthouse", "bundle size", "lazy load"], ["caching"], "Budget the bundle, lazy-load routes, measure Core Web Vitals."),
    # ── Tier 2: workflow ─────────────────────────────────────────────────────
    ("git-workflow", 2, ["branch", "merge", "rebase", "pull request"], ["commit-conventions"], "Short-lived branches, rebase to keep history linear, small reviewable PRs."),
    ("code-review", 2, ["code review", "review", "pr review", "approve"], [], "Review for correctness and clarity; a different person than the author; no rubber-stamps."),
    ("testing-strategy", 2, ["test", "unit test", "integration test", "coverage"], ["test-required"], "Pyramid: many unit, some integration, few e2e; test behaviour not implementation."),
    ("refactoring", 2, ["refactor", "cleanup", "tech debt"], ["testing-strategy"], "Green tests before and after; one refactor per commit; no behaviour change."),
    ("error-handling", 2, ["error handling", "exception", "retry", "timeout"], [], "Fail loud at boundaries, retry transient with backoff, never swallow errors."),
    ("api-versioning", 2, ["versioning", "breaking change", "deprecation"], ["api-design"], "Version on breaking change; deprecate with a window; communicate the sunset."),
    # ── Tier 3: on-demand reference ──────────────────────────────────────────
    ("architecture-overview", 3, ["architecture", "system design", "high level design"], [], "Reference: services, boundaries, and the data flow between them."),
    ("data-model-reference", 3, ["data model", "entity", "er diagram"], [], "Reference: canonical entities, relationships, and ownership."),
    ("service-catalog", 3, ["service catalog", "service map", "ownership"], [], "Reference: each service, its owner, SLOs, and on-call."),
    ("runbook-deploy", 3, ["deploy runbook", "release checklist"], [], "Reference: step-by-step production deploy and verification checklist."),
    ("runbook-incident", 3, ["incident runbook", "outage playbook"], [], "Reference: severity definitions, escalation paths, and comms templates."),
    ("postmortem-template", 3, ["postmortem", "retro template", "rca"], [], "Reference: blameless postmortem structure — timeline, impact, actions."),
    ("style-guide-full", 3, ["style guide", "naming conventions"], [], "Reference: the full language and naming style guide."),
    ("onboarding", 3, ["onboarding", "getting started", "new engineer"], [], "Reference: local setup, repo map, and first-week checklist."),
    ("glossary", 3, ["glossary", "terminology", "domain terms"], [], "Reference: domain terms and their precise meanings."),
    ("dependency-policy", 3, ["dependency policy", "adding a library", "licensing"], [], "Reference: criteria and approval for adding third-party dependencies."),
]

BUNDLES: dict[str, list[str]] = {
    "deploy": ["safe-deploy", "docker", "ci-cd", "rollback"],
    "deploy-k8s": ["safe-deploy", "kubernetes", "ci-cd", "rollback"],
    "backend-api": ["api-design", "rest-conventions", "authentication", "authorization"],
    "data-layer": ["database-migrations", "sql-optimization", "database-indexing", "connection-pooling"],
    "security": ["secrets-management", "authentication", "authorization", "password-hashing", "input-validation"],
    "incident": ["incident-response", "rollback", "observability", "alerting"],
    "frontend": ["component-design", "frontend-state", "accessibility", "i18n"],
    "async-processing": ["queue-processing", "background-jobs", "webhooks", "cron-jobs"],
    "observability": ["logging", "monitoring", "observability", "alerting"],
    "review-ready": ["code-review", "testing-strategy", "git-workflow"],
    "api-evolution": ["api-design", "api-versioning", "rest-conventions"],
    "data-governance": ["data-retention", "backups", "secrets-management"],
}


def _title(rule_id: str) -> str:
    return rule_id.replace("-", " ").title()


def _body(rule_id: str, tier: int, triggers: list[str], summary: str) -> str:
    title = _title(rule_id)
    when = (
        "Always-on behavioural policy."
        if tier == 1
        else f"On-demand reference; load explicitly when relevant ({', '.join(triggers)})."
        if tier == 3
        else f"Loads when the prompt mentions: {', '.join(triggers)}."
    )
    return (
        f"# {title}\n\n"
        f"{summary}\n\n"
        f"## When this applies\n{when}\n\n"
        f"## Guidance\n"
        f"- {summary}\n"
        f"- Make the safe choice the default; document the exception when you deviate.\n"
        f"- Prefer the boring, well-understood option over the clever one.\n"
    )


def main() -> None:
    rules_dir = OUT / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    # clear any stale generated rules
    for old in rules_dir.glob("*.md"):
        old.unlink()

    for rule_id, tier, triggers, deps, summary in RULES:
        # Quote summary: several summaries contain ': ' which YAML would otherwise
        # read as a nested mapping. None contain a double-quote, so plain quoting is safe.
        assert '"' not in summary, f"summary for {rule_id} needs escaping"
        fm = ["---", f"id: {rule_id}", f'title: "{_title(rule_id)}"', f"tier: {tier}"]
        if triggers:
            fm.append(f"triggers: [{', '.join(triggers)}]")
        if deps:
            fm.append(f"deps: [{', '.join(deps)}]")
        fm.append(f'summary: "{summary}"')
        fm.append("---")
        body = "\n".join(fm) + "\n\n" + _body(rule_id, tier, triggers, summary)
        (rules_dir / f"{rule_id}.md").write_text(body)

    bundles_lines = ["# Example bundles: each groups related rules; deps resolve transitively.\n"]
    for name, members in BUNDLES.items():
        bundles_lines.append(f"{name}: [{', '.join(members)}]")
    (OUT / "bundles.yaml").write_text("\n".join(bundles_lines) + "\n")

    # representative eval prompts (no internal references)
    prompts = [
        "we need to deploy v2 to staging tonight",
        "the production database query is slow, what indexes should we add",
        "set up authentication and authorization for the new API",
        "we have a sev1 outage, walk me through incident response",
        "add pagination and rate limiting to this endpoint",
        "make this React component accessible",
        "process these events asynchronously off a queue",
        "rotate our API keys and audit dependencies for CVEs",
        "write a database migration that adds a nullable column",
        "review this pull request before we merge",
    ]
    (OUT.parent / "test_prompts.txt").write_text("\n".join(prompts) + "\n")

    print(f"Generated {len(RULES)} rules, {len(BUNDLES)} bundles → {OUT}")


if __name__ == "__main__":
    main()
