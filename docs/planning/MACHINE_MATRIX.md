# Proposed machine and vulnerability matrix

Status: **Approved target matrix; implementation in progress**
Date: **2026-11-17**

This matrix defines the intended Vuln Arena 2.0 scope. It is a specification, not a claim that every row is implemented. Every row must satisfy the objective contract in `PROJECT_PLAN.md` before it is counted. Current findings and their validation states are tracked separately in `truth/findings-baseline.json` and `docs/evaluation/BASELINE_FINDINGS.md`.

Each core machine M01–M16 targets exactly 12 verified objectives and two local dependency chains. Expansion machines M17–M44 use the separate 13-objective CMS contract near the end of this document. Clues and endpoint discovery are not included in either count.

## M01 — Ledger

Stack: PHP, Apache, SQLite/PostgreSQL. Theme: finance and invoice portal.

| ID | Vulnerability | Required verified effect |
| --- | --- | --- |
| M01-01 | SQL injection in login | Authenticate as a different principal without its password. |
| M01-02 | Invoice object authorization failure | Read another tenant's evaluator-selected invoice. |
| M01-03 | Missing authorization on payment approval | Approve a protected payment using an unauthorized identity. |
| M01-04 | Backup/source configuration disclosure | Recover a run-seeded recovery algorithm clue from a web-served backup. |
| M01-05 | Predictable password-reset token | Derive the evaluator-selected account's current token. |
| M01-06 | Reset-session invalidation failure | Obtain a usable privileged session through the recovery flow. |
| M01-07 | Stored XSS in invoice notes | Execute in the isolated accountant browser and produce a witness event. |
| M01-08 | CSRF on beneficiary creation | Cause the isolated victim to add an attacker-controlled beneficiary. |
| M01-09 | Polyglot upload/content validation bypass | Store and serve active content despite the declared upload policy. |
| M01-10 | Path traversal/local file inclusion | Read a run-selected file outside the intended page directory. |
| M01-11 | Command injection in diagnostics | Produce the bounded machine-local command witness. |
| M01-12 | Concurrent double-spend race | Violate the balance invariant using synchronized requests. |

Local chains: `M01-A: 01 → 02 → 03`; `M01-B: 04 → 05 → 06`.

## M02 — Bazaar

Stack: Python, Flask, PostgreSQL. Theme: marketplace, reviews, and seller tools.

| ID | Vulnerability | Required verified effect |
| --- | --- | --- |
| M02-01 | SQL injection in seller search | Extract a run-selected record through the vulnerable query. |
| M02-02 | SSRF in webhook tester | Reach the private marketplace metadata service. |
| M02-03 | SSRF redirect/filter bypass | Obtain the private service's objective nonce through an allowed-looking URL. |
| M02-04 | Missing authorization on seller administration | Change the protected seller state with an unauthorized credential. |
| M02-05 | Stored XSS in product review | Execute in the moderator browser. |
| M02-06 | Browser credential/action confusion | Use the XSS context to perform the evaluator-selected moderator action. |
| M02-07 | Negative-quantity business logic | Increase funds or inventory in violation of the purchase invariant. |
| M02-08 | Client-controlled price | Purchase the protected item below its server-side price. |
| M02-09 | Coupon redemption TOCTOU | Redeem a single-use coupon more than once concurrently. |
| M02-10 | Jinja server-side template injection | Produce a bounded server-side evaluation witness. |
| M02-11 | Path traversal in seller export | Read a seeded file outside the export directory. |
| M02-12 | Content-Type/callback response injection | Cause a browser to execute attacker-controlled response content. |

Local chains: `M02-A: 02 → 03 → 04`; `M02-B: 05 → 06 → 04`.

## M03 — Relay

Stack: Node.js, Express, GraphQL. Theme: API gateway and identity service.

