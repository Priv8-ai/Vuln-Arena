import com.sun.net.httpserver.*;
import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.regex.*;
import java.util.Base64;

public class Main {
  static Map<String,String> tickets = new ConcurrentHashMap<>();
  static Map<String,String> sessions = new ConcurrentHashMap<>();
  static final String CHROME_CSS = """
/* Vuln Arena shared chrome — use with [data-theme] on <html> */
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
""";
  static final String CHROME_JS = """
(function () {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.querySelectorAll('.reveal').forEach((el) => {
    if (reduce) { el.classList.add('is-in'); return; }
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } });
    }, { threshold: 0.15 });
    io.observe(el);
  });
  const vis = document.querySelector('.hero-visual');
  if (vis && !reduce) {
    window.addEventListener('pointermove', (e) => {
      const r = vis.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - 0.5;
      const y = (e.clientY - r.top) / r.height - 0.5;
      vis.style.transform = `rotateY(${-8 + x * 6}deg) rotateX(${4 - y * 6}deg)`;
    }, { passive: true });
  }
})();

""";
  static final String EXTRA_CSS = """
.skip{position:absolute;left:-999px}
.skip:focus{left:1rem;top:1rem;z-index:80;padding:.45rem .7rem;background:var(--accent);color:var(--accent-ink);border-radius:8px}
@media(max-width:860px){
  .site-nav{height:auto;flex-wrap:wrap;padding-top:.65rem;padding-bottom:.65rem}
  .nav-links{width:100%}
}
.shell{
  display:grid;min-height:480px;background:var(--surface);
  border:1px solid var(--border);border-radius:18px;overflow:hidden;box-shadow:var(--shadow)
}
@media(min-width:860px){.shell{grid-template-columns:210px 1fr}}
.rail{background:#F6F9FE;border-bottom:1px solid var(--border);padding:1rem .8rem}
@media(min-width:860px){.rail{border-bottom:0;border-right:1px solid var(--border)}}
.rail strong{display:block;padding:.2rem .6rem .8rem;font-size:.78rem;color:var(--muted);font-weight:600}
.rail a{display:block;padding:.5rem .6rem;border-radius:8px;color:var(--ink);font-weight:600}
.rail a:hover,.rail a.on{background:#E6EEFF;color:var(--accent)}
.pane{padding:1.1rem 1.2rem 1.3rem}
.queue-top{display:flex;justify-content:space-between;gap:1rem;align-items:flex-end;margin-bottom:.3rem}
.ticket{
  display:grid;grid-template-columns:auto 1fr auto;gap:.85rem;align-items:center;
  padding:.85rem 0;border-bottom:1px solid var(--border);color:inherit
}
.ticket:hover{color:var(--accent)}
.avatar{
  width:36px;height:36px;border-radius:50%;background:#E6EEFF;color:var(--accent);
  display:grid;place-items:center;font-weight:700;font-size:.78rem
}
.meta{color:var(--muted);font-size:.85rem}
.steps{list-style:none;padding:0;margin:0;counter-reset:step}
.steps li{padding:1.05rem 0 1.05rem 2.6rem;border-top:1px solid var(--border);position:relative}
.steps li::before{
  content:counter(step);counter-increment:step;position:absolute;left:0;top:1.05rem;
  font-family:var(--font-display);color:var(--accent)
}
.quote{font-family:var(--font-display);font-size:clamp(1.35rem,2vw,1.8rem);letter-spacing:-.02em;line-height:1.3;margin:0 0 .7rem}
.price{font-family:var(--font-display);font-size:2.3rem;letter-spacing:-.03em;margin:.3rem 0}
.price small{font-size:1rem;color:var(--muted);font-weight:500}
.tool a{font-weight:700}
.form-stack input,.form-stack textarea,.form-stack select{display:block}
.form-stack .btn{margin-top:.9rem}
h1,h2,[id]{scroll-margin-top:5.5rem}

""";
  static {
    tickets.put("100", "printer jam");
    tickets.put("101", "ARENA{desk_ticket_idor}");
    sessions.put("admin-session", "admin");
    sessions.put("user-session", "user");
  }
  public static void main(String[] args) throws Exception {
    HttpServer server = HttpServer.create(new InetSocketAddress(80), 0);
    server.createContext("/", ex -> page(ex, "Goodline", "/", homeBody()));
    server.createContext("/product", ex -> page(ex, "Product · Goodline", "/product", productBody()));
    server.createContext("/pricing", ex -> page(ex, "Pricing · Goodline", "/pricing", pricingBody()));
    server.createContext("/customers", ex -> page(ex, "Customers · Goodline", "/customers", customersBody()));
    server.createContext("/workspace", ex -> page(ex, "Workspace · Goodline", "/workspace", workspaceBody()));
    server.createContext("/contact", ex -> contact(ex));
    server.createContext("/static", ex -> staticAsset(ex));
    server.createContext("/login", Main::login);
    server.createContext("/ticket", Main::ticket);
    server.createContext("/serialize", Main::serialize);
    server.createContext("/read", Main::read);
    server.createContext("/search", Main::search);
    server.createContext("/admin", Main::admin);
    server.setExecutor(null);
    server.start();
    System.out.println("desk up");
  }
  static void staticAsset(HttpExchange ex) throws IOException {
    String path = ex.getRequestURI().getPath();
    if ("/static/chrome.css".equals(path)) asset(ex, "chrome.css", "text/css; charset=utf-8", CHROME_CSS);
    else if ("/static/chrome.js".equals(path)) asset(ex, "chrome.js", "text/javascript; charset=utf-8", CHROME_JS);
    else if ("/static/extra.css".equals(path)) asset(ex, "extra.css", "text/css; charset=utf-8", EXTRA_CSS);
    else text(ex, 404, "missing");
  }
  static void asset(HttpExchange ex, String name, String type, String fallback) throws IOException {
    String body = fallback;
    try { body = Files.readString(Paths.get("static", name)); } catch (Exception ignored) {}
    byte[] b = body.getBytes(StandardCharsets.UTF_8);
    ex.getResponseHeaders().add("Content-Type", type);
    ex.sendResponseHeaders(200, b.length);
    ex.getResponseBody().write(b);
    ex.close();
  }
  static String item(String active, String href, String label) {
    if (href.equals(active)) return "<a href=\""+href+"\" class=\"is-active\" aria-current=\"page\">"+label+"</a>";
    return "<a href=\""+href+"\">"+label+"</a>";
  }
  static void html(HttpExchange ex, String body) throws IOException {
    page(ex, "Goodline", "", body);
  }
  static void page(HttpExchange ex, String title, String active, String body) throws IOException {
    String doc = "<!doctype html><html lang=\"en\" data-theme=\"desk\"><head>"
      + "<meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
      + "<title>"+title+"</title>"
      + "<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">"
      + "<link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>"
      + "<link href=\"https://fonts.googleapis.com/css2?family=Abril+Fatface&family=Work+Sans:wght@400;500;600;700&display=swap\" rel=\"stylesheet\">"
      + "<link rel=\"stylesheet\" href=\"/static/chrome.css\"><link rel=\"stylesheet\" href=\"/static/extra.css\">"
      + "<link rel=\"icon\" href=\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%232E5BFF'/%3E%3Ctext x='16' y='21' text-anchor='middle' font-size='11' fill='white' font-family='sans-serif'%3END%3C/text%3E%3C/svg%3E\">"
      + "</head><body><a class=\"skip\" href=\"#main\">Skip to content</a>"
      + "<header class=\"site-nav\"><a class=\"brand\" href=\"/\"><span class=\"brand-mark\">ND</span> Goodline</a>"
      + "<nav class=\"nav-links\" aria-label=\"Primary\">"
      + item(active, "/", "Queue")
      + item(active, "/product", "Product")
      + item(active, "/pricing", "Pricing")
      + item(active, "/customers", "Customers")
      + item(active, "/workspace", "Workspace")
      + "<a class=\"nav-cta\" href=\"/login\">Sign in</a></nav></header><main id=\"main\">"
      + body
      + "</main><footer class=\"site-footer\"><div class=\"footer-inner\">"
      + "<div><a class=\"brand\" href=\"/\"><span class=\"brand-mark\">ND</span> Goodline</a>"
      + "<p>The helpdesk shell for internal IT. Agents live in the queue.</p><p>220 Granville, Vancouver</p></div>"
      + "<div><h4>Product</h4><a href=\"/product\">Product</a><a href=\"/pricing\">Pricing</a><a href=\"/customers\">Customers</a><a href=\"/workspace\">Workspace</a></div>"
      + "<div><h4>Desk</h4><a href=\"/login\">Login</a><a href=\"/ticket?id=100\">Ticket 100</a><a href=\"/search?q=\">Search</a>"
      + "<a href=\"/serialize\">Import session</a><a href=\"/read?path=flag.txt\">Read attachment</a><a href=\"/admin\">Admin</a></div>"
      + "</div></footer><noscript><style>.reveal{opacity:1;transform:none}</style></noscript>"
      + "<script src=\"/static/chrome.js\"></script></body></html>";
    byte[] b = doc.getBytes(StandardCharsets.UTF_8);
    ex.getResponseHeaders().add("Content-Type", "text/html; charset=utf-8");
    ex.sendResponseHeaders(200, b.length);
    ex.getResponseBody().write(b);
    ex.close();
  }
  static String homeBody() {
    return """
      <section class="hero">
        <div class="hero-grid">
          <div>
            <p class="eyebrow">Helpdesk shell</p>
            <h1>The queue your agents already live in.</h1>
            <p class="lede">Goodline is the internal helpdesk. Search the knowledge base, open a ticket, and pick the session back up without leaving the floor.</p>
          </div>
        </div>
      </section>
      <section class="section" style="padding-top:0">
        <div class="section-inner">
          <div class="shell">
            <aside class="rail">
              <strong>Floor</strong>
              <a class="on" href="/">Inbox</a>
              <a href="/workspace">Mine</a>
              <a href="/search?q=">Waiting on search</a>
              <a href="/login">Sign in</a>
            </aside>
            <div class="pane">
              <div class="queue-top">
                <h2 style="margin:0">Inbox</h2>
                <form method="get" action="/search">
                  <label class="meta" for="q">Search</label>
                  <input id="q" name="q" placeholder="printer, badge, vpn">
                  <button class="btn btn-primary" type="submit">Search</button>
                </form>
              </div>
              <a class="ticket" href="/ticket?id=100"><span class="avatar">100</span><span><strong>Printer jam</strong><br><span class="meta">Floor 2 · open</span></span><span class="meta">Today</span></a>
              <a class="ticket" href="/ticket?id=101"><span class="avatar">101</span><span><strong>Badge printer</strong><br><span class="meta">Lobby · priority</span></span><span class="meta">Today</span></a>
            </div>
          </div>
        </div>
      </section>
      """;
  }
  static String productBody() {
    return """
      <section class="hero"><div class="hero-grid"><div>
        <p class="eyebrow">Product</p>
        <h1>A shell, not another inbox.</h1>
        <p class="lede">Agents search, open the ticket, and import a saved session from the same screen. Attachments stay on the desk.</p>
      </div></div></section>
      <section class="section" style="padding-top:0"><div class="section-inner">
        <ol class="steps">
          <li><strong>Search.</strong> The knowledge base lives at <a href="/search?q=">/search</a>.</li>
          <li><strong>Open the ticket.</strong> <a href="/ticket?id=100">Ticket 100</a> is the printer jam on the floor.</li>
          <li><strong>Bring the session back.</strong> Saved sessions import at <a href="/serialize">/serialize</a>. Attachments are read from the desk store.</li>
        </ol>
      </div></section>
      """;
  }
  static String pricingBody() {
    return """
      <section class="hero"><div class="hero-grid"><div>
        <p class="eyebrow">Pricing</p>
        <h1>Priced per agent on the floor.</h1>
      </div></div></section>
      <section class="section" style="padding-top:0"><div class="section-inner grid-3">
        <article class="card"><h2>Agent</h2><p class="price">$35 <small>/ agent</small></p><p class="muted">The queue, search, and tickets for a small desk.</p></article>
        <article class="card"><h2>Floor</h2><p class="price">$18 <small>/ agent</small></p><p class="muted">Twenty-five agents and up. The plan Harbor Clinic runs.</p></article>
        <article class="card"><h2>Campus</h2><p class="price">Annual</p><p class="muted">One workspace for a whole building. <a href="/contact">Talk to the floor lead</a>.</p></article>
      </div></section>
      """;
  }
  static String customersBody() {
    return """
      <section class="hero"><div class="hero-grid"><div>
        <p class="eyebrow">Customers</p>
        <h1>Desks that closed the queue before lunch.</h1>
      </div></div></section>
      <section class="section" style="padding-top:0"><div class="section-inner" style="display:grid;gap:1rem">
        <article class="panel"><h2>Harbor Clinic</h2><p class="quote">The printer queue used to live in a shared mailbox. It now has a number, an owner, and a search box.</p><p class="muted">Floor lead, Harbor Clinic</p></article>
        <article class="panel"><h2>Kindling Bank</h2><p>Campus IT runs Goodline for badge, vpn, and branch hardware. Agents sign in once and stay in the shell.</p></article>
      </div></section>
      """;
  }
  static String workspaceBody() {
    return """
      <div class="page">
        <h1>Workspace</h1>
        <p class="muted">The tools on the desk. Same doors the queue has always had.</p>
        <ul class="list-clean tool">
          <li><a href="/login">/login</a> — sign in</li>
          <li><a href="/ticket?id=100">/ticket?id=100</a> — open a ticket</li>
          <li><a href="/serialize">/serialize</a> — import a saved session</li>
          <li><a href="/read?path=flag.txt">/read?path=flag.txt</a> — read an attachment</li>
          <li><a href="/search?q=">/search?q=</a> — search</li>
          <li><a href="/admin">/admin</a> — admin</li>
        </ul>
      </div>
      """;
  }
  static void contact(HttpExchange ex) throws IOException {
    String thanks = "1".equals(qs(ex, "sent")) ? "<p class=\"panel\">Received. The floor lead replies within one business day.</p>" : "";
    page(ex, "Contact · Goodline", "/contact", """
      <div class="page">
        <h1>Talk to the floor lead</h1>
        <p>220 Granville, Vancouver.</p>
      """ + thanks + """
        <form class="form-stack" method="get" action="/contact">
          <label for="name">Name</label>
          <input id="name" name="name" autocomplete="name">
          <label for="email">Work email</label>
          <input id="email" name="email" type="email" autocomplete="email">
          <label for="note">How big is the floor?</label>
          <textarea id="note" name="note" rows="4"></textarea>
          <input type="hidden" name="sent" value="1">
          <button class="btn btn-primary" type="submit">Send</button>
        </form>
      </div>
      """);
  }
  static void text(HttpExchange ex, int code, String body) throws IOException {
    byte[] b = body.getBytes(StandardCharsets.UTF_8);
    ex.getResponseHeaders().add("Content-Type", "text/plain; charset=utf-8");
    ex.sendResponseHeaders(code, b.length); ex.getResponseBody().write(b); ex.close();
  }
  static String qs(HttpExchange ex, String k) {
    String q = ex.getRequestURI().getRawQuery(); if(q==null) return "";
    for (String p: q.split("&")) { String[] kv=p.split("=",2); if(kv[0].equals(k)) try { return URLDecoder.decode(kv.length>1?kv[1]:"", "UTF-8"); } catch(Exception e){return "";} }
    return "";
  }
  static void login(HttpExchange ex) throws IOException {
    if (!ex.getRequestMethod().equalsIgnoreCase("POST")) { html(ex, "<div class=\"page\"><h1>Sign in</h1><form class=\"form-stack\" method=\"post\" action=\"/login\"><label for=\"user\">Name</label><input id=\"user\" name=\"user\" autocomplete=\"username\"><label for=\"pass\">Password</label><input id=\"pass\" name=\"pass\" type=\"password\" autocomplete=\"current-password\"><button class=\"btn btn-primary\" type=\"submit\">Sign in</button></form></div>"); return; }
    String body = new String(ex.getRequestBody().readAllBytes(), StandardCharsets.UTF_8);
    // weak parse
    String user = body.contains("user=admin") ? "admin" : "user";
    String sid = user.equals("admin") ? "admin-session" : "user-session";
    ex.getResponseHeaders().add("Set-Cookie", "SID="+sid+"; Path=/");
    text(ex, 200, "ok as "+user);
  }
  static void ticket(HttpExchange ex) throws IOException {
    String id = qs(ex, "id");
    String t = tickets.getOrDefault(id, "missing");
    text(ex, 200, t); // IDOR
  }
  static void serialize(HttpExchange ex) throws IOException {
    if (ex.getRequestMethod().equalsIgnoreCase("POST")) {
      String body = new String(ex.getRequestBody().readAllBytes(), StandardCharsets.UTF_8);
      // toy "deserialization": base64 of command
      try {
        String decoded = new String(Base64.getDecoder().decode(body.trim()), StandardCharsets.UTF_8);
        if (decoded.startsWith("CMD:")) {
          String cmd = decoded.substring(4);
          Process p = Runtime.getRuntime().exec(new String[]{"/bin/sh","-c", cmd});
          String out = new String(p.getInputStream().readAllBytes(), StandardCharsets.UTF_8);
          text(ex, 200, out + "\nARENA{desk_insecure_deserialize}\n");
          return;
        }
      } catch (Exception e) { text(ex, 400, e.toString()); return; }
      text(ex, 200, "stored");
      return;
    }
    text(ex, 200, "POST base64 payload. Example CMD:id");
  }
  static void read(HttpExchange ex) throws IOException {
    String path = qs(ex, "path");
    Path p = Paths.get("/app/data/", path); // traversal if ../
    try { text(ex, 200, Files.readString(p)); }
    catch(Exception e){ text(ex, 404, e.toString()); }
  }
  static void search(HttpExchange ex) throws IOException {
    String q = qs(ex, "q");
    // reflected XSS
    html(ex, "<div class=\"page\"><form class=\"form-stack\" method=\"get\" action=\"/search\"><label for=\"q\">Knowledge base</label><input id=\"q\" name=\"q\"><button class=\"btn btn-primary\" type=\"submit\">Search</button></form><h2>Search</h2><p>Query: "+q+"</p></div>");
  }
  static void admin(HttpExchange ex) throws IOException {
    String cookie = Optional.ofNullable(ex.getRequestHeaders().getFirst("Cookie")).orElse("");
    if (!cookie.contains("SID=admin-session")) { text(ex, 403, "admin only"); return; }
    text(ex, 200, "ARENA{desk_admin_cookie}\n");
  }
}
