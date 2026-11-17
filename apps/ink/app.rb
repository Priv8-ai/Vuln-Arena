require 'sinatra'
require 'json'
require 'webrick'
require 'erb'

set :bind, '0.0.0.0'
set :port, 80
set :server, 'webrick'
set :protection, false
set :traps, false

POSTS = {
  '1' => { 'title' => 'Welcome', 'body' => 'Ink CMS demo', 'author' => 'admin' },
  '2' => { 'title' => 'Hidden', 'body' => 'ARENA{ink_post_idor}', 'author' => 'admin' }
}
USERS = { 'editor' => 'editor', 'admin' => 'admin' }

CHROME_CSS = <<~'CHROME_CSS_BODY'
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

CHROME_CSS_BODY
CHROME_JS = <<~'CHROME_JS_BODY'
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

CHROME_JS_BODY
EXTRA_CSS = <<~'EXTRA_CSS_BODY'
.skip{position:absolute;left:-999px}
.skip:focus{left:1rem;top:1rem;z-index:80;padding:.45rem .7rem;background:var(--accent);color:var(--accent-ink);border-radius:8px}
@media(max-width:860px){
  .site-nav{height:auto;flex-wrap:wrap;padding-top:.65rem;padding-bottom:.65rem}
  .nav-links{width:100%}
}
.mast{
  display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap;align-items:baseline;
  border-top:1px solid var(--ink);border-bottom:1px solid var(--ink);
  padding:.45rem 0;margin-bottom:1.4rem;font-size:.95rem
}
.issue{
  font-family:var(--font-display);font-weight:560;
  font-size:clamp(4.2rem,14vw,8.5rem);line-height:.82;letter-spacing:-.045em;margin:0
}
.contents{list-style:none;padding:0;margin:1.4rem 0 0}
.contents a{
  display:grid;grid-template-columns:7.5rem 1fr auto;gap:1rem;align-items:baseline;
  padding:.95rem 0;border-bottom:1px solid var(--border);color:var(--ink)
}
.contents a:hover{opacity:1}
.kicker{color:var(--muted)}
.essay{max-width:38rem;font-size:1.22rem;line-height:1.55}
.dropcap::first-letter{
  font-family:var(--font-display);float:left;font-size:3.5rem;line-height:.75;padding:.15rem .45rem 0 0
}
.pull{
  font-family:var(--font-display);font-size:clamp(1.7rem,3vw,2.3rem);
  line-height:1.22;letter-spacing:-.02em;margin:0;max-width:16ch
}
.colophon{max-width:36rem}
@media(max-width:700px){.contents a{grid-template-columns:1fr}}
.form-stack input,.form-stack textarea,.form-stack select{display:block}
.form-stack .btn{margin-top:.9rem}
h1,h2,[id]{scroll-margin-top:5.5rem}

EXTRA_CSS_BODY

def asset_body(name, fallback)
  path = File.join(__dir__, 'static', name)
  File.exist?(path) ? File.read(path) : fallback
end

def nav_link(active, href, label)
  if active == href
    "<a href=\"#{href}\" class=\"is-active\" aria-current=\"page\">#{label}</a>"
  else
    "<a href=\"#{href}\">#{label}</a>"
  end
end

def layout(title, desc, active, body)
  content_type 'text/html; charset=utf-8'
  <<~HTML
    <!doctype html>
    <html lang="en" data-theme="ink">
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>#{title}</title>
    <meta name="description" content="#{desc}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/static/chrome.css">
    <link rel="stylesheet" href="/static/extra.css">
    <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%23101010'/%3E%3Ctext x='16' y='21' text-anchor='middle' font-size='12' fill='%23F5F3EF' font-family='Georgia'%3EIF%3C/text%3E%3C/svg%3E">
    </head>
    <body>
    <a class="skip" href="#main">Skip to content</a>
    <header class="site-nav">
      <a class="brand" href="/"><span class="brand-mark">IF</span> Margin</a>
      <nav class="nav-links" aria-label="Primary">
        #{nav_link(active, '/', 'Issue')}
        #{nav_link(active, '/journal', 'Journal')}
        #{nav_link(active, '/about', 'The press')}
        #{nav_link(active, '/submissions', 'Submissions')}
        <a class="nav-cta" href="/login">Sign in</a>
      </nav>
    </header>
    <main id="main">
    #{body}
    </main>
    <footer class="site-footer">
      <div class="footer-inner">
        <div>
          <a class="brand" href="/"><span class="brand-mark">IF</span> Margin</a>
          <p>A press for long pieces. Issue 18 is on the stand.</p>
          <p>14 Mercer Street, New York</p>
        </div>
        <div>
          <h4>The issue</h4>
          <a href="/journal">Journal</a>
          <a href="/about">The press</a>
          <a href="/submissions">Submissions</a>
          <a href="/contact">Contact</a>
        </div>
        <div>
          <h4>Desk</h4>
          <a href="/posts/1">Post 1</a>
          <a href="/login">Login</a>
          <a href="/export?file=README.md">Export</a>
          <a href="/page">Page preview</a>
          <a href="/render?name=reader">Greeting</a>
        </div>
      </div>
    </footer>
    <noscript><style>.reveal{opacity:1;transform:none}</style></noscript>
    <script src="/static/chrome.js"></script>
    </body></html>
  HTML