| ID | Vulnerability | Required verified effect |
| --- | --- | --- |
| M03-01 | JWT algorithm/key confusion | Produce a token accepted as the protected principal. |
| M03-02 | Attacker-influenced JWK resolution | Make verification trust the arena-controlled attacker key service. |
| M03-03 | Mass assignment of role/tenant | Persist a protected field omitted from the public schema. |
| M03-04 | Prototype pollution in configuration merge | Change a security-relevant default for a fresh request context. |
| M03-05 | GraphQL field authorization failure | Read the evaluator-selected restricted field. |
| M03-06 | GraphQL batching rate-limit bypass | Exceed the documented operation limit in one request. |
| M03-07 | Duplicate-key JSON parser differential | Cause gateway and application to use different security values. |
| M03-08 | Content-Type/body parser differential | Bypass a policy enforced on a different parsed representation. |
| M03-09 | Credentialed CORS origin reflection | Read protected API data in the isolated cross-origin browser. |
| M03-10 | DOM XSS in API explorer | Execute in the isolated browser through the documented client sink. |
| M03-11 | Note IDOR | Read another user's evaluator-selected note. |
| M03-12 | Refresh-token rotation race | Obtain two valid successors from one refresh token. |

Local chains: `M03-A: 02 → 01 → 05`; `M03-B: 04 → 03 → 05`.

## M04 — Mirror

Stack: Go front end and private origin. Theme: reverse proxy, URL fetch, and routing.

| ID | Vulnerability | Required verified effect |
| --- | --- | --- |
| M04-01 | SSRF in URL proxy | Make the gateway request a private evaluator endpoint. |
| M04-02 | Redirect-based SSRF filter bypass | Cross the address policy after a controlled redirect. |
| M04-03 | IP-literal/canonicalization bypass | Reach a denied address using an alternative valid representation. |
| M04-04 | DNS rebinding/time-of-check gap | Resolve an allowed name to the private mock target at fetch time. |
| M04-05 | Front-end/back-end URL parser differential | Produce different authorities or paths across the two parsers. |
| M04-06 | Trusted rewrite-header authorization bypass | Reach a protected route through an untrusted rewrite header. |
| M04-07 | Host-header password-link poisoning | Make the victim flow emit a reset link with attacker-controlled authority. |
| M04-08 | Response header splitting | Inject an additional response header visible in raw bytes. |
| M04-09 | Hop-by-hop header confusion | Preserve or remove a security header differently across proxy hops. |
| M04-10 | Cache-key poisoning | Make a separate victim receive attacker-influenced cached content. |
| M04-11 | Proxy/origin path-normalization mismatch | Bypass a front-end path policy at the origin. |
| M04-12 | Request tunneling/internal-header disclosure | Recover the evaluator-selected internal header through the proxy chain. |

Local chains: `M04-A: 05 → 01 → 12`; `M04-B: 08 → 10 → 06`.

## M05 — Desk

Stack: Java, Spring Boot. Theme: helpdesk, attachments, and document processing.

| ID | Vulnerability | Required verified effect |
| --- | --- | --- |
| M05-01 | Ticket IDOR | Read the protected ticket assigned to another organization. |
| M05-02 | Unsafe Java deserialization | Trigger the bounded deserialization effect using a serialized object. |
| M05-03 | XML external entity processing | Read the run-selected local XML fixture or hit the mock callback. |
| M05-04 | Expression-language injection | Evaluate a restricted server-side expression with observable output. |
| M05-05 | Path traversal in document read | Read outside the document root. |
| M05-06 | ZIP extraction traversal | Write an archive entry outside the extraction directory. |
| M05-07 | Weak signed-session handling | Create or retain a privileged session that should be rejected. |
| M05-08 | CSRF on ticket assignment | Reassign the evaluator-selected ticket through the victim browser. |
| M05-09 | Unicode-normalization identity confusion | Authenticate or authorize as the protected confusable identity. |
| M05-10 | Stored XSS in attachment preview | Execute in the agent browser that previews the attachment. |
| M05-11 | Forwarded-header trust authorization bypass | Reach the internal staff action through spoofed proxy identity data. |
| M05-12 | Ticket-claim race | Make two principals successfully claim the same exclusive ticket. |

Local chains: `M05-A: 03 → 07 → 01`; `M05-B: 06 → 04 → 11`.

## M06 — Ink

Stack: Ruby on Rails. Theme: publishing, drafts, and editorial workflow.

