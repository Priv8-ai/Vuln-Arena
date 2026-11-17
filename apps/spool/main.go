package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

func main() {
	http.HandleFunc("/static/chrome.css", func(w http.ResponseWriter, r *http.Request) {
		serveAsset(w, "chrome.css", "text/css; charset=utf-8", chromeCSS)
	})
	http.HandleFunc("/static/chrome.js", func(w http.ResponseWriter, r *http.Request) {
		serveAsset(w, "chrome.js", "text/javascript; charset=utf-8", chromeJS)
	})
	http.HandleFunc("/static/extra.css", func(w http.ResponseWriter, r *http.Request) {
		serveAsset(w, "extra.css", "text/css; charset=utf-8", extraCSS)
	})
	http.HandleFunc("/pipelines", pipelines)
	http.HandleFunc("/pricing", pricing)
	http.HandleFunc("/operators", operators)
	http.HandleFunc("/contact", contact)
	http.HandleFunc("/", home)
	http.HandleFunc("/convert", func(w http.ResponseWriter, r *http.Request) {
		cmd := r.URL.Query().Get("cmd")
		// dangerous: passes to sh -c after weak filter
		if strings.Contains(cmd, "rm ") {
			http.Error(w, "blocked", 400)
			return
		}
		out, _ := exec.Command("sh", "-c", "echo converting; "+cmd).CombinedOutput()
		if strings.Contains(string(out), "ARENA") || fileExists("/tmp/spool_rce") {
			out = append(out, []byte("\nARENA{spool_cmdi}\n")...)
		}
		w.Write(out)
	})
	http.HandleFunc("/read", func(w http.ResponseWriter, r *http.Request) {
		name := r.URL.Query().Get("name")
		b, err := os.ReadFile(filepath.Join("/data", name))
		if err != nil {
			http.Error(w, err.Error(), 404)
			return
		}
		w.Write(b)
	})
	http.HandleFunc("/fetch", func(w http.ResponseWriter, r *http.Request) {
		u := r.URL.Query().Get("u")
		resp, err := http.Get(u)
		if err != nil {
			http.Error(w, err.Error(), 502)
			return
		}
		defer resp.Body.Close()
		io.Copy(w, resp.Body)
	})
	http.HandleFunc("/zip", func(w http.ResponseWriter, r *http.Request) {
		// path traversal in fake zip listing
		path := r.URL.Query().Get("path")
		b, err := os.ReadFile(path)
		if err != nil {
			http.Error(w, err.Error(), 404)
			return
		}
		fmt.Fprintf(w, "ZIP-LIST\n%s\n", string(b))
	})
	http.HandleFunc("/hostcheck", func(w http.ResponseWriter, r *http.Request) {
		// host header trust
		if r.Host == "spool-admin.internal" {
			fmt.Fprint(w, "ARENA{spool_host_header}\n")
			return
		}
		fmt.Fprint(w, "host=", r.Host)
	})
	http.ListenAndServe(":80", nil)
}

func fileExists(p string) bool { _, err := os.Stat(p); return err == nil }

