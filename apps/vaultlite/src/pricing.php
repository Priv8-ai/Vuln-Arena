<?php
require __DIR__.'/layout.php';
vault_open('Retainers · Lockbox', 'pricing', 'Lockbox retainers for correspondence, counsel, and a named locker.');
?>
<section class="page-hero" id="content">
  <div class="section-inner">
    <hr class="gold-rule">
    <p class="eyebrow">Retainers</p>
    <h1>Priced like a desk, not a seat.</h1>
    <p class="lede">You are not billed for every associate who needs to read a letter. The retainer follows the locker: how sealed it is, and whether it has a name of its own.</p>
  </div>
</section>
<section class="section" style="padding-top:.4rem">
  <div class="section-inner">
    <div class="grid-3">
      <article class="card plan">
        <h3>Correspondence</h3>
        <span class="amount">$0</span>
        <span class="per">the welcome object</span>
        <ul>
          <li>A locker and a list</li>
          <li>The opening note</li>
          <li>Client sign-in</li>
        </ul>
        <a class="btn btn-ghost" href="/login.php">Sign in</a>
      </article>
      <article class="card plan is-featured">
        <span class="chip">Chambers</span>
        <h3>Counsel</h3>
        <span class="amount">$1,800</span>
        <span class="per">per quarter</span>
        <ul>
          <li>Intake for the matter</li>
          <li>Signatures from the desk</li>
          <li>An auditor door</li>
        </ul>
        <a class="btn btn-primary" href="/custody.php">See custody</a>
      </article>
      <article class="card plan">
        <h3>Partnership</h3>
        <span class="amount">$7,200</span>
        <span class="per">per quarter, named locker</span>
        <ul>
          <li>A locker in the client’s name</li>
          <li>House introduction</li>
          <li>A person who answers</li>
        </ul>
        <a class="btn btn-ghost" href="/about.php">Write the house</a>
      </article>
    </div>
  </div>
</section>
<section class="section band">
  <div class="section-inner prose">
    <h2>What is not on the invoice</h2>
    <p>Seats. Activity graphs. A second product for “sharing.” If an associate needs the memorandum, they use the client’s locker under a credential you issued, or they do not see it.</p>
    <p>Questions on a retainer: custody@vaultlite.test.</p>
  </div>
</section>
<?php vault_end(); ?>
