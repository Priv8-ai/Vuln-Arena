# Machine catalog

Generated from the agent brief and maintainer truth. Run `python scripts/build_machine_manifest.py --check` to detect drift.

## Coverage

- **44** public black-box machines on localhost
- **49** Compose services including private helpers
- **482** finding rows in the comparison catalog
- **480** rows assigned to one machine plus **2** cross-machine legacy rows
- **364** objectives with the full live acceptance contract
- **1120** live acceptance checks across positive, control, shortcut, and replay dimensions

`legacy_catalog_only` means the machine is runnable and smoke-tested, but its planned v2 objective set is not yet accepted. It must not be counted in the verified denominator.

## Machines

| ID | Service | Product/family | Tier | Direct | Domain | Accepted / catalogued | Chains | Contract |
| --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| M01 | `ledger` | Ledgerly finance portal (PHP/Apache/SQLite) | core | 18001 | `ledger.arena.localhost:18080` | 0 / 16 | 4 | `legacy_catalog_only` |
| M02 | `bazaar` | Morrow Market marketplace (Python/Flask) | core | 18002 | `bazaar.arena.localhost:18080` | 0 / 15 | 1 | `legacy_catalog_only` |
| M03 | `relay` | Relaywork API and identity console (Node/Express) | core | 18003 | `relay.arena.localhost:18080` | 0 / 12 | 1 | `legacy_catalog_only` |
| M04 | `mirror` | Northstar Edge gateway (Go) | core | 18004 | `mirror.arena.localhost:18080` | 0 / 7 | 1 | `legacy_catalog_only` |
| M05 | `desk` | Goodline helpdesk (Java) | core | 18005 | `desk.arena.localhost:18080` | 0 / 8 | 1 | `legacy_catalog_only` |
| M06 | `ink` | Margin publishing desk (Ruby/Sinatra) | core | 18006 | `ink.arena.localhost:18080` | 0 / 8 | 0 | `legacy_catalog_only` |
| M07 | `pulse` | Signalwatch live channel (Node/WS) | core | 18007 | `pulse.arena.localhost:18080` | 0 / 8 | 1 | `legacy_catalog_only` |
| M08 | `vaultlite` | Lockbox object custody (PHP) | core | 18008 | `vaultlite.arena.localhost:18080` | 0 / 9 | 2 | `legacy_catalog_only` |
| M09 | `forge` | Foundry CI job runner (Python/FastAPI) | core | 18009 | `forge.arena.localhost:18080` | 0 / 9 | 3 | `legacy_catalog_only` |
| M10 | `canvas` | Kiteboard collaboration (Node/EJS) | core | 18010 | `canvas.arena.localhost:18080` | 0 / 7 | 0 | `legacy_catalog_only` |
| M11 | `spool` | Backlog conversion warehouse (Go) | core | 18011 | `spool.arena.localhost:18080` | 0 / 6 | 0 | `legacy_catalog_only` |
| M12 | `atlas` | Alder & Rowe public site (Nginx/static) | core | 18012 | `atlas.arena.localhost:18080` | 0 / 11 | 3 | `legacy_catalog_only` |
| M13 | `quorum` | Quorum approval operations (.NET/ASP.NET Core) | core | 18013 | `quorum.arena.localhost:18080` | 0 / 0 | 0 | `legacy_catalog_only` |
| M14 | `foundry` | Kilnworks build room (Python/Django/Redis) | core | 18014 | `foundry.arena.localhost:18080` | 0 / 0 | 0 | `legacy_catalog_only` |
| M15 | `cacheline` | Edgewise delivery console (Nginx/Node multi-tier cache) | core | 18015 | `cacheline.arena.localhost:18080` | 0 / 0 | 0 | `legacy_catalog_only` |
| M16 | `harbor` | Tidevault object storage (Rust/Axum) | core | 18016 | `harbor.arena.localhost:18080` | 0 / 0 | 0 | `legacy_catalog_only` |
| M17 | `cms-wordpress` | Pressroom (WordPress) | cms | 18017 | `cms-wordpress.arena.localhost:18080` | 13 / 13 | 2 | `full_acceptance_verified` |
| M18 | `cms-shopify` | Northcart (Shopify) | cms | 18018 | `cms-shopify.arena.localhost:18080` | 13 / 13 | 2 | `full_acceptance_verified` |
| M19 | `cms-wix` | Canvasite (Wix) | cms | 18019 | `cms-wix.arena.localhost:18080` | 13 / 13 | 2 | `full_acceptance_verified` |
| M20 | `cms-squarespace` | Gallery (Squarespace) | cms | 18020 | `cms-squarespace.arena.localhost:18080` | 13 / 13 | 2 | `full_acceptance_verified` |
| M21 | `cms-joomla` | Civicline (Joomla) | cms | 18021 | `cms-joomla.arena.localhost:18080` | 13 / 13 | 2 | `full_acceptance_verified` |
| M22 | `cms-tilda` | Tilestone (Tilda) | cms | 18022 | `cms-tilda.arena.localhost:18080` | 13 / 13 | 2 | `full_acceptance_verified` |
| M23 | `cms-webflow` | Flowcraft (Webflow) | cms | 18023 | `cms-webflow.arena.localhost:18080` | 13 / 13 | 2 | `full_acceptance_verified` |
| M24 | `cms-duda` | AgencyDock (Duda) | cms | 18024 | `cms-duda.arena.localhost:18080` | 13 / 13 | 2 | `full_acceptance_verified` |
| M25 | `cms-godaddy` | Launchpad (GoDaddy Website Builder) | cms | 18025 | `cms-godaddy.arena.localhost:18080` | 13 / 13 | 2 | `full_acceptance_verified` |
| M26 | `cms-drupal` | Canopy (Drupal) | cms | 18026 | `cms-drupal.arena.localhost:18080` | 13 / 13 | 2 | `full_acceptance_verified` |
| M27 | `cms-adobe` | Experience Studio (Adobe Experience Manager) | cms | 18027 | `cms-adobe.arena.localhost:18080` | 13 / 13 | 2 | `full_acceptance_verified` |
| M28 | `cms-google-sites` | Siteboard (Google Sites) | cms | 18028 | `cms-google-sites.arena.localhost:18080` | 13 / 13 | 2 | `full_acceptance_verified` |
| M29 | `cms-lovable` | Promptpage (Lovable) | cms | 18029 | `cms-lovable.arena.localhost:18080` | 13 / 13 | 2 | `full_acceptance_verified` |
| M30 | `cms-prestashop` | Parcelshop (PrestaShop) | cms | 18030 | `cms-prestashop.arena.localhost:18080` | 13 / 13 | 2 | `full_acceptance_verified` |
| M31 | `cms-bitrix` | Workgrid (Bitrix) | cms | 18031 | `cms-bitrix.arena.localhost:18080` | 13 / 13 | 2 | `full_acceptance_verified` |
| M32 | `cms-weebly` | Pagelet (Weebly) | cms | 18032 | `cms-weebly.arena.localhost:18080` | 13 / 13 | 2 | `full_acceptance_verified` |
| M33 | `cms-typo3` | Chronicle (TYPO3) | cms | 18033 | `cms-typo3.arena.localhost:18080` | 13 / 13 | 2 | `full_acceptance_verified` |
| M34 | `cms-jimdo` | Quicksite (Jimdo) | cms | 18034 | `cms-jimdo.arena.localhost:18080` | 13 / 13 | 2 | `full_acceptance_verified` |
| M35 | `cms-opencart` | Cartline (OpenCart) | cms | 18035 | `cms-opencart.arena.localhost:18080` | 13 / 13 | 2 | `full_acceptance_verified` |
| M36 | `cms-tiendanube` | Cloudshop (Nuvemshop/Tiendanube) | cms | 18036 | `cms-tiendanube.arena.localhost:18080` | 13 / 13 | 2 | `full_acceptance_verified` |
| M37 | `cms-ghost` | Nightjar (Ghost) | cms | 18037 | `cms-ghost.arena.localhost:18080` | 13 / 13 | 2 | `full_acceptance_verified` |
| M38 | `cms-moodle` | Coursedeck (Moodle) | cms | 18038 | `cms-moodle.arena.localhost:18080` | 13 / 13 | 2 | `full_acceptance_verified` |
| M39 | `cms-mediawiki` | Commonroom (MediaWiki) | cms | 18039 | `cms-mediawiki.arena.localhost:18080` | 13 / 13 | 2 | `full_acceptance_verified` |
| M40 | `cms-strapi` | Fieldbase (Strapi) | cms | 18040 | `cms-strapi.arena.localhost:18080` | 13 / 13 | 2 | `full_acceptance_verified` |
| M41 | `platform-laravel` | Novadesk (Laravel) | platform | 18041 | `platform-laravel.arena.localhost:18080` | 13 / 13 | 2 | `full_acceptance_verified` |
| M42 | `platform-django` | Cabinet (Django) | platform | 18042 | `platform-django.arena.localhost:18080` | 13 / 13 | 2 | `full_acceptance_verified` |
| M43 | `platform-nextjs` | Frontmatter (Next.js) | platform | 18043 | `platform-nextjs.arena.localhost:18080` | 13 / 13 | 2 | `full_acceptance_verified` |
| M44 | `platform-spring` | PortalOne (Spring) | platform | 18044 | `platform-spring.arena.localhost:18080` | 13 / 13 | 2 | `full_acceptance_verified` |

## Runtime groups

- `core`: M01–M16, including private Redis and origin helpers where required.
- `cms`: M17–M40, routed through the localhost-only CMS gateway and internal metadata mock.
- `platform`: M41–M44, using the same isolated acceptance harness.
- `all`: every public target. Fixed host ports mean one benchmark run may be active at a time.

Use `python arena.py catalog`, `python arena.py start --machines all`, and `python arena.py verify --mode full` for the managed lifecycle.