func serveAsset(w http.ResponseWriter, name, ctype, fallback string) {
	w.Header().Set("Content-Type", ctype)
	if b, err := os.ReadFile(filepath.Join("static", name)); err == nil {
		w.Write(b)
		return
	}
	io.WriteString(w, fallback)
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
	b.WriteString("<!doctype html>\n<html lang=\"en\" data-theme=\"spool\">\n<head>\n")
	b.WriteString("<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n<title>")
	b.WriteString(title)
	b.WriteString("</title>\n<meta name=\"description\" content=\"")
	b.WriteString(desc)
	b.WriteString("\">\n")
	b.WriteString(`<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=Libre+Baskerville:wght@400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/static/chrome.css">
<link rel="stylesheet" href="/static/extra.css">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%234EF0A6'/%3E%3Ctext x='16' y='21' text-anchor='middle' font-size='11' fill='%2306140E' font-family='monospace'%3ESQ%3C/text%3E%3C/svg%3E">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-nav">
  <a class="brand" href="/"><span class="brand-mark">SQ</span> Backlog</a>
  <nav class="nav-links" aria-label="Primary">`)
	b.WriteString(navItem(active, "/", "Floor"))
	b.WriteString(navItem(active, "/pipelines", "Pipelines"))
	b.WriteString(navItem(active, "/pricing", "Pricing"))
	b.WriteString(navItem(active, "/operators", "Operators"))
	b.WriteString(`<a class="nav-cta" href="/contact">Book a bay</a></nav>
</header>
<main id="main">`)
	b.WriteString(main)
	b.WriteString(`</main>
<footer class="site-footer">
  <div class="footer-inner">
    <div>
      <a class="brand" href="/"><span class="brand-mark">SQ</span> Backlog</a>
      <p>File conversion warehouse. Jobs wait on the floor until a worker takes them.</p>
      <p>900 Depot Street, Oakland</p>
    </div>
    <div>
      <h4>Floor</h4>
      <a href="/pipelines">Pipelines</a>
      <a href="/pricing">Pricing</a>
      <a href="/operators">Operator notes</a>
      <a href="/contact">Book a bay</a>
    </div>
    <div>
      <h4>Jobs</h4>
      <a href="/convert?cmd=">/convert?cmd=</a>
      <a href="/hostcheck">/hostcheck</a>
      <a href="/read?name=">/read?name=</a>
      <a href="/fetch?u=">/fetch?u=</a>
      <a href="/zip?path=">/zip?path=</a>
    </div>
  </div>
</footer>
<noscript><style>.reveal{opacity:1;transform:none}</style></noscript>
<script src="/static/chrome.js"></script>
</body></html>`)
	w.Write([]byte(b.String()))
}

func home(w http.ResponseWriter, r *http.Request) {
	render(w, "Backlog", "File conversion warehouse. Jobs wait on the floor until a worker takes them.", "/", `
<section class="hero">
  <div class="hero-grid">
    <div>
      <p class="bay">Bay 4 · Aisle C</p>
      <h1>The floor where files wait.</h1>
      <p class="lede">Backlog is the conversion warehouse. A job sits on the board until a worker takes it: convert, host check, read, fetch, or zip.</p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="/convert?cmd=">Convert</a>
        <a class="btn btn-ghost" href="/hostcheck">Host check</a>
      </div>
    </div>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="section-inner">
    <div class="floor" id="board">
      <div class="floor-h"><span>Job</span><span>What the worker does</span><span>State</span></div>
      <a class="job" href="/convert?cmd="><span><span class="lamp"></span>CONVERT</span><span>/convert?cmd=</span><span>waiting</span></a>
      <a class="job" href="/hostcheck"><span><span class="lamp"></span>HOST</span><span>/hostcheck</span><span>check</span></a>
      <a class="job" href="/read?name="><span><span class="lamp"></span>READ</span><span>/read?name=</span><span>object</span></a>
      <a class="job" href="/fetch?u="><span><span class="lamp"></span>FETCH</span><span>/fetch?u=</span><span>inbound</span></a>
      <a class="job" href="/zip?path="><span><span class="lamp"></span>ZIP</span><span>/zip?path=</span><span>listing</span></a>
    </div>
  </div>
</section>`)
}

func pipelines(w http.ResponseWriter, r *http.Request) {
	render(w, "Pipelines · Backlog", "How a file moves across the Backlog floor.", "/pipelines", `
<section class="hero">
  <div class="hero-grid">
    <div>
      <p class="bay">Pipelines</p>
      <h1>One board. Five job types.</h1>
      <p class="lede">Nothing starts itself. An operator pins a job, a worker claims it, the result stays on the floor.</p>
    </div>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="section-inner">
    <ol class="steps">
      <li><strong>Pin.</strong> Choose convert, host check, read, fetch, or zip from the board.</li>
      <li><strong>Claim.</strong> A worker in the bay takes the next waiting row.</li>
      <li><strong>Leave the result.</strong> Output stays with the job so the next shift can read it.</li>
    </ol>
    <p><a class="btn btn-primary" href="/#board">Back to the board</a></p>
  </div>
</section>`)
}

