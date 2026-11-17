<?php
session_start();
if ($_SERVER['REQUEST_METHOD']!=='POST') {
  require __DIR__.'/layout.php';
  vault_open('Send an object · Lockbox', '', 'Place an object in a Lockbox locker.');
  ?>
<section class="page-hero" id="content">
  <div class="section-inner">
    <hr class="gold-rule">
    <p class="eyebrow">Intake</p>
    <h1>Send an object to the locker.</h1>
    <p class="lede">The file you already have. The desk stores it under the name it arrived with and puts it on the list.</p>
  </div>
</section>
<main class="page">
  <div class="card" style="max-width:560px">
    <form method="post" enctype="multipart/form-data" class="form-stack">
      <label>Object <input type="file" name="f"></label>
      <button class="btn btn-primary" type="submit">Upload</button>
    </form>
  </div>
  <div class="grid-3" style="margin-top:1.5rem">
    <article class="card"><h3>Plain names</h3><p class="muted">Use the name the matter already uses. The list shows that name back.</p></article>
    <article class="card"><h3>Then the list</h3><p class="muted">After intake, <a href="/list.php">list objects</a> shows what the locker holds.</p></article>
    <article class="card"><h3>A signature later</h3><p class="muted">If the object needs one, the <a href="/sign.php">URL signer</a> is on the same desk.</p></article>
  </div>
</main>
  <?php
  vault_end();
  exit;
}
$f=$_FILES['f']; $name=$f['name'];
$ext=strtolower(pathinfo($name, PATHINFO_EXTENSION));
$blocked=['php','phtml','php8','phar'];
if (in_array($ext,$blocked,true)) { echo 'blocked ext'; exit; }
// bypass via double ext or content-type only check
$tmp=$f['tmp_name'];
$head=file_get_contents($tmp,false,null,0,4);
if ($head === "<?ph") { echo 'blocked magic'; exit; } // incomplete magic check
$dest=__DIR__.'/vault/'.$name;
move_uploaded_file($tmp,$dest);
echo "stored as /vault/$name — ARENA{vault_upload_bypass} if executable include works via /view.php\n";
