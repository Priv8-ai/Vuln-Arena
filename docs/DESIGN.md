# Design notes (operator only)

Each app exposes common + advanced vulns, leaks, response tricks, and at least one chain hook.
False-positive traps: some 500s and blocked panels are intentional noise — scoring penalizes unverified claims.
Cross-app: Atlas backup notes hint Forge SSRF; Mirror can proxy to sibling service hostnames on the arena network.

## UI systems (2026-11)

Full product skins via ui-forge / design-skills pack (vanilla chrome). Tokens live in `shared/ui/chrome.css`; brands in `shared/ui/BRANDS.md`. Challenge routes, comments, and sinks are preserved under the marketing chrome.

M17–M44 add a data-driven experience layer in `apps/cms-suite/experiences.json`. Every profile owns a unique layout token, typography mode, visual metaphor, product nouns, workspace title, metrics, workflow stages, and records. Shared templates supply consistent accessibility and benchmark behavior while `experience.css` changes the composition for all 28 layouts. Required surfaces are `/`, `/workspace`, `/library`, `/insights`, `/moderation`, and the profile's recognizable family routes.

## Addressing and control plane

Direct loopback ports remain the canonical compatibility endpoints. `arena-router` adds realistic per-service subdomains and a searchable dashboard on port 18080. Its map, dashboard target data, and optional `.arena.test` hosts block are generated from the machine manifest; release verification rejects drift or missing routes.

The router does not join `cms-private`. Profile traffic continues through `cms-gateway`, preserving the internal-only target network and fixed upstream allowlist.
