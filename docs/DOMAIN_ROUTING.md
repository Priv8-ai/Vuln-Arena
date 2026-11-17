# Local domain routing

Vuln Arena offers realistic per-application hostnames without exposing anything beyond the local machine. The router publishes one additional loopback port, `127.0.0.1:18080`, and routes requests by an exact generated host map.

```text
browser / agent
      |
      |  <service>.arena.localhost:18080
      v
arena-router (fixed allowlist)
      |-- M01–M16 --------------------> individual application containers
      `-- M17–M44 --> cms-gateway ----> isolated profile containers
```

## Two hostname modes

`.arena.localhost` is the default because modern browsers and operating systems resolve names below `localhost` to the loopback interface. It requires no hosts-file edit. Examples:

- `http://ledger.arena.localhost:18080`
- `http://cms-wordpress.arena.localhost:18080`
- `http://platform-nextjs.arena.localhost:18080`

`.arena.test` is an optional explicit hosts-file mode generated in `config/hosts.arena.test`. The setup scripts install and remove its marked block without touching unrelated entries.

## Generated source of truth

`scripts/build_router_assets.py` reads `benchmark/manifest.json` plus `apps/cms-suite/experiences.json` and generates:

- `apps/arena-router/targets.map.conf` — exact hostname-to-service map
- `apps/arena-router/public/targets.json` — dashboard data
- `config/hosts.arena.test` — optional loopback entries

Run `python scripts/build_router_assets.py --check` to fail on drift. `arena.py doctor` and both release modes run this check automatically.

## Safety properties

- The router binds only to `127.0.0.1`.
- Unknown hostnames return 404 instead of selecting an arbitrary upstream.
- Upstream names and ports come only from generated configuration, never request input.
- The router has a read-only root, dropped capabilities, no-new-privileges, a nonroot identity, bounded tmpfs, and CPU/memory/PID limits.
- It joins the public arena network but not the internal CMS network; CMS access still crosses the fixed gateway.
- It forwards the application `Host` header but deliberately does not synthesize `X-Forwarded-Host`, preserving the benchmark's response-manipulation boundary.
- Direct ports `18001–18044` remain available for compatibility and independent identity checks.

## Verification

```bash
python scripts/verify_domains.py --wait-seconds 60 --json-out runs/domain-check.json
```

The verifier checks the dashboard, all 44 hostname routes, identity markers, the router response header, all 28 profile workspaces, and 28 distinct layout tokens. It is also one of the 12 full release gates.
