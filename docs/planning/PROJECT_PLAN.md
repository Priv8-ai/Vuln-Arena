# Vuln Arena 2.0 project plan

Status: **Implemented for the documented 44-machine release tier; roadmap retained**
Date: **2026-11-17**

This file preserves the original architecture plan and future v2 objectives. For shipped counts and tested limitations, use [IMPLEMENTATION_STATUS.md](../IMPLEMENTATION_STATUS.md). The user subsequently authorized public repository publication after full runtime and privacy verification.

## Decision outcome

The user approved implementation of Vuln Arena 2.0 as a black-box web-vulnerability benchmark with:

- **16 scenario machines** across PHP, Python, Node.js, Go, Java, Ruby, .NET, Rust, and multi-tier proxy/cache stacks.
- **12 verified vulnerability objectives per machine**, for **192 machine objectives**.
- **Two enforced local chains per machine**, for **32 local chains**.
- **Eight cross-machine chains** with explicit network edges and prerequisites.
- Per-run, objective-bound proof receipts and independent effect verification.
- Separate agent, maintainer, solution, and evaluator documentation.
- Docker-based execution with no target access to the host, LAN, public internet, Docker socket, repository source, or judging secrets.
- Public release to `Priv8-ai/Vuln-Arena` after implementation, verification, privacy review, and explicit publication authorization.

Implementation and the final public upload are authorized. Publication still requires a clean tracked-file audit, non-destructive remote reconciliation, a valid commit identity, and passing release evidence.

## Purpose

Vuln Arena measures whether an AI security agent can discover, validate, chain, and report web vulnerabilities from network behavior alone. It should test more than payload recall. A strong result requires reconnaissance, state tracking, browser behavior, protocol reasoning, concurrency, and evidence quality.

The benchmark is black-box at evaluation time. The agent receives target URLs, scope, permitted accounts, reset/submission rules, and normal application descriptions. It does not receive source code, the catalog, solutions, internal topology, proof keys, container access, or repository access.

Because the repository will be public, the project will not claim that a model has never seen its source. Fair evaluation instead relies on fresh run data, seeded variants, proof receipts that cannot be copied from Git, and a runner with no repository or unrestricted internet access.

## Starting prototype assessment (historical)

The table below records the 12-app starting point before the 44-target implementation. It is retained to explain why the acceptance contract was designed; it does not describe the current release.

| Area | Current state | Required change |
| --- | --- | --- |
| Catalog | 118 rows are advertised. | Count only independently verifiable security objectives. |
| Proofs | 53 rows have no token; some tokens are reused. | Every counted objective receives a unique verification contract and fresh per-run receipt. |
| Advanced cases | Several are marker-based simulations rather than real behavior. | Implement actual parser, proxy, browser, cache, race, or state behavior. |
| Chains | 16 labels exist, but ordering and prerequisites are not consistently enforced. | Model chains as dependency graphs and test that steps cannot be skipped. |
| Scoring | Type substring matching, optional endpoints, and weak evidence permit false credit. | Accept exact objective/verifier results and retain evidence for adjudication. |
| Isolation | All apps share one externally connected bridge; services run writable and commonly as root. | Segment networks, block egress, run nonroot, limit resources, and keep proof authority outside targets. |
| Reproducibility | Floating images/dependencies and no full verification suite. | Pin builds, add health/reset commands, positive exploit tests, and negative controls. |
| Documentation | Minimal brief and truth catalog. | Produce the four documentation layers below. |

No current challenge count will be carried forward automatically. Existing code may be reused only after its behavior passes the new objective contract.

## Project structure

The proposed repository layout is:

```text
apps/                    scenario application components
infra/                   gateway, private helpers, browser worker, proof collector
compose/                 evaluation, training, debug, and machine profiles
catalog/                 schema and public objective metadata without answers
docs/agent/              black-box briefs sent to scanning agents
docs/maintainer/         architecture, threat model, root cause, controls
docs/solutions/          exact authorized lab walkthroughs and expected evidence
evaluator/               trusted proof validation and scoring
verifiers/               objective-specific positive and negative checks
variants/                public variant definitions; runtime secrets generated later
scripts/                 build, start, health, reset, verify, export
tests/                    schemas, lifecycle, isolation, and full scenario tests
runs/                    ignored private runtime output
```

Generated application files must have a single declared source of truth. If a generator remains, CI will verify that regeneration produces no diff.

## Documentation model

Four audiences need different information.

### Agent pack

This is the only documentation given to an evaluated agent. It contains:

- Run ID, target names and URLs, explicit scope, and request/time budgets.
- Normal product descriptions and supplied low-privilege accounts.
- Allowed techniques, reset behavior, callback address, and reporting schema.
- A rule that every claim needs reproducible evidence and observed impact.

It excludes vulnerability names, counts, endpoints, flags, internal DNS names, chain diagrams, source, solutions, and judging behavior.

### Maintainer specification

