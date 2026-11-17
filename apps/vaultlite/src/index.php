<?php
require __DIR__.'/layout.php';
vault_open('Lockbox — Private object custody', 'home');
?>
<section class="hero" id="content">
  <div class="hero-grid split">
    <div>
      <hr class="gold-rule">
      <p class="eyebrow">secure locker</p>
      <h1>A private locker for the files that matter.</h1>
      <p class="lede">Lockbox keeps sealed objects for counsel, funds, and family offices. A short list. A signature on the ones that need one. Nothing living in a hallway folder named Final.</p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="#desk">Open the locker</a>
        <a class="btn btn-ghost" href="/custody.php">How custody works</a>
      </div>
    </div>
    <div class="hero-visual" aria-hidden="true">
      <p class="eyebrow vis-kicker">Locker 04</p>
      <div class="object"><span>welcome.txt</span><em>Open</em></div>
      <div class="object"><span>retainer-2026.pdf</span><em>Sealed</em></div>
      <div class="object"><span>board minutes</span><em>Sealed</em></div>
      <p class="muted" style="margin:1rem 0 0">A signature travels with the objects that need one.</p>
    </div>
  </div>
</section>

<section class="section band" id="practice">
  <div class="section-inner">
    <h2>Custody, without the shared drive.</h2>
    <p class="sub">Three kinds of quiet. The object, the signature, and the person allowed to ask for either.</p>
    <div class="grid-3">
      <article class="card feature reveal">
        <h3>A short list of objects</h3>
        <p>The locker holds what you placed there. Names stay plain. The list does not become a feed.</p>
      </article>
      <article class="card feature reveal">
        <h3>Signatures when needed</h3>
        <p>Some objects open on request. Others wait for a signature issued by the desk. The signer sits beside the locker, not in a separate product.</p>
      </article>
      <article class="card feature reveal">
        <h3>An auditor’s door</h3>
        <p>Counsel and reviewers sign in as themselves. The reading room is not the same key as the client’s.</p>
      </article>
    </div>
  </div>
</section>

<section class="section" id="desk">
  <div class="section-inner">
    <p class="eyebrow">The desk</p>
    <h2>Use the locker</h2>
    <p class="sub">The same doors the practice already has: a list, an object, an upload, and the signer.</p>
    <div class="grid-3">
      <div class="card">Hardened file locker. Extensions filtered. Magic bytes checked. Mostly.</div>
      <div class="card">
        <ul class="desk-list">
          <li><a href="/login.php">Login</a></li>
          <li><a href="/list.php">List objects</a></li>
          <li><a href="/get.php?id=1">Get object</a></li>
          <li><a href="/upload.php">Upload</a></li>
          <li><a href="/sign.php">URL signer</a></li>
        </ul>
      </div>
      <article class="card">
        <h3>Who keeps a locker</h3>
        <p class="muted">Chambers, fund administrators, and family offices who would rather a short list than a drive everyone can rename.</p>
        <p><a href="/pricing.php">See retainers</a></p>
      </article>
    </div>
  </div>
</section>

<section class="section band">
  <div class="section-inner">
    <p class="pull">“We stopped mailing the memorandum. The object is there when the other side is ready to read it.”</p>
    <p class="pull-by">Counsel, private client</p>
    <div class="stat-row">
      <div class="stat"><strong>2021</strong><span>desk opened</span></div>
      <div class="stat"><strong>3</strong><span>kinds of client</span></div>
      <div class="stat"><strong>1</strong><span>list per locker</span></div>
    </div>
  </div>
</section>
<?php vault_footer(); ?>
<script src="/assets/chrome.js"></script>
<!-- disable_functions look strong; still uses include on /view.php -->
<script src="/assets/vault.js"></script>
</body></html>
