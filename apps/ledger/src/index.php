<?php
require __DIR__.'/init_db.php';
require __DIR__.'/layout.php';
db();
ledger_open('Ledgerly — Billing for practices that close on time', 'home');
?>
<section class="hero" id="content">
  <div class="hero-grid split">
    <div>
      <p class="eyebrow">Practice finance</p>
      <h1>Close the month without the Sunday spreadsheet.</h1>
      <p class="lede">Ledgerly is the billing desk for studios and advisories that have outgrown a shared workbook. Invoices, statements, and the close live in one place, with a person still signing the month.</p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="#sign-in">Sign in</a>
        <a class="btn btn-ghost" href="/search.php">Search the books</a>
      </div>
      <div class="stat-row">
        <div class="stat"><strong>11 min</strong><span>median close, last quarter</span></div>
        <div class="stat"><strong>48</strong><span>entities on one practice desk</span></div>
        <div class="stat"><strong>14,200</strong><span>invoices posted this quarter</span></div>
      </div>
    </div>
    <div class="hero-visual" aria-hidden="true">
      <div class="vis-top">
        <span class="chip">November close</span>
        <span class="muted">ML-2041</span>
      </div>
      <p class="vis-title">Northwind Practice</p>
      <div class="statement-row"><span>Opening cash</span><b>$428,110.00</b></div>
      <div class="statement-row"><span>Invoices issued</span><b>86</b></div>
      <div class="statement-row"><span>Collected</span><b>$191,440.18</b></div>
      <div class="statement-row total"><span>Still open</span><b>$36,820.40</b></div>
      <p class="muted vis-foot">Awaiting partner sign-off · Harbour books</p>
    </div>
  </div>
</section>

<section class="section" style="padding-top:0">
  <div class="section-inner">
    <ul class="wordmarks">
      <li>Northwind Practice</li>
      <li>Harbor Counsel</li>
      <li>Field &amp; Moss</li>
      <li>Kite Studio</li>
      <li>Lumen Advisory</li>
    </ul>
  </div>
</section>

<section class="section band" id="product">
  <div class="section-inner">
    <h2>A desk, not another export.</h2>
    <p class="sub">Everything a practice actually touches during the month: the invoice, the statement a client mailed, and the note someone wrote in the margin.</p>
    <div class="grid-3">
      <article class="card feature reveal">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>
        <h3>Invoice search</h3>
        <p>Find a vendor, a month, or the sentence written on the note. The books stay searchable after the close.</p>
      </article>
      <article class="card feature reveal">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M12 4v12"/><path d="M7 9l5-5 5 5"/><path d="M4 20h16"/></svg>
        <h3>Statement intake</h3>
        <p>Clients send the file they already have. It lands on the statement desk instead of in a partner’s inbox.</p>
      </article>
      <article class="card feature reveal">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18"/><path d="M8 4v5"/></svg>
        <h3>One close calendar</h3>
        <p>Multi-entity practices keep a single sign-off. The month is done when the partner says it is.</p>
      </article>
    </div>
  </div>
</section>

<section class="section">
  <div class="section-inner">
    <h2>How a practice runs the month</h2>
    <p class="sub">Three steps. No implementation project hiding in the footer.</p>
    <ol class="steps">
      <li class="card reveal"><span>01</span><h3>Open the entities</h3><p>Each company you still reconcile by hand gets a place on the desk. Profiles stay attached to the people who bill them.</p></li>
      <li class="card reveal"><span>02</span><h3>Post and collect</h3><p>Invoices go out. Statements come back. Search still works when someone asks about a line from March.</p></li>
      <li class="card reveal"><span>03</span><h3>Sign the close</h3><p>The partner reviews what is open, what was collected, and what is waiting on a statement.</p></li>
    </ol>
  </div>
</section>

<section class="section band" id="sign-in">
  <div class="section-inner signin-grid">
    <div>
      <p class="eyebrow">Client sign-in</p>
      <h2>Open your books.</h2>
      <p class="muted">Sign in to manage invoices. API docs in /api/help.php</p>
      <p><a href="/search.php">Search invoices</a> · <a href="/profile.php?id=2">Profiles</a> · <a href="/upload.php">Statements</a></p>
    </div>
    <div class="card">
      <form method="post" action="/login.php" class="form-stack">
        <label>Email <input name="email" value="alice@ledger.local" autocomplete="username"></label>
        <label>Password <input name="password" type="password" autocomplete="current-password"></label>
        <button class="btn btn-primary" type="submit">Login</button>
      </form>
      <p class="muted" style="margin-top:1rem"><a href="/reset.php">Reset access</a> if the practice issued you a token.</p>
    </div>
  </div>
</section>

<section class="section">
  <div class="section-inner">
    <h2>Straightforward pricing</h2>
    <p class="sub">Priced per practice, not per seat. The desk is the product.</p>
    <div class="grid-3">
      <article class="card plan reveal">
        <h3>Studio</h3>
        <span class="amount">$0</span>
        <span class="per">Single entity</span>
        <p>For the practice that is still one company and one close.</p>
      </article>
      <article class="card plan is-featured reveal">
        <h3>Practice</h3>
        <span class="amount">$49</span>
        <span class="per">per entity / month</span>
        <p>Search, statements, and a partner desk for advisories with a real book of clients.</p>
      </article>
      <article class="card plan reveal">
        <h3>House</h3>
        <span class="amount">$190</span>
        <span class="per">up to twelve entities</span>
        <p>One invoice for the firm. Every entity still has its own books.</p>
      </article>
    </div>
    <p style="margin-top:1.4rem"><a class="btn btn-ghost" href="/pricing.php">Compare plans</a></p>
  </div>
</section>
<?php ledger_footer(); ?>
<script src="/static/chrome.js"></script>
<!-- TODO: remove debug panel /debug.php?key= -->
<!-- staging reset helper used email reset tokens in JS bundle -->
<script src="/static/app.js"></script>
</body></html>
