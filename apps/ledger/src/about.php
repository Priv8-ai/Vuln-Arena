<?php
require __DIR__.'/layout.php';
ledger_open('About · Ledgerly', 'about', 'Ledgerly builds the billing desk for multi-entity practices.');
?>
<section class="page-hero" id="content">
  <div class="section-inner">
    <p class="eyebrow">The firm</p>
    <h1>Books for practices that still sign the close.</h1>
    <p class="lede">Meridian started as a close calendar for three London advisories who were tired of a workbook named Final. It is now the desk those firms run the month on.</p>
  </div>
</section>
<section class="section">
  <div class="section-inner">
    <div class="grid-3">
      <article class="card feature reveal">
        <h3>Built around the partner</h3>
        <p>Software should end at a signature, not at a dashboard nobody opens. The close is a decision, and the desk keeps the papers for it.</p>
      </article>
      <article class="card feature reveal">
        <h3>Many entities, one practice</h3>
        <p>Studios pick up companies. Advisories inherit them. Each entity keeps its own invoices without a second login for the firm.</p>
      </article>
      <article class="card feature reveal">
        <h3>Notes stay searchable</h3>
        <p>The sentence on an invoice is part of the record. Six months later, search still finds it.</p>
      </article>
    </div>
  </div>
</section>
<section class="section band">
  <div class="section-inner">
    <h2>Who keeps a desk here</h2>
    <p class="sub">Small on purpose. If you have a controller and a Sunday spreadsheet, you are the practice we built for.</p>
    <div class="grid-3">
      <article class="card"><h3>Studios</h3><p class="muted">Project billing that outgrew a tab called Invoices 2024.</p></article>
      <article class="card"><h3>Advisories</h3><p class="muted">Retainers, pass-through costs, and a partner who still reads the notes.</p></article>
      <article class="card"><h3>Multi-entity firms</h3><p class="muted">A house of companies with one close calendar and separate books.</p></article>
    </div>
    <div class="stat-row">
      <div class="stat"><strong>2019</strong><span>first practice on the desk</span></div>
      <div class="stat"><strong>2</strong><span>rooms, London and Chicago</span></div>
      <div class="stat"><strong>40</strong><span>people, most of them accountants</span></div>
    </div>
  </div>
</section>
<section class="section">
  <div class="section-inner">
    <h2>Come see a close</h2>
    <p class="sub">Harbour Works, London · West Loop, Chicago. Or open a studio desk and run a month yourself.</p>
    <div class="hero-actions">
      <a class="btn btn-primary" href="/#sign-in">Sign in</a>
      <a class="btn btn-ghost" href="/trust.php">Read the trust notes</a>
    </div>
  </div>
</section>
<?php ledger_end(); ?>