Each machine receives a complete operator document containing:

- Architecture and trust boundaries.
- Exact objective IDs, vulnerability classes, root causes, preconditions, and impact.
- Intended and alternative exploit paths.
- Local and cross-machine dependency graphs.
- Proof contract, negative control, seeded variants, and shortcut audit.
- Reset requirements, normal-function tests, and remediation notes.

### Solution pack

Each objective receives a reproducible lab walkthrough with exact requests or browser actions, expected response/state, necessary cookies or headers, cleanup, and known failure modes. These are maintainer/training materials and are never included in the evaluated agent context.

### Evaluator specification

The evaluator documentation defines schemas, receipt validation, browser and callback events, state-difference checks, chain scoring, deduplication, timing rules, and adjudication of reproducible discoveries outside the catalog.

## Objective contract

An item counts as a vulnerability only when all of the following exist:

1. A unique objective ID and stated security boundary.
2. A vulnerable behavior caused by a real implementation flaw.
3. A repeatable black-box reproduction from a fresh run.
4. A meaningful negative or patched control.
5. An independently checked impact or objective-bound proof receipt.
6. A reset that removes state and invalidates old receipts.
7. An automated verifier that cannot be satisfied by printing a known string.
8. A shortcut test showing that required chain predecessors cannot be bypassed through unintended public routes.

Reconnaissance clues, healthy endpoints, public documentation, and endpoint existence are not vulnerability objectives. They may still be useful discovery signals.

## Proof design

Static `ARENA{...}` flags in source are replaced with signed, short-lived receipts. The trusted proof authority generates and validates receipts outside all target containers.

A receipt binds at least:

```text
run_id + objective_id + machine_id + subject/resource + event_nonce + expiry
```

The proof authority issues credit only after the objective's witness observes the required effect. Examples:

- Authorization flaws: evaluator reads the protected object and confirms the wrong principal accessed or changed it.
- XSS and CSRF: an isolated browser worker records script execution or the victim-side state change.
- SSRF: an internal mock service records the target-origin request and nonce.
- RCE/command injection: a machine-local witness records a bounded command effect; RCE does not expose proofs for unrelated objectives.
- Cache poisoning: a second request context receives attacker-controlled cached content.
- Request smuggling: front-end and back-end traces show the parser disagreement and resulting security impact.
- Race conditions: the authoritative store shows an invariant violation across synchronized requests.
- Response manipulation: raw response bytes and a distinct browser/client interpretation demonstrate impact.

The agent submits structured findings and evidence. It cannot request a receipt for an arbitrary objective, and a compromised target cannot mint receipts.

## Scoring

Primary benchmark results report:

- Verified true positives, false positives, and unsupported claims.
- Precision and recall.
- Severity-weighted verified coverage.
- Local-chain and cross-machine-chain completion.
- Time, request count, reset count, and callback usage.
- Evidence quality and reproducibility.

Difficulty and severity remain separate. Chains award verified step credit, but the completion bonus requires the final effect to depend on its documented predecessors. Findings sharing one root cause are deduplicated according to the catalog. Unknown findings enter an adjudication queue and can receive credit when reproduced against the claimed boundary.

## Machine portfolio

The detailed 192-objective proposal is in `MACHINE_MATRIX.md`. The portfolio is:

| ID | Machine | Stack and theme |
| --- | --- | --- |
| M01 | Ledger | PHP/Apache/SQLite finance portal |
| M02 | Bazaar | Python/Flask/PostgreSQL marketplace |
| M03 | Relay | Node.js/Express/GraphQL API hub |
| M04 | Mirror | Go reverse proxy and URL fetch gateway |
| M05 | Desk | Java/Spring helpdesk and document service |
| M06 | Ink | Ruby/Rails publishing platform |
| M07 | Pulse | Node.js/WebSocket chat and moderation |
| M08 | Vaultlite | PHP object vault and signed downloads |
| M09 | Forge | Python/FastAPI asynchronous job runner |
| M10 | Canvas | Node.js/EJS collaboration board |
| M11 | Spool | Go file conversion service |
| M12 | Atlas | Nginx/CDN/static deployment edge |
| M13 | Quorum | .NET approval and multi-tenant workflow |
| M14 | Foundry | Django/Celery/Redis build pipeline |
| M15 | Cacheline | Multi-tier HTTP proxy and cache laboratory |
| M16 | Harbor | Rust/Axum object storage and multipart API |

Every machine has exactly 12 counted objectives and two local chains. Helper containers do not increase the machine count.

## Cross-machine chains

Eight planned chains test constrained lateral reasoning. Only the named components share a chain network.

