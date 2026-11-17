# Release verification

The public release contract is executable. `scripts/verify_release.py` writes a machine-readable `release.json` and a readable `release.md` under ignored `runs/` storage.

## Static gates

```bash
python scripts/verify_release.py --out-dir runs/release-static
```

All eight gates must pass:

1. generated findings-baseline drift;
2. generated machine-manifest drift;
3. generated router-asset drift;
4. Python compilation;
5. JSON Schema contracts;
6. Docker Compose configuration;
7. public-release privacy audit; and
8. Compose isolation policy.

## Full runtime gates

Start a seeded run, then pass its identifier so the verifier uses the same private proof namespace:

```bash
python arena.py start --machines all --run-id release-candidate
python scripts/verify_release.py \
  --runtime \
  --run-id release-candidate \
  --out-dir runs/release-candidate/release
```

Runtime mode adds four gates:

1. all 44 direct HTTP identities;
2. dashboard plus all 44 subdomain routes and all 28 layout identities;
3. 1,120 CMS/platform checks: 364 positive objectives, 420 negative controls, 84 shortcut checks, and 252 reset/replay checks; and
4. live isolation and CMS egress denial.

## Last local evidence

On **2026-11-17**, the full one-click Windows installation completed successfully and the subsequent release run passed **12/12 gates**. The same run also completed browser rendering sweeps across:

- 28 desktop workspaces with 28 unique layouts;
- 28 mobile product homes;
- zero console errors;
- zero horizontal-overflow failures; and
- representative full-page screenshots for the dashboard, Pressroom, and Northcart.

Runtime reports and proof seeds are intentionally not committed. Reproduce them locally or download CI's `full-runtime-evidence` artifact from an authorized manual workflow run.

## Interpretation

The 12/12 result proves deployability and the documented accepted tier. It does not upgrade the 118 M01–M16 legacy catalog rows into full v2 objectives. Those core applications are built, routed, and smoke-tested, but remain outside the accepted denominator until they receive the same positive/control/shortcut/replay contract.
