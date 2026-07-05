---
id: dependency-audit
title: Dependency audit
tier: 2
triggers: [dependency, supply chain, npm audit, pip audit, sbom, cve]
deps: []
summary: Scan for known CVEs before merging dependency bumps. Generate an SBOM.
---

# Dependency audit

Every dependency bump — even a patch version — is an opportunity for a supply-chain attack to land. Treat it as a code change, not paperwork.

**Before merging a dependency PR:**

- Run an audit (`pip-audit`, `npm audit --production`, `cargo audit`, etc.) on the lockfile diff. Fail the build on known criticals.
- Skim the upstream changelog. A version bump from a project you don't recognise the maintainer of, with a release note like "performance improvements," is worth one more click.
- Compare publish date against commit date. A package published an hour ago, by a maintainer who hasn't shipped in 18 months, is unusual.
- If the dependency is new (not a bump), verify the package name. Typosquatting attacks (`reqeusts` for `requests`, `colorama-utils` for nothing) are still common.

**Generate an SBOM.** A Software Bill of Materials (Cyclonedx, SPDX) generated at build time gives you an answer to "are we affected by CVE-N" in minutes instead of days. Tools: `syft`, `cyclonedx-py`, `cdxgen`. Store the SBOM alongside the build artefact.

**Pin and lock.** Floating versions (`^1.2.0`, `~=1.2`) are convenient until they're a deploy outage. Pin exact versions in production lockfiles. Update intentionally.
