<?php

function vault_open(string $title, string $active = '', string $description = ''): void {
    if (session_status() !== PHP_SESSION_ACTIVE) {
        session_start();
    }
    if ($description === '') {
        $description = 'Lockbox is private object custody for counsel, funds, and family offices.';
    }
    $titleEsc = htmlspecialchars($title, ENT_QUOTES, 'UTF-8');
    $descEsc = htmlspecialchars($description, ENT_QUOTES, 'UTF-8');
    $items = [
        'home' => ['/', 'The locker'],
        'custody' => ['/custody.php', 'Custody'],
        'pricing' => ['/pricing.php', 'Retainers'],
        'about' => ['/about.php', 'The house'],
    ];
    $who = (string)($_SESSION['user'] ?? '');
    echo '<!doctype html><html lang="en" data-theme="vaultlite"><head>';
    echo '<meta charset="utf-8">';
    echo '<meta name="viewport" content="width=device-width, initial-scale=1">';
    echo '<meta name="theme-color" content="#0B0B0C">';
    echo '<title>' . $titleEsc . '</title>';
    echo '<meta name="description" content="' . $descEsc . '">';
    echo '<link rel="preconnect" href="https://fonts.googleapis.com">';
    echo '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>';
    echo '<link href="https://fonts.googleapis.com/css2?family=Newsreader:wght@400;500;600;700&family=Public+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">';
    echo '<link rel="stylesheet" href="/assets/chrome.css">';
    echo '<link rel="stylesheet" href="/assets/site.css">';
    echo '<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 32 32\'%3E%3Crect width=\'32\' height=\'32\' rx=\'6\' fill=\'%23C9A96A\'/%3E%3Ctext x=\'16\' y=\'22\' text-anchor=\'middle\' font-family=\'Georgia\' font-size=\'16\' fill=\'%2314110A\'%3EV%3C/text%3E%3C/svg%3E">';
    echo '</head><body>';
    echo '<a class="skip" href="#content">Skip to content</a>';
    echo '<nav class="site-nav" aria-label="Primary">';
    echo '<a class="brand" href="/"><span class="brand-mark">V</span> Lockbox</a>';
    echo '<div class="nav-links">';
    foreach ($items as $key => $item) {
        $cls = $active === $key ? ' class="is-active"' : '';
        $aria = $active === $key ? ' aria-current="page"' : '';
        echo '<a href="' . htmlspecialchars($item[0], ENT_QUOTES, 'UTF-8') . '"' . $cls . $aria . '>' . htmlspecialchars($item[1], ENT_QUOTES, 'UTF-8') . '</a>';
    }
    echo '</div>';
    if ($who !== '') {
        echo '<span class="chip">' . htmlspecialchars($who, ENT_QUOTES, 'UTF-8') . '</span>';
    } else {
        echo '<a class="nav-cta" href="/login.php">Sign in</a>';
    }
    echo '</nav>';
}

function vault_footer(): void {
    echo <<<'HTML'
<footer class="site-footer">
  <div class="footer-inner">
    <div>
      <a class="brand" href="/"><span class="brand-mark">V</span> Lockbox</a>
      <p>Private object custody for counsel, funds, and family offices. A short list. No shared drive.</p>
      <p>By introduction · Upper room, Harbour House</p>
    </div>
    <div>
      <h4>Locker</h4>
      <a href="/login.php">Login</a>
      <a href="/list.php">List objects</a>
      <a href="/get.php?id=1">Get object</a>
      <a href="/upload.php">Upload</a>
      <a href="/sign.php">URL signer</a>
    </div>
    <div>
      <h4>House</h4>
      <a href="/custody.php">Custody</a>
      <a href="/pricing.php">Retainers</a>
      <a href="/about.php">The house</a>
      <a href="/login.php">Sign in</a>
    </div>
  </div>
  <div class="section-inner legal">© 2026 Lockbox. Objects leave only with the client.</div>
</footer>
HTML;
}

function vault_end(): void {
    vault_footer();
    echo '<script src="/assets/chrome.js"></script></body></html>';
}
