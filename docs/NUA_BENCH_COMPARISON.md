# Vuln Arena compared with NUA Bench

Snapshot date: **2026-11-17**. This is a capability comparison, not a claim that a larger count automatically makes a better benchmark.

## Evidence baseline

The [NUA Bench repository](https://github.com/Nua-org/nua-bench) presents five Dockerized applications and 100 vulnerabilities. Its lab guides document 20 findings per application with concrete exploitation paths; for example, see the [Lab 1 guide](https://raw.githubusercontent.com/Nua-org/nua-bench/main/nua-lab-01/README.md) and [Lab 5 guide](https://raw.githubusercontent.com/Nua-org/nua-bench/main/nua-lab-05/README.md). The checked Compose definitions show realistic supporting components and multi-container layouts, including [Lab 1](https://raw.githubusercontent.com/Nua-org/nua-bench/main/nua-lab-01/docker-compose.yml) and [Lab 5](https://raw.githubusercontent.com/Nua-org/nua-bench/main/nua-lab-05/docker-compose.yml).

Vuln Arena's numbers below come from generated `benchmark/manifest.json` and `truth/findings-baseline.json`; drift in either artifact fails release verification.

## Current comparison

| Dimension | NUA Bench | Vuln Arena now | Interpretation |
| --- | --- | --- | --- |
| Public applications | 5 | 44 | Vuln Arena has substantially broader target and framework surface. |
| Catalogued findings | 100 documented findings | 482 comparison rows | Vuln Arena separates 364 accepted rows from 118 legacy references; 482 is not presented as 482 fully verified findings. |
| Fully accepted findings | Repository guides provide reproduction for 20 per lab | 364 objectives across 28 machines | Vuln Arena has machine-executed positive, control, shortcut, and replay gates for the accepted tier. |
| Live acceptance checks | Per-lab documented solution paths | 1,120 automated checks | Vuln Arena records 364 positive, 420 negative-control, 84 shortcut, and 252 reset/replay checks in JSON. |
| Chains | Application workflows and chained impact are documented | 72 catalogued chains: 56 accepted, 16 legacy | Vuln Arena reports complete, partial, and missed chains separately. |
| Implementation diversity | Five purpose-built, distinct applications | 16 multi-language originals plus 28 isolated profiles with unique visual/workflow systems on one shared engine | NUA is currently stronger in unique backend implementation per application; Vuln Arena combines much broader presentation/workflow diversity with an explicitly recorded shared-engine limitation. |
| Run variation | Static repository fixtures in the inspected labs | Fresh HMAC-derived proofs, reset capabilities, and preview secrets per run | Vuln Arena reduces proof-copying and cross-profile replay shortcuts. |
| Result contract | Human-readable lab answers | Versioned agent JSON schema plus offline matched/missed/unexpected/ambiguous/duplicate comparison | Vuln Arena is designed for repeatable agent-to-agent differential analysis. |
| Network publication | Checked Compose examples use ordinary host-port mappings | Every public port is explicitly bound to `127.0.0.1` | Vuln Arena's release gate fails any non-loopback publication. |
| Egress boundary | Multi-container bridge networks | CMS/platform targets join an internal-only network behind a fixed gateway | Vuln Arena proves CMS internet denial at runtime; equivalent segmentation for every legacy core machine remains work. |
| Lifecycle | Per-lab Compose commands | One-click installers plus a selector-aware CLI for catalog, start, status, agent pack, verify, compare, and stop | Vuln Arena creates a private run record and an answer-free agent pack together. |
| Addressing | Per-lab published ports | 44 direct loopback ports plus 44 generated subdomains and a searchable local dashboard | The generated router preserves independent target identity and is validated as a release gate. |
| Release evidence | Repository documentation and Compose files | Static CI plus opt-in 12-gate Docker verification with JSON/Markdown evidence and 28-layout desktop/mobile browser sweeps | Vuln Arena makes drift, privacy, isolation, routing, responsive rendering, and runtime acceptance explicit checks. |

## What “more advanced” means here

The project should exceed a reference benchmark through measurable properties, not marketing language:

1. **Effect verification:** a finding must produce the specified security effect; a vulnerability-name guess or copied token is insufficient.
2. **Controls:** every accepted objective has a meaningful non-exploit case, and the suite proves reset/replay behavior.
3. **Shortcut resistance:** public pages, source assets, and other profiles cannot yield credit directly.
4. **Freshness:** run-derived proofs and capabilities change without changing the public target contract.
5. **Differential reporting:** known misses, duplicates, ambiguous matches, unexpected findings, and partial chains remain independently visible.
6. **Safe black-box operation:** agent packs contain scope and report instructions but not source, truth, seeds, or evaluator capabilities.
7. **Releasable evidence:** a public candidate must pass privacy, schema, drift, isolation, smoke, acceptance, and egress gates.

## Honest remaining gaps

- M01–M16 are runnable, realistic, and catalogued, but their 192 planned v2 objectives do not yet have the same full acceptance lifecycle. They stay outside the verified denominator.
- The 28 CMS/platform profiles have distinct state, brands, routes, proof namespaces, containers, product pages, and layout systems, but share an implementation engine. Selected profiles should become purpose-built stacks to improve backend semantic diversity.
- Browser objectives currently use response/DOM evidence rather than an isolated victim-browser worker with event receipts.
- Fixed localhost ports allow one managed run at a time. Concurrent evaluation needs per-run gateway namespaces and dynamic routing.
- Several legacy images still need nonroot/read-only/limit consistency, dependency lockfiles, digest pinning, and per-scenario network segmentation.

## Priority roadmap

1. Promote M01–M04 to the complete acceptance contract, including browser and proxy/parser witnesses.
2. Add the isolated browser worker and arena-owned callback collector.
3. Split high-value profiles—WordPress, Drupal, Ghost, Strapi, Laravel, Django, Next.js, and Spring—into distinct implementations while preserving objective IDs.
4. Add per-run Compose project names, dynamic gateway ports, and concurrent-run isolation tests.
5. Finish core egress denial, nonroot/read-only controls, dependency locks, image digests, and health checks.
6. Add seeded scenario variants that change records, identities, ordering, and chain prerequisites without changing expected vulnerability classes.

The practical goal is therefore: keep Vuln Arena's breadth and acceptance rigor, while matching NUA Bench's strongest property—purpose-built application workflows—across progressively more machines.