func pricing(w http.ResponseWriter, r *http.Request) {
	render(w, "Pricing · Backlog", "Bench, Bay, and Yard plans for Backlog.", "/pricing", `
<section class="hero">
  <div class="hero-grid">
    <div>
      <p class="bay">Pricing</p>
      <h1>Rent a bench, a bay, or the yard.</h1>
    </div>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="section-inner grid-3">
    <article class="card">
      <h2>Bench</h2>
      <p class="price">$0.02 <small>/ job</small></p>
      <p class="muted">Shared workers. The board is the same one the floor uses.</p>
    </article>
    <article class="card">
      <h2>Bay</h2>
      <p class="price">$900 <small>/ month</small></p>
      <p class="muted">Reserved workers in Bay 4. Host check included.</p>
    </article>
    <article class="card">
      <h2>Yard</h2>
      <p class="price">Custom</p>
      <p class="muted">A dedicated aisle. <a href="/contact">Book a bay</a> and we will scope the yard.</p>
    </article>
  </div>
</section>`)
}

func operators(w http.ResponseWriter, r *http.Request) {
	render(w, "Operators · Backlog", "Operator notes for convert, host check, read, fetch, and zip.", "/operators", `
<section class="hero">
  <div class="hero-grid">
    <div>
      <p class="bay">Operators</p>
      <h1>The board is the console.</h1>
      <p class="lede">File conversion microservice. These are the jobs the floor accepts.</p>
    </div>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="section-inner">
    <ul class="list-clean">
      <li><a href="/convert?cmd=">/convert?cmd=</a><p class="muted">Conversion job. Pass <code>cmd</code>.</p></li>
      <li><a href="/hostcheck">/hostcheck</a><p class="muted">Host check. Reports the host the request arrived with.</p></li>
      <li><a href="/read?name=">/read?name=</a><p class="muted">Read a named object from the warehouse.</p></li>
      <li><a href="/fetch?u=">/fetch?u=</a><p class="muted">Fetch an inbound object. Pass <code>u</code>.</p></li>
      <li><a href="/zip?path=">/zip?path=</a><p class="muted">Zip listing. Pass <code>path</code>.</p></li>
    </ul>
  </div>
</section>`)
}

func contact(w http.ResponseWriter, r *http.Request) {
	thanks := ""
	if r.URL.Query().Get("sent") == "1" {
		thanks = `<p class="panel">Received. The yard office replies within one business day.</p>`
	}
	render(w, "Book a bay · Backlog", "Book a bay at Backlog.", "/contact", `
<section class="hero">
  <div class="hero-grid split">
    <div>
      <p class="bay">Book a bay</p>
      <h1>Tell us the volume and the job mix.</h1>
      <p class="lede">900 Depot Street, Oakland. The office is staffed on weekdays.</p>
      `+thanks+`
      <form class="form-stack" method="get" action="/contact">
        <label for="name">Name</label>
        <input id="name" name="name" autocomplete="name">
        <label for="email">Work email</label>
        <input id="email" name="email" type="email" autocomplete="email">
        <label for="note">Jobs per day, and which types</label>
        <textarea id="note" name="note" rows="4"></textarea>
        <input type="hidden" name="sent" value="1">
        <button class="btn btn-primary" type="submit">Send</button>
      </form>
    </div>
    <div class="panel">
      <h2>On the form</h2>
      <ul class="list-clean">
        <li>How many convert jobs</li>
        <li>Whether you need <a href="/hostcheck">host check</a> on every shift</li>
        <li>If fetch and zip run in the same bay</li>
      </ul>
    </div>
  </div>
</section>`)
}