end

get '/static/chrome.css' do
  content_type 'text/css; charset=utf-8'
  asset_body('chrome.css', CHROME_CSS)
end

get '/static/chrome.js' do
  content_type 'text/javascript; charset=utf-8'
  asset_body('chrome.js', CHROME_JS)
end

get '/static/extra.css' do
  content_type 'text/css; charset=utf-8'
  asset_body('extra.css', EXTRA_CSS)
end

get '/' do
  layout(
    'Margin',
    'Margin is a press for long pieces. Issue 18 is on the stand.',
    '/',
    <<~HTML
      <section class="section">
        <div class="section-inner">
          <div class="mast"><span>Margin</span><span>Issue 18</span><span>Autumn</span></div>
          <p class="issue">18</p>
          <h1>Notes on rooms, repair, and the long paragraph.</h1>
          <p class="lede" style="max-width:36rem">The autumn issue is about what people keep when they run out of space. One public essay, the staff folio, and the desk that still prints a greeting.</p>
          <ul class="contents">
            <li><a href="/posts/1"><span class="kicker">Essay</span><span>Welcome</span><span>Post 1</span></a></li>
            <li><a href="/posts/2"><span class="kicker">Staff</span><span>Hidden folio</span><span>Post 2</span></a></li>
            <li><a href="/journal"><span class="kicker">Reading</span><span>From the journal</span><span>Read</span></a></li>
            <li><a href="/page"><span class="kicker">Preview</span><span>Page</span><span>Open</span></a></li>
            <li><a href="/render?name=reader"><span class="kicker">Desk</span><span>Greeting</span><span>reader</span></a></li>
          </ul>
        </div>
      </section>
    HTML
  )
end

get '/journal' do
  layout(
    'Journal · Margin',
    'A reading from Margin issue 18.',
    '/journal',
    <<~HTML
      <section class="section">
        <div class="section-inner essay">
          <p class="kicker">Journal · Issue 18</p>
          <h1>The spare room</h1>
          <p class="dropcap">The spare room had been a claim for years, a place the house pointed to when someone asked where the good plates had gone. In autumn the editors walked it with a tape and wrote down only what was still in use.</p>
          <p class="pull">Write down only what is still in use.</p>
          <p>The machine-readable copy of the welcome essay is <a href="/posts/1">post 1</a>. A page preview takes a message. The desk can still <a href="/render?name=reader">set a greeting</a>.</p>
          <p><a href="/page?msg=The%20spare%20room">Preview this note</a></p>
        </div>
      </section>
    HTML
  )
end

get '/about' do
  layout(
    'The press · Margin',
    'Margin publishes two issues a year from Mercer Street.',
    '/about',
    <<~HTML
      <section class="section">
        <div class="section-inner colophon">
          <p class="kicker">The press</p>
          <h1>Two issues a year, printed when the piece is finished.</h1>
          <p>Margin started as a desk above a bookstore on Mercer Street. We still edit there. The public issue is on the stand. The staff folio stays on the desk until an editor signs it out.</p>
          <p>14 Mercer Street, New York. The shop downstairs is Mercer Books, which keeps a table for the current issue.</p>
          <p><a class="btn btn-primary" href="/submissions">Send a manuscript</a></p>
        </div>
      </section>
    HTML
  )