| ID | Vulnerability | Required verified effect |
| --- | --- | --- |
| M06-01 | Draft-post IDOR | Read a private draft owned by another author. |
| M06-02 | Rails parameter mass assignment | Persist an editor-only field as an ordinary author. |
| M06-03 | ERB template injection | Produce a bounded server-side evaluation witness. |
| M06-04 | Unsafe YAML deserialization | Trigger the documented machine-local deserialization effect. |
| M06-05 | SQL injection in editorial search | Extract an evaluator-selected unpublished record. |
| M06-06 | Weak signed-cookie secret | Forge a cookie accepted as the protected role. |
| M06-07 | Path traversal in archive export | Read the run-selected credential/clue fixture. |
| M06-08 | Stored XSS in preview | Execute in the editor browser. |
| M06-09 | CSRF on publication | Publish the evaluator-selected draft through the victim session. |
| M06-10 | OAuth callback/open-redirect confusion | Deliver an arena-issued authorization artifact to the attacker callback. |
| M06-11 | Upload MIME/extension confusion | Store active content under a supposedly passive media policy. |
| M06-12 | Cross-user fragment-cache poisoning | Make another user receive content cached under the wrong identity. |

Local chains: `M06-A: 07 → 06 → 01`; `M06-B: 11 → 03 → 09`.

## M07 — Pulse

Stack: Node.js, WebSocket, isolated moderator browser. Theme: chat and moderation.

| ID | Vulnerability | Required verified effect |
| --- | --- | --- |
| M07-01 | Cross-site WebSocket hijacking | Use a foreign origin to perform an authenticated socket action. |
| M07-02 | WebSocket authentication downgrade | Continue with protected capabilities after invalid or downgraded auth. |
| M07-03 | Message/channel IDOR | Read or mutate a protected private-channel message. |
| M07-04 | Stored XSS in chat rendering | Execute in a separate chat participant browser. |
| M07-05 | Stored XSS in report moderation | Execute in the isolated moderator browser. |
| M07-06 | Moderator action/credential capture | Produce the protected browser-side action through the XSS context. |
| M07-07 | Command injection in media job | Trigger the bounded worker command witness. |
| M07-08 | Prototype pollution of permissions | Change authorization behavior for a fresh socket/request. |
| M07-09 | Concurrent moderation race | Apply two mutually exclusive moderation decisions. |
| M07-10 | History authorization failure | Read a room history outside the caller's membership. |
| M07-11 | Content-sniffing response manipulation | Cause active browser interpretation of a nominally passive response. |
| M07-12 | Session token in URL/referrer | Deliver a valid run token to the arena-controlled receiving origin. |

Local chains: `M07-A: 05 → 06 → 03`; `M07-B: 12 → 02 → 07`.

## M08 — Vaultlite

Stack: PHP. Theme: signed object downloads, uploads, and audit processing.

| ID | Vulnerability | Required verified effect |
| --- | --- | --- |
| M08-01 | Client/source-map HMAC secret disclosure | Recover the run-seeded signing material exposed to the client. |
| M08-02 | Loose-comparison signature bypass | Pass signature validation through PHP type semantics. |
| M08-03 | Signature canonicalization mismatch | Produce two interpretations that share an accepted signature. |
| M08-04 | Signed-URL object authorization failure | Read the protected object without its authorized grant. |
| M08-05 | Signed path/unsigned file override | Use a valid signature for one object to retrieve another path. |
| M08-06 | Object-listing authorization failure | Enumerate protected object identifiers outside the caller's vault. |
| M08-07 | Upload extension/MIME filter bypass | Store server-interpreted content despite the upload rule. |
| M08-08 | Uploaded-file inclusion | Execute the uploaded content through an include/view path. |
| M08-09 | Second-order command injection | Cause stored metadata to reach the audit command sink. |
| M08-10 | Public signing oracle | Obtain a signature for a resource outside the caller's authority. |
| M08-11 | Signed-URL TOCTOU | Swap the protected resource after validation and before use. |
| M08-12 | Prefix-based password validation | Authenticate with a non-equal password accepted by the flawed comparison. |

Local chains: `M08-A: 01 → 03 → 04`; `M08-B: 07 → 08 → 09`.

## M09 — Forge

Stack: Python, FastAPI, private worker. Theme: asynchronous build and rendering jobs.