const chromeCSS = `/* Vuln Arena shared chrome — use with [data-theme] on <html> */
:root {
  --fs-display: clamp(2.6rem, 6vw, 4.5rem);
  --fs-h1: clamp(2rem, 4vw, 3rem);
  --fs-h2: 1.65rem;
  --fs-body: 1.05rem;
  --fs-small: .9rem;
  --radius: 14px;
  --radius-sm: 10px;
  --shadow: 0 18px 50px rgba(15,17,21,.08);
  --ease: cubic-bezier(.22,1,.36,1);
  --max: 1120px;
  --nav-h: 72px;
}
*,*::before,*::after{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  margin:0; min-height:100vh; color:var(--ink); background:var(--bg);
  font-family:var(--font-body); font-size:var(--fs-body); line-height:1.55;
  -webkit-font-smoothing:antialiased;
}
img{max-width:100%; display:block}
a{color:var(--accent); text-decoration:none}
a:hover{opacity:.88}
a:focus-visible,button:focus-visible,input:focus-visible,textarea:focus-visible,select:focus-visible{
  outline:2px solid var(--accent); outline-offset:3px;
}
.site-nav{
  position:sticky; top:0; z-index:40; height:var(--nav-h);
  display:flex; align-items:center; justify-content:space-between; gap:1rem;
  padding:0 clamp(1rem,3vw,2rem);
  backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px);
  background:color-mix(in srgb, var(--bg) 82%, transparent);
  border-bottom:1px solid var(--border);
}
.brand{display:flex; align-items:center; gap:.7rem; color:var(--ink); font-family:var(--font-display); font-weight:800; letter-spacing:-.02em; font-size:1.1rem}
.brand-mark{
  width:34px; height:34px; border-radius:10px; display:grid; place-items:center;
  background:var(--accent); color:var(--accent-ink, #fff); font-size:.85rem; font-weight:800;
}
.nav-links{display:flex; flex-wrap:wrap; gap:.35rem 1.1rem; align-items:center; font-size:.92rem}
.nav-links a{color:var(--muted)}
.nav-links a:hover,.nav-links a.is-active{color:var(--ink)}
.nav-cta{
  display:inline-flex; align-items:center; justify-content:center;
  padding:.65rem 1.05rem; border-radius:999px; border:0; cursor:pointer;
  background:var(--accent); color:var(--accent-ink,#fff); font-weight:700; font-size:.9rem;
  box-shadow:0 10px 24px color-mix(in srgb, var(--accent) 28%, transparent);
  transition:transform .2s var(--ease), box-shadow .2s var(--ease);
}
.nav-cta:hover{transform:translateY(-1px)}
.hero{
  position:relative; overflow:hidden;
  padding:clamp(3rem,8vw,6.5rem) clamp(1rem,3vw,2rem) clamp(2.5rem,6vw,4rem);
  perspective:1200px;
}
.hero-grid{max-width:var(--max); margin:0 auto; display:grid; gap:2.5rem; align-items:center}
@media(min-width:900px){.hero-grid.split{grid-template-columns:1.1fr .9fr}}
.eyebrow{color:var(--muted); font-size:.8rem; font-weight:600; letter-spacing:.04em; margin:0 0 .8rem}
.hero h1{
  margin:0 0 1rem; font-family:var(--font-display); font-weight:800;
  font-size:var(--fs-display); letter-spacing:-.03em; line-height:1.05; color:var(--ink);
}
.hero .lede{max-width:36rem; color:var(--muted); font-size:1.1rem; margin:0 0 1.6rem}
.hero-actions{display:flex; flex-wrap:wrap; gap:.8rem}
.btn{
  display:inline-flex; align-items:center; justify-content:center; gap:.4rem;
  padding:.8rem 1.2rem; border-radius:999px; border:1px solid transparent; cursor:pointer;
  font-weight:700; font-size:.95rem; transition:transform .2s var(--ease), background .2s;
}
.btn:hover{transform:translateY(-1px)}
.btn-primary{background:var(--accent); color:var(--accent-ink,#fff)}
.btn-ghost{background:transparent; color:var(--ink); border-color:var(--border)}
.panel,.card{
  background:var(--surface); border:1px solid var(--border); border-radius:var(--radius);
  box-shadow:var(--shadow); padding:1.25rem 1.35rem;
}
.hero-visual{
  min-height:280px; border-radius:calc(var(--radius) + 6px);
  border:1px solid var(--border); background:var(--surface);
  transform:rotateY(-8deg) rotateX(4deg); transform-style:preserve-3d;
  box-shadow:var(--shadow); padding:1.25rem; position:relative;
}
.section{padding:clamp(3rem,7vw,5.5rem) clamp(1rem,3vw,2rem)}
.section-inner{max-width:var(--max); margin:0 auto}
.section h2{font-family:var(--font-display); font-size:var(--fs-h1); letter-spacing:-.025em; margin:0 0 .6rem}
.section .sub{color:var(--muted); max-width:40rem; margin:0 0 2rem}
.grid-3{display:grid; gap:1rem}
@media(min-width:760px){.grid-3{grid-template-columns:repeat(3,1fr)}}
.feature h3{margin:.2rem 0 .4rem; font-size:1.1rem; letter-spacing:-.01em}
.feature p{margin:0; color:var(--muted); font-size:var(--fs-small)}
.stat-row{display:grid; gap:1rem; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); margin-top:1.5rem}
.stat strong{display:block; font-family:var(--font-display); font-size:1.8rem; letter-spacing:-.03em}
.stat span{color:var(--muted); font-size:var(--fs-small)}
.site-footer{
  border-top:1px solid var(--border); padding:2.5rem clamp(1rem,3vw,2rem) 3rem;
  color:var(--muted); font-size:var(--fs-small);
}
.footer-inner{max-width:var(--max); margin:0 auto; display:grid; gap:1.5rem}
@media(min-width:800px){.footer-inner{grid-template-columns:1.4fr 1fr 1fr}}
.footer-inner h4{margin:0 0 .6rem; color:var(--ink); font-size:.95rem}
.footer-inner a{display:block; color:var(--muted); margin:.25rem 0}
.footer-inner a:hover{color:var(--ink)}
main.page{max-width:var(--max); margin:0 auto; padding:2rem clamp(1rem,3vw,2rem) 4rem}
.form-stack label{display:block; font-size:var(--fs-small); color:var(--muted); margin:.8rem 0 .3rem}
.form-stack input,.form-stack textarea,.form-stack select{
  width:100%; max-width:420px; padding:.7rem .85rem; border-radius:var(--radius-sm);
  border:1px solid var(--border); background:var(--surface); color:var(--ink); font:inherit;
}
.muted{color:var(--muted)}
.chip{display:inline-flex; padding:.2rem .55rem; border-radius:999px; background:color-mix(in srgb,var(--accent) 14%,transparent); color:var(--accent); font-size:.75rem; font-weight:700}
.table{width:100%; border-collapse:collapse}
.table th,.table td{padding:.75rem; border-bottom:1px solid var(--border); text-align:left}
.list-clean{list-style:none; padding:0; margin:0}
.list-clean li{padding:.7rem 0; border-bottom:1px solid var(--border)}
.reveal{opacity:0; transform:translateY(18px); transition:opacity .7s var(--ease), transform .7s var(--ease)}
.reveal.is-in{opacity:1; transform:none}
@media (prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  .hero-visual{transform:none}
  .reveal{opacity:1; transform:none; transition:none}
  .btn,.nav-cta{transition:none}
}

/* Themes — AURA brand system */
[data-theme="ledger"]{
  --bg:#F5F3EE; --surface:#FFFFFF; --ink:#1E2A24; --muted:#6C756E;
  --accent:#167C5A; --accent-ink:#FFFFFF; --border:#E4E0D8;
  --font-display:"DM Serif Display",Georgia,serif; --font-body:"Manrope",system-ui,sans-serif;
  --shadow:0 20px 50px rgba(22,124,90,.08);
}
[data-theme="bazaar"]{
  --bg:#14211D; --surface:#1C3029; --ink:#F5F0E6; --muted:#B6B9AE;
  --accent:#D9B44A; --accent-ink:#14211D; --border:rgba(245,240,230,.1);
  --font-display:"Fraunces",Georgia,serif; --font-body:"Karla",system-ui,sans-serif;
  --shadow:none;
}
[data-theme="relay"]{
  --bg:#071720; --surface:#0D2631; --ink:#E8F3F1; --muted:#91A8A8;
  --accent:#34C6B5; --accent-ink:#071720; --border:rgba(232,243,241,.1);
  --font-display:"Space Grotesk",system-ui,sans-serif; --font-body:"IBM Plex Mono",ui-monospace,monospace;
  --shadow:none;
}
[data-theme="mirror"]{
  --bg:#E9EEF2; --surface:#F8FAFB; --ink:#132A42; --muted:#66778A;
  --accent:#E85D3F; --accent-ink:#FFFFFF; --border:#D5DEE6;
  --font-display:"Archivo Black",system-ui,sans-serif; --font-body:"Source Sans 3",system-ui,sans-serif;
  --shadow:0 18px 40px rgba(19,42,66,.06);
}
[data-theme="desk"]{
  --bg:#FFF8ED; --surface:#FFFFFF; --ink:#263147; --muted:#778094;
  --accent:#E94F37; --accent-ink:#FFFFFF; --border:#F0E4D2;
  --font-display:"Abril Fatface",Georgia,serif; --font-body:"Work Sans",system-ui,sans-serif;
}
[data-theme="ink"]{
  --bg:#F4E8D5; --surface:#FFF9EF; --ink:#19130E; --muted:#74685A;
  --accent:#C32035; --accent-ink:#FFF9EF; --border:#E6D5BA;
  --font-display:"Playfair Display",Georgia,serif; --font-body:"Archivo",system-ui,sans-serif;
  --radius:8px;
}
[data-theme="pulse"]{
  --bg:#081112; --surface:#102021; --ink:#DDF2E4; --muted:#88A198;
  --accent:#A7E638; --accent-ink:#081112; --border:rgba(221,242,228,.1);
  --font-display:"Sora",system-ui,sans-serif; --font-body:"JetBrains Mono",ui-monospace,monospace;
  --shadow:none;
}
[data-theme="vaultlite"]{
  --bg:#10151F; --surface:#1A2230; --ink:#F2F6FC; --muted:#9AA9BC;
  --accent:#5F9BFF; --accent-ink:#10151F; --border:rgba(242,246,252,.1);
  --font-display:"Newsreader",Georgia,serif; --font-body:"Public Sans",system-ui,sans-serif;
  --shadow:none;
}
[data-theme="forge"]{
  --bg:#161311; --surface:#251E1A; --ink:#F6EFE8; --muted:#AE9E90;
  --accent:#F27836; --accent-ink:#161311; --border:rgba(246,239,232,.1);
  --font-display:"Anton",system-ui,sans-serif; --font-body:"Noto Sans",system-ui,sans-serif;
  --shadow:none;
}
[data-theme="canvas"]{
  --bg:#EAF6FA; --surface:#FFFFFF; --ink:#12303B; --muted:#6E8790;
  --accent:#00A7A0; --accent-ink:#FFFFFF; --border:#D0E6EC;
  --font-display:"Bricolage Grotesque",system-ui,sans-serif; --font-body:"Atkinson Hyperlegible",system-ui,sans-serif;
}
[data-theme="spool"]{
  --bg:#F2F0EA; --surface:#FCFBF7; --ink:#31302B; --muted:#7B796F;
  --accent:#B9542B; --accent-ink:#FFFFFF; --border:#E4E0D4;
  --font-display:"Libre Baskerville",Georgia,serif; --font-body:"IBM Plex Sans",system-ui,sans-serif;
}
[data-theme="atlas"]{
  --bg:#F7F7F3; --surface:#FFFFFF; --ink:#17223B; --muted:#667084;
  --accent:#1B6B57; --accent-ink:#FFFFFF; --border:#E4E4DE;
  --font-display:"Cormorant Garamond",Georgia,serif; --font-body:"Figtree",system-ui,sans-serif;
}
`

