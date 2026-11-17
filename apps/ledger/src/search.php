<?php
require __DIR__.'/init_db.php';
require __DIR__.'/layout.php';
$q = $_GET['q'] ?? '';
ledger_open('Search invoices · Ledgerly', 'search', 'Search invoice notes across the practice.');
?>
<section class="page-hero" id="content">
  <div class="section-inner">
    <p class="eyebrow">Invoice search</p>
    <h1>Find a note in the books</h1>
    <p class="lede">Vendor, month, or the line someone wrote when the invoice went out.</p>
    <form method="get" action="/search.php" class="form-stack wide" style="margin-top:1.2rem">
      <label>Search notes
        <input name="q" value="<?= $q ?>" placeholder="Vendor, month, or note">
      </label>
      <button class="btn btn-primary" type="submit">Search</button>
    </form>
  </div>
</section>
<main class="page">
<?php
if ($q !== '') {
  // Reflected XSS + SQLi via note search
  echo "<p>Results for: $q</p>";
  try {
    $sql = "SELECT id,note,amount FROM invoices WHERE note LIKE '%$q%'";
    foreach (db()->query($sql) as $r) {
      echo "<div class='card'>#{$r['id']} {$r['note']} — {$r['amount']}</div>";
    }
  } catch (Throwable $e) { echo "<pre>".$e->getMessage()."</pre>"; }
} else {
  echo '<p class="muted">Ask for a note and the matching invoices open here.</p>';
}
?>
</main>
<?php ledger_end(); ?>