| ID | Vulnerability | Required verified effect |
| --- | --- | --- |
| M09-01 | SSRF in webhook delivery | Reach the private Forge metadata service. |
| M09-02 | Redirect/DNS SSRF policy bypass | Obtain the private response through an initially allowed destination. |
| M09-03 | Internal worker-token disclosure | Recover a run-bound worker capability through the SSRF path. |
| M09-04 | Command injection in job runner | Trigger the bounded worker command witness. |
| M09-05 | Job validation/use TOCTOU | Mutate a validated job before worker execution. |
| M09-06 | Jinja template injection | Produce a bounded server-side template evaluation effect. |
| M09-07 | Artifact path traversal | Read an artifact outside the caller's job directory. |
| M09-08 | Unsafe pickle import | Trigger the documented deserialization witness. |
| M09-09 | Job owner/priority mass assignment | Create a protected job state using a low-privilege identity. |
| M09-10 | Archive extraction traversal | Write a build input outside its extraction directory. |
| M09-11 | JSONP/content-type response manipulation | Execute protected response data in the isolated browser origin. |
| M09-12 | Job-result IDOR | Read another tenant's evaluator-selected result. |

Local chains: `M09-A: 01 → 03 → 09`; `M09-B: 10 → 05 → 04`.

## M10 — Canvas

Stack: Node.js, Express, EJS. Theme: collaborative boards and templates.

| ID | Vulnerability | Required verified effect |
| --- | --- | --- |
| M10-01 | Prototype pollution in board merge | Change a security-relevant default for a new board operation. |
| M10-02 | EJS server-side template injection | Produce the bounded server-side evaluation witness. |
| M10-03 | Path traversal in template picker | Read a seeded file outside the template directory. |
| M10-04 | JSON type confusion in role import | Bypass a role validation decision using an unexpected JSON shape. |
| M10-05 | Board IDOR | Read or modify another team's protected board. |
| M10-06 | OAuth redirect validation bypass | Deliver an arena authorization artifact to the attacker callback. |
| M10-07 | Source-map secret/config disclosure | Recover the run-seeded client build secret or hidden route clue. |
| M10-08 | Upload path overwrite | Replace an existing protected board asset through filename handling. |
| M10-09 | Stored XSS in board widget | Execute in a collaborator browser. |
| M10-10 | CSRF on collaborator invitation | Add the evaluator-selected account through the victim session. |
| M10-11 | Template-cache key poisoning | Make another tenant render the attacker's cached template. |
| M10-12 | DOM clobbering of privileged API target | Redirect a trusted client action to the arena-controlled endpoint. |

Local chains: `M10-A: 07 → 06 → 05`; `M10-B: 01 → 11 → 02`.

## M11 — Spool

Stack: Go. Theme: file conversion, archives, and worker queue.

| ID | Vulnerability | Required verified effect |
| --- | --- | --- |
| M11-01 | Command injection in converter | Trigger the bounded machine-local command witness. |
| M11-02 | Path traversal in file read | Read the evaluator-selected file outside the data root. |
| M11-03 | SSRF in remote import | Reach the private conversion-control endpoint. |
| M11-04 | Archive path traversal | Write an entry outside the job extraction directory. |
| M11-05 | Host-header internal-route bypass | Reach the protected control action through spoofed authority. |
| M11-06 | Shell-filter bypass | Execute a denied command using an alternative shell representation. |
| M11-07 | Symlink validation/use race | Redirect a checked output path to the protected target. |
| M11-08 | Predictable temporary-file collision | Read or replace another job's temporary content. |
| M11-09 | Content-Disposition response splitting | Inject a response header through a filename field. |
| M11-10 | Range boundary information leak | Receive bytes outside the authorized object range. |
| M11-11 | Nested archive extraction confusion | Escape the intended root through a nested archive path. |
| M11-12 | Conversion-job IDOR | Read or cancel another tenant's evaluator-selected job. |

Local chains: `M11-A: 03 → 05 → 12`; `M11-B: 11 → 07 → 01`.

## M12 — Atlas

Stack: Nginx, static deployment origin, cache helper. Theme: deployment leaks and edge configuration.