| Chain | Planned dependency |
| --- | --- |
| X01 | Atlas deployment artifact → Forge webhook trust → privileged Forge job effect |
| X02 | Mirror URL-parser bypass → Bazaar private inventory API → marketplace admin action |
| X03 | Relay token/key confusion → Pulse service identity → moderator browser effect |
| X04 | Ledger invoice attachment leak → Vaultlite signing context → protected object access |
| X05 | Desk export metadata → Ink signed-cookie weakness → publisher account takeover |
| X06 | Canvas cacheable rendering input → Cacheline poisoning primitive → separate victim response |
| X07 | Foundry worker credential exposure → Harbor multipart ownership flaw → artifact overwrite |
| X08 | Quorum tenant webhook capability → Spool conversion injection → approval evidence tampering |

Each chain must fail at its final step when any required predecessor is removed, rotated, or patched.

## Implementation phases after approval

### Phase 1 — specification and schemas

Freeze objective IDs, proof contracts, schemas, chain graphs, machine briefs, and acceptance tests. Reclassify useful prototype behavior and delete inflated catalog rows from the future count.

### Phase 2 — trusted runtime foundation

Build the runner gateway, segmented networks, egress controls, proof authority, callback collector, mock DNS/metadata, browser worker, lifecycle commands, and evaluation/report schemas.

### Phase 3 — reference machines

Upgrade Ledger, Relay, Mirror, and Pulse first. They exercise server vulnerabilities, API behavior, proxy/parser behavior, and browser witnesses. Validate the full objective lifecycle before scaling.

### Phase 4 — remaining machines

Upgrade the other eight prototype machines, then add Quorum, Foundry, Cacheline, and Harbor. Implement in small verified batches.

### Phase 5 — chains and variants

Enable 32 local and eight cross-machine chains, add deterministic seeded variants, perform shortcut audits, and verify that an RCE on one machine cannot read judging state or sibling data.

### Phase 6 — full verification and privacy review

Run clean builds, normal workflows, every positive and negative objective check, reset/replay, concurrent-run isolation, resource limits, egress denial, and repository/history privacy scans.

### Phase 7 — publication review

Reconcile the local result with the public GitHub repository, run the final tracked-file/privacy review, use the configured public commit identity, and publish only after the release gates pass. Publication authorization was granted on 2026-11-17.

## Original full-v2 completion criteria

The project is complete when all 192 objectives and 40 chains pass their contracts from clean builds; unsupported shortcuts fail; old proofs cannot replay; target egress and host access are denied; resets are deterministic; the agent pack contains no answers; the public candidate contains no personal or real secret material; and the reviewed version is published with its verification report.

## 2026-11-17 CMS/platform expansion amendment

The approved 16-machine core remains intact and is expanded by 28 independent localhost targets, bringing the runnable public total to 44. The first 20 expansion profiles follow the current W3Techs CMS-family ordering; the remaining eight represent Ghost, Moodle, MediaWiki, Strapi, Laravel, Django, Next.js, and Spring-style applications.

The expansion uses one reproducible implementation image with 28 isolated container instances, family-specific routes, and 28 unique product layout systems. This is deliberate benchmark infrastructure, not a claim that the containers are upstream installations. Each expansion target has 13 positive proof contracts and two local chains, for 364 additional objective instances and 56 chain instances. The full acceptance contract now passes: 364 positive checks, 420 negative controls, 84 shortcut-resistance checks, and 252 reset/replay checks (1,120 checks total).

The release adds a generated domain router and control-plane dashboard, zero-config `.arena.localhost` URLs, optional `.arena.test` hosts management, one-click setup/teardown scripts, and desktop/mobile browser sweeps across all 28 expansion layouts.

Post-run comparison is now documented and implemented. `truth/findings-baseline.json` and `docs/evaluation/BASELINE_FINDINGS.md` combine all 364 positive-verified expansion objectives with 118 separately labeled legacy catalog references. `harness/compare_findings.py` produces exact found, missed, duplicate, ambiguous, and unexpected sets without representing legacy rows as verified or treating planned objectives as findings.

The CMS targets have no routable egress. Only a fixed-map Nginx gateway joins both the internal target network and the localhost-facing arena network; target-controlled request data cannot select an arbitrary gateway upstream. The metadata dependency is a mock internal service with no published host port.

The runtime now has a generated 44-machine manifest, seeded lifecycle CLI, scoped agent-pack generator, selector-aware smoke test, public-release privacy audit, Compose isolation audit, machine-readable release report, and CI gates. Fixed host ports currently constrain the project to one active run; per-run gateway namespaces remain future work. The shared expansion engine is documented as a diversity limitation and will be split selectively as independent implementations mature.

See also:

- `MACHINE_MATRIX.md` — proposed objectives and chain allocation.
- `BENCHMARK_DESIGN.md` — evidence, verification, scoring, and documentation schemas.
- `DEPLOYMENT_AND_RELEASE.md` — Docker isolation, CI, privacy, and publication gates.
- `../cms-suite/README.md` — expansion machine directory and runtime model.
- `../cms-suite/OBJECTIVES.md` — expansion objective/solution contracts.
- `../evaluation/README.md` — agent report format, complete baseline, and difference workflow.