end

get '/submissions' do
  layout(
    'Submissions · Margin',
    'Send a manuscript to Margin.',
    '/submissions',
    <<~HTML
      <section class="section">
        <div class="section-inner">
          <p class="kicker">Submissions</p>
          <h1>Send the piece, not a pitch deck.</h1>
          <p class="lede" style="max-width:36rem">We read in the order files arrive. Export the posts readme if you need the house note that travels with every manuscript.</p>
          <p><a href="/export?file=README.md">Export</a></p>
          <form class="form-stack" action="/upload" method="post" enctype="multipart/form-data">
            <label for="file">Manuscript</label>
            <input id="file" name="file" type="file">
            <button class="btn btn-primary" type="submit">Send the file</button>
          </form>
        </div>
      </section>
    HTML
  )
end

get '/contact' do
  thanks = params['sent'] == '1' ? '<p class="panel">Received. The desk writes back within a week.</p>' : ''
  layout(
    'Contact · Margin',
    'Write to Margin on Mercer Street.',
    '/contact',
    <<~HTML
      <section class="section">
        <div class="section-inner">
          <p class="kicker">Contact</p>
          <h1>Write to the desk.</h1>
          <p>14 Mercer Street, New York.</p>
          #{thanks}
          <form class="form-stack" method="get" action="/contact">
            <label for="name">Name</label>
            <input id="name" name="name" autocomplete="name">
            <label for="email">Email</label>
            <input id="email" name="email" type="email" autocomplete="email">
            <label for="note">What are you sending?</label>
            <textarea id="note" name="note" rows="4"></textarea>
            <input type="hidden" name="sent" value="1">
            <button class="btn btn-primary" type="submit">Send</button>
          </form>
        </div>
      </section>
    HTML
  )
end

get '/login' do
  layout(
    'Sign in · Margin',
    'Sign in to the Margin desk.',
    '/login',
    <<~HTML
      <div class="page">
        <h1>Sign in</h1>
        <p class="muted">Editors and the desk share this door.</p>
        <form class="form-stack" method="post" action="/login">
          <label for="user">Name</label>
          <input id="user" name="user" autocomplete="username">
          <label for="pass">Password</label>
          <input id="pass" name="pass" type="password" autocomplete="current-password">
          <button class="btn btn-primary" type="submit">Sign in</button>
        </form>
      </div>
    HTML
  )
end

get '/posts/:id' do
  p = POSTS[params['id']]
  halt 404, 'no' unless p
  content_type :json
  p.to_json
end

post '/login' do
  u, pw = params['user'], params['pass']
  halt 401, 'no' unless USERS[u] == pw
  response.set_cookie('user', u)
  response.set_cookie('role', u == 'admin' ? 'admin' : 'editor')
  'ok'
end

post '/profile' do
  data = begin
    JSON.parse(request.body.read)
  rescue StandardError
    params
  end
  role = data['role'] || request.cookies['role']
  user = data['user'] || request.cookies['user']
  flag = (role == 'admin' && request.cookies['role'] != 'admin') ? 'ARENA{ink_mass_assignment}' : ''
  content_type :json
  { user: user, role: role, flag: flag }.to_json
end

get '/export' do
  file = params['file'] || 'README.md'
  path = File.join('/app/posts', file)
  begin
    File.read(path)
  rescue StandardError => e
    e.to_s
  end
end

get '/render' do
  # intentional ERB injection surface
  name = params['name'] || 'reader'
  ERB.new("Hello #{name}").result
end

get '/page' do
  url = params['url'].to_s
  msg = params['msg'].to_s
  if url != ''
    redirect url
  else
    content_type 'text/html'
    layout('Message', 'A page preview.', '', "<h1>Message</h1><div>#{msg}</div>")
  end
end

get '/admin' do
  halt 403, 'no' unless request.cookies['role'] == 'admin'
  "ARENA{ink_admin}\n"
end

get '/uploads/*' do
  send_file File.join('/app/uploads', params['splat'].first)
end

post '/upload' do
  f = params['file']
  halt 400, 'no file' unless f
  name = f[:filename]
  File.open(File.join('/app/uploads', name), 'wb') { |out| out.write(f[:tempfile].read) }
  "stored /uploads/#{name}"
end