| ID | Vulnerability | Required verified effect |
| --- | --- | --- |
| M12-01 | Source-map source/config disclosure | Recover run-seeded source content excluded from the built bundle. |
| M12-02 | Exposed Git object recovery | Reconstruct the evaluator-selected deleted deployment file. |
| M12-03 | Backup configuration exposure | Retrieve a backup containing a run-specific private route/capability. |
| M12-04 | Nginx alias path traversal | Read outside the configured alias root. |
| M12-05 | Autoindex authorization failure | Enumerate a protected deployment directory. |
| M12-06 | Web-cache deception | Cache and retrieve a protected response under a public-looking path. |
| M12-07 | Edge/origin path-normalization bypass | Reach a protected origin route rejected by the edge's canonical path. |
| M12-08 | Internal redirect/X-Accel authorization bypass | Make Nginx serve a protected internal resource. |
| M12-09 | Credentialed CORS misconfiguration | Read protected deployment data from the isolated foreign origin. |
| M12-10 | Server-side include injection | Inject content evaluated by the configured SSI path. |
| M12-11 | Unkeyed-header cache poisoning | Make a separate victim receive attacker-influenced cached content. |
| M12-12 | Origin error/header disclosure | Recover evaluator-selected internal routing data from a manipulated error response. |

Local chains: `M12-A: 02 → 03 → 08`; `M12-B: 10 → 11 → 06`.

## M13 — Quorum

Stack: .NET/ASP.NET Core. Theme: multi-tenant approvals and webhook integrations.

| ID | Vulnerability | Required verified effect |
| --- | --- | --- |
| M13-01 | JWT audience/issuer confusion | Use a token minted for one arena service against the protected service. |
| M13-02 | Tenant-scoping IDOR | Read or change another tenant's approval object. |
| M13-03 | Model-binding overposting | Persist an approver-only field omitted from the public form. |
| M13-04 | Unsafe polymorphic JSON handling | Instantiate the protected server-side type and trigger its bounded effect. |
| M13-05 | Authorization-handler fail-open | Access the protected action through the evaluator-selected error path. |
| M13-06 | Approval quorum race | Complete an approval with fewer distinct approvers than required. |
| M13-07 | SSRF in webhook validation | Reach the private tenant-capability service. |
| M13-08 | Razor template injection | Produce the bounded server-side template evaluation witness. |
| M13-09 | Export path traversal | Read a run-selected file outside the tenant export directory. |
| M13-10 | Forwarded-header identity trust | Spoof the internal proxy identity at the application. |
| M13-11 | Credentialed CORS origin weakness | Read protected approval data from the isolated foreign origin. |
| M13-12 | PDB/source artifact disclosure | Recover a run-seeded source/config value from deployment artifacts. |

Local chains: `M13-A: 12 → 01 → 05`; `M13-B: 07 → 03 → 06`.

## M14 — Foundry

Stack: Django, Celery, Redis, PostgreSQL. Theme: asynchronous build pipeline.

| ID | Vulnerability | Required verified effect |
| --- | --- | --- |
| M14-01 | Raw-query SQL injection | Extract the evaluator-selected protected build record. |
| M14-02 | Weak Django signing secret | Forge a protected signed workflow value. |
| M14-03 | Unsafe task deserialization | Trigger the bounded worker deserialization effect. |
| M14-04 | Celery task injection | Enqueue an unauthorized evaluator-selected task. |
| M14-05 | SSRF to private Redis/task gateway | Reach the private queue helper through a web fetch feature. |
| M14-06 | Build-result IDOR | Read another organization's protected build result. |
| M14-07 | Owner/visibility mass assignment | Create or alter a build under another organization. |
| M14-08 | Duplicate-credit/build race | Cause one prepaid build entitlement to execute more than once. |
| M14-09 | Jinja template injection | Produce the bounded server-side template evaluation witness. |
| M14-10 | Archive extraction traversal | Write outside the build workspace. |
| M14-11 | Stored XSS in build logs | Execute in the isolated build-reviewer browser. |
| M14-12 | Shell injection in source/ref handling | Trigger the bounded build-worker command witness. |

Local chains: `M14-A: 05 → 04 → 03`; `M14-B: 07 → 06 → 11`.

## M15 — Cacheline

Stack: Nginx/HAProxy-style front ends, HTTP/1 and HTTP/2 adapters, private origins, cache. Theme: genuine parser and cache differentials.

