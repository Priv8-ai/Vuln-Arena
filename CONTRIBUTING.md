# Contributing

Vuln Arena accepts benchmark improvements that preserve black-box reproducibility and the safety boundary.

## Objective acceptance contract

A new objective is not counted as verified until it has all of the following:

1. a documented normal workflow and narrow expected security effect;
2. a deterministic positive black-box check;
3. a meaningful negative/control check;
4. reset and replay validation;
5. a shortcut test covering public assets, static proofs, or direct final-step access as applicable;
6. a run-bound proof or independent state/browser witness;
7. maintainer solution material kept outside the agent pack; and
8. machine-readable truth, report matching, and release-test coverage.

Clues, route aliases, and multiple payloads for one root cause do not create extra objectives. A chain receives completion credit only when every required node is independently matched.

## Change workflow

```bash
python arena.py doctor
python scripts/build_findings_baseline.py
python scripts/build_machine_manifest.py
python scripts/build_router_assets.py
python scripts/verify_release.py
```

For runtime changes, start the relevant selectors and run `python arena.py verify --machines <selector> --mode full`. Before a release candidate, run `python scripts/verify_release.py --runtime --run-id <run-id>` with all 44 targets active. UI changes to the expansion suite must also render every profile at desktop and mobile width without console errors or horizontal overflow.

Keep generated runtime results under `runs/`. Do not commit seeds, private environment files, browser profiles, databases, agent captures, or comparison reports.

## Public-repository hygiene

Use fictional data and reserved domains such as `.test`, `.example`, and `.invalid`. Do not add personal names, real email addresses, local home paths, provider tokens, private keys, copied production records, or proprietary assets. Intentional secret-shaped challenge fixtures must be synthetic, documented in truth, and scoped to the vulnerable container.

Do not weaken loopback bindings, internal networks, dropped capabilities, read-only filesystems, or resource limits merely to simplify a scenario. If a vulnerability requires a dangerous primitive, bound its observable effect to the target container or an arena-owned mock service.