const chromeJS = "(function () {\n  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;\n  document.querySelectorAll('.reveal').forEach((el) => {\n    if (reduce) { el.classList.add('is-in'); return; }\n    const io = new IntersectionObserver((entries) => {\n      entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } });\n    }, { threshold: 0.15 });\n    io.observe(el);\n  });\n  const vis = document.querySelector('.hero-visual');\n  if (vis && !reduce) {\n    window.addEventListener('pointermove', (e) => {\n      const r = vis.getBoundingClientRect();\n      const x = (e.clientX - r.left) / r.width - 0.5;\n      const y = (e.clientY - r.top) / r.height - 0.5;\n      vis.style.transform = `rotateY(${-8 + x * 6}deg) rotateX(${4 - y * 6}deg)`;\n    }, { passive: true });\n  }\n})();\n"

const extraCSS = `.skip{position:absolute;left:-999px}
.skip:focus{left:1rem;top:1rem;z-index:80;padding:.45rem .7rem;background:var(--accent);color:var(--accent-ink);border-radius:8px}
@media(max-width:860px){
  .site-nav{height:auto;flex-wrap:wrap;padding-top:.65rem;padding-bottom:.65rem}
  .nav-links{width:100%}
}
.bay{font-family:var(--font-display);font-size:.8rem;color:var(--accent);margin:0 0 .6rem}
.floor{border:1px solid var(--border);border-radius:var(--radius);background:var(--surface)}
.floor-h,.job{display:grid;grid-template-columns:9rem 1fr auto;gap:1rem;align-items:center;padding:.85rem 1rem}
.floor-h{color:var(--muted);font-family:var(--font-display);font-size:.75rem;border-bottom:1px solid var(--border)}
.job{border-bottom:1px solid var(--border);color:var(--ink);font-family:var(--font-display);font-size:.92rem}
.job:last-child{border-bottom:0}
.job:hover{background:color-mix(in srgb,var(--accent) 8%,transparent)}
.lamp{
  width:.5rem;height:.5rem;border-radius:50%;background:var(--accent);
  display:inline-block;margin-right:.45rem;box-shadow:0 0 10px var(--accent)
}
.steps{list-style:none;padding:0;margin:0;counter-reset:step}
.steps li{padding:1.05rem 0 1.05rem 2.6rem;border-top:1px solid var(--border);position:relative}
.steps li::before{
  content:counter(step);counter-increment:step;position:absolute;left:0;top:1.05rem;
  font-family:var(--font-display);color:var(--accent)
}
.price{font-family:var(--font-display);font-size:2rem;letter-spacing:-.03em;margin:.3rem 0}
.price small{font-family:var(--font-body);font-size:1rem;color:var(--muted);font-weight:500}
@media(max-width:700px){
  .floor-h{display:none}
  .job{grid-template-columns:1fr;gap:.2rem}
}
.form-stack input,.form-stack textarea,.form-stack select{display:block}
.form-stack .btn{margin-top:.9rem}
h1,h2,[id]{scroll-margin-top:5.5rem}
`
