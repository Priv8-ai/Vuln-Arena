package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
)

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/", home)
	mux.HandleFunc("/platform", platform)
	mux.HandleFunc("/pricing", pricing)
	mux.HandleFunc("/customers", customers)
	mux.HandleFunc("/docs", docs)
	mux.HandleFunc("/contact", contact)
	mux.HandleFunc("/proxy", proxy)
	mux.HandleFunc("/_internal/flag", func(w http.ResponseWriter, r *http.Request) {
		// only meant from localhost inside network — but host header tricks apply on sibling path
		fmt.Fprint(w, "ARENA{mirror_internal_flag}")
	})
	mux.HandleFunc("/legacy", legacy)
	mux.Handle("/static/", http.StripPrefix("/static/", http.FileServer(http.Dir(staticDir()))))
	http.ListenAndServe(":80", hop(mux))
}

func staticDir() string {
	if st, err := os.Stat("/static"); err == nil && st.IsDir() {
		return "/static"
	}
	return "static"
}

func hop(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// X-Original-URL / X-Rewrite-URL trust
		if u := r.Header.Get("X-Original-URL"); u != "" {
			r.URL.Path = u
		}
		if u := r.Header.Get("X-Rewrite-URL"); u != "" {
			r.URL.Path = u
		}
		// host header confusion logging endpoint
		if r.URL.Path == "/admin" && r.Host != "mirror" && strings.Contains(r.Host, "localhost") {
			// decoy
		}
		next.ServeHTTP(w, r)
	})
}

func proxy(w http.ResponseWriter, r *http.Request) {
	raw := r.URL.Query().Get("url")
	if raw == "" {
		http.Error(w, "url required", 400)
		return
	}
	// SSRF
	resp, err := http.Get(raw)
	if err != nil {
		http.Error(w, err.Error(), 502)
		return
	}
	defer resp.Body.Close()
	w.Header().Set("Content-Type", resp.Header.Get("Content-Type"))
	io.Copy(w, resp.Body)
}

func legacy(w http.ResponseWriter, r *http.Request) {
	// response splitting lite via redirect
	next := r.URL.Query().Get("next")
	if next != "" {
		w.Header().Set("Location", next)
		// intentional header injection if CRLF present
		if strings.Contains(next, "\n") || strings.Contains(next, "%0d") || strings.Contains(next, "%0a") {
			w.Header().Set("X-Injected", "ARENA{mirror_header_injection}")
		}
		w.WriteHeader(302)
		return
	}
	// cache key / vary weirdness
	if r.Header.Get("X-Cache-Poison") != "" {
		w.Header().Set("Cache-Control", "public, max-age=60")
		w.Header().Set("X-Poisoned", r.Header.Get("X-Cache-Poison"))
		fmt.Fprint(w, "ARENA{mirror_cache_poison_sim}")
		return
	}
	fmt.Fprint(w, "legacy ok")
}

func init() {
	_ = os.WriteFile("/static/.hidden_flag.txt", []byte("ARENA{mirror_static_hidden}\n"), 0644)
}

func navItem(active, href, label string) string {
	if active == href {
		return fmt.Sprintf(`<a href="%s" class="is-active" aria-current="page">%s</a>`, href, label)
	}
	return fmt.Sprintf(`<a href="%s">%s</a>`, href, label)
}

func render(w http.ResponseWriter, title, desc, active, main string) {
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	var b strings.Builder
	b.WriteString("<!doctype html>\n<html lang=\"en\" data-theme=\"mirror\">\n<head>\n")
	b.WriteString("<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n<title>")
	b.WriteString(title)
	b.WriteString("</title>\n<meta name=\"description\" content=\"")
	b.WriteString(desc)
	b.WriteString("\">\n")
	b.WriteString(`<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Source+Sans+3:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/static/chrome.css">
<link rel="stylesheet" href="/static/extra.css">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%234E8DFF'/%3E%3Ctext x='16' y='21' text-anchor='middle' font-size='12' fill='white' font-family='sans-serif'%3EME%3C/text%3E%3C/svg%3E">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-nav">
  <a class="brand" href="/"><span class="brand-mark">ME</span> Northstar Edge</a>
  <nav class="nav-links" aria-label="Primary">`)
	b.WriteString(navItem(active, "/", "Product"))
	b.WriteString(navItem(active, "/platform", "Platform"))
	b.WriteString(navItem(active, "/pricing", "Pricing"))
	b.WriteString(navItem(active, "/customers", "Customers"))
	b.WriteString(navItem(active, "/docs", "Docs"))
	b.WriteString(`<a class="nav-cta" href="/contact">Talk to routing</a></nav>
</header>
<main id="main">`)
	b.WriteString(main)
	b.WriteString(`</main>
<footer class="site-footer">
  <div class="footer-inner">
    <div>
      <a class="brand" href="/"><span class="brand-mark">ME</span> Northstar Edge</a>
      <p>Edge proxy for teams that publish a route and keep the old hop alive.</p>
      <p>18 Harbor Lane, Suite 400, Halifax</p>
    </div>
    <div>
      <h4>Product</h4>
      <a href="/platform">Platform</a>
      <a href="/pricing">Pricing</a>
      <a href="/customers">Customers</a>
      <a href="/docs">Operator notes</a>
    </div>
    <div>
      <h4>Operators</h4>
      <a href="/proxy?url=">Try /proxy?url=</a>
      <a href="/legacy">Legacy hop</a>
      <a href="/contact">Contact</a>
    </div>
  </div>
</footer>
<noscript><style>.reveal{opacity:1;transform:none}</style></noscript>
<script src="/static/chrome.js"></script>
<script src="/static/app.js"></script>
</body></html>`)
	w.Write([]byte(b.String()))
}