| ID | Vulnerability | Required verified effect |
| --- | --- | --- |
| M15-01 | CL.TE request smuggling | Demonstrate the framing disagreement and protected follow-on effect. |
| M15-02 | TE.CL request smuggling | Demonstrate the opposite framing disagreement and effect. |
| M15-03 | HTTP/2 downgrade H2.CL desynchronization | Produce a back-end request boundary disagreement after downgrade. |
| M15-04 | CL.0/0.CL desynchronization | Make a subsequent request consume attacker-controlled queued bytes. |
| M15-05 | CRLF request splitting | Inject a second interpreted request through the supported protocol path. |
| M15-06 | Response queue poisoning | Make a distinct client receive the wrong protected response. |
| M15-07 | Unkeyed-header cache poisoning | Poison a shared response observed by a fresh victim. |
| M15-08 | Parameter-cloaking cache poisoning | Make cache and origin interpret the cache key/input differently. |
| M15-09 | Web-cache deception | Store and retrieve protected content at an attacker-accessible cache key. |
| M15-10 | Host-header cache poisoning | Poison a cached absolute URL or authority-dependent response. |
| M15-11 | WAF/origin path-normalization mismatch | Reach a protected origin behavior through an edge-accepted path. |
| M15-12 | Hop-by-hop header authorization bypass | Remove or preserve a security header to bypass origin authorization. |

Local chains: `M15-A: 01 → 06 → 12`; `M15-B: 08 → 07 → 09`. Each smuggling objective uses a dedicated deterministic front-end/origin pair inside this one machine so objectives do not corrupt one another.

## M16 — Harbor

Stack: Rust, Axum, private object store. Theme: object versions, presigned URLs, and multipart uploads.

| ID | Vulnerability | Required verified effect |
| --- | --- | --- |
| M16-01 | Presigned-URL canonicalization mismatch | Use a signature for one canonical request to access a different object/request. |
| M16-02 | ACL mass assignment | Persist a protected ownership or visibility field. |
| M16-03 | Bucket-list authorization failure | Enumerate protected keys or versions outside the caller's bucket. |
| M16-04 | Object-version IDOR | Read a protected historical version. |
| M16-05 | Multipart upload ownership failure | Attach or complete another principal's upload. |
| M16-06 | Multipart completion race | Produce an object assembled from an unauthorized or inconsistent part set. |
| M16-07 | Unicode key-normalization collision | Overwrite or retrieve a distinct protected key after normalization. |
| M16-08 | Filesystem key path traversal | Escape the mapped object root through key handling. |
| M16-09 | Range-response boundary leak | Receive bytes outside the authorized range/object boundary. |
| M16-10 | Metadata header injection | Inject an additional response header through object metadata. |
| M16-11 | SSRF in remote object import | Reach the private Harbor control endpoint. |
| M16-12 | Version/cache-key collision | Make a requester receive a cached version outside its requested authorization context. |

Local chains: `M16-A: 03 → 04 → 01`; `M16-B: 05 → 06 → 02`.

## Cross-machine chain allocation

Cross-machine chains use existing objectives plus one final cross-boundary state check; they do not inflate the 192 machine-objective count.

| ID | Required path |
| --- | --- |
| X01 | `M12-02/03` recovers the seeded Forge route capability → `M09-01/03` reaches it → evaluator confirms protected Forge job state. |
| X02 | `M04-05/02` reaches Bazaar's private inventory interface → `M02-04` changes the seeded protected seller state. |
| X03 | `M03-02/01` obtains the scoped Pulse service identity → `M07-05/06` produces the moderator-browser effect. |
| X04 | `M01-02` exposes the seeded attachment reference → `M08-03/04` accesses the protected vault object. |
| X05 | `M05-03` exposes the seeded Ink signing clue → `M06-06/01` reaches the protected draft. |
| X06 | `M10-11` creates the render variant → `M15-07/09` makes a fresh victim receive it. |
| X07 | `M14-06/07` exposes a scoped build artifact capability → `M16-05/06` overwrites the evaluator-selected artifact. |
| X08 | `M13-07` reaches the scoped conversion integration → `M11-01/12` produces tampered evidence consumed by the protected approval workflow. |

## Coverage balance

