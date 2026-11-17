<?php
require __DIR__.'/layout.php';
vault_open('Custody · Lockbox', 'custody', 'How Lockbox holds objects, signatures, and the client list.');
?>
<section class="page-hero" id="content">
  <div class="section-inner">
    <hr class="gold-rule">
    <p class="eyebrow">Custody</p>
    <h1>What the locker actually does.</h1>
    <p class="lede">An object is a file with a name. A locker is the list of those names for one client. A signature is how the desk marks an object that should not open on a bare request.</p>
  </div>
</section>
<section class="section" style="padding-top:.4rem">
  <div class="section-inner">
    <div class="grid-3">
      <article class="card reveal">
        <p class="eyebrow">01</p>
        <h3>Place</h3>
        <p>Send the file through intake. It is stored under the name it arrived with and appears on the list.</p>
        <p><a href="/upload.php">Upload</a></p>
      </article>
      <article class="card reveal">
        <p class="eyebrow">02</p>
        <h3>Read</h3>
        <p>The list is the index. Opening an object is a separate step, so a name on the list is not the same as handing over the file.</p>
        <p><a href="/list.php">List objects</a> · <a href="/get.php?id=1">Get object</a></p>
      </article>
      <article class="card reveal">
        <p class="eyebrow">03</p>
        <h3>Sign</h3>
        <p>When an object needs a mark from the desk, the signer issues it. The mark travels with the request to open.</p>
        <p><a href="/sign.php">URL signer</a></p>
      </article>
    </div>
  </div>
</section>
<section class="section band">
  <div class="section-inner prose">
    <h2>Who may ask</h2>
    <p>Clients and auditors sign in as themselves. The reading room is intentionally dull: a list, an object, a signature. There is no activity feed and no folder tree to wander.</p>
    <p>The sample object on a new locker is the welcome note. Everything after that is something you placed.</p>
    <p><a class="btn btn-primary" href="/login.php">Sign in</a> <a class="btn btn-ghost" href="/pricing.php">Retainers</a></p>
  </div>
</section>
<?php vault_end(); ?>