func home(w http.ResponseWriter, r *http.Request) {
	render(w, "Northstar Edge", "Edge proxy for partner routes, legacy hops, and header overrides.", "/", `
<section class="hero">
  <div class="hero-grid split">
    <div>
      <p class="eyebrow">Edge proxy</p>
      <h1>The hop in front of apps you keep private.</h1>
      <p class="lede">Northstar Edge publishes routes for partner traffic and keeps a legacy hop for clients that still send the old redirect. Header overrides supported for legacy clients.</p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="/docs">Operator notes</a>
        <a class="btn btn-ghost" href="/pricing">See plans</a>
      </div>
    </div>
    <div class="hero-visual">
      <div class="route-board">
        <header><span>Host</span><span>Origin</span><span>Hop</span></header>
        <div class="route-row"><span>partners.northwind.test</span><span>origin-a</span><span class="hop"><span class="live"></span>edge-3</span></div>
        <div class="route-row"><span>preview.harbor.test</span><span>mirror</span><span>legacy</span></div>
        <div class="route-row"><span>billing.fieldnote.test</span><span>origin-c</span><span>edge-1</span></div>
      </div>
      <p class="muted" style="margin:.9rem 0 0"><a href="/proxy?url=">Try /proxy?url=</a></p>
    </div>
  </div>
</section>
<section class="section">
  <div class="section-inner reveal">
    <h2>Three ways a client arrives</h2>
    <p class="sub">A published route, the legacy hop, or a header the old client still sends.</p>
    <ol class="steps">
      <li><strong>Published route.</strong> The host matches a row and the edge forwards to that origin.</li>
      <li><strong>Legacy hop.</strong> Older clients call <a href="/legacy">/legacy</a> and pass <code>next</code>.</li>
      <li><strong>Header override.</strong> Header overrides supported for legacy clients. Integrations that never took the new contract keep working.</li>
    </ol>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="section-inner">
    <figure class="panel">
      <blockquote class="quote">We stopped publishing origin hostnames to partners. The edge owns the route table now.</blockquote>
      <figcaption class="muted">Platform lead, Northwind Freight</figcaption>
    </figure>
  </div>
</section>`)
}

func platform(w http.ResponseWriter, r *http.Request) {
	render(w, "Platform · Northstar Edge", "How Northstar Edge matches a host, honors a legacy hop, and fetches a named URL.", "/platform", `
<section class="hero">
  <div class="hero-grid">
    <div class="narrow">
      <p class="eyebrow">Platform</p>
      <h1>One route table. Two client generations.</h1>
      <p class="lede">New partners use a published host. Clients that still speak the old redirect contract use the legacy hop. Both land on the same edge.</p>
    </div>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="section-inner grid-3">
    <article class="card feature">
      <h3>Published routes</h3>
      <p>Each host names an origin. The board on the product page is the same shape operators edit.</p>
    </article>
    <article class="card feature">
      <h3>Proxy fetch</h3>
      <p>The proxy console takes a <code>url</code>. <a href="/proxy?url=">Try /proxy?url=</a></p>
    </article>
    <article class="card feature">
      <h3>Legacy hop</h3>
      <p>Pass <code>next</code> on <a href="/legacy">/legacy</a> when a client still expects a redirect.</p>
    </article>
  </div>
</section>`)
}

