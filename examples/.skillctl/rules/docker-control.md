---
id: docker-control
title: Docker operations
tier: 2
triggers: [docker, container, image, dockerfile]
deps: []
summary: Pin tags, build reproducibly, scan for known CVEs before shipping.
---

# Docker operations

**Never run `:latest` in production.** Pin to a digest (`image@sha256:...`) or, at minimum, an immutable tag like `v1.4.2-2026-05-11`. A `:latest` reference means yesterday's build and today's build can run side-by-side in your fleet without you noticing.

**Builds must be reproducible.** Two builds of the same commit on different days should produce identical layer hashes. If they don't, you have unpinned base images, unpinned `pip`/`npm` resolution, or build-arg drift. Fix it before it bites.

**Scan before push.** Run a known-CVE scanner (Trivy, Grype, or the registry's built-in) on every image before it leaves the build pipeline. Fail the build on critical CVEs in the base layer. Document an exception process for the unavoidable ones — but make exceptions visible, not silent.

**Layer sensibly.** Put rarely-changing layers (system packages, language runtime) early; put often-changing layers (application code) late. This is not premature optimisation — it's the difference between a 2-minute and a 20-second rebuild on every commit.
