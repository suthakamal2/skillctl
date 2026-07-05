---
id: security-review
title: Security review checklist
tier: 2
triggers: [security review, vulnerability, threat model, authz, authn, owasp]
deps: []
summary: A mental OWASP pass before opening sensitive PRs. Escalate the unfamiliar.
---

# Security review checklist

Before opening a PR that touches authentication, authorisation, user data, secrets, file uploads, or any external boundary, run a quick OWASP-shaped mental check:

- **Injection.** Are all SQL / shell / OS commands parameterised? Any string-concatenated query into a DB is a fail.
- **Broken access control.** Does every endpoint that returns user-scoped data verify the caller is allowed to see *that* user's data, not just that they are *some* authenticated user?
- **Cryptographic failures.** Are passwords hashed with a modern KDF (argon2id, bcrypt, scrypt)? Are secrets in env vars or a vault, not in the source?
- **Insecure design.** Can the worst-case caller (malicious authenticated user, rate-limited but persistent attacker) cause damage proportional to the worst case you've thought about, or worse?
- **Misconfiguration.** Default credentials? Verbose error pages in production? Debug endpoints exposed?
- **Vulnerable dependencies.** Have you pinned, and have you scanned? (See `dependency-audit`.)
- **Auth/session.** Sessions invalidated on logout and password change? CSRF protected? Token rotation working?
- **Logging.** Do you log enough to detect an attack, but not so much that secrets land in the logs?

If you find yourself unsure on any item, escalate to a human reviewer who owns security. "I think it's fine" is the answer that ships breaches. The cost of an extra review pass is hours; the cost of a breach is months.
