# Implementation status

Date: **2026-11-17**
Release state: **runtime-complete for the documented acceptance tier**

This page separates deployed functionality from future benchmark work so application count and verified-objective count are never conflated.

## Implemented and validated

- **44 independently addressable web targets** on direct loopback ports `18001–18044` and friendly subdomains through `127.0.0.1:18080`.
- **49 Compose services**: 44 targets, `foundry-redis`, `cacheline-origin`, `cms-metadata`, `cms-gateway`, and `arena-router`.
- **16 original multi-stack applications** spanning PHP, Flask, Node.js, Go, Java, Ruby, FastAPI, Nginx, ASP.NET Core, Django/Redis, Nginx/Node, and Rust/Axum.
- **28 CMS/framework family replicas** covering the selected top-20 CMS families plus Ghost, Moodle, MediaWiki, Strapi, Laravel, Django, Next.js, and Spring-style applications.
- **28 unique layout systems** backed by profile-specific typography, colors, hero visualization, metrics, workflow stages, records, and route vocabulary.
- Realistic home, workspace, library, insights, moderation, and family-discovery pages for every expansion profile.
- A generated subdomain control plane with a searchable 44-machine dashboard, zero-config `.arena.localhost` domains, optional managed `.arena.test` domains, and exact allowlisted upstream routing.
- Windows batch/PowerShell and Unix shell installers and teardown scripts. The normal path generates artifacts, checks prerequisites, installs optional hosts entries, builds the stack, starts a fresh seeded run, validates all routes, runs full acceptance, records the current run, and opens the dashboard.
- **364 fully accepted objective instances** and **56 accepted chains** across M17–M44.
- **1,120 live acceptance checks**: 364 positive effects, 420 negative controls, 84 shortcut-resistance checks, and 252 reset/replay checks.
- A generated comparison baseline with **482 rows and 72 chains**: the accepted tier above plus 118 separately labeled legacy references and 16 legacy chains.
- Run-derived HMAC proofs, reset capabilities, preview secrets, and profile-bound namespaces.
- A schema-validated answer-free agent pack containing direct and domain URLs, scope, rules, and the report contract.
- An offline comparator reporting matched, missed, unexpected, ambiguous, duplicate, complete-chain, partial-chain, and missed-chain results.
- Loopback-only publication, an internal-only CMS network, fixed gateway maps, resource guards, forbidden-mount checks, and live CMS internet-denial verification.
- Public-release privacy scanning for likely credentials, private keys, personal home paths, internal identifiers, and non-synthetic email domains while preserving documented synthetic leak fixtures.
- Static CI plus an opt-in full Docker release workflow with JSON/Markdown evidence artifacts.

## Latest verification

The one-click installer was run end to end on Windows Docker Desktop on 2026-11-17. It built the full stack, passed 44/44 direct targets, passed 44/44 subdomain targets, and completed the accepted suite. A subsequent seeded release run passed **12/12 gates**, including runtime egress denial.

Playwright browser sweeps then rendered all 28 expansion workspaces at desktop size and all 28 product homes at mobile size. The final sweep found 28 unique layouts, no failed HTTP responses, no missing application shells/heroes, no horizontal overflow, and no console errors.

Reproduce with:

```bash
python arena.py doctor
python arena.py start --machines all --run-id acceptance-run
python arena.py verify --mode full --run-id acceptance-run
python scripts/verify_release.py --runtime --run-id acceptance-run --out-dir runs/acceptance-run/release
```

## Explicit limitations

- M01–M16 are realistic, runnable, catalogued, routed, and smoke-tested, but their 118 catalog rows are still the `legacy_catalog_only` tier. They do not count toward the 364 accepted objectives.
- The 28 expansion targets have independent containers, state, identities, routes, proof namespaces, and visual systems, but share a purpose-built Flask implementation engine. They are training replicas, not redistributed upstream products.
- Browser-sensitive CMS objectives currently validate response/DOM effects; an isolated victim-browser worker with signed event receipts remains a future hardening track.
- Fixed host ports allow one managed benchmark run at a time on a workstation.
- The strict internal-network egress proof applies to M17–M44. Several older core services still share the normal `arena` bridge for intentional multi-stack compatibility.
- Some legacy images still need complete dependency locking, digest pinning, nonroot conversion, and read-only filesystem migration.
- A public software license has not been selected. Public visibility does not itself grant reuse rights; the repository owner should add the chosen license separately.

These limits are reflected in the manifest, comparison output, documentation, and release claims rather than hidden behind the total application count.