func pricing(w http.ResponseWriter, r *http.Request) {
	render(w, "Pricing · Northstar Edge", "Route, Fabric, and Private edge plans for Northstar Edge.", "/pricing", `
<section class="hero">
  <div class="hero-grid">
    <div>
      <p class="eyebrow">Pricing</p>
      <h1>Pay for the hops you publish.</h1>
      <p class="lede">Every plan includes the legacy hop and header overrides. Private edge is a single-tenant POP.</p>
    </div>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="section-inner grid-3">
    <article class="card">
      <h2>Route</h2>
      <p class="price">$400 <small>/ month</small></p>
      <p class="muted">One origin, three published hosts, shared edge.</p>
    </article>
    <article class="card">
      <h2>Fabric</h2>
      <p class="price">$1,800 <small>/ month</small></p>
      <p class="muted">Unlimited published routes on the shared fabric. The plan Northwind runs.</p>
    </article>
    <article class="card">
      <h2>Private edge</h2>
      <p class="price">Custom</p>
      <p class="muted">A POP that answers only your hosts. <a href="/contact">Talk to routing</a>.</p>
    </article>
  </div>
</section>`)
}

func customers(w http.ResponseWriter, r *http.Request) {
	render(w, "Customers · Northstar Edge", "Teams that put Northstar Edge in front of internal apps.", "/customers", `
<section class="hero">
  <div class="hero-grid">
    <div class="narrow">
      <p class="eyebrow">Customers</p>
      <h1>Origins stay off the public host list.</h1>
      <ul class="logo-row">
        <li>Northwind Freight</li>
        <li>Harbor Clinic</li>
        <li>Fieldnote Press</li>
      </ul>
    </div>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="section-inner" style="display:grid;gap:1rem">
    <article class="panel">
      <h2>Northwind Freight</h2>
      <p>Partner portals used to point at origin hostnames. They now resolve on the edge. Billing still uses the legacy hop because two carriers never shipped a client update.</p>
    </article>
    <article class="panel">
      <h2>Harbor Clinic</h2>
      <p>Preview hosts for the patient portal terminate at Northstar Edge. Staff reach the real origin only from the clinic network.</p>
    </article>
  </div>
</section>`)
}

func docs(w http.ResponseWriter, r *http.Request) {
	render(w, "Docs · Northstar Edge", "Operator notes for the proxy console and the legacy hop.", "/docs", `
<section class="hero">
  <div class="hero-grid">
    <div class="narrow">
      <p class="eyebrow">Docs</p>
      <h1>Operator notes</h1>
      <p class="lede">Routes traffic to internal apps. Header overrides supported for legacy clients.</p>
    </div>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="section-inner">
    <ul class="list-clean">
      <li><a href="/proxy?url=">Try /proxy?url=</a><p class="muted">Proxy console. Pass <code>url</code>. A missing url is rejected.</p></li>
      <li><a href="/legacy">Legacy hop</a><p class="muted">Call <code>/legacy</code> with <code>next</code> when a client still expects a redirect. With no parameters the hop answers <code>legacy ok</code>.</p></li>
      <li><a href="/platform">Platform</a><p class="muted">How published routes, the proxy, and the legacy hop sit together.</p></li>
    </ul>
  </div>
</section>`)
}

func contact(w http.ResponseWriter, r *http.Request) {
	thanks := ""
	if r.URL.Query().Get("sent") == "1" {
		thanks = `<p class="panel">Received. A routing engineer replies within one business day.</p>`
	}
	render(w, "Contact · Northstar Edge", "Talk to Northstar Edge routing.", "/contact", `
<section class="hero">
  <div class="hero-grid split">
    <div>
      <p class="eyebrow">Contact</p>
      <h1>Tell us what you need to put behind the edge.</h1>
      <p class="lede">18 Harbor Lane, Suite 400, Halifax. Weekdays 9 to 6 Atlantic.</p>
      `+thanks+`
      <form class="form-stack" method="get" action="/contact">
        <label for="name">Name</label>
        <input id="name" name="name" autocomplete="name">
        <label for="email">Work email</label>
        <input id="email" name="email" type="email" autocomplete="email">
        <label for="note">What are you routing?</label>
        <textarea id="note" name="note" rows="4"></textarea>
        <input type="hidden" name="sent" value="1">
        <button class="btn btn-primary" type="submit">Send</button>
      </form>
    </div>
    <div class="panel">
      <h2>Bring</h2>
      <ul class="list-clean">
        <li>The hosts partners use today</li>
        <li>Which clients still need <a href="/legacy">/legacy</a></li>
        <li>Whether header overrides have to stay on</li>
      </ul>
    </div>
  </div>
</section>`)
}
