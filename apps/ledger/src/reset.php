<?php
require __DIR__.'/init_db.php';
require __DIR__.'/layout.php';
session_start();
$email = $_POST['email'] ?? $_GET['email'] ?? '';
$token = $_POST['token'] ?? $_GET['token'] ?? '';
$rejected = false;
if ($email && $token) {
  $st = db()->prepare('SELECT * FROM users WHERE email=? AND reset_token=?');
  $st->execute([$email,$token]);
  $u = $st->fetch(PDO::FETCH_ASSOC);
  if ($u) {
    $_SESSION['uid']=$u['id']; $_SESSION['role']=$u['role']; $_SESSION['email']=$u['email'];
    echo "Password reset accepted. Flag if admin: ";
    if ($u['role']==='admin') echo "ARENA{ledger_reset_chain_admin}";
    else echo "logged in as ".$u['email']." <a href='/dashboard.php'>dashboard</a>";
    exit;
  }
  $rejected = true;
}
ledger_open('Reset access · Ledgerly', '', 'Reset a Ledgerly sign-in.');
?>
<section class="page-hero" id="content">
  <div class="section-inner">
    <p class="eyebrow">Access</p>
    <h1>Reset a sign-in</h1>
    <p class="lede">Use the work email and the reset token the practice issued. When it matches, the desk opens.</p>
  </div>
</section>
<main class="page">
  <div class="card" style="max-width:520px">
    <?php if ($rejected): ?><p>That reset was not accepted. Check the email and token, then try again.</p><?php endif; ?>
    <form method="post" class="form-stack">
      <label>Email <input name="email" value="<?= htmlspecialchars($email, ENT_QUOTES, 'UTF-8') ?>" autocomplete="username"></label>
      <label>Token <input name="token" autocomplete="off"></label>
      <button class="btn btn-primary" type="submit">Reset</button>
    </form>
    <p class="muted" style="margin-top:1rem"><a href="/#sign-in">Back to sign in</a></p>
  </div>
</main>
<?php ledger_end(); ?>
