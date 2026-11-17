<?php
require __DIR__.'/layout.php';
vault_open('The house · Lockbox', 'about', 'Lockbox is a custody desk for objects that should not live on a shared drive.');
?>
<section class="page-hero" id="content">
  <div class="section-inner">
    <hr class="gold-rule">
    <p class="eyebrow">The house</p>
    <h1>Opened for two chambers. Still a short list.</h1>
    <p class="lede">Lockbox began in 2021 as a place to put the memorandum that should not be mailed twice. The practice is the same: few objects, named clients, a person at the desk.</p>
  </div>
</section>
<section class="section">
  <div class="section-inner">
    <div class="grid-3">
      <article class="card feature reveal">
        <h3>Counsel</h3>
        <p>Briefs, retainers, and the draft you do not want in a thread. The locker is the record of what was sent.</p>
      </article>
      <article class="card feature reveal">
        <h3>Funds</h3>
        <p>Side letters and notices that administrators would rather pull from one list than from a directory of copies.</p>
      </article>
      <article class="card feature reveal">
        <h3>Family offices</h3>
        <p>The documents a principal asks for by name. Not a drive the whole household can reorganize.</p>
      </article>
    </div>
  </div>
</section>
<section class="section band">
  <div class="section-inner prose">
    <h2>The room</h2>
    <p>Upper room, Harbour House. Introductions come from a client the desk already knows. We do not keep a public waiting list, and we do not add a locker because a form was filled in overnight.</p>
    <p>If you already have a client id, <a href="/login.php">sign in</a>. If you are asking whether the house is a fit, write to custody@vaultlite.test.</p>
    <p><a class="btn btn-primary" href="/custody.php">Read the custody notes</a></p>
  </div>
</section>
<?php vault_end(); ?>
