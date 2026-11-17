<?php
require __DIR__.'/layout.php';
ledger_open('Trust · Ledgerly', '', 'How Ledgerly handles practice access, statements, and the close.');
?>
<section class="page-hero" id="content">
  <div class="section-inner">
    <p class="eyebrow">Trust</p>
    <h1>The close is a record. Treat it like one.</h1>
    <p class="lede">Practices ask where a statement went, who can see a client profile, and what the desk keeps after the month is signed. This is the plain version.</p>
  </div>
</section>
<section class="section" style="padding-top:.5rem">
  <div class="section-inner">
    <div class="grid-3">
      <article class="card feature reveal">
        <h3>Sign-in belongs to the practice</h3>
        <p>Each person has their own desk login. Partners see the firm tools. Everyone else sees the books they were invited to.</p>
      </article>
      <article class="card feature reveal">
        <h3>Statements stay in the cabinet</h3>
        <p>Files uploaded for a close stay with that practice. They are not dropped into a shared drive named after the client.</p>
      </article>
      <article class="card feature reveal">
        <h3>Notes remain part of the invoice</h3>
        <p>Search exists so a question in July can find a line from February without exporting the year.</p>
      </article>
    </div>
  </div>
</section>
<section class="section band">
  <div class="section-inner">
    <h2>For the people who wire the desk</h2>
    <p class="sub">The HTTP reference for invoice search, profiles, and the practice ping lives with the product, not in a PDF.</p>
    <p class="card">API docs in /api/help.php — <a href="/api/help.php">open the reference</a>.</p>
    <div class="hero-actions" style="margin-top:1.2rem">
      <a class="btn btn-primary" href="/about.php">About the firm</a>
      <a class="btn btn-ghost" href="/#sign-in">Sign in</a>
    </div>
  </div>
</section>
<section class="section">
  <div class="section-inner">
    <h2>Write to the desk</h2>
    <p class="sub">Trust questions go to the same people who run the close with you. desk@meridianledger.test · Harbour Works, London.</p>
  </div>
</section>
<?php ledger_end(); ?>
