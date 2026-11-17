<?php
session_start();
if (empty($_SESSION['uid'])) { header('Location: /'); exit; }
require __DIR__.'/layout.php';
ledger_open('Desk · Ledgerly', 'desk', 'Your Ledgerly practice desk.');
?>
<section class="page-hero" id="content">
  <div class="section-inner">
    <p class="eyebrow">Ledger dashboard — <?= htmlspecialchars($_SESSION['email']) ?> (<?= htmlspecialchars($_SESSION['role']) ?>)</p>
    <h1>Your practice desk</h1>
    <p class="lede">Invoices for this sign-in, and the statement cabinet if a client file is still outstanding.</p>
  </div>
</section>
<main class="page">
  <div class="grid-3">
    <div class="card">Welcome. Open <a href="/invoices.php?user_id=<?= (int)$_SESSION['uid'] ?>">your invoices</a>.</div>
    <?php if (($_SESSION['role'] ?? '') === 'admin'): ?>
    <div class="card">Admin tools: <a href="/admin.php">panel</a></div>
    <?php endif; ?>
    <div class="card">
      <h3>Statements</h3>
      <p>Bring in the file a client already exported. <a href="/upload.php">Open statement intake</a>.</p>
    </div>
  </div>
  <div class="card" style="margin-top:1rem">
    <h3>While you are here</h3>
    <p class="muted">Search still reaches every note on the books, including months you have already signed.</p>
    <p><a href="/search.php">Search invoices</a> · <a href="/profile.php?id=2">Profiles</a></p>
  </div>
</main>
<?php ledger_end(); ?>
