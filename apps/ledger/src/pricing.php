<?php
require __DIR__.'/layout.php';
ledger_open('Pricing · Ledgerly', 'pricing', 'Ledgerly pricing for studio, practice, and house desks.');
?>
<section class="page-hero" id="content">
  <div class="section-inner">
    <p class="eyebrow">Pricing</p>
    <h1>Per practice. Not per seat.</h1>
    <p class="lede">Invite the partner, the bookkeeper, and the client contact. The price follows the entities on the desk, not the number of people who need to see them.</p>
  </div>
</section>
<section class="section" style="padding-top:1rem">
  <div class="section-inner">
    <div class="grid-3">
      <article class="card plan">
        <h3>Studio</h3>
        <span class="amount">$0</span>
        <span class="per">one entity</span>
        <ul>
          <li>Invoice desk and search</li>
          <li>Statement intake</li>
          <li>One close calendar</li>
        </ul>
        <a class="btn btn-ghost" href="/#sign-in">Start on the studio desk</a>
      </article>
      <article class="card plan is-featured">
        <span class="chip">Most practices</span>
        <h3>Practice</h3>
        <span class="amount">$49</span>
        <span class="per">per entity / month</span>
        <ul>
          <li>Everything in Studio</li>
          <li>Up to eight entities</li>
          <li>Partner sign-off on the close</li>
        </ul>
        <a class="btn btn-primary" href="/#sign-in">Open a practice desk</a>
      </article>
      <article class="card plan">
        <h3>House</h3>
        <span class="amount">$190</span>
        <span class="per">month, up to twelve entities</span>
        <ul>
          <li>One firm invoice</li>
          <li>Separate books per entity</li>
          <li>Shared statement cabinet</li>
        </ul>
        <a class="btn btn-ghost" href="/about.php">Talk to the house team</a>
      </article>
    </div>
    <div class="card" style="margin-top:1.5rem;overflow:auto">
      <table class="table">
        <thead>
          <tr><th></th><th>Studio</th><th>Practice</th><th>House</th></tr>
        </thead>
        <tbody>
          <tr><td>Entities</td><td>1</td><td>8</td><td>12</td></tr>
          <tr><td>Invoice search</td><td>Included</td><td>Included</td><td>Included</td></tr>
          <tr><td>Statement intake</td><td>Included</td><td>Included</td><td>Included</td></tr>
          <tr><td>Partner desk</td><td>—</td><td>Included</td><td>Included</td></tr>
          <tr><td>Annual close review</td><td>—</td><td>—</td><td>Included</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</section>
<section class="section band">
  <div class="section-inner">
    <h2>Questions practices actually ask</h2>
    <details class="card">
      <summary>Do clients get a login?</summary>
      <p>They can, for profiles you choose to share. Most firms send the invoice and keep the desk internal. Statement intake also accepts a file from someone who never signs in.</p>
    </details>
    <details class="card">
      <summary>What happens to a statement after upload?</summary>
      <p>It stays with the practice cabinet and is referenced from the month it belongs to. You can keep searching invoices while the file sits beside them.</p>
    </details>
    <details class="card">
      <summary>Can we move a workbook in mid-month?</summary>
      <p>Yes. Studios usually start with the open invoices only. Historical notes can follow once the current close is calm.</p>
    </details>
    <p style="margin-top:1.2rem"><a class="btn btn-primary" href="/#sign-in">Sign in</a></p>
  </div>
</section>
<?php ledger_end(); ?>
