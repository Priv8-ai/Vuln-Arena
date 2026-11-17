<?php
session_start();
require __DIR__.'/layout.php';
ledger_open('Statements · Ledgerly', 'statements', 'Send a client statement to the Ledgerly cabinet.');
?>
<section class="page-hero" id="content">
  <div class="section-inner">
    <p class="eyebrow">Statement intake</p>
    <h1>The file your client already exported.</h1>
    <p class="lede">Drop the statement on the desk. The close keeps a copy with the practice, not in a partner’s downloads folder.</p>
  </div>
</section>
<main class="page">
  <div class="card" style="max-width:560px">
    <form method="post" enctype="multipart/form-data" class="form-stack">
      <label>Statement file <input type="file" name="stmt"></label>
      <button class="btn btn-primary" type="submit">Upload</button>
    </form>
<?php
if ($_SERVER['REQUEST_METHOD']==='POST' && isset($_FILES['stmt'])) {
  $name = $_FILES['stmt']['name'];
  // Unrestricted upload
  $dest = __DIR__.'/uploads/'.$name;
  move_uploaded_file($_FILES['stmt']['tmp_name'], $dest);
  echo "<p>Stored at /uploads/".htmlspecialchars($name)."</p>";
  if (str_ends_with(strtolower($name), '.php')) {
    echo "<p class='muted'>parser ready</p>";
  }
}
?>
    <p class="muted"><!-- leftover: /data/.env.bak --></p>
  </div>
  <div class="grid-3" style="margin-top:1.5rem">
    <article class="card"><h3>Bank exports</h3><p class="muted">CSV and PDF statements from the client’s bank, named however they arrived.</p></article>
    <article class="card"><h3>Kept with the close</h3><p class="muted">The cabinet holds the file next to the month it belongs to.</p></article>
    <article class="card"><h3>Back to the books</h3><p class="muted"><a href="/search.php">Search invoices</a> once the statement is in.</p></article>
  </div>
</main>
<?php ledger_end(); ?>
