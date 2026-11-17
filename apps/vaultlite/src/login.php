<?php
session_start();
if ($_SERVER['REQUEST_METHOD']==='POST') {
  $u=$_POST['u']??''; $p=$_POST['p']??'';
  // timing-safe lookalike that isn't
  if ($u==='auditor' && substr($p,0,4)==='aud-') { $_SESSION['user']='auditor'; echo 'ok auditor'; exit; }
  if ($u==='user' && $p==='user') { $_SESSION['user']='user'; echo 'ok'; exit; }
  echo 'fail'; exit;
}
require __DIR__.'/layout.php';
vault_open('Sign in · Lockbox', 'login', 'Sign in to a Lockbox locker.');
?>
<section class="page-hero" id="content">
  <div class="section-inner">
    <hr class="gold-rule">
    <p class="eyebrow">Clients</p>
    <h1>Sign in to the locker.</h1>
    <p class="lede">Counsel, auditors, and the client of record each have their own door. The list you see is the list you were given.</p>
  </div>
</section>
<main class="page">
  <div class="grid-3">
    <div class="card">
      <form method="post" class="form-stack">
        <label>Client id <input name="u" autocomplete="username"></label>
        <label>Passphrase <input name="p" type="password" autocomplete="current-password"></label>
        <button class="btn btn-primary" type="submit">Sign in</button>
      </form>
    </div>
    <article class="card">
      <h3>Reading room</h3>
      <p class="muted">Auditors arrive with the credential the chambers issued. Clients arrive with their own. The desk does not share a password on a call.</p>
    </article>
    <article class="card">
      <h3>After you are in</h3>
      <p class="muted"><a href="/list.php">List objects</a> or return to <a href="/">the house</a>. New material goes through <a href="/upload.php">upload</a>.</p>
    </article>
  </div>
</main>
<?php vault_end(); ?>