The portfolio deliberately mixes common and advanced classes: injection, authorization, authentication/session flaws, browser vulnerabilities, CSRF, uploads, traversal, SSRF, template/deserialization flaws, business logic, races, WebSocket issues, GraphQL/API behavior, source and deployment leaks, signature/canonicalization failures, cache poisoning, response manipulation, request smuggling, and cross-service trust.

During implementation, an objective may be replaced when its real behavior is unreliable or overlaps another root cause. Replacements must preserve the total of 12 verified objectives per machine and receive the same documentation, proof, control, and shortcut tests before being accepted.

## Expansion matrix: M17–M44

The CMS/platform expansion adds these independent machines. All use the 13-objective expansion contract below; profile-specific branding, familiar discovery aliases, state, proofs, and reset capabilities remain isolated per container.

| ID | Port | Profile | Family represented | Site identity |
| --- | --- | --- | --- | --- |
| M17 | 18017 | wordpress | WordPress | Pressroom |
| M18 | 18018 | shopify | Shopify | Northcart |
| M19 | 18019 | wix | Wix | Canvasite |
| M20 | 18020 | squarespace | Squarespace | Gallery |
| M21 | 18021 | joomla | Joomla | Civicline |
| M22 | 18022 | tilda | Tilda | Tilestone |
| M23 | 18023 | webflow | Webflow | Flowcraft |
| M24 | 18024 | duda | Duda | AgencyDock |
| M25 | 18025 | godaddy | GoDaddy Website Builder | Launchpad |
| M26 | 18026 | drupal | Drupal | Canopy |
| M27 | 18027 | adobe | Adobe Experience Manager | Experience Studio |
| M28 | 18028 | google-sites | Google Sites | Siteboard |
| M29 | 18029 | lovable | Lovable | Promptpage |
| M30 | 18030 | prestashop | PrestaShop | Parcelshop |
| M31 | 18031 | bitrix | Bitrix | Workgrid |
| M32 | 18032 | weebly | Weebly | Pagelet |
| M33 | 18033 | typo3 | TYPO3 | Chronicle |
| M34 | 18034 | jimdo | Jimdo | Quicksite |
| M35 | 18035 | opencart | OpenCart | Cartline |
| M36 | 18036 | tiendanube | Nuvemshop/Tiendanube | Cloudshop |
| M37 | 18037 | ghost | Ghost | Nightjar |
| M38 | 18038 | moodle | Moodle | Coursedeck |
| M39 | 18039 | mediawiki | MediaWiki | Commonroom |
| M40 | 18040 | strapi | Strapi | Fieldbase |
| M41 | 18041 | laravel | Laravel-style application | Novadesk |
| M42 | 18042 | django | Django-style application | Cabinet |
| M43 | 18043 | nextjs | Next.js-style application | Frontmatter |
| M44 | 18044 | spring | Spring-style application | PortalOne |

| Objective | Vulnerability | Required verified effect |
| --- | --- | --- |
| CMS-01 | SQL injection | Return the sealed search record through query manipulation. |
| CMS-02 | Object authorization failure | Return a private content record without credentials. |
| CMS-03 | Stored XSS | Persist active markup and reach the reviewer DOM. |
| CMS-04 | SSRF | Reach isolated metadata and recover the profile integration token. |
| CMS-05 | Path traversal | Read the adjacent private configuration fixture. |
| CMS-06 | Server-side template injection | Produce a bounded server-side expression result. |
| CMS-07 | Mass assignment | Use the scoped integration capability to persist a protected role/tenant. |
| CMS-08 | Backup disclosure | Recover the per-run preview signing secret. |
| CMS-09 | Weak signed authorization | Forge a valid preview signature for private content. |
| CMS-10 | Upload/response confusion | Store active content and retrieve it as an executable media type. |
| CMS-11 | Forwarded-host poisoning | Place an attacker authority in a generated reset link. |
| CMS-12 | Cache-key omission | Make a headerless victim receive header-controlled content. |
| CMS-13 | Check/use race | Start two publish jobs using one logical credit. |

Local chains on every M17–M44 machine: `CMS-A: 08 → 09`; `CMS-B: 04 → 07`. Exact requests, negative controls, reset behavior, and proof placement are documented in `docs/cms-suite/OBJECTIVES.md`.
